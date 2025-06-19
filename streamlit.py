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
    AVAILABLE_MODELS,
    APIProvider,
    sampling_loop,
    model_supports_extended_thinking,
    get_max_tokens_for_model,
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
    if "enable_extended_thinking" not in st.session_state:
        st.session_state.enable_extended_thinking = False
    if "thinking_budget_tokens" not in st.session_state:
        st.session_state.thinking_budget_tokens = 10000
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = None


def _reset_model():
    st.session_state.model = PROVIDER_TO_DEFAULT_MODEL_NAME[
        cast(APIProvider, st.session_state.provider)
    ]


async def main():
    """Render loop for streamlit"""
    setup_state()

    st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)

    st.title("🚀 Claude Computer Use for Mac")
    st.caption("Enhanced with Claude 3.7 & Claude 4 🧠")

    st.markdown("""
    This is an enhanced version of [Mac Computer Use](https://github.com/deedy/mac_computer_use), a fork of [Anthropic Computer Use](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/README.md) to work natively on Mac.
    
    **🆕 New Features:**
    - **Claude 4 Support** - Most capable models with up to 64k output tokens
    - **Extended Thinking** - Claude's step-by-step reasoning for complex tasks
    - **Smart Model Selection** - Easy switching between Claude 3.5, 3.7, and 4 models
    - **Enhanced UI** - Better model configuration and debugging tools
    
    **⚡ Quick Start:** Select Claude Sonnet 4 or Opus 4 from the sidebar for the best experience!
    """)
    
    # Show current model status
    current_model = st.session_state.get('model', 'Not selected')
    if model_supports_extended_thinking(current_model):
        st.success(f"🎯 **Current Model:** {current_model} (Extended Thinking Supported)")
    else:
        st.info(f"🎯 **Current Model:** {current_model}")
    

    with st.sidebar:

        def _reset_api_provider():
            if st.session_state.provider_radio != st.session_state.provider:
                _reset_model()
                st.session_state.provider = st.session_state.provider_radio
                st.session_state.auth_validated = False

        provider_options = [option.value for option in APIProvider]
        st.radio(
            "API Provider",
            options=provider_options,
            key="provider_radio",
            format_func=lambda x: x.title(),
            on_change=_reset_api_provider,
        )

        # Model selection with dropdown
        available_models = AVAILABLE_MODELS.get(st.session_state.provider, [])
        model_options = [model[0] for model in available_models]
        model_descriptions = {model[0]: model[1] for model in available_models}
        
        if st.session_state.model not in model_options and model_options:
            st.session_state.model = model_options[0]
        
        selected_model = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(st.session_state.model) if st.session_state.model in model_options else 0,
            format_func=lambda x: f"{x} - {model_descriptions.get(x, '')}",
            key="model_selector"
        )
        
        if selected_model != st.session_state.model:
            st.session_state.model = selected_model
            # Reset max_tokens when model changes
            st.session_state.max_tokens = None
        
        # Show model capabilities
        if model_supports_extended_thinking(st.session_state.model):
            st.success("✨ This model supports Extended Thinking")
        
        max_tokens_for_model = get_max_tokens_for_model(st.session_state.model)
        st.info(f"📊 Max output tokens: {max_tokens_for_model:,}")
        
        # Allow manual model entry for advanced users
        with st.expander("🔧 Advanced: Custom Model"):
            custom_model = st.text_input(
                "Enter custom model name",
                value=st.session_state.model,
                help="For advanced users who want to specify a custom model name"
            )
            if custom_model != st.session_state.model:
                st.session_state.model = custom_model

        if st.session_state.provider == APIProvider.ANTHROPIC:
            st.text_input(
                "Anthropic API Key",
                type="password",
                key="api_key",
                on_change=lambda: save_to_storage("api_key", st.session_state.api_key),
            )

        # Extended Thinking Configuration
        if model_supports_extended_thinking(st.session_state.model):
            with st.expander("🧠 Extended Thinking Settings", expanded=False):
                st.checkbox(
                    "Enable Extended Thinking",
                    key="enable_extended_thinking",
                    help="Enable Claude's step-by-step reasoning process for complex tasks"
                )
                
                if st.session_state.enable_extended_thinking:
                    st.slider(
                        "Thinking Budget (tokens)",
                        min_value=1024,
                        max_value=32000,
                        value=st.session_state.thinking_budget_tokens,
                        step=1024,
                        key="thinking_budget_tokens",
                        help="Maximum tokens Claude can use for internal reasoning"
                    )
                    st.info("💡 Higher budgets allow more thorough analysis but increase latency and cost")

        # Advanced Settings
        with st.expander("⚙️ Advanced Settings", expanded=False):
            # Max tokens override
            default_max_tokens = get_max_tokens_for_model(st.session_state.model)
            st.number_input(
                "Max Output Tokens",
                min_value=1000,
                max_value=default_max_tokens,
                value=st.session_state.max_tokens or default_max_tokens,
                step=1000,
                key="max_tokens",
                help=f"Maximum tokens for output (model default: {default_max_tokens:,})"
            )
            
            st.number_input(
                "Only send N most recent images",
                min_value=0,
                key="only_n_most_recent_images",
                help="To decrease the total tokens sent, remove older screenshots from the conversation",
            )
            
            st.text_area(
                "Custom System Prompt Suffix",
                key="custom_system_prompt",
                help="Additional instructions to append to the system prompt. see computer_use_demo/loop.py for the base system prompt.",
                on_change=lambda: save_to_storage(
                    "system_prompt", st.session_state.custom_system_prompt
                ),
            )
            
            st.checkbox("Hide screenshots", key="hide_images")

        if st.button("Reset", type="primary"):
            with st.spinner("Resetting..."):
                st.session_state.clear()
                setup_state()

                subprocess.run("pkill Xvfb; pkill tint2", shell=True)  # noqa: ASYNC221
                await asyncio.sleep(1)
                subprocess.run("./start_all.sh", shell=True)  # noqa: ASYNC221

    if not st.session_state.auth_validated:
        if auth_error := validate_auth(
            st.session_state.provider, st.session_state.api_key
        ):
            st.warning(f"Please resolve the following auth issue:\n\n{auth_error}")
            return
        else:
            st.session_state.auth_validated = True

    chat, http_logs = st.tabs(["Chat", "HTTP Exchange Logs"])
    new_message = st.chat_input(
        "Type a message to send to Claude to control the computer..."
    )

    with chat:
        # render past chats
        for message in st.session_state.messages:
            if isinstance(message["content"], str):
                _render_message(message["role"], message["content"])
            elif isinstance(message["content"], list):
                for block in message["content"]:
                    # the tool result we send back to the Anthropic API isn't sufficient to render all details,
                    # so we store the tool use responses
                    if isinstance(block, dict) and block["type"] == "tool_result":
                        _render_message(
                            Sender.TOOL, st.session_state.tools[block["tool_use_id"]]
                        )
                    elif isinstance(block, dict) and block.get("type") in ["thinking", "redacted_thinking"]:
                        # Handle thinking blocks
                        _render_message(message["role"], block)
                    else:
                        _render_message(
                            message["role"],
                            cast(BetaTextBlock | BetaToolUseBlock, block),
                        )

        # render past http exchanges
        for identity, response in st.session_state.responses.items():
            _render_api_response(response, identity, http_logs)

        # render past chats
        if new_message:
            st.session_state.messages.append(
                {
                    "role": Sender.USER,
                    "content": [TextBlock(type="text", text=new_message)],
                }
            )
            _render_message(Sender.USER, new_message)

        try:
            most_recent_message = st.session_state["messages"][-1]
        except IndexError:
            return

        if most_recent_message["role"] is not Sender.USER:
            # we don't have a user message to respond to, exit early
            return

        with st.spinner("Running Agent..."):
            # run the agent sampling loop with the newest message
            st.session_state.messages = await sampling_loop(
                system_prompt_suffix=st.session_state.custom_system_prompt,
                model=st.session_state.model,
                provider=st.session_state.provider,
                messages=st.session_state.messages,
                output_callback=partial(_render_message, Sender.BOT),
                tool_output_callback=partial(
                    _tool_output_callback, tool_state=st.session_state.tools
                ),
                api_response_callback=partial(
                    _api_response_callback,
                    tab=http_logs,
                    response_state=st.session_state.responses,
                ),
                api_key=st.session_state.api_key,
                only_n_most_recent_images=st.session_state.only_n_most_recent_images,
                max_tokens=st.session_state.max_tokens,
                enable_extended_thinking=st.session_state.enable_extended_thinking,
                thinking_budget_tokens=st.session_state.thinking_budget_tokens,
            )


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
    
    # Check for thinking blocks
    is_thinking_block = (hasattr(message, 'type') and getattr(message, 'type') == 'thinking') or \
                       (isinstance(message, dict) and message.get('type') == 'thinking')
    is_redacted_thinking = (hasattr(message, 'type') and getattr(message, 'type') == 'redacted_thinking') or \
                          (isinstance(message, dict) and message.get('type') == 'redacted_thinking')
    
    if not message or (
        is_tool_result
        and st.session_state.hide_images
        and not hasattr(message, "error")
        and not hasattr(message, "output")
    ):
        return
        
    with st.chat_message(sender):
        if is_thinking_block:
            # Render thinking blocks with special styling
            thinking_content = getattr(message, 'thinking', '')
            # Estimate token count for thinking content (rough approximation)
            estimated_tokens = len(thinking_content.split()) * 1.3 if thinking_content else 0
            
            with st.expander(f"🧠 Claude's Thinking Process (~{int(estimated_tokens)} tokens)", expanded=False):
                if thinking_content:
                    st.markdown(thinking_content)
                else:
                    st.info("Thinking content not available (may be summarized)")
                if hasattr(message, 'signature'):
                    st.caption("✅ Verified thinking block")
        elif is_redacted_thinking:
            # Render redacted thinking blocks
            with st.expander("🧠 Claude's Thinking Process (Redacted)", expanded=False):
                st.info("Some of Claude's internal reasoning has been automatically encrypted for safety reasons. This doesn't affect the quality of responses.")
        elif is_tool_result:
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


if __name__ == "__main__":
    asyncio.run(main())
