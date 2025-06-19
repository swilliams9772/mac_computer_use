import asyncio
import shlex
from typing import ClassVar, Literal

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .run import run


class AppleScriptTool(BaseAnthropicTool):
    """
    A tool that allows the agent to execute AppleScript commands on macOS.
    Provides high-level automation for macOS applications and system functions.
    """

    name: ClassVar[Literal["applescript"]] = "applescript"
    api_type: str = "custom"  # Always use "custom" for custom tools

    def __init__(self, api_version: str = "custom"):
        # Custom tools always use "custom" type for API calls
        self.api_version = api_version
        super().__init__()

    async def __call__(
        self,
        script: str | None = None,
        script_type: str = "direct",
        application: str | None = None,
        **kwargs
    ):
        """
        Execute AppleScript commands for macOS automation.
        
        Args:
            script: The AppleScript code to execute
            script_type: Either 'direct' for inline script or 'file' for script file path
            application: Optional specific application to target
        """
        if script is None:
            raise ToolError("script parameter is required.")

        if script_type not in ["direct", "file"]:
            raise ToolError("script_type must be either 'direct' or 'file'.")

        try:
            if script_type == "direct":
                # Execute inline AppleScript
                if application:
                    # Wrap script to target specific application
                    wrapped_script = f'tell application "{application}"\n{script}\nend tell'
                else:
                    wrapped_script = script
                
                # Use osascript to execute the script
                cmd = f"osascript -e {shlex.quote(wrapped_script)}"
            else:
                # Execute AppleScript from file
                if not script.endswith('.scpt') and not script.endswith('.applescript'):
                    raise ToolError("Script file must have .scpt or .applescript extension.")
                cmd = f"osascript {shlex.quote(script)}"

            # Execute the command
            return_code, stdout, stderr = await run(cmd, timeout=60.0)
            
            if return_code != 0:
                return CLIResult(
                    output=stdout,
                    error=f"AppleScript execution failed with code {return_code}: {stderr}"
                )
            
            return CLIResult(output=stdout, error=stderr if stderr else None)

        except Exception as e:
            return CLIResult(error=f"AppleScript tool error: {str(e)}")

    def to_params(self):
        return {
            "type": self.api_type,
            "name": self.name,
            "description": "Execute AppleScript commands for macOS automation and application control",
            "input_schema": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "The AppleScript code to execute or path to script file"
                    },
                    "script_type": {
                        "type": "string",
                        "enum": ["direct", "file"],
                        "description": "Whether to execute inline script ('direct') or script file ('file')",
                        "default": "direct"
                    },
                    "application": {
                        "type": "string",
                        "description": "Optional: Specific macOS application to target (e.g., 'Safari', 'Finder', 'Mail')"
                    }
                },
                "required": ["script"]
            }
        } 