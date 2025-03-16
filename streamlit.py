"""
Entrypoint for streamlit, see https://docs.streamlit.io/
"""

import asyncio
import base64
import os
import subprocess
from datetime import datetime
from enum import StrEnum
from functools import partial
from pathlib import PosixPath
from typing import cast
import time

import streamlit as st
from anthropic import APIResponse
from anthropic.types import (
    TextBlock,
)
from anthropic.types.beta import BetaMessage, BetaTextBlock, BetaToolUseBlock
from anthropic.types.tool_use_block import ToolUseBlock
from streamlit.delta_generator import DeltaGenerator

from loop import (
    PROVIDER_TO_DEFAULT_MODEL_NAME,
    APIProvider,
    sampling_loop,
    CLAUDE_3_7_SONNET,
    CLAUDE_3_7_SONNET_BEDROCK,
    CLAUDE_3_7_SONNET_VERTEX,
)
from tools import ToolResult
from dotenv import load_dotenv

load_dotenv()


CONFIG_DIR = PosixPath("~/.anthropic").expanduser()
API_KEY_FILE = CONFIG_DIR / "api_key"
STREAMLIT_STYLE = """
<style>
    /* Hide chat input while agent loop is running */
    .stApp[data-teststate=running] .stChatInput textarea,
    .stApp[data-test-script-state=running] .stChatInput textarea {
        display: none;
    }
     /* Hide the streamlit deploy button */
    .stDeployButton {
        visibility: hidden;
    }
</style>
"""

WARNING_TEXT = ""


class Sender(StrEnum):
    USER = "user"
    BOT = "assistant"
    TOOL = "tool"


def setup_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_key" not in st.session_state:
        # Try to load API key from file first, then environment
        st.session_state.api_key = load_from_storage("api_key") or os.getenv(
            "ANTHROPIC_API_KEY", ""
        )
    if "provider" not in st.session_state:
        st.session_state.provider = (
            os.getenv("API_PROVIDER", "anthropic") or APIProvider.ANTHROPIC
        )
    if "provider_radio" not in st.session_state:
        st.session_state.provider_radio = st.session_state.provider
    if "model" not in st.session_state:
        _reset_model()
    if "auth_validated" not in st.session_state:
        st.session_state.auth_validated = False
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "tools" not in st.session_state:
        st.session_state.tools = {}
    if "only_n_most_recent_images" not in st.session_state:
        st.session_state.only_n_most_recent_images = 10
    if "custom_system_prompt" not in st.session_state:
        st.session_state.custom_system_prompt = load_from_storage("system_prompt") or ""
    if "hide_images" not in st.session_state:
        st.session_state.hide_images = False
    if "enable_thinking" not in st.session_state:
        st.session_state.enable_thinking = False


def _reset_model():
    st.session_state.model = PROVIDER_TO_DEFAULT_MODEL_NAME[
        cast(APIProvider, st.session_state.provider)
    ]


def get_model_options(provider: APIProvider) -> list[str]:
    """Return available models for the selected provider"""
    if provider == APIProvider.ANTHROPIC:
        return [
            PROVIDER_TO_DEFAULT_MODEL_NAME[provider],
            CLAUDE_3_7_SONNET
        ]
    elif provider == APIProvider.BEDROCK:
        return [
            PROVIDER_TO_DEFAULT_MODEL_NAME[provider],
            CLAUDE_3_7_SONNET_BEDROCK
        ]
    elif provider == APIProvider.VERTEX:
        return [
            PROVIDER_TO_DEFAULT_MODEL_NAME[provider],
            CLAUDE_3_7_SONNET_VERTEX
        ]
    return [PROVIDER_TO_DEFAULT_MODEL_NAME[provider]]


def get_model_display_name(model_id: str) -> str:
    """Return a user-friendly display name for the model"""
    if model_id in [CLAUDE_3_7_SONNET, CLAUDE_3_7_SONNET_BEDROCK, CLAUDE_3_7_SONNET_VERTEX]:
        return "Claude 3.7 Sonnet (with thinking capability)"
    elif "claude-3-5" in model_id.lower():
        return "Claude 3.5 Sonnet"
    return model_id


