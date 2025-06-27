from collections import defaultdict
from pathlib import Path
from typing import Literal, get_args

# Import removed - using generic dict for to_params() return type

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .run import maybe_truncate, run

Command = Literal[
    "view",
    "create",
    "str_replace",
    "insert",
    "undo_edit",
]
SNIPPET_LINES: int = 4


class EditTool(BaseAnthropicTool):
    """
    An filesystem editor tool that allows the agent to view, create, and edit files.
    The tool parameters are defined by Anthropic and are not editable.
    """

    api_type: str  # Will be set dynamically based on version
    name: str  # Will be set based on version
    _file_history: dict[Path, list[str]]

    def __init__(self, api_version: str = "text_editor_20241022"):
        self.api_type = api_version
        # Set the appropriate name based on API version
        if api_version == "text_editor_20250429":
            self.name = "str_replace_based_edit_tool"  # Claude 4 name
        else:
            self.name = "str_replace_editor"  # Claude 3.7 and 3.5 name
        
        self._file_history = defaultdict(list)
        super().__init__()

    def _supports_undo_edit(self) -> bool:
        """Check if the current API version supports undo_edit command."""
        return self.api_type != "text_editor_20250429"  # Claude 4 doesn't support undo_edit

    def to_params(self):
        return {
            "name": self.name,
            "type": self.api_type,
        }

    async def __call__(
        self,
        *,
        command: Command,
        path: str,
        file_text: str | None = None,
        view_range: list[int] | None = None,
        old_str: str | None = None,
        new_str: str | None = None,
        insert_line: int | None = None,
        **kwargs,
    ):
        _path = Path(path)
        self.validate_path(command, _path)
        if command == "view":
            return await self.view(_path, view_range)
        elif command == "create":
            if not file_text:
                return ToolResult(error="❌ **Missing file content:** The `file_text` parameter is required when creating a file")
            self.write_file(_path, file_text)
            self._file_history[_path].append(file_text)
            return ToolResult(output=f"✅ **File created successfully** at: `{_path}`\n📝 Content: {len(file_text)} characters")
        elif command == "str_replace":
            if not old_str:
                return ToolResult(error="❌ **Missing search text:** The `old_str` parameter is required to specify what text to replace")
            return self.str_replace(_path, old_str, new_str)
        elif command == "insert":
            if insert_line is None:
                return ToolResult(error="❌ **Missing line number:** The `insert_line` parameter is required to specify where to insert text")
            if not new_str:
                return ToolResult(error="❌ **Missing content:** The `new_str` parameter is required to specify what text to insert")
            return self.insert(_path, insert_line, new_str)
        elif command == "undo_edit":
            if not self._supports_undo_edit():
                return ToolResult(error=f"❌ **Unsupported command:** The `undo_edit` command is not available in {self.api_type}. This feature is only available in text_editor_20250124 and text_editor_20241022.")
            return self.undo_edit(_path)
        
        available_commands = ", ".join(get_args(Command))
        return ToolResult(error=f"❌ **Unknown command:** '{command}' is not recognized. Available commands: {available_commands}")

    def validate_path(self, command: str, path: Path):
        """
        Check that the path/command combination is valid.
        """
        # Check if its an absolute path
        if not path.is_absolute():
            suggested_path = Path("") / path
            raise ToolError(
                f"❌ **Invalid path:** '{path}' must be an absolute path starting with '/'. Did you mean: `{suggested_path}`?"
            )
        # Check if path exists
        if not path.exists() and command != "create":
            raise ToolError(
                f"❌ **File not found:** '{path}' does not exist. Use the 'create' command to create new files, or use 'view' to explore existing directories."
            )
        if path.exists() and command == "create":
            raise ToolError(
                f"❌ **File already exists:** '{path}' already exists. Use 'str_replace' to modify existing files, or choose a different filename."
            )
        # Check if the path points to a directory
        if path.is_dir():
            if command != "view":
                raise ToolError(
                    f"❌ **Directory operation:** '{path}' is a directory. Only the 'view' command can be used on directories to explore their contents."
                )

    async def view(self, path: Path, view_range: list[int] | None = None):
        """Implement the view command"""
        if path.is_dir():
            if view_range:
                return ToolResult(error="❌ **Invalid parameter:** The `view_range` parameter cannot be used when viewing directories")

            _, stdout, stderr = await run(
                rf"find {path} -maxdepth 2 -not -path '*/\.*'"
            )
            if not stderr:
                stdout = f"📁 **Directory contents of {path}** (up to 2 levels, excluding hidden files):\n{stdout}\n"
                return CLIResult(output=stdout)
            else:
                return CLIResult(error=f"❌ **Directory access error:** {stderr}")

        file_content = self.read_file(path)
        init_line = 1
        total_lines = len(file_content.split("\n"))
        
        if view_range:
            if len(view_range) != 2 or not all(isinstance(i, int) for i in view_range):
                return ToolResult(error="❌ **Invalid view range:** Must be a list of two integers [start_line, end_line]")
            
            file_lines = file_content.split("\n")
            n_lines_file = len(file_lines)
            init_line, final_line = view_range
            
            if init_line < 1 or init_line > n_lines_file:
                return ToolResult(error=f"❌ **Invalid start line:** {init_line} is out of range. File has {n_lines_file} lines (1-{n_lines_file})")
                
            if final_line > n_lines_file:
                return ToolResult(error=f"❌ **Invalid end line:** {final_line} exceeds file length. File has {n_lines_file} lines")
                
            if final_line != -1 and final_line < init_line:
                return ToolResult(error=f"❌ **Invalid range:** End line ({final_line}) must be greater than or equal to start line ({init_line})")

            if final_line == -1:
                file_content = "\n".join(file_lines[init_line - 1 :])
            else:
                file_content = "\n".join(file_lines[init_line - 1 : final_line])

        result_output = self._make_output(file_content, str(path), init_line=init_line)
        if view_range:
            result_output = f"📄 **Viewing lines {init_line}-{final_line if final_line != -1 else total_lines} of {path}:**\n{result_output}"
        else:
            result_output = f"📄 **File content of {path}** ({total_lines} lines):\n{result_output}"
            
        return CLIResult(output=result_output)

    def str_replace(self, path: Path, old_str: str, new_str: str | None):
        """Implement the str_replace command, which replaces old_str with new_str in the file content"""
        # Read the file content
        file_content = self.read_file(path).expandtabs()
        old_str = old_str.expandtabs()
        new_str = new_str.expandtabs() if new_str is not None else ""

        # Check if old_str is unique in the file
        occurrences = file_content.count(old_str)
        if occurrences == 0:
            return ToolResult(error=f"❌ **Text not found:** The text `{old_str}` does not appear in {path}. Please check the exact text you want to replace.")
        elif occurrences > 1:
            file_content_lines = file_content.split("\n")
            lines = [
                idx + 1
                for idx, line in enumerate(file_content_lines)
                if old_str in line
            ]
            return ToolResult(error=f"❌ **Multiple matches found:** The text `{old_str}` appears {occurrences} times on lines {lines}. Please make the search text more specific to match exactly one occurrence.")

        # Replace old_str with new_str
        new_file_content = file_content.replace(old_str, new_str)

        # Write the new content to the file
        self.write_file(path, new_file_content)

        # Save the content to history
        self._file_history[path].append(file_content)

        # Create a snippet of the edited section
        replacement_line = file_content.split(old_str)[0].count("\n")
        start_line = max(0, replacement_line - SNIPPET_LINES)
        end_line = replacement_line + SNIPPET_LINES + new_str.count("\n")
        snippet = "\n".join(new_file_content.split("\n")[start_line : end_line + 1])

        # Prepare the success message
        success_msg = f"✅ **File edited successfully** - Replaced text in {path}\n"
        success_msg += f"🔄 **Change:** `{old_str[:50]}{'...' if len(old_str) > 50 else ''}` → `{new_str[:50]}{'...' if len(new_str) > 50 else ''}`\n\n"
        success_msg += self._make_output(
            snippet, f"Updated content preview", start_line + 1
        )
        success_msg += "\n💡 **Tip:** Review the changes carefully and use the file again if additional edits are needed."

        return CLIResult(output=success_msg)

    def insert(self, path: Path, insert_line: int, new_str: str):
        """Implement the insert command, which inserts new_str at the specified line in the file content."""
        file_text = self.read_file(path).expandtabs()
        new_str = new_str.expandtabs()
        file_text_lines = file_text.split("\n")
        n_lines_file = len(file_text_lines)

        if insert_line < 0 or insert_line > n_lines_file:
            return ToolResult(error=f"❌ **Invalid line number:** {insert_line} is out of range. Valid range is 0-{n_lines_file} (0 = insert at beginning, {n_lines_file} = insert at end)")

        new_str_lines = new_str.split("\n")
        new_file_text_lines = (
            file_text_lines[:insert_line]
            + new_str_lines
            + file_text_lines[insert_line:]
        )
        snippet_lines = (
            file_text_lines[max(0, insert_line - SNIPPET_LINES) : insert_line]
            + new_str_lines
            + file_text_lines[insert_line : insert_line + SNIPPET_LINES]
        )

        new_file_text = "\n".join(new_file_text_lines)
        snippet = "\n".join(snippet_lines)

        self.write_file(path, new_file_text)
        self._file_history[path].append(file_text)

        success_msg = f"✅ **Text inserted successfully** at line {insert_line} in {path}\n"
        success_msg += f"📝 **Added:** {len(new_str_lines)} line(s)\n\n"
        success_msg += self._make_output(
            snippet,
            "Updated content preview",
            max(1, insert_line - SNIPPET_LINES + 1),
        )
        success_msg += "\n💡 **Tip:** Check the indentation and formatting to ensure the inserted text aligns properly with the existing code."
        return CLIResult(output=success_msg)

    def undo_edit(self, path: Path):
        """Implement the undo_edit command."""
        if not self._file_history[path]:
            return ToolResult(error=f"❌ **No edit history:** No previous edits found for {path}. Cannot undo changes.")

        old_text = self._file_history[path].pop()
        self.write_file(path, old_text)

        return CLIResult(
            output=f"✅ **Edit undone successfully** for {path}\n\n{self._make_output(old_text, str(path))}\n\n💡 **Tip:** The file has been restored to its previous state. You can continue editing or use 'view' to verify the changes."
        )

    def read_file(self, path: Path):
        """Read the content of a file from a given path; raise a ToolError if an error occurs."""
        try:
            content = path.read_text()
            return content
        except UnicodeDecodeError:
            raise ToolError(f"❌ **Encoding error:** Cannot read {path} - file appears to be binary or uses unsupported encoding") from None
        except PermissionError:
            raise ToolError(f"❌ **Permission denied:** Cannot read {path} - check file permissions") from None
        except Exception as e:
            raise ToolError(f"❌ **File read error:** {str(e)} while reading {path}") from None

    def write_file(self, path: Path, file: str):
        """Write the content of a file to a given path; raise a ToolError if an error occurs."""
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file)
        except PermissionError:
            raise ToolError(f"❌ **Permission denied:** Cannot write to {path} - check file and directory permissions") from None
        except OSError as e:
            if "No space left on device" in str(e):
                raise ToolError(f"❌ **Disk full:** Cannot write to {path} - insufficient disk space") from None
            else:
                raise ToolError(f"❌ **File write error:** {str(e)} while writing to {path}") from None
        except Exception as e:
            raise ToolError(f"❌ **Unexpected error:** {str(e)} while writing to {path}") from None

    def _make_output(
        self,
        file_content: str,
        file_descriptor: str,
        init_line: int = 1,
        expand_tabs: bool = True,
    ):
        """Generate output for the CLI based on the content of a file."""
        file_content = maybe_truncate(file_content)
        if expand_tabs:
            file_content = file_content.expandtabs()
        file_content = "\n".join(
            [
                f"{i + init_line:6}\t{line}"
                for i, line in enumerate(file_content.split("\n"))
            ]
        )
        return (
            f"```\n{file_content}\n```"
        )
