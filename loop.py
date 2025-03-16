"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

from anthropic import Anthropic, AnthropicBedrock, AnthropicVertex, APIResponse
from anthropic.types import (
    ToolResultBlockParam,
)
from anthropic.types.beta import (
    BetaContentBlock,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
)

from tools import BashTool, ComputerTool, EditTool, ToolCollection, ToolResult, WebSearchTool
from context_manager import apply_mcp, ConversationManager

# Beta flag for Claude 3.5 Sonnet
BETA_FLAG = "computer-use-2024-10-22"

# Tool types for Claude 3.5
COMPUTER_TOOL_2024 = "computer_20241022"
BASH_TOOL_2024 = "bash_20241022"
TEXT_EDITOR_TOOL_2024 = "text_editor_20241022"

# Tool types for Claude 3.7
COMPUTER_TOOL_2025 = "computer_20250124"  # This is not supported by Claude 3.7 based on the error
BASH_TOOL_2025 = "bash_20250124"
TEXT_EDITOR_TOOL_2025 = "text_editor_20250124"

class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


PROVIDER_TO_DEFAULT_MODEL_NAME: dict[APIProvider, str] = {
    APIProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
    APIProvider.BEDROCK: "anthropic.claude-3-5-sonnet-20241022-v2:0",
    APIProvider.VERTEX: "claude-3-5-sonnet-v2@20241022",
}

# Claude 3.7 Sonnet model names
CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
CLAUDE_3_7_SONNET_BEDROCK = "anthropic.claude-3-7-sonnet-20250219-v1:0"
CLAUDE_3_7_SONNET_VERTEX = "claude-3-7-sonnet-v1@20250219"

# This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
# SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
# * You are utilizing a macOS Sonoma 15.7 environment using {platform.machine()} architecture with internet access.
# * You can install applications using homebrew with your bash tool. Use curl instead of wget.
# * To open Chrome, please just click on the Chrome icon in the Dock or use Spotlight.
# * Using bash tool you can start GUI applications. GUI apps can be launched directly or with `open -a "Application Name"`. GUI apps will appear natively within macOS, but they may take some time to appear. Take a screenshot to confirm it did.
# * When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
# * When viewing a page it can be helpful to zoom out so that you can see everything on the page. In Chrome, use Command + "-" to zoom out or Command + "+" to zoom in.
# * When using your computer function calls, they take a while to run and send back to you. Where possible/feasible, try to chain multiple of these calls all into one function calls request.
# * The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
# </SYSTEM_CAPABILITY>
# <IMPORTANT>
# * When using Chrome, if any first-time setup dialogs appear, IGNORE THEM. Instead, click directly in the address bar and enter the appropriate search term or URL there.
# * If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext (available via homebrew) to convert it to a text file, and then read that text file directly with your StrReplaceEditTool.
# </IMPORTANT>"""
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilizing a macOS Sonoma 15.7 environment using {platform.machine()} architecture with command line internet access.
* Package management:
  - Use homebrew for package installation
  - Use curl for HTTP requests
  - Use npm/yarn for Node.js packages
  - Use pip for Python packages

* Browser automation available via Playwright:
  - Supports Chrome, Firefox, and WebKit
  - Can handle JavaScript-heavy applications
  - Capable of screenshots, navigation, and interaction
  - Handles dynamic content loading

* System automation:
  - cliclick for simulating mouse/keyboard input
  - osascript for AppleScript commands
  - launchctl for managing services
  - defaults for reading/writing system preferences

* Development tools:
  - Standard Unix/Linux command line utilities
  - Git for version control
  - Docker for containerization
  - Common build tools (make, cmake, etc.)

* Output handling:
  - For large output, redirect to tmp files: command > /tmp/output.txt
  - Use grep with context: grep -n -B <before> -A <after> <query> <filename>
  - Stream processing with awk, sed, and other text utilities

* Note: Command line function calls may have latency. Chain multiple operations into single requests where feasible.

* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>"""

async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlock], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[[APIResponse[BetaMessage]], None],
    error_callback: Callable[[Exception], None] = None,
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
    enable_thinking: bool = False,
    search_engine: str = "duckduckgo",
    enable_mcp: bool = False,
):
    """
    Run a sampling loop that calls the Anthropic API and processes the response.
    
    Args:
        model: The model to use (e.g. "claude-3-opus").
        provider: The API provider to use (e.g. "anthropic").
        system_prompt_suffix: Additional text to append to the system prompt.
        messages: The messages to send to the API.
        output_callback: Called for each content block received from the API.
        tool_output_callback: Called for each tool result.
        api_response_callback: Called for each API response.
        error_callback: Called for errors.
        api_key: The API key to use.
        only_n_most_recent_images: Only keep this many most recent images.
        max_tokens: Maximum number of tokens to generate.
        enable_thinking: Whether to enable the "thinking" beta feature.
        search_engine: The search engine to use for web searches (duckduckgo, google, bing).
        enable_mcp: Whether to enable Model Context Pruning.
    """
    try:
        # Apply Model Context Pruning if enabled
        if enable_mcp:
            messages = apply_mcp(messages)
            
        # Filter messages to only include the most recent images
        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(
                messages, only_n_most_recent_images
            )
        
        # Detect Claude 3.7 models
        is_claude_3_7 = "claude-3-7" in model.lower()

        # Initialize tool collection
        bash_tool = BashTool()
        computer_tool = ComputerTool()
        edit_tool = EditTool()
        web_search_tool = WebSearchTool(engine=search_engine)
        
        tools = {
            "bash": bash_tool,
            "computer": computer_tool,
            "str_replace_editor": edit_tool,
            "web_search": web_search_tool,
        }
        tool_collection = ToolCollection(tools=tools)
        
        # Set system prompt
        system_prompt = (
            f"You are Claude, an AI assistant created by Anthropic. You run on a user's computer "
            f"and can help by executing a variety of tools to take actions on a user's behalf. "
            f"Some specific capabilities include helping users by: "
            f"- Running shell commands on the user's computer "
            f"- Controlling the user's mouse and keyboard to navigate the OS "
            f"- Editing files on the user's computer. "
            f"- Searching the web for information. "
            f"When you perform a tool use, such as running a shell command, simply call the right "
            f"function with parameters directly, e.g. `bash(...)`. The user will see the result "
            f"of the command. "
            f"You can use the standard bash commands like ls, cat, nano etc. You'll get the output "
            f"and can use that to determine what to do next."
            f"\n\n{system_prompt_suffix}"
        )

        # Initialize the appropriate API client based on provider
        if provider == APIProvider.ANTHROPIC:
            client = Anthropic(api_key=api_key)
        elif provider == APIProvider.BEDROCK:
            client = AnthropicBedrock(
                aws_access_key=api_key.get("aws_access_key_id"),
                aws_secret_key=api_key.get("aws_secret_access_key"),
            )
        elif provider == APIProvider.VERTEX:
            client = AnthropicVertex()
        else:
            raise ValueError(f"Unsupported API provider: {provider}")
        
        # Set up API parameters
        api_params = {
            "max_tokens": max_tokens,
            "messages": messages,
            "model": model,
            "system": system_prompt
        }
            
        # Set the appropriate beta flag and tool configuration based on model
        if is_claude_3_7:
            # For Claude 3.7, don't use beta flags but use the 2025 tool types
            # api_params["betas"] = [BETA_FLAG_2025]  # Removing this line as it's causing the error
            
            # Configure tools with 2025 type identifiers
            api_params["tools"] = [
                # Removing this as it's not supported for Claude 3.7 Sonnet
                # {
                #    "type": COMPUTER_TOOL_2025,
                #    "name": "computer"
                # },
                {
                    "type": BASH_TOOL_2025,
                    "name": "bash"
                },
                {
                    "type": TEXT_EDITOR_TOOL_2025,
                    "name": "str_replace_editor"
                },
                {
                    "type": "custom",
                    "name": "web_search",
                    "description": "Search the web for information to answer questions about current events, facts, or any other topic.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string", 
                                "description": "The search query to look up on the web"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "Number of results to return (max 10)",
                                "default": 5
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            ]
        else:
            # For Claude 3.5, use 2024 beta flag and standard tool collection
            api_params["betas"] = [BETA_FLAG]
            
            # Configure tools with 2024 type identifiers
            api_params["tools"] = [
                {
                    "type": COMPUTER_TOOL_2024,
                    "name": "computer"
                },
                {
                    "type": BASH_TOOL_2024,
                    "name": "bash"
                },
                {
                    "type": TEXT_EDITOR_TOOL_2024,
                    "name": "str_replace_editor"
                },
                {
                    "type": "custom",
                    "name": "web_search",
                    "description": "Search the web for information to answer questions about current events, facts, or any other topic.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string", 
                                "description": "The search query to look up on the web"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "Number of results to return (max 10)",
                                "default": 5
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            ]
        
        # Add thinking parameter if it's Claude 3.7 Sonnet and thinking is enabled
        if enable_thinking and is_claude_3_7:
            # Set the thinking parameter with a budget based on AWS documentation
            thinking_budget = max(1024, max_tokens // 2)  # Use half of max_tokens as thinking budget
            api_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget
            }
        
        raw_response = client.beta.messages.with_raw_response.create(**api_params)

        api_response_callback(cast(APIResponse[BetaMessage], raw_response))

        response = raw_response.parse()

        messages.append(
            {
                "role": "assistant",
                "content": cast(list[BetaContentBlockParam], response.content),
            }
        )

        tool_result_content: list[BetaToolResultBlockParam] = []
        for content_block in cast(list[BetaContentBlock], response.content):
            print("CONTENT", content_block)
            output_callback(content_block)
            if content_block.type == "tool_use":
                try:
                    result = await tool_collection.run(
                        name=content_block.name,
                        tool_input=cast(dict[str, Any], content_block.input),
                    )
                except Exception as e:
                    # Handle tool execution errors
                    result = ToolResult(
                        error=f"Error executing tool {content_block.name}: {str(e)}",
                        system="Tool execution failed due to an internal error."
                    )
                
                tool_result_content.append(
                    _make_api_tool_result(result, content_block.id)
                )
                tool_output_callback(result, content_block.id)

        if not tool_result_content:
            return messages

        messages.append({"content": tool_result_content, "role": "user"})
        
    except Exception as e:
        print(f"Error in sampling loop: {str(e)}")
        if error_callback:
            error_callback(e)
        # Return current messages to avoid losing conversation history
        return messages


def _maybe_filter_to_n_most_recent_images(
    messages: list[BetaMessageParam],
    images_to_keep: int,
    min_removal_threshold: int = 10,
):
    """
    With the assumption that images are screenshots that are of diminishing value as
    the conversation progresses, remove all but the final `images_to_keep` tool_result
    images in place, with a chunk of min_removal_threshold to reduce the amount we
    break the implicit prompt cache.
    """
    if images_to_keep is None:
        return messages

    tool_result_blocks = cast(
        list[ToolResultBlockParam],
        [
            item
            for message in messages
            for item in (
                message["content"] if isinstance(message["content"], list) else []
            )
            if isinstance(item, dict) and item.get("type") == "tool_result"
        ],
    )

    total_images = sum(
        1
        for tool_result in tool_result_blocks
        for content in tool_result.get("content", [])
        if isinstance(content, dict) and content.get("type") == "image"
    )

    images_to_remove = total_images - images_to_keep
    # for better cache behavior, we want to remove in chunks
    images_to_remove -= images_to_remove % min_removal_threshold

    for tool_result in tool_result_blocks:
        if isinstance(tool_result.get("content"), list):
            new_content = []
            for content in tool_result.get("content", []):
                if isinstance(content, dict) and content.get("type") == "image":
                    if images_to_remove > 0:
                        images_to_remove -= 1
                        continue
                new_content.append(content)
            tool_result["content"] = new_content


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text