async def main():
    """Run the Streamlit application."""
    st.set_page_config(page_title="Claude Computer Use", page_icon="🧠", layout="wide")
    st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)

    # Initialize session state for messages if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render the sidebar and get settings
    _render_sidebar()

    st.title("Claude Computer Use")

    # Display the chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:  # assistant
            with st.chat_message("assistant"):
                st.write(msg["content"])

    # Handle user inputs and generate responses
    prompt = st.chat_input("Send a message to Claude")
    if prompt:
        # Add user message to chat history
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get API settings from session state
        provider = APIProvider(st.session_state.provider)
        model = st.session_state.model
        enable_thinking = st.session_state.get("thinking", True)
        search_engine = st.session_state.get("search_engine", "duckduckgo")

        # Get API keys based on provider
        if provider == APIProvider.ANTHROPIC:
            api_key = st.session_state.get("anthropic_api_key", os.getenv("ANTHROPIC_API_KEY", ""))
        elif provider == APIProvider.BEDROCK:
            api_key = {
                "aws_access_key_id": st.session_state.get("aws_access_key_id", os.getenv("AWS_ACCESS_KEY_ID", "")),
                "aws_secret_access_key": st.session_state.get("aws_secret_access_key", os.getenv("AWS_SECRET_ACCESS_KEY", "")),
            }
        else:  # vertex
            api_key = st.session_state.get("google_api_key", os.getenv("GOOGLE_API_KEY", ""))

        # Display assistant response with spinner
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_text = ""
            tool_outputs = []

            st.markdown('<span data-teststate="running"></span>', unsafe_allow_html=True)

            # Callback for handling content updates
            def content_callback(content):
                nonlocal response_text
                if content.type == "text":
                    response_text += content.text
                    response_placeholder.write(response_text)
                elif hasattr(content, "type") and content.type == "thinking":
                    # Display thinking in a colored box
                    thinking_text = content.thinking
                    response_placeholder.markdown(
                        f"{response_text}\n\n"
                        f"<div style='background-color: #f0f0f0; padding: 10px; "
                        f"border-radius: 5px; margin: 10px 0;'>"
                        f"<details><summary><b>Claude's Thinking Process</b></summary>"
                        f"<pre style='white-space: pre-wrap;'>{thinking_text}</pre>"
                        f"</details></div>",
                        unsafe_allow_html=True
                    )

            # Callback for handling tool outputs
            def tool_callback(result, tool_use_id):
                nonlocal tool_outputs
                # Display the tool output
                if result.output:
                    tool_outputs.append(
                        {
                            "id": tool_use_id,
                            "type": "output",
                            "content": result.output
                        }
                    )
                    # Show tool outputs in a styled box
                    tool_output_html = "<div style='background-color: #e6f7ff; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
                    tool_output_html += "<details open><summary><b>Tool Output</b></summary>"
                    tool_output_html += "<pre style='white-space: pre-wrap;'>"
                    for output in tool_outputs:
                        tool_output_html += f"{output['content']}\n\n"
                    tool_output_html += "</pre></details></div>"
                    
                    response_placeholder.markdown(
                        f"{response_text}\n\n{tool_output_html}",
                        unsafe_allow_html=True
                    )
                
                # Handle image outputs
                if result.base64_image:
                    st.image(
                        base64.b64decode(result.base64_image),
                        caption="Generated Image",
                        use_column_width=True
                    )

            # Callback for API responses
            def api_response_callback(response):
                pass  # We can implement this later if needed

            # Callback for errors
            def error_callback(error):
                _display_error(error)

            try:
                # Build message history
                messages = [{"role": "user", "content": prompt}]

                # Call the sampling loop from loop.py
                await sampling_loop(
                    model=model,
                    provider=provider,
                    system_prompt_suffix=f"You are using the {search_engine} search engine for web searches.",
                    messages=messages,
                    output_callback=content_callback,
                    tool_output_callback=tool_callback,
                    api_response_callback=api_response_callback,
                    error_callback=error_callback,
                    api_key=api_key,
                    max_tokens=4096,
                    enable_thinking=enable_thinking,
                    search_engine=search_engine,
                )

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )

            except Exception as e:
                _display_error(e)

            finally:
                st.markdown('<span data-teststate="complete"></span>', unsafe_allow_html=True)


def validate_auth(provider: APIProvider, api_key: str | None):
    if provider == APIProvider.ANTHROPIC:
        if not api_key:
            return "Enter your Anthropic API key in the sidebar to continue."
    if provider == APIProvider.BEDROCK:
        import boto3

        if not boto3.Session().get_credentials():
            return "You must have AWS credentials set up to use the Bedrock API."
    if provider == APIProvider.VERTEX:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        if not os.environ.get("CLOUD_ML_REGION"):
            return "Set the CLOUD_ML_REGION environment variable to use the Vertex API."
        try:
            google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        except DefaultCredentialsError:
            return "Your google cloud credentials are not set up correctly."


def load_from_storage(filename: str) -> str | None:
    """Load data from a file in the storage directory."""
    try:
        file_path = CONFIG_DIR / filename
        if file_path.exists():
            data = file_path.read_text().strip()
            if data:
                return data
    except Exception as e:
        st.write(f"Debug: Error loading {filename}: {e}")
    return None


