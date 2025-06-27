import asyncio
import os
from typing import ClassVar, Literal

# Import removed - using generic dict for to_params() return type

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class _BashSession:
    """A session of a bash shell."""

    _started: bool
    _process: asyncio.subprocess.Process

    command: str = "/bin/bash"
    _output_delay: float = 0.2  # seconds
    _timeout: float = 120.0  # seconds
    _sentinel: str = "<<exit>>"

    def __init__(self):
        self._started = False
        self._timed_out = False

    async def start(self):
        if self._started:
            return

        self._process = await asyncio.create_subprocess_shell(
            self.command,
            preexec_fn=os.setsid,
            shell=True,
            bufsize=0,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._started = True

    def stop(self):
        """Terminate the bash shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return
        self._process.terminate()

    async def run(self, command: str):
        """Execute a command in the bash shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return ToolResult(
                system="tool must be restarted",
                error=f"bash has exited with returncode {self._process.returncode}",
            )
        if self._timed_out:
            raise ToolError(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted",
            )

        # we know these are not None because we created the process with PIPEs
        assert self._process.stdin
        assert self._process.stdout
        assert self._process.stderr

        # send command to the process
        self._process.stdin.write(
            command.encode() + f"; echo '{self._sentinel}'\n".encode()
        )
        await self._process.stdin.drain()

        # read output from the process, until the sentinel is found
        try:
            async with asyncio.timeout(self._timeout):
                while True:
                    await asyncio.sleep(self._output_delay)
                    # if we read directly from stdout/stderr, it will wait forever for
                    # EOF. use the StreamReader buffer directly instead.
                    output = self._process.stdout._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
                    if self._sentinel in output:
                        # strip the sentinel and break
                        output = output[: output.index(self._sentinel)]
                        break
        except asyncio.TimeoutError:
            self._timed_out = True
            raise ToolError(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted",
            ) from None

        if output.endswith("\n"):
            output = output[:-1]

        error = self._process.stderr._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
        if error.endswith("\n"):
            error = error[:-1]

        # clear the buffers so that the next output can be read correctly
        self._process.stdout._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]
        self._process.stderr._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]

        return CLIResult(output=output, error=error)


class BashTool(BaseAnthropicTool):
    """
    A tool that allows the agent to run bash commands.
    The tool parameters are defined by Anthropic and are not editable.
    """

    _session: _BashSession | None
    name: ClassVar[Literal["bash"]] = "bash"
    api_type: str  # Will be set dynamically based on version

    def __init__(self, api_version: str = "bash_20241022"):
        self.api_type = api_version
        self._session = None
        super().__init__()

    async def __call__(
        self, command: str | None = None, restart: bool = False, **kwargs
    ):
        if restart:
            if self._session:
                self._session.stop()
            self._session = _BashSession()
            await self._session.start()

            return ToolResult(output="✅ **Bash session restarted** - Ready for new commands", system="tool has been restarted.")

        if self._session is None:
            self._session = _BashSession()
            await self._session.start()

        if command is not None:
            if not command.strip():
                return ToolResult(error="❌ **Empty command:** Please provide a command to execute")
            
            # Provide helpful warnings for potentially dangerous commands
            dangerous_patterns = ['rm -rf /', 'sudo rm', 'format', 'fdisk', 'dd if=']
            if any(pattern in command.lower() for pattern in dangerous_patterns):
                return ToolResult(error="⚠️ **Potentially dangerous command detected:** Please review the command carefully before execution")
            
            try:
                result = await self._session.run(command)
                
                # Enhanced result formatting
                if result.error and result.output:
                    return ToolResult(
                        output=f"✅ **Command executed with warnings:**\n```\n{result.output}\n```",
                        error=f"⚠️ **Warnings/Errors:**\n```\n{result.error}\n```"
                    )
                elif result.error:
                    return ToolResult(
                        error=f"❌ **Command failed:**\n```\n{result.error}\n```\n💡 **Tip:** Check the command syntax and ensure you have proper permissions"
                    )
                elif result.output:
                    return ToolResult(
                        output=f"✅ **Command executed successfully:**\n```\n{result.output}\n```"
                    )
                else:
                    return ToolResult(
                        output="✅ **Command executed successfully** (no output produced)"
                    )
                    
            except Exception as e:
                return ToolResult(
                    error=f"❌ **Execution error:** {str(e)}\n💡 **Tip:** Try restarting the bash session if the error persists"
                )

        return ToolResult(error="❌ **No command provided:** Please specify a command to execute")

    def to_params(self):
        # For Anthropic-defined tools (bash_20250124, bash_20241022), only include type and name
        # Anthropic provides the description and input_schema internally
        if self.api_type in ["bash_20250124", "bash_20241022"]:
            return {
                "type": self.api_type,
                "name": self.name,
            }
        else:
            # For custom tools or older versions, include full description and schema
            return {
                "type": self.api_type,
                "name": self.name,
                "description": """Execute bash commands in a persistent shell session.

**Key Features:**
- Persistent session maintains state between commands
- Support for complex command sequences and pipelines
- Environment variables and directory changes persist
- Safe execution with built-in dangerous command detection

**Usage Examples:**
- `ls -la` - List files with details
- `cd /path/to/directory` - Change directory
- `brew install package` - Install software (macOS)
- `pip install package` - Install Python packages
- `git status` - Check git repository status
- `find . -name "*.py"` - Search for Python files

**Safety Features:**
- Automatic detection of potentially dangerous commands
- Session restart capability for recovery
- Comprehensive error reporting with helpful tips

**Best Practices:**
- Use `pwd` to check current directory
- Use `ls` to explore available files and folders
- Check command output before proceeding with file operations
- Use `restart: true` if the session becomes unresponsive""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute. Examples:\n" +
                            "• 'ls -la' - List directory contents\n" +
                            "• 'cd ~/Documents' - Change to Documents folder\n" +
                            "• 'brew install wget' - Install software via Homebrew\n" +
                            "• 'python script.py' - Run a Python script\n" +
                            "• 'git clone https://github.com/user/repo.git' - Clone repository\n" +
                            "• 'find . -name \"*.txt\" | head -10' - Find text files"
                        },
                        "restart": {
                            "type": "boolean", 
                            "description": "Set to true to restart the bash session (useful for recovery)",
                            "default": False
                        }
                    },
                    "required": ["command"]
                }
            }
