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
* You are utilizing a macOS Sequoia 15.6 Beta environment on {platform.machine()} architecture (Apple M4) with command line internet access.
* Hardware specifications:
  - Apple M4 chip with 4 performance cores and 6 efficiency cores
  - Unified memory architecture for optimal performance
  - Enhanced GPU with hardware acceleration
  - Neural Engine for ML workloads
  - Advanced thermal management

* Package management:
  - Use homebrew for package installation (brew install)
  - Use curl for HTTP requests (preferred over wget)
  - Use npm/yarn for Node.js packages
  - Use pip for Python packages

* System automation and M4 optimizations:
  - cliclick for precise mouse/keyboard input (M4-optimized timing)
  - osascript for AppleScript commands (also available via dedicated applescript tool)
  - launchctl for managing services
  - defaults for reading/writing system preferences
  - AppleScript tool for high-level macOS application automation
  - shortcuts command for running macOS Shortcuts
  - system_profiler for detailed hardware information
  - pmset for power and thermal management

* macOS Sequoia 15.6 Beta specific features:
  - Enhanced Safari with improved form handling
  - Better WebKit performance and compatibility
  - Improved accessibility features
  - Enhanced autofill and form detection
  - Better thermal management on M4

* Apple Silicon M4 optimizations:
  - Unified memory architecture (no separate GPU memory)
  - Hardware-accelerated video/image processing
  - Native performance cores for demanding tasks
  - Efficiency cores for background operations
  - Enhanced machine learning acceleration
  - Improved energy efficiency

* Development tools:
  - Standard Unix/Linux command line utilities
  - Git for version control
  - Docker for containerization (Apple Silicon native)
  - Common build tools (make, cmake, etc.)
  - Xcode command line tools

* Output handling and performance:
  - For large output, redirect to tmp files: command > /tmp/output.txt
  - Use grep with context: grep -n -B <before> -A <after> <query> <filename>
  - Stream processing with awk, sed, and other text utilities
  - Prefer batch operations for better M4 performance

* Tool efficiency and parallel execution:
  - When multiple independent actions are needed, plan them upfront and execute together
  - Use screenshot tool to verify state before and after complex sequences
  - Chain related commands within single tool calls when possible
  - For file operations, prefer batch processing over individual operations
  - Leverage M4's parallel processing capabilities

* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<MACBOOK_AIR_M4_BEST_PRACTICES>
Hardware-Specific Optimizations:

1. **Thermal Awareness**: Monitor system thermal state during intensive operations
   - Use pmset -g therm to check thermal conditions
   - Reduce operation frequency if thermal pressure is high
   - Leverage efficiency cores for background tasks

2. **Memory Efficiency**: Optimize for unified memory architecture
   - Be mindful of memory usage across CPU/GPU operations
   - Use memory-mapped files for large data processing
   - Leverage the Neural Engine for appropriate workloads

3. **Performance Core Utilization**: 
   - Use performance cores for demanding interactive tasks
   - Schedule batch operations during low-activity periods
   - Monitor CPU usage with Activity Monitor or top command

4. **Display Optimization**: M4 MacBook Air specific resolutions
   - 13-inch: 2560 x 1664 native resolution
   - 15-inch: 3024 x 1964 native resolution
   - Account for Retina scaling in coordinate calculations
   - Use high-DPI aware screenshot operations
</MACBOOK_AIR_M4_BEST_PRACTICES>

<SEQUOIA_FORM_INTERACTION_STRATEGIES>
Enhanced Web Form Automation for macOS Sequoia 15.6 Beta:

1. **Form Field Detection and Interaction**:
   - Use enhanced accessibility features in Sequoia
   - Leverage improved Safari form handling
   - Employ smart field detection with multiple fallback methods
   - Account for improved autofill behavior

2. **Input Method Selection**:
   - Text fields: Enhanced triple-click selection + type method
   - Dropdowns: Click-wait-select with keyboard navigation fallback
   - Radio buttons: Precise center-click with state verification
   - Checkboxes: Center-click with checked state validation
   - Buttons: Center-click with action result verification

