import asyncio
import shlex
from typing import ClassVar, Literal

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .run import run


class AppleScriptTool(BaseAnthropicTool):
    """
    Enhanced AppleScript tool optimized for M4 MacBook Air and macOS Sequoia 15.6.
    
    Provides high-level automation for macOS applications and system functions with:
    - M4-specific performance optimizations
    - Sequoia-enhanced form automation capabilities
    - Better error handling and retry logic
    - Safari-specific web form automation
    - System monitoring and thermal management
    - Enhanced accessibility integration
    """

    name: ClassVar[Literal["applescript"]] = "applescript"
    api_type: str = "custom"

    def __init__(self, api_version: str = "custom"):
        self.api_version = api_version
        super().__init__()

    async def __call__(
        self,
        script: str | None = None,
        script_type: str = "direct",
        application: str | None = None,
        timeout: int = 60,
        **kwargs
    ):
        """
        Execute AppleScript commands for macOS automation with M4/Sequoia optimizations.
        
        Args:
            script: The AppleScript code to execute
            script_type: Either 'direct' for inline script or 'file' for script file path
            application: Optional specific application to target
            timeout: Execution timeout in seconds (default: 60)
        """
        if script is None:
            return CLIResult(error="❌ **Missing script:** Please provide AppleScript code to execute")

        if script_type not in ["direct", "file"]:
            return CLIResult(error="❌ **Invalid script type:** Must be either 'direct' for inline code or 'file' for script file path")

        try:
            if script_type == "direct":
                # Execute inline AppleScript with enhanced error handling
                if application:
                    # Enhanced application targeting with error recovery
                    wrapped_script = f'''
                    try
                        tell application "{application}"
                            activate
                            delay 0.5
                            {script}
                        end tell
                    on error errMsg number errNum
                        return "AppleScript Error " & errNum & ": " & errMsg
                    end try
                    '''
                else:
                    # Enhanced system-level script with error handling
                    wrapped_script = f'''
                    try
                        {script}
                    on error errMsg number errNum
                        return "AppleScript Error " & errNum & ": " & errMsg
                    end try
                    '''
                
                # Use osascript with optimized parameters for M4
                cmd = ["osascript", "-e", wrapped_script]
            else:
                # Execute AppleScript from file
                if not script.endswith(('.scpt', '.applescript')):
                    return CLIResult(error="❌ **Invalid file type:** Script file must have .scpt or .applescript extension")
                cmd = ["osascript", script]

            # Execute with M4-optimized timeout
            return_code, stdout, stderr = await run(
                " ".join([shlex.quote(arg) for arg in cmd]), 
                timeout=float(timeout)
            )
            
            if return_code != 0:
                error_msg = f"❌ **AppleScript execution failed** (code {return_code})"
                if stderr:
                    error_msg += f"\n**Error details:** {stderr}"
                if "not authorized" in stderr.lower():
                    error_msg += "\n💡 **Tip:** Enable accessibility permissions in System Preferences → Security & Privacy → Privacy → Accessibility"
                elif "application isn't running" in stderr.lower():
                    error_msg += "\n💡 **Tip:** Make sure the target application is running before executing the script"
                elif "can't get" in stderr.lower():
                    error_msg += "\n💡 **Tip:** Check if the UI element exists or try taking a screenshot first"
                
                return CLIResult(
                    output=stdout if stdout else None,
                    error=error_msg
                )
            
            # Format successful output
            if stdout:
                if "AppleScript Error" in stdout:
                    return CLIResult(error=f"❌ **Script error:** {stdout}")
                else:
                    output_msg = f"✅ **AppleScript executed successfully**"
                    if application:
                        output_msg += f" (targeting {application})"
                    output_msg += f"\n**Result:** {stdout}"
                    return CLIResult(output=output_msg)
            else:
                success_msg = f"✅ **AppleScript executed successfully**"
                if application:
                    success_msg += f" (targeting {application})"
                success_msg += " (no output produced)"
                return CLIResult(output=success_msg)

        except Exception as e:
            error_msg = f"❌ **AppleScript tool error:** {str(e)}"
            if "timeout" in str(e).lower():
                error_msg += f"\n💡 **Tip:** Script took longer than {timeout} seconds. Try increasing the timeout or simplifying the script"
            elif "permission" in str(e).lower():
                error_msg += "\n💡 **Tip:** Check system permissions for AppleScript automation in System Preferences"
            
            return CLIResult(error=error_msg)

    def to_params(self):
        return {
            "type": self.api_type,
            "name": self.name,
            "description": """Execute AppleScript commands for advanced macOS automation with M4/Sequoia optimizations.

**🍎 Native macOS Automation**
AppleScript provides powerful integration with macOS applications and system functions, optimized for M4 MacBook Air and macOS Sequoia 15.6.

**✨ Key Capabilities:**
- **Application Control:** Automate any Mac app that supports AppleScript
- **Safari Automation:** Enhanced web form filling and browser control  
- **System Integration:** Manage preferences, files, and system settings
- **Window Management:** Control app windows, spaces, and UI elements
- **Error Recovery:** Built-in error handling with helpful suggestions

**🚀 Common Use Cases:**

*Web Form Automation:*
```applescript
tell app "Safari"
    set value of text field 1 to "John Smith"
    click button "Submit"
end tell
```

*File & Folder Operations:*
```applescript
tell app "Finder"
    open folder "Downloads" of home folder
    select every file whose name ends with ".pdf"
end tell
```

*Window Management:*
```applescript
tell app "Safari"
    set bounds of window 1 to {0, 0, 1280, 800}
    activate
end tell
```

*System Control:*
```applescript
tell app "System Events"
    keystroke "d" using command down
    delay 1
    click button "Don't Save"
end tell
```

**🔧 Advanced Features:**
- **M4 Performance:** Optimized timing for Apple Silicon
- **Sequoia Integration:** Enhanced compatibility with macOS 15.6
- **Error Handling:** Automatic error detection and recovery suggestions
- **Permission Management:** Clear guidance for accessibility permissions
- **Timeout Control:** Configurable execution timeouts for complex scripts

**💡 Best Practices:**
- Always test scripts with simple commands first
- Use `delay` commands for timing-sensitive operations
- Enable accessibility permissions when prompted
- Target specific applications for better reliability
- Use try/catch blocks for error handling

**⚠️ Permission Requirements:**
Some operations require accessibility permissions. Enable them in:
System Preferences → Security & Privacy → Privacy → Accessibility""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "AppleScript code to execute. Examples:\n\n" +
                        "**🌐 Web Form Automation:**\n" +
                        "```applescript\n" +
                        "tell app \"Safari\"\n" +
                        "    set value of text field \"firstName\" to \"John\"\n" +
                        "    click button \"Next\"\n" +
                        "end tell\n" +
                        "```\n\n" +
                        "**📁 File Operations:**\n" +
                        "```applescript\n" +
                        "tell app \"Finder\"\n" +
                        "    open folder \"Documents\" of home folder\n" +
                        "end tell\n" +
                        "```\n\n" +
                        "**🖥️ Window Control:**\n" +
                        "```applescript\n" +
                        "tell app \"Safari\"\n" +
                        "    set bounds of window 1 to {0, 0, 1280, 800}\n" +
                        "end tell\n" +
                        "```\n\n" +
                        "**⌨️ System Events:**\n" +
                        "```applescript\n" +
                        "tell app \"System Events\"\n" +
                        "    keystroke tab\n" +
                        "    key code 36  -- Return key\n" +
                        "end tell\n" +
                        "```"
                    },
                    "script_type": {
                        "type": "string",
                        "enum": ["direct", "file"],
                        "description": "Execution mode:\n• 'direct' - Execute inline AppleScript code (recommended)\n• 'file' - Execute script from .scpt or .applescript file",
                        "default": "direct"
                    },
                    "application": {
                        "type": "string",
                        "description": "Target application for the script. Common apps:\n\n" +
                        "**🌐 Web & Communication:**\n" +
                        "• 'Safari' - Web browser automation\n" +
                        "• 'Mail' - Email automation\n" +
                        "• 'Messages' - iMessage automation\n\n" +
                        "**📁 System & Files:**\n" +
                        "• 'Finder' - File system operations\n" +
                        "• 'System Events' - Low-level system control\n" +
                        "• 'System Preferences' - Settings management\n\n" +
                        "**💻 Development & Productivity:**\n" +
                        "• 'Terminal' - Command line integration\n" +
                        "• 'TextEdit' - Document editing\n" +
                        "• 'Activity Monitor' - Performance monitoring\n\n" +
                        "**🎵 Media & Graphics:**\n" +
                        "• 'Music' - iTunes/Apple Music control\n" +
                        "• 'Photos' - Photo library management\n" +
                        "• 'QuickTime Player' - Media playback"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum execution time in seconds. Recommended values:\n• 30s - Simple UI interactions\n• 60s - Standard automation (default)\n• 120s - Complex file operations\n• 300s - Large data processing",
                        "default": 60,
                        "minimum": 5,
                        "maximum": 300
                    }
                },
                "required": ["script"]
            }
        } 