"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
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

from tools import AppleScriptTool, BashTool, ComputerTool, EditTool, SiliconTool, ToolCollection, ToolResult

BETA_FLAG = "computer-use-2025-01-24"  # Updated to latest version


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# Updated model mappings to include Claude 3.7 and Claude 4
PROVIDER_TO_DEFAULT_MODEL_NAME: dict[APIProvider, str] = {
    APIProvider.ANTHROPIC: "claude-sonnet-4-20250514",  # Default to Claude 4 Sonnet
    APIProvider.BEDROCK: "us.anthropic.claude-sonnet-4-20250514-v1:0",  # Use cross-region inference profile
    APIProvider.VERTEX: "claude-sonnet-4@20250514",
}

# Available models by provider
AVAILABLE_MODELS: dict[APIProvider, list[tuple[str, str]]] = {
    APIProvider.ANTHROPIC: [
        ("claude-opus-4-20250514", "Claude Opus 4 - Most capable"),
        ("claude-sonnet-4-20250514", "Claude Sonnet 4 - High performance"),
        ("claude-3-7-sonnet-20250219", "Claude Sonnet 3.7 - With extended thinking"),
        ("claude-3-5-sonnet-20241022", "Claude Sonnet 3.5 v2 - Previous generation"),
        ("claude-3-5-haiku-20241022", "Claude Haiku 3.5 - Fast and efficient"),
        ("claude-3-opus-20240229", "Claude Opus 3 - Legacy"),
    ],
    APIProvider.BEDROCK: [
        ("us.anthropic.claude-opus-4-20250514-v1:0", "Claude Opus 4 - Most capable (Cross-Region)"),
        ("us.anthropic.claude-sonnet-4-20250514-v1:0", "Claude Sonnet 4 - High performance (Cross-Region)"),
        ("us.anthropic.claude-3-7-sonnet-20250219-v1:0", "Claude Sonnet 3.7 - With extended thinking (Cross-Region)"),
        ("us.anthropic.claude-3-5-sonnet-20241022-v2:0", "Claude Sonnet 3.5 v2 (Cross-Region)"),
        ("us.anthropic.claude-3-5-haiku-20241022-v1:0", "Claude Haiku 3.5 (Cross-Region)"),
        ("us.anthropic.claude-3-opus-20240229-v1:0", "Claude Opus 3 - Legacy (Cross-Region)"),
    ],
    APIProvider.VERTEX: [
        ("claude-opus-4@20250514", "Claude Opus 4 - Most capable"),
        ("claude-sonnet-4@20250514", "Claude Sonnet 4 - High performance"),
        ("claude-3-7-sonnet@20250219", "Claude Sonnet 3.7 - With extended thinking"),
        ("claude-3-5-sonnet-v2@20241022", "Claude Sonnet 3.5 v2"),
        ("claude-3-5-haiku@20241022", "Claude Haiku 3.5"),
        ("claude-3-opus@20240229", "Claude Opus 3 - Legacy"),
    ],
}

# Models that support extended thinking
EXTENDED_THINKING_MODELS = {
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514", 
    "claude-3-7-sonnet-20250219",
    "anthropic.claude-opus-4-20250514-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-3-7-sonnet-20250219-v1:0",
    "us.anthropic.claude-opus-4-20250514-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "claude-opus-4@20250514",
    "claude-sonnet-4@20250514",
    "claude-3-7-sonnet@20250219",
}

# Models that support token-efficient tools (Claude 3.7 only)
TOKEN_EFFICIENT_MODELS = {
    "claude-3-7-sonnet-20250219",
    "anthropic.claude-3-7-sonnet-20250219-v1:0",
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "claude-3-7-sonnet@20250219",
}

# Models that support interleaved thinking (Claude 4 only)
INTERLEAVED_THINKING_MODELS = {
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "anthropic.claude-opus-4-20250514-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-opus-4-20250514-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "claude-opus-4@20250514",
    "claude-sonnet-4@20250514",
}