3. **Error Recovery Patterns**:
   - Field focus issues: Use tab navigation to ensure proper focus
   - Input validation: Check for error states after input
   - Form submission: Verify form state before attempting submission
   - Dialog handling: Enhanced escape and dismissal strategies

4. **Sequoia-Specific Enhancements**:
   - Leverage improved WebKit form element detection
   - Use enhanced Safari autofill integration
   - Account for better form validation feedback
   - Utilize improved accessibility tree navigation

5. **M4-Optimized Timing**:
   - Reduced click delays (50ms vs 100ms)
   - Faster typing with larger chunk sizes (75 vs 50 characters)
   - Optimized screenshot timing (600ms vs 800ms)
   - Enhanced scroll responsiveness (2x multiplier)
</SEQUOIA_FORM_INTERACTION_STRATEGIES>

<CLAUDE_4_BEST_PRACTICES>
When approaching complex tasks on M4 MacBook Air with Sequoia, follow these enhanced Claude 4 principles:

1. **Be Explicit and Systematic**: Claude 4 responds best to clear, explicit instructions. Break down multi-step tasks into clear phases and state your plan before execution. Be specific about desired outputs and behaviors. When you want comprehensive results, explicitly request "Include as many relevant features and interactions as possible. Go beyond the basics."

2. **Leverage Extended Thinking Strategically**: Use thinking time to plan optimal approaches, especially for:
   - Multi-application workflows requiring careful sequencing
   - System configuration changes with potential side effects
   - Complex debugging with multiple potential failure points
   - Form automation sequences requiring validation
   - Analysis tasks requiring step-by-step reasoning
   
   After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding.

3. **Optimize Parallel Tool Execution**: For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially. Claude 4 excels at parallel tool execution with near 100% success rate when prompted to do so.

4. **Enhanced Error Recovery and Verification**: 
   - After each step, take a screenshot and carefully evaluate if you have achieved the right outcome
   - Explicitly show your thinking: "I have evaluated step X and confirmed [specific result]"
   - If not correct, try again with alternative approaches
   - Only when you confirm a step was executed correctly should you move on
   - Implement progressive retry strategies with different methods

5. **Context-Aware Thermal and Performance Management**:
   - Monitor M4 thermal state during intensive operations
   - Use appropriate delays optimized for M4 performance characteristics
   - Leverage Sequoia's enhanced form handling and accessibility features
   - Account for unified memory architecture benefits in tool chaining

6. **Advanced Tool Coordination**:
   - Use keyboard shortcuts extensively (comprehensive Mac shortcuts database available)
   - Chain multiple related commands within single tool calls when possible
   - Prefer native macOS tools and leverage AppleScript for complex automation
   - Utilize Mission Control and Spaces for efficient workspace management
   - Apply M4-specific optimizations for timing and thermal awareness
</CLAUDE_4_BEST_PRACTICES>

<PARALLEL_EXECUTION_STRATEGIES>
For maximum efficiency on M4 hardware:

* **Information Gathering**: When you need to check multiple things, gather all information in parallel:
  - Take screenshot + check system status + list files simultaneously
  - Use multiple bash commands in sequence within one tool call
  - Leverage M4's multi-core architecture for concurrent operations

* **Verification Steps**: After complex operations, verify success across multiple dimensions:
  - Visual confirmation (screenshot)
  - File system verification (ls, file commands)
  - Process verification (ps, system monitoring)
  - Thermal state monitoring (pmset -g therm)

* **Multi-Application Tasks**: When working with multiple applications:
  - Plan the complete workflow across all applications
  - Use application switching shortcuts efficiently
  - Take state snapshots before major transitions
  - Utilize Spaces and Mission Control for organization

* **Performance Monitoring**: Continuously monitor M4 performance:
  - Check thermal state before intensive operations
  - Monitor memory usage during large operations
  - Use Activity Monitor for resource tracking
  - Adjust operation timing based on system load
</PARALLEL_EXECUTION_STRATEGIES>

<FORM_TESTING_BEST_PRACTICES>
Optimized strategies for testing forms like the Burial Allowance application:

1. **Test Case Execution**:
   - Read all test cases upfront to plan execution strategy
   - Group related test cases for efficient batch execution
   - Use screenshots to document test results
   - Maintain test state consistency between cases

