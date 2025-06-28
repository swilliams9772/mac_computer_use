"""Collection classes for managing multiple tools."""

from typing import Any

from anthropic.types.beta import BetaToolUnionParam

from .base import (
    BaseAnthropicTool,
    ToolError,
    ToolFailure,
    ToolResult,
)


class ToolCollection:
    """A collection of anthropic-defined tools."""

    def __init__(self, *tools: BaseAnthropicTool):
        self.tools = tools
        self.tool_map = {tool.to_params()["name"]: tool for tool in tools}

    def to_params(
        self,
    ) -> list[BetaToolUnionParam]:
        return [tool.to_params() for tool in self.tools]

    async def run(self, *, name: str, tool_input: dict[str, Any]) -> ToolResult:
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        
        # Check if this is a server-side tool that should not be executed locally
        tool_params = tool.to_params()
        if tool_params.get("type", "").startswith("web_search_"):
            # This is a server-side tool - should not be executed locally
            # The API should have already handled this tool call
            return ToolFailure(error=f"Tool {name} is a server-side tool and should not be executed locally. This indicates a configuration error.")
        
        # Special handling for web search tool by name (in case type is not set correctly)
        if name == "web_search":
            return ToolFailure(error=f"Web search tool should be handled server-side by Anthropic API, not locally. If you're seeing this error, it means the tool configuration needs to be checked.")
        
        try:
            return await tool(**tool_input)
        except ToolError as e:
            return ToolFailure(error=e.message)
