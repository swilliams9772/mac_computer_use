"""Tool collection that holds all the tools used by the model."""

import sys
from typing import Any, Dict, Iterable

from anthropic.types.beta import BetaToolUnionParam

from .base import (
    BaseAnthropicTool,
    ToolError,
    ToolFailure,
    ToolResult,
)


class ToolCollection:
    """Collection of tools that can be used by the model."""

    def __init__(self, *tools_list, tools: Dict[str, BaseAnthropicTool] = None):
        """
        Initialize the tool collection with tools.
        
        Args:
            *tools_list: Variable number of tools to add to the collection
            tools: Dictionary of tool name to tool instance
        """
        self.tools: Dict[str, BaseAnthropicTool] = {}
        
        # Add tools from the list
        for tool in tools_list:
            tool_name = getattr(tool, "name", tool.__class__.__name__)
            self.tools[tool_name] = tool
        
        # Add tools from the dictionary
        if tools:
            self.tools.update(tools)

    def __call__(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Call the specified tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        
        Raises:
            KeyError: If the tool is not found
        """
        if tool_name not in self.tools:
            return ToolResult(error=f"Tool '{tool_name}' not found")
        
        return self.tools[tool_name](**kwargs)

    def to_params(self) -> list[BetaToolUnionParam]:
        """Returns a list of tool parameters for the API call."""
        return [tool.to_params() for tool in self.tools.values()]

    async def run(self, *, name: str, tool_input: dict[str, Any]) -> ToolResult:
        tool = self.tools.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        try:
            return await tool(**tool_input)
        except ToolError as e:
            return ToolFailure(error=e.message)