def save_to_storage(filename: str, data: str) -> None:
    """Save data to a file in the storage directory."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        file_path = CONFIG_DIR / filename
        file_path.write_text(data)
        # Ensure only user can read/write the file
        file_path.chmod(0o600)
    except Exception as e:
        st.write(f"Debug: Error saving {filename}: {e}")


def _api_response_callback(
    response: APIResponse[BetaMessage],
    tab: DeltaGenerator,
    response_state: dict[str, APIResponse[BetaMessage]],
):
    """
    Handle an API response by storing it to state and rendering it.
    """
    response_id = datetime.now().isoformat()
    response_state[response_id] = response
    _render_api_response(response, response_id, tab)


def _tool_output_callback(
    tool_output: ToolResult, tool_id: str, tool_state: dict[str, ToolResult]
):
    """Handle a tool output by storing it to state and rendering it."""
    tool_state[tool_id] = tool_output
    _render_message(Sender.TOOL, tool_output)


def _render_api_response(
    response: APIResponse[BetaMessage], response_id: str, tab: DeltaGenerator
):
    """Render an API response to a streamlit tab"""
    with tab:
        with st.expander(f"Request/Response ({response_id})"):
            newline = "\n\n"
            st.markdown(
                f"`{response.http_request.method} {response.http_request.url}`{newline}{newline.join(f'`{k}: {v}`' for k, v in response.http_request.headers.items())}"
            )
            st.json(response.http_request.read().decode())
            st.markdown(
                f"`{response.http_response.status_code}`{newline}{newline.join(f'`{k}: {v}`' for k, v in response.headers.items())}"
            )
            st.json(response.http_response.text)


def _render_message(
    sender: Sender,
    message: str | BetaTextBlock | BetaToolUseBlock | ToolResult,
):
    """Convert input from the user or output from the agent to a streamlit message."""
    # streamlit's hotreloading breaks isinstance checks, so we need to check for class names
    is_tool_result = not isinstance(message, str) and (
        isinstance(message, ToolResult)
        or message.__class__.__name__ == "ToolResult"
        or message.__class__.__name__ == "CLIResult"
    )
    if not message or (
        is_tool_result
        and st.session_state.hide_images
        and not hasattr(message, "error")
        and not hasattr(message, "output")
    ):
        return
    with st.chat_message(sender):
        if is_tool_result:
            message = cast(ToolResult, message)
            if message.output:
                if message.__class__.__name__ == "CLIResult":
                    st.code(message.output)
                else:
                    st.markdown(message.output)
            if message.error:
                st.error(message.error)
            if message.base64_image and not st.session_state.hide_images:
                st.image(base64.b64decode(message.base64_image))
        elif isinstance(message, BetaTextBlock) or isinstance(message, TextBlock):
            st.write(message.text)
        elif isinstance(message, BetaToolUseBlock) or isinstance(message, ToolUseBlock):
            st.code(f"Tool Use: {message.name}\nInput: {message.input}")
        else:
            st.markdown(message)


def _display_error(error: Exception):
    """Display error messages to the user in a friendly way."""
    error_msg = str(error)
    if "thinking.type: Field required" in error_msg:
        st.error("Error: There was an issue with the thinking feature. Try upgrading the Anthropic SDK to the latest version.")
    elif "thinking: Input tag" in error_msg and "does not match any of the expected tags" in error_msg:
        st.error("Error: Invalid thinking parameter format. This has been fixed in the latest version of the application.")
        st.info("Please restart the application to apply the fix.")
    elif "does not support tool types:" in error_msg and "Did you mean one of" in error_msg:
        st.error("Error: Claude 3.7 Sonnet requires newer tool types than what's currently configured.")
        st.info("This has been fixed in the latest version of the application. Please restart the application to apply the fix.")
    elif "Input tag 'computer_20250124' found using 'type' does not match any of the expected tags" in error_msg:
        st.error("Error: Claude 3.7 Sonnet does not support the 'computer_20250124' tool type.")
        st.info("This has been fixed in the latest version. Please restart the application to apply the fix.")
    elif "Unexpected value(s)" in error_msg and "for the anthropic-beta header" in error_msg:
        st.error("Error: Invalid beta flag for this model version.")
        st.info("This has been fixed in the latest version of the application. Please restart the application to apply the fix.")
    elif "invalid_api_key" in error_msg:
        st.error("Error: Invalid API key. Please check your API key in the sidebar.")
    elif "rate_limit_exceeded" in error_msg:
        st.error("Error: Rate limit exceeded. Please wait a moment and try again.")
    elif "model_not_available" in error_msg or "model_not_found" in error_msg:
        st.error(f"Error: The selected model ({st.session_state.model}) is not available. Please select a different model.")
    else:
        st.error(f"An error occurred: {error_msg}")
    
    # Log detailed error for debugging
    print(f"Error details: {error}")
    

def _render_sidebar():
    """Render the sidebar with options to configure the assistant."""
    st.sidebar.title("Settings")

    provider = st.sidebar.selectbox(
        "API Provider",
        ["anthropic", "bedrock", "vertex"],
        index=0,
        key="provider",
    )

    # Initialize session state for model if not present
    if "model" not in st.session_state:
        st.session_state.model = PROVIDER_TO_DEFAULT_MODEL_NAME[APIProvider(provider)]

    # Filter models based on provider
    if provider == "anthropic":
        models = ["claude-3-5-sonnet-20241022", "claude-3-7-sonnet-20250224"]
    elif provider == "bedrock":
        models = ["anthropic.claude-3-5-sonnet-20241022-v2:0", "anthropic.claude-3-7-sonnet-20250224:0"]
    else:  # vertex
        models = ["claude-3-5-sonnet-v2@20241022", "claude-3-7-sonnet@20250224"]

    # Replace if selected model is not valid for provider
    if st.session_state.model not in models:
        st.session_state.model = PROVIDER_TO_DEFAULT_MODEL_NAME[APIProvider(provider)]

    selected_model = st.sidebar.selectbox(
        "Model", models, index=models.index(st.session_state.model), key="model"
    )

    with st.sidebar.expander("API Keys", expanded=False):
        st.info(
            "Enter your API keys below. These will be stored in session state and not logged."
        )
        if provider == "anthropic":
            st.session_state.anthropic_api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value=st.session_state.get("anthropic_api_key", os.getenv("ANTHROPIC_API_KEY", "")),
                key="anthropic_api_key_input",
            )
        elif provider == "bedrock":
            st.session_state.aws_access_key_id = st.text_input(
                "AWS Access Key ID",
                type="password",
                value=st.session_state.get("aws_access_key_id", os.getenv("AWS_ACCESS_KEY_ID", "")),
                key="aws_access_key_id_input",
            )
            st.session_state.aws_secret_access_key = st.text_input(
                "AWS Secret Access Key",
                type="password",
                value=st.session_state.get("aws_secret_access_key", os.getenv("AWS_SECRET_ACCESS_KEY", "")),
                key="aws_secret_access_key_input",
            )
        elif provider == "vertex":
            st.session_state.google_api_key = st.text_input(
                "Google API Key",
                type="password",
                value=st.session_state.get("google_api_key", os.getenv("GOOGLE_API_KEY", "")),
                key="google_api_key_input",
            )

    with st.sidebar.expander("Web Search API Keys", expanded=False):
        st.info(
            "Enter your search engine API keys below. DuckDuckGo works without keys but has limited results."
        )
        st.session_state.search_engine = st.selectbox(
            "Search Engine",
            ["duckduckgo", "google", "bing"],
            index=0,
            key="search_engine",
        )
        
        if st.session_state.search_engine == "google":
            st.session_state.google_search_api_key = st.text_input(
                "Google Search API Key",
                type="password",
                value=st.session_state.get("google_search_api_key", os.getenv("GOOGLE_API_KEY", "")),
                key="google_search_api_key_input",
            )
            st.session_state.google_cx_id = st.text_input(
                "Google Custom Search CX ID",
                type="password",
                value=st.session_state.get("google_cx_id", os.getenv("GOOGLE_CX_ID", "")),
                key="google_cx_id_input",
            )
            # Update environment variables for web search tool
            os.environ["GOOGLE_API_KEY"] = st.session_state.google_search_api_key
            os.environ["GOOGLE_CX_ID"] = st.session_state.google_cx_id
            
        elif st.session_state.search_engine == "bing":
            st.session_state.bing_api_key = st.text_input(
                "Bing API Key",
                type="password",
                value=st.session_state.get("bing_api_key", os.getenv("BING_API_KEY", "")),
                key="bing_api_key_input",
            )
            # Update environment variable for web search tool
            os.environ["BING_API_KEY"] = st.session_state.bing_api_key

    with st.sidebar.expander("Advanced Options", expanded=False):
        st.session_state.thinking = st.toggle(
            "Enable Thinking",
            value=st.session_state.get("thinking", True),
            key="thinking_toggle",
        )
        st.markdown("*Note: Thinking is only available with Claude 3.7 Sonnet models.*")

    st.sidebar.divider()
    
    st.session_state.provider = provider
    
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    asyncio.run(main())
