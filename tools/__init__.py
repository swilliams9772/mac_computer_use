"""
Enhanced Tools Collection for Claude Computer Use
Comprehensive tool suite optimized for macOS M4 and Claude 4 models

This module provides:
- Core tools: Computer, Bash, Edit, AppleScript, Silicon
- Enhanced tools: EnhancedBashTool with smart execution
- Web Search: Official Anthropic web search tool with advanced formatting
- Tool coordination and management systems
"""

from .base import BaseAnthropicTool, ToolResult, ToolError, CLIResult, ToolFailure
from .computer import ComputerTool
from .bash import BashTool
from .edit import EditTool
from .applescript import AppleScriptTool
from .silicon import SiliconTool
from .enhanced_bash import EnhancedBashTool
from .web_search import WebSearchTool, EnhancedWebBrowser, WebSearchResultFormatter
from .collection import ToolCollection

# Tool Categories for better organization
CORE_TOOLS = [
    "ComputerTool",
    "BashTool", 
    "EditTool",
    "AppleScriptTool",
    "SiliconTool",
]

ENHANCED_TOOLS = [
    "EnhancedBashTool",
    "WebSearchTool",
    "EnhancedWebBrowser",
    "WebSearchResultFormatter",
]

BASE_CLASSES = [
    "BaseAnthropicTool",
    "ToolResult", 
    "ToolError",
    "CLIResult",
    "ToolFailure",
]

MANAGEMENT_TOOLS = [
    "ToolCollection",
]

# Server-side tools configuration for Anthropic API
SERVER_TOOLS_CONFIG = {
    "web_search": {
        "type": "web_search_20250305",
        "name": "web_search",
        "description": "Official Anthropic web search tool for real-time information retrieval",
        "default_config": {
            "max_uses": 5,
            "user_location": {
                "type": "approximate",
                "city": "San Francisco",
                "region": "California",
                "country": "US",
                "timezone": "America/Los_Angeles"
            }
        },
        "supported_models": [
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514", 
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-latest",
            "claude-3-5-haiku-latest"
        ]
    }
}

def get_web_search_config(
    max_uses: int = 5,
    allowed_domains: list[str] = None,
    blocked_domains: list[str] = None,
    city: str = "San Francisco",
    region: str = "California",
    country: str = "US",
    timezone: str = "America/Los_Angeles",
    enable_location: bool = True
) -> dict:
    """
    Generate web search tool configuration for the Anthropic API.
    
    Args:
        max_uses: Maximum number of searches per request (1-10)
        allowed_domains: List of allowed domains (exclusive with blocked_domains)
        blocked_domains: List of blocked domains (exclusive with allowed_domains)
        city: City for search localization
        region: Region/state for search localization
        country: Country code for search localization
        timezone: IANA timezone ID for search localization
        enable_location: Whether to enable location-based search
        
    Returns:
        Dictionary with web search tool configuration
        
    Example:
        >>> config = get_web_search_config(
        ...     max_uses=3,
        ...     allowed_domains=["docs.anthropic.com", "github.com"],
        ...     city="New York",
        ...     region="New York",
        ...     country="US"
        ... )
    """
    config = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_uses
    }
    
    # Domain filtering (mutually exclusive)
    if allowed_domains and blocked_domains:
        raise ValueError("Cannot specify both allowed_domains and blocked_domains")
    
    if allowed_domains:
        config["allowed_domains"] = allowed_domains
    elif blocked_domains:
        config["blocked_domains"] = blocked_domains
    
    # Location configuration
    if enable_location and city and region and country:
        config["user_location"] = {
            "type": "approximate",
            "city": city,
            "region": region,
            "country": country,
            "timezone": timezone
        }
    
    return config

def is_web_search_supported(model: str) -> bool:
    """
    Check if a model supports the web search tool.
    
    Args:
        model: Model name to check
        
    Returns:
        True if the model supports web search, False otherwise
    """
    supported_models = SERVER_TOOLS_CONFIG["web_search"]["supported_models"]
    
    # Handle different model naming conventions
    base_model = model
    if "us.anthropic." in model:
        base_model = model.replace("us.anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "anthropic." in model:
        base_model = model.replace("anthropic.", "").replace("-v1:0", "").replace("-v2:0", "")
    elif "@" in model:
        base_model = model.split("@")[0]
        if base_model == "claude-3-5-sonnet-v2":
            base_model = "claude-3-5-sonnet-latest"
    
    return base_model in supported_models

def create_enhanced_tool_collection(
    tool_versions: dict = None,
    enable_web_search: bool = True,
    web_search_config: dict = None
) -> ToolCollection:
    """
    Create an enhanced tool collection with optimal configurations.
    
    Args:
        tool_versions: Tool version mappings
        enable_web_search: Whether to include web search capabilities
        web_search_config: Web search configuration options
        
    Returns:
        Configured ToolCollection instance
    """
    # Get tool versions from kwargs or use latest
    if tool_versions is None:
        tool_versions = {
            "computer": "computer_20250124",
            "bash": "bash_20250124", 
            "text_editor": "text_editor_20250429",
            "applescript": "custom",
            "silicon": "custom"
        }
    
    tools = [
        ComputerTool(api_version=tool_versions["computer"]),
        BashTool(api_version=tool_versions["bash"]),
        EditTool(api_version=tool_versions["text_editor"]),
        AppleScriptTool(api_version=tool_versions["applescript"]),
        SiliconTool(api_version=tool_versions["silicon"]),
    ]
    
    # Add enhanced bash tool if requested
    tools.append(EnhancedBashTool())
    
    return ToolCollection(*tools)

__all__ = [
    # Base classes
    *BASE_CLASSES,
    
    # Core tools
    *CORE_TOOLS,
    
    # Enhanced tools
    *ENHANCED_TOOLS,
    
    # Tool management
    *MANAGEMENT_TOOLS,
    
    # Utility functions
    "get_web_search_config",
    "is_web_search_supported", 
    "create_enhanced_tool_collection",
    "SERVER_TOOLS_CONFIG",
] 