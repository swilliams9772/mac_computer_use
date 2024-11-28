"""Collection classes for managing multiple tools."""

import asyncio
from typing import List, Optional, Dict
from anthropic.types.beta import BetaToolUnionParam

from .base import BaseAnthropicTool, ToolError, ToolResult
from .bash import BashTool


class ToolCollection:
    """A collection of anthropic-defined tools."""

    def __init__(self, tools: List[BaseAnthropicTool]):
        self.tools = tools
        # Create tool map using the name from tool parameters
        self.tool_map = {}
        for tool in tools:
            params = tool.to_params()
            if isinstance(params, dict) and "function" in params:
                name = params["function"].get("name")
                if name:
                    self.tool_map[name] = tool

    def to_params(self) -> List[BetaToolUnionParam]:
        return [tool.to_params() for tool in self.tools]

    async def execute(self, command: str | None = None, **kwargs) -> ToolResult:
        """Execute a command using the appropriate tool."""
        try:
            if not self.tools:
                return ToolResult(
                    output=None,
                    error="No tools available"
                )
            
            # Handle natural language commands
            if command and not kwargs:
                # Parse natural language command
                cmd_parts = command.lower().split(" and ")
                results = []
                
                for part in cmd_parts:
                    part = part.strip()
                    
                    # Handle special commands
                    if "open" in part:
                        # Map common app names to their macOS names
                        app_map = {
                            "safari": "Safari",
                            "chrome": "Google Chrome",
                            "firefox": "Firefox",
                            "activity monitor": "Activity Monitor",
                            "terminal": "Terminal",
                            "system preferences": "System Preferences",
                            "settings": "System Settings",
                            "finder": "Finder",
                            "notes": "Notes",
                            "calendar": "Calendar",
                            "mail": "Mail",
                            "messages": "Messages",
                            "photos": "Photos",
                            "preview": "Preview",
                            "calculator": "Calculator"
                        }
                        
                        # Extract app name
                        app_name = None
                        for known_app, macos_name in app_map.items():
                            if known_app in part:
                                app_name = macos_name
                                break
                                
                        if not app_name:
                            # Try to capitalize the app name as a fallback
                            words = part.replace("open", "").strip().split()
                            app_name = " ".join(word.capitalize() for word in words)
                        
                        # Use ComputerTool for application commands
                        tool = next(
                            (t for t in self.tools if not isinstance(t, BashTool)), 
                            None
                        )
                        if not tool:
                            return ToolResult(error="No ComputerTool available")
                            
                        results.append(await tool(action="open_app", text=app_name))
                        
                    elif "screenshot" in part:
                        # Use ComputerTool for screenshots
                        tool = next(
                            (t for t in self.tools if not isinstance(t, BashTool)), 
                            None
                        )
                        if not tool:
                            return ToolResult(error="No ComputerTool available")
                        results.append(await tool(action="screenshot"))
                        
                    else:
                        # Use BashTool for raw commands
                        tool = next(
                            (t for t in self.tools if isinstance(t, BashTool)), 
                            None
                        )
                        if not tool:
                            return ToolResult(error="No BashTool available")
                        results.append(await tool(command=part))
                
                # Combine results
                final_result = ToolResult(output="", error="")
                for result in results:
                    if result.error:
                        if final_result.error:
                            final_result = final_result.replace(
                                error=final_result.error + "\n" + result.error
                            )
                        else:
                            final_result = final_result.replace(error=result.error)
                    if result.output:
                        if final_result.output:
                            final_result = final_result.replace(
                                output=final_result.output + "\n" + result.output
                            )
                        else:
                            final_result = final_result.replace(output=result.output)
                    if result.base64_image:
                        final_result = final_result.replace(
                            base64_image=result.base64_image
                        )
                return final_result
                
            else:
                # Use ComputerTool for actions
                tool = next(
                    (t for t in self.tools if not isinstance(t, BashTool)), 
                    None
                )
                if not tool:
                    return ToolResult(
                        error="No ComputerTool available for action"
                    )
                return await tool(**kwargs)
            
        except ToolError as e:
            return ToolResult(output=None, error=str(e))
        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Unexpected error: {str(e)}"
            )