2. **Form Field Interaction**:
   - Always verify field focus before input
   - Use clear-and-type pattern for reliable text entry
   - Validate input acceptance after each field
   - Handle conditional field display (show/hide logic)

3. **Navigation and State Management**:
   - Take screenshots at key navigation points
   - Verify section transitions work correctly
   - Test back/forward navigation
   - Validate form persistence across sections

4. **Error Handling and Validation**:
   - Test both valid and invalid input scenarios
   - Verify error message display and formatting
   - Test field validation timing (immediate vs on-submit)
   - Validate required field enforcement

5. **Cross-Browser and Performance Testing**:
   - Test in Safari (primary) with Sequoia enhancements
   - Verify form performance on M4 hardware
   - Test with different screen resolutions
   - Validate accessibility features work correctly
</FORM_TESTING_BEST_PRACTICES>

<CLAUDE_4_TESTING_OPTIMIZATION>
When conducting systematic testing (especially form testing):

1. **Plan Before Execution**: Use thinking time to analyze all test cases upfront and create an optimal execution strategy. Group related tests and identify dependencies.

2. **Explicit Step Verification**: After each step, take a screenshot and carefully evaluate if you have achieved the right outcome. Explicitly show your thinking: "I have evaluated step X and confirmed [specific result]." If not correct, try again. Only when you confirm a step was executed correctly should you move on to the next one.

3. **Parallel Tool Execution**: For maximum efficiency, whenever you need to perform multiple independent operations (like checking multiple form fields or taking multiple screenshots), invoke all relevant tools simultaneously rather than sequentially.

4. **Form-Specific Strategies**:
   - Use enhanced click-clear-type patterns for text fields
   - Verify field state after each input operation  
   - Test validation messages and error states systematically
   - Document unexpected behaviors with screenshots
   - Use keyboard shortcuts when mouse interactions fail

5. **Test Documentation**: Create comprehensive test reports including:
   - Screenshots of key states and transitions
   - Clear pass/fail status for each test case
   - Detailed failure analysis with reproduction steps
   - Performance observations and recommendations