# Max tokens by model - aligned with official Anthropic documentation
MODEL_MAX_TOKENS = {
    "claude-opus-4-20250514": 32000,     # Claude Opus 4: 32k max output
    "claude-sonnet-4-20250514": 64000,   # Claude Sonnet 4: 64k max output  
    "claude-3-7-sonnet-20250219": 64000, # Claude Sonnet 3.7: 64k max output
    "claude-3-5-sonnet-20241022": 8192,  # Claude Sonnet 3.5 v2: 8k max output
    "claude-3-5-sonnet-20240620": 8192,  # Claude Sonnet 3.5 v1: 8k max output
    "claude-3-5-haiku-20241022": 8192,   # Claude Haiku 3.5: 8k max output
    "claude-3-opus-20240229": 4096,      # Claude Opus 3: 4k max output
    "claude-3-haiku-20240307": 4096,     # Claude Haiku 3: 4k max output
}

# Extended thinking budget recommendations by model (up to 128k tokens for Claude 4)
RECOMMENDED_THINKING_BUDGETS = {
    "claude-opus-4-20250514": 128000,    # Claude Opus 4: Up to 128k thinking tokens
    "claude-sonnet-4-20250514": 128000,  # Claude Sonnet 4: Up to 128k thinking tokens
    "claude-3-7-sonnet-20250219": 64000, # Claude Sonnet 3.7: Up to 64k thinking tokens
    "claude-3-5-sonnet-20241022": 32000, # Claude Sonnet 3.5: Up to 32k thinking tokens
    "claude-3-5-haiku-20241022": 16000,  # Claude Haiku 3.5: Up to 16k thinking tokens
}