6. **Error Recovery**: When tests fail, use thinking time to analyze the failure mode and implement systematic retry strategies with different approaches.
</CLAUDE_4_TESTING_OPTIMIZATION>"""

# Tool version mappings based on model capabilities
def get_tool_versions_for_model(model: str) -> dict[str, str]:
    """Get the appropriate tool versions for a given model."""
    # Extract base model name for Bedrock/Vertex models
    base_model = model
    if "us.anthropic." in model:
        # Handle cross-region inference profiles like us.anthropic.claude-sonnet-4-20250514-v1:0
        base_model = model.replace("us.anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "anthropic." in model:
        base_model = model.replace("anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "@" in model:
        # Handle Vertex format like claude-sonnet-4@20250514
        parts = model.split("@")
        base_model = parts[0]
        if len(parts) > 1:
            # Reconstruct with date
            base_model = f"{base_model}-{parts[1]}"
        if base_model == "claude-3-5-sonnet-v2":
            base_model = "claude-3-5-sonnet-20241022"
    
    # Claude 4 models (Opus and Sonnet) - Latest tool versions with enhanced features
    if any(claude4_model in base_model for claude4_model in ["claude-opus-4-", "claude-sonnet-4-"]):
        return {
            "computer": "computer_20250124",
            "text_editor": "text_editor_20250429",  # Claude 4 gets the latest text editor version
            "bash": "bash_20250124",
            "applescript": "custom",  # Custom tools always use "custom"
            "silicon": "custom",      # Custom tools always use "custom"
            "beta_flag": "computer-use-2025-01-24"
        }
    # Claude 3.7 Sonnet - Supports extended thinking with token-efficient tools
    elif "claude-3-7-sonnet" in base_model:
        return {
            "computer": "computer_20250124",
            "text_editor": "text_editor_20250124",  # Claude 3.7 uses this version for token efficiency
            "bash": "bash_20250124",
            "applescript": "custom",  # Custom tools always use "custom"
            "silicon": "custom",      # Custom tools always use "custom"
            "beta_flag": "computer-use-2025-01-24"
        }
    # Claude 3.5 models (fallback to older but stable versions)
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
    
    # Add token efficiency for Claude 3.7 FIRST (most important for performance)
    if model_supports_token_efficiency(model):
        beta_flags.append("token-efficient-tools-2025-02-19")
    
    # Add interleaved thinking for Claude 4 FIRST (most important for performance)
    if model_supports_interleaved_thinking(model):
        beta_flags.append("interleaved-thinking-2025-05-14")
    
    # Get the primary tool beta flag LAST (required but less performance critical)
    tool_versions = get_tool_versions_for_model(model)
    beta_flags.append(tool_versions["beta_flag"])
    
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
    enable_interleaved_thinking: bool = False,
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

        # Enable interleaved thinking for Claude 4 if requested
        if enable_interleaved_thinking and model_supports_interleaved_thinking(model):
            # Ensure interleaved thinking beta flag is included
            beta_flags = api_params["betas"]
            if "interleaved-thinking-2025-05-14" not in beta_flags:
                beta_flags.append("interleaved-thinking-2025-05-14")
            api_params["betas"] = beta_flags

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
        except (httpx.TimeoutException, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            # Enhanced timeout error handling based on Anthropic best practices
            timeout_duration = getattr(client, 'timeout', api_timeout)
            thinking_info = ""
            if enable_extended_thinking:
                thinking_info = f" (Extended thinking budget: {thinking_budget_tokens:,} tokens)"
            
            # Provide specific guidance for large thinking budgets
            batch_recommendation = ""
            if thinking_budget_tokens > 32000:
                batch_recommendation = " For thinking budgets above 32k tokens, consider using Anthropic's Message Batches API to avoid networking issues."
            
            raise TimeoutError(
                f"API request timed out after {timeout_duration} seconds{thinking_info}. "
                f"For complex tasks or large thinking budgets, try: reducing thinking budget, "
                f"increasing timeout, simplifying the request, or using batch processing.{batch_recommendation}"
            ) from e
        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors with actionable guidance based on Anthropic documentation
            if e.response.status_code == 429:
                retry_after = e.response.headers.get('retry-after', '60')
                tier_info = "Consider upgrading your rate limit tier or reducing request frequency."
                raise RuntimeError(
                    f"Rate limit exceeded (HTTP 429). Retry after {retry_after} seconds. "
                    f"Current model: {model}. {tier_info}"
                ) from e
            elif e.response.status_code == 413:
                size_guidance = (
                    "Try reducing: max_tokens, thinking budget, message history length, "
                    "or number of images. Consider breaking large requests into smaller batches."
                )
                raise RuntimeError(f"Request too large (HTTP 413). {size_guidance}") from e
            elif e.response.status_code == 529:
                retry_guidance = "Use exponential backoff: wait 1s, then 2s, 4s, 8s, etc. between retries."
                raise RuntimeError(
                    f"Anthropic's API is temporarily overloaded (HTTP 529). {retry_guidance}"
                ) from e
            elif e.response.status_code == 400:
                param_guidance = "Check your model name, beta flags, tool parameters, and message format."
                raise RuntimeError(f"Bad request (HTTP 400). {param_guidance}") from e
            elif e.response.status_code == 401:
                raise RuntimeError("Invalid API key (HTTP 401). Check your ANTHROPIC_API_KEY.") from e
            elif e.response.status_code == 403:
                raise RuntimeError("Access forbidden (HTTP 403). Check your API key permissions and model access.") from e
            else:
                raise RuntimeError(f"API request failed with status {e.response.status_code}: {str(e)}") from e
        except Exception as e:
            # Handle other API errors gracefully with enhanced context
            error_type = type(e).__name__
            # Safely handle provider type (could be string or enum)
            provider_value = provider.value if hasattr(provider, 'value') else str(provider)
            model_info = f"Model: {model}, Provider: {provider_value}"
            raise RuntimeError(
                f"API request failed ({error_type}): {str(e)}. "
                f"{model_info}. Check your API key, model availability, and request parameters."
            ) from e
        
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