def get_max_tokens_for_model(model: str) -> int:
    """Get the maximum tokens for a given model."""
    # Extract base model name for Bedrock/Vertex models
    base_model = model
    if "us.anthropic." in model:
        # Handle cross-region inference profiles
        base_model = model.replace("us.anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "anthropic." in model:
        base_model = model.replace("anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "@" in model:
        base_model = model.split("@")[0]
        if base_model == "claude-3-5-sonnet-v2":
            base_model = "claude-3-5-sonnet-20241022"
        elif "-" in base_model and "@" not in base_model:
            # Handle format like claude-opus-4@20250514 -> claude-opus-4-20250514
            base_model = base_model.replace("@", "-")
    
    return MODEL_MAX_TOKENS.get(base_model, 4096)

def get_recommended_thinking_budget(model: str) -> int:
    """Get the recommended thinking budget for a given model."""
    # Extract base model name for Bedrock/Vertex models
    base_model = model
    if "us.anthropic." in model:
        base_model = model.replace("us.anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "anthropic." in model:
        base_model = model.replace("anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "@" in model:
        base_model = model.split("@")[0]
        if base_model == "claude-3-5-sonnet-v2":
            base_model = "claude-3-5-sonnet-20241022"
        elif "-" in base_model and "@" not in base_model:
            base_model = base_model.replace("@", "-")
    
    return RECOMMENDED_THINKING_BUDGETS.get(base_model, 10000)

def model_supports_extended_thinking(model: str) -> bool:
    """Check if a model supports extended thinking."""
    return model in EXTENDED_THINKING_MODELS

def model_supports_token_efficiency(model: str) -> bool:
    """Check if a model supports token-efficient tools (Claude 3.7 only)."""
    return model in TOKEN_EFFICIENT_MODELS

def model_supports_interleaved_thinking(model: str) -> bool:
    """Check if a model supports interleaved thinking (Claude 4 only)."""
    return model in INTERLEAVED_THINKING_MODELS

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
* You are utilizing a macOS environment using {platform.machine()} architecture with command line internet access.
* Package management:
  - Use homebrew for package installation
  - Use curl for HTTP requests
  - Use npm/yarn for Node.js packages
  - Use pip for Python packages

* System automation:
  - cliclick for simulating mouse/keyboard input
  - osascript for AppleScript commands (also available via dedicated applescript tool)
  - launchctl for managing services
  - defaults for reading/writing system preferences
  - AppleScript tool for high-level macOS application automation
  - shortcuts command for running macOS Shortcuts
  - system_profiler for detailed hardware information

* Apple Silicon optimizations (if available):
  - Unified memory architecture
  - Hardware-accelerated video/image processing
  - Native performance cores and efficiency cores

* Development tools:
  - Standard Unix/Linux command line utilities
  - Git for version control
  - Docker for containerization
  - Common build tools (make, cmake, etc.)

* Output handling:
  - For large output, redirect to tmp files: command > /tmp/output.txt
  - Use grep with context: grep -n -B <before> -A <after> <query> <filename>
  - Stream processing with awk, sed, and other text utilities

* Tool efficiency and parallel execution:
  - When multiple independent actions are needed, plan them upfront and execute together
  - Use screenshot tool to verify state before and after complex sequences
  - Chain related commands within single tool calls when possible
  - For file operations, prefer batch processing over individual operations

* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<CLAUDE_4_BEST_PRACTICES>
When approaching complex tasks:

1. **Be Explicit and Systematic**: Break down multi-step tasks into clear phases. State your plan before execution.

2. **Leverage Extended Thinking**: For complex reasoning, use thinking time to plan optimal approaches, especially for:
   - Multi-application workflows
   - System configuration changes
   - Debugging complex issues
   - File management operations

3. **Optimize Tool Usage**: 
   - Take screenshots strategically to understand current state
   - Use bash tool for multiple related commands in sequence
   - Leverage AppleScript for complex application automation
   - Prefer specific actions over general ones (e.g., cmd+c instead of right-click menu)

4. **Error Recovery**: 
   - Always verify successful completion with screenshots
   - Have fallback strategies for common failure modes
   - Use system monitoring tools to diagnose issues

5. **Context Awareness**:
   - Pay attention to application states and focus
   - Use appropriate delays (wait action) for UI transitions
   - Consider macOS-specific behaviors (e.g., dock hiding, spaces)

6. **Efficiency Patterns**:
   - Batch file operations when possible
   - Use keyboard shortcuts extensively (comprehensive Mac shortcuts available)
   - Prefer native macOS tools over third-party alternatives
   - Utilize Mission Control and Spaces for workspace management
</CLAUDE_4_BEST_PRACTICES>

<PARALLEL_EXECUTION_STRATEGIES>
For maximum efficiency:

* **Information Gathering**: When you need to check multiple things, gather all information in parallel:
  - Take screenshot + check system status + list files simultaneously
  - Use multiple bash commands in sequence within one tool call

* **Verification Steps**: After complex operations, verify success across multiple dimensions:
  - Visual confirmation (screenshot)
  - File system verification (ls, file commands)
  - Process verification (ps, system monitoring)

* **Multi-Application Tasks**: When working with multiple applications:
  - Plan the complete workflow across all applications
  - Use application switching shortcuts efficiently
  - Take state snapshots before major transitions
</PARALLEL_EXECUTION_STRATEGIES>"""

# Tool version mappings based on model capabilities
def get_tool_versions_for_model(model: str) -> dict[str, str]:
    """Get the appropriate tool versions for a given model."""
    # Claude 4 models (Opus and Sonnet) - Latest tool versions
    if any(claude4_model in model for claude4_model in ["claude-opus-4-", "claude-sonnet-4-"]):
        return {
            "computer": "computer_20250124",
            "text_editor": "text_editor_20250429",  # Updated for Claude 4
            "bash": "bash_20250124",
            "applescript": "custom",  # Custom tools always use "custom"
            "silicon": "custom",      # Custom tools always use "custom"
            "beta_flag": "computer-use-2025-01-24"
        }
    # Claude 3.7 Sonnet - Supports extended thinking with older text editor
    elif "claude-3-7-sonnet" in model:
        return {
            "computer": "computer_20250124",
            "text_editor": "text_editor_20250124",  # Claude 3.7 uses older version
            "bash": "bash_20250124",
            "applescript": "custom",  # Custom tools always use "custom"
            "silicon": "custom",      # Custom tools always use "custom"
            "beta_flag": "computer-use-2025-01-24"
        }
    # Claude 3.5 models (fallback to older versions)
    else:
        return {
            "computer": "computer_20241022",
            "text_editor": "text_editor_20241022",
            "bash": "bash_20241022",
            "applescript": "custom",  # Custom tools always use "custom"
            "silicon": "custom",      # Custom tools always use "custom"
            "beta_flag": "computer-use-2024-10-22"
        }

def get_beta_flags_for_model(model: str) -> list[str]:
    """Get all appropriate beta flags for a given model."""
    beta_flags = []
    
    # Get the primary tool beta flag
    tool_versions = get_tool_versions_for_model(model)
    beta_flags.append(tool_versions["beta_flag"])
    
    # Add token efficiency for Claude 3.7
    if model_supports_token_efficiency(model):
        beta_flags.append("token-efficient-tools-2025-02-19")
    
    # Add interleaved thinking for Claude 4
    if model_supports_interleaved_thinking(model):
        beta_flags.append("interleaved-thinking-2025-05-14")
    
    return beta_flags

def get_beta_flag_for_model(model: str) -> str:
    """Get the primary beta flag for a given model (backward compatibility)."""
    tool_versions = get_tool_versions_for_model(model)
    return tool_versions["beta_flag"]

async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlock], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[[APIResponse[BetaMessage]], None],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int | None = None,
    enable_extended_thinking: bool = False,
    thinking_budget_tokens: int = 10000,
    api_timeout: int = 120,
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    # Get appropriate tool versions for the model
    tool_versions = get_tool_versions_for_model(model)
    
    tool_collection = ToolCollection(
        ComputerTool(api_version=tool_versions["computer"]),
        BashTool(api_version=tool_versions["bash"]),
        EditTool(api_version=tool_versions["text_editor"]),
        AppleScriptTool(api_version=tool_versions["applescript"]),
        SiliconTool(api_version=tool_versions["silicon"]),
    )
    system = (
        f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}"
    )

    # Set default max_tokens based on model if not provided
    if max_tokens is None:
        max_tokens = get_max_tokens_for_model(model)

    while True:
        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(messages, only_n_most_recent_images)

        if provider == APIProvider.ANTHROPIC:
            # Enhanced timeout configuration using user-configurable timeout
            read_timeout = min(api_timeout * 0.8, api_timeout - 10)  # Leave buffer for processing
            client = Anthropic(
                api_key=api_key, 
                timeout=httpx.Timeout(
                    timeout=float(api_timeout),  # Total timeout from user setting
                    read=read_timeout,           # Read timeout with buffer
                    write=120.0,                 # 2 minute write timeout for large requests
                    connect=30.0                 # 30 second connect timeout
                )
            )
        elif provider == APIProvider.VERTEX:
            read_timeout = min(api_timeout * 0.8, api_timeout - 10)
            client = AnthropicVertex(
                timeout=httpx.Timeout(
                    timeout=float(api_timeout),
                    read=read_timeout,
                    write=120.0,
                    connect=30.0
                )
            )
        elif provider == APIProvider.BEDROCK:
            read_timeout = min(api_timeout * 0.8, api_timeout - 10)
            client = AnthropicBedrock(
                timeout=httpx.Timeout(
                    timeout=float(api_timeout),
                    read=read_timeout,
                    write=120.0,
                    connect=30.0
                )
            )

        # Prepare API call parameters
        api_params = {
            "max_tokens": max_tokens,
            "messages": messages,
            "model": model,
            "system": system,
            "tools": tool_collection.to_params(),
            "betas": get_beta_flags_for_model(model),
        }

        # Add extended thinking parameters if supported and enabled
        if enable_extended_thinking and model_supports_extended_thinking(model):
            # Use recommended thinking budget if not explicitly set
            if thinking_budget_tokens == 10000:  # Default value
                thinking_budget_tokens = get_recommended_thinking_budget(model)
            
            thinking_config = {
                "type": "enabled",
                "budget_tokens": thinking_budget_tokens
            }
            
            # For interleaved thinking models, allow budget to exceed max_tokens
            if model_supports_interleaved_thinking(model):
                # With interleaved thinking, budget can exceed max_tokens up to context window
                thinking_config["budget_tokens"] = min(thinking_budget_tokens, 200000)  # 200k context window limit
                
            api_params["thinking"] = thinking_config

        # Call the API with explicit stream=False and proper timeout to avoid SDK streaming recommendation
        # we use raw_response to provide debug information to streamlit. Your
        # implementation may be able call the SDK directly with:
        # `response = client.messages.create(...)` instead.
        api_params["stream"] = False
        
        try:
            raw_response = client.beta.messages.with_raw_response.create(**api_params)
        except (httpx.TimeoutException, httpx.ReadTimeout) as e:
            # Return timeout error in a format the UI can handle
            raise TimeoutError(f"API request timed out after {client.timeout} seconds. This can happen with complex tasks or when using Extended Thinking. Try reducing the thinking budget or simplifying your request.") from e
        except Exception as e:
            # Handle other API errors gracefully
            raise RuntimeError(f"API request failed: {str(e)}") from e
        
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
                result = await tool_collection.run(
                    name=content_block.name,
                    tool_input=cast(dict[str, Any], content_block.input),
                )
                tool_result_content.append(
                    _make_api_tool_result(result, content_block.id)
                )
                tool_output_callback(result, content_block.id)

        if not tool_result_content:
            return messages

        messages.append({"content": tool_result_content, "role": "user"})


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
