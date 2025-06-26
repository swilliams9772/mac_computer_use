import asyncio
import base64
import os
import shlex
import pyautogui
import keyboard
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict
from uuid import uuid4

# Import removed - using generic dict for to_params() return type

from .base import BaseAnthropicTool, ToolError, ToolResult
from .run import run

OUTPUT_DIR = "/tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

# Mac Keyboard Shortcuts Database
MAC_SHORTCUTS = {
    "common": {
        "cut": "cmd+x",
        "copy": "cmd+c",
        "paste": "cmd+v",
        "undo": "cmd+z",
        "redo": "shift+cmd+z",
        "select_all": "cmd+a",
        "find": "cmd+f",
        "find_next": "cmd+g",
        "find_previous": "shift+cmd+g",
        "hide_app": "cmd+h",
        "hide_others": "option+cmd+h",
        "minimize": "cmd+m",
        "minimize_all": "option+cmd+m",
        "open": "cmd+o",
        "print": "cmd+p",
        "quit": "cmd+q",
        "save": "cmd+s",
        "new_tab": "cmd+t",
        "close_window": "cmd+w",
        "close_all_windows": "option+cmd+w",
        "force_quit": "option+cmd+esc",
        "spotlight": "cmd+space",
        "character_viewer": "ctrl+cmd+space",
        "fullscreen": "ctrl+cmd+f",
        "quick_look": "space",
        "switch_apps": "cmd+tab",
        "switch_windows": "cmd+`",
        "screenshot_selection": "shift+cmd+4",
        "screenshot_screen": "shift+cmd+3",
        "screenshot_interactive": "shift+cmd+5",
        "new_folder": "shift+cmd+n",
        "preferences": "cmd+,",
        "quick_note": "fn+q"
    },
    
    "system": {
        "sleep": "option+cmd+power",
        "displays_sleep": "ctrl+shift+power",
        "restart_dialog": "ctrl+power",
        "force_restart": "ctrl+cmd+power",
        "shutdown_dialog": "ctrl+option+cmd+power",
        "lock_screen": "ctrl+cmd+q",
        "logout": "shift+cmd+q",
        "logout_immediate": "option+shift+cmd+q"
    },
    
    "finder": {
        "duplicate": "cmd+d",
        "eject": "cmd+e",
        "get_info": "cmd+i",
        "show_original": "cmd+r",
        "computer": "shift+cmd+c",
        "desktop": "shift+cmd+d",
        "recents": "shift+cmd+f",
        "go_to_folder": "shift+cmd+g",
        "home": "shift+cmd+h",
        "icloud_drive": "shift+cmd+i",
        "network": "shift+cmd+k",
        "downloads": "option+cmd+l",
        "documents": "shift+cmd+o",
        "preview_pane": "shift+cmd+p",
        "airdrop": "shift+cmd+r",
        "tab_bar": "shift+cmd+t",
        "utilities": "shift+cmd+u",
        "show_hide_dock": "option+cmd+d",
        "path_bar": "option+cmd+p",
        "sidebar": "option+cmd+s",
        "status_bar": "cmd+/",
        "view_options": "cmd+j",
        "connect_server": "cmd+k",
        "make_alias": "ctrl+cmd+a",
        "new_window": "cmd+n",
        "smart_folder": "option+cmd+n",
        "move_to_trash": "cmd+delete",
        "empty_trash": "shift+cmd+delete",
        "empty_trash_no_confirm": "option+shift+cmd+delete",
        "icon_view": "cmd+1",
        "list_view": "cmd+2",
        "column_view": "cmd+3",
        "gallery_view": "cmd+4",
        "back": "cmd+[",
        "forward": "cmd+]",
        "up_folder": "cmd+up",
        "open_item": "cmd+down"
    },
    
    "text_editing": {
        "bold": "cmd+b",
        "italic": "cmd+i",
        "underline": "cmd+u",
        "add_link": "cmd+k",
        "fonts": "cmd+t",
        "definition": "ctrl+cmd+d",
        "spelling_grammar": "shift+cmd+:",
        "find_misspelled": "cmd+;",
        "delete_word_left": "option+delete",
        "delete_char_left": "ctrl+h",
        "delete_char_right": "ctrl+d",
        "delete_to_end": "ctrl+k",
        "page_up": "fn+up",
        "page_down": "fn+down",
        "document_start": "fn+left",
        "document_end": "fn+right",
        "line_start": "cmd+left",
        "line_end": "cmd+right",
        "word_left": "option+left",
        "word_right": "option+right",
        "select_to_start": "shift+cmd+up",
        "select_to_end": "shift+cmd+down",
        "select_line_start": "shift+cmd+left",
        "select_line_end": "shift+cmd+right",
        "move_line_start": "ctrl+a",
        "move_line_end": "ctrl+e",
        "move_forward": "ctrl+f",
        "move_backward": "ctrl+b",
        "center_cursor": "ctrl+l",
        "move_up": "ctrl+p",
        "move_down": "ctrl+n",
        "new_line": "ctrl+o",
        "transpose_chars": "ctrl+t",
        "left_align": "cmd+{",
        "right_align": "cmd+}",
        "center_align": "shift+cmd+|",
        "copy_style": "option+cmd+c",
        "paste_style": "option+cmd+v",
        "paste_match_style": "option+shift+cmd+v"
    },
    
    "accessibility": {
        "invert_colors": "ctrl+option+cmd+8",
        "reduce_contrast": "ctrl+option+cmd+,",
        "increase_contrast": "ctrl+option+cmd+.",
        "focus_menu_bar": "ctrl+f2",
        "focus_dock": "ctrl+f3",
        "focus_window": "ctrl+f4",
        "focus_toolbar": "ctrl+f5",
        "focus_floating": "ctrl+f6",
        "previous_panel": "ctrl+shift+f6",
        "tab_navigation": "ctrl+f7",
        "focus_status_menu": "ctrl+f8",
        "accessibility_panel": "option+cmd+f5"
    },
    
    "mission_control": {
        "mission_control": "ctrl+up",
        "app_windows": "ctrl+down",
        "show_desktop": "fn+f11",
        "spaces_left": "ctrl+left",
        "spaces_right": "ctrl+right"
    },
    
    "volume_brightness": {
        "volume_up": "f12",
        "volume_down": "f11",
        "mute": "f10",
        "brightness_up": "f2",
        "brightness_down": "f1"
    }
}

# Common task shortcuts for easier access
TASK_SHORTCUTS = {
    "file_operations": {
        "new_file": "cmd+n",
        "open_file": "cmd+o",
        "save_file": "cmd+s",
        "save_as": "shift+cmd+s",
        "close_file": "cmd+w",
        "duplicate_file": "cmd+d",
        "move_to_trash": "cmd+delete",
        "get_file_info": "cmd+i"
    },
    
    "navigation": {
        "go_back": "cmd+[",
        "go_forward": "cmd+]",
        "go_up": "cmd+up",
        "go_home": "shift+cmd+h",
        "go_to_applications": "shift+cmd+a",
        "go_to_utilities": "shift+cmd+u",
        "go_to_downloads": "option+cmd+l"
    },
    
    "window_management": {
        "new_window": "cmd+n",
        "close_window": "cmd+w",
        "minimize_window": "cmd+m",
        "hide_app": "cmd+h",
        "switch_apps": "cmd+tab",
        "switch_windows": "cmd+`",
        "fullscreen": "ctrl+cmd+f"
    },
    
    "text_operations": {
        "select_all": "cmd+a",
        "copy": "cmd+c",
        "cut": "cmd+x",
        "paste": "cmd+v",
        "undo": "cmd+z",
        "redo": "shift+cmd+z",
        "find": "cmd+f",
        "replace": "option+cmd+f"
    }
}

# Key name mappings for macOS
MAC_KEY_MAP = {
    # Modifier keys
    "command": "cmd",
    "cmd": "cmd",
    "⌘": "cmd",
    "option": "alt",
    "alt": "alt", 
    "⌥": "alt",
    "control": "ctrl",
    "ctrl": "ctrl",
    "⌃": "ctrl",
    "shift": "shift",
    "⇧": "shift",
    "fn": "fn",
    
    # Special keys
    "return": "enter",
    "enter": "enter",
    "space": "space",
    "spacebar": "space",
    "tab": "tab",
    "escape": "esc",
    "esc": "esc",
    "delete": "backspace",
    "backspace": "backspace",
    "forward_delete": "delete",
    
    # Arrow keys
    "up": "up",
    "down": "down", 
    "left": "left",
    "right": "right",
    "up_arrow": "up",
    "down_arrow": "down",
    "left_arrow": "left", 
    "right_arrow": "right",
    
    # Function keys
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
    "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
    "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    
    # Other keys
    "grave": "`",
    "backtick": "`",
    "tilde": "~",
    "comma": ",",
    "period": ".",
    "semicolon": ";",
    "colon": ":",
    "slash": "/",
    "backslash": "\\",
    "quote": "'",
    "double_quote": '"',
    "left_bracket": "[",
    "right_bracket": "]",
    "left_brace": "{",
    "right_brace": "}",
    "minus": "-",
    "plus": "+",
    "equals": "=",
    "pipe": "|"
}

def get_shortcut_for_task(task: str, category: str = None) -> str | None:
    """Get the keyboard shortcut for a specific task."""
    if category and category in TASK_SHORTCUTS:
        return TASK_SHORTCUTS[category].get(task)
    
    # Search across all categories
    for cat_shortcuts in TASK_SHORTCUTS.values():
        if task in cat_shortcuts:
            return cat_shortcuts[task]
    
    # Search in main shortcuts
    for cat_shortcuts in MAC_SHORTCUTS.values():
        if task in cat_shortcuts:
            return cat_shortcuts[task]
    
    return None

def get_shortcuts_by_category(category: str) -> dict[str, str]:
    """Get all shortcuts for a specific category."""
    return MAC_SHORTCUTS.get(category, {})

def normalize_key_combination(key_combo: str) -> str:
    """Normalize a key combination to standard format."""
    if not key_combo:
        return ""
    
    parts = key_combo.lower().replace(" ", "").split("+")
    normalized_parts = []
    
    for part in parts:
        normalized = MAC_KEY_MAP.get(part, part)
        normalized_parts.append(normalized)
    
    return "+".join(normalized_parts)

def find_shortcuts_containing(search_term: str) -> dict[str, dict[str, str]]:
    """Find all shortcuts that contain a specific search term in their name."""
    results = {}
    search_lower = search_term.lower()
    
    for category, shortcuts in MAC_SHORTCUTS.items():
        category_results = {}
        for shortcut_name, shortcut_keys in shortcuts.items():
            if search_lower in shortcut_name.lower():
                category_results[shortcut_name] = shortcut_keys
        if category_results:
            results[category] = category_results
    
    return results

Action = Literal[
    "key",
    "hold_key",  # New in 20250124
    "type",
    "cursor_position",
    "mouse_move",
    "left_mouse_down",  # New in 20250124
    "left_mouse_up",  # New in 20250124
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "triple_click",  # New in 20250124
    "scroll",  # New in 20250124
    "wait",  # New in 20250124
    "screenshot",
]


class Resolution(TypedDict):
    width: int
    height: int


# sizes above XGA/WXGA are not recommended (see README.md)
# scale down to one of these targets if ComputerTool._scaling_enabled is set
MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}
SCALE_DESTINATION = MAX_SCALING_TARGETS["FWXGA"]


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse of the current macOS computer.
    The tool parameters are defined by Anthropic and are not editable.
    Requires cliclick to be installed: brew install cliclick
    
    Enhanced with comprehensive Mac keyboard shortcuts database including:
    - Common shortcuts (copy, paste, undo, etc.)
    - System shortcuts (sleep, logout, force quit, etc.)
    - Finder shortcuts (navigation, file operations, etc.)
    - Text editing shortcuts (cursor movement, selection, etc.)
    - Accessibility shortcuts (focus control, etc.)
    - Mission Control shortcuts
    - Volume and brightness controls
    
    The tool can now:
    - Accept task names like "copy" instead of "cmd+c"
    - Normalize various key combination formats
    - Search for shortcuts by category or term
    - Provide better error messages and feedback
    
    Example usage:
    - action="key", text="copy" -> performs cmd+c
    - action="key", text="cmd+c" -> performs cmd+c (normalized)
    - action="key", text="Command-C" -> performs cmd+c (normalized)
    """

    name: Literal["computer"] = "computer"
    api_type: str  # Will be set dynamically based on version
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 1.0  # macOS is generally faster than X11
    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        return {
            "display_width_px": self.width,
            "display_height_px": self.height,
            "display_number": self.display_num,
        }

    def to_params(self):
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self, api_version: str = "computer_20241022"):
        super().__init__()
        self.api_type = api_version
        
        self.width, self.height = pyautogui.size()
        assert self.width and self.height, "WIDTH, HEIGHT must be set"
        self.display_num = None  # macOS doesn't use X11 display numbers

    def get_mac_shortcut(self, task: str, category: str = None) -> str | None:
        """Get the Mac keyboard shortcut for a specific task."""
        return get_shortcut_for_task(task, category)
    
    def list_shortcuts_for_category(self, category: str) -> dict[str, str]:
        """List all available shortcuts for a category."""
        return get_shortcuts_by_category(category)
    
    def search_shortcuts(self, search_term: str) -> dict[str, dict[str, str]]:
        """Search for shortcuts containing a specific term."""
        return find_shortcuts_containing(search_term)
    
    def get_all_categories(self) -> list[str]:
        """Get all available shortcut categories."""
        return list(MAC_SHORTCUTS.keys()) + list(TASK_SHORTCUTS.keys())

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        duration: int | None = None,  # New in 20250124 - for hold_key and wait
        scroll_amount: int | None = None,  # New in 20250124 - for scroll
        scroll_direction: str | None = None,  # New in 20250124 - for scroll
        start_coordinate: tuple[int, int] | None = None,  # New in 20250124 - for left_click_drag
        **kwargs,
    ):
        print("Action: ", action, text, coordinate)
        if action == "mouse_move":
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if not isinstance(coordinate, list) or len(coordinate) != 2:
                raise ToolError(f"{coordinate} must be a tuple of length 2")
            if not all(isinstance(i, int) and i >= 0 for i in coordinate):
                raise ToolError(f"{coordinate} must be a tuple of non-negative ints")

            x, y = self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])
            return await self.shell(f"cliclick m:{x},{y}")

        if action == "left_click_drag":
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if not isinstance(coordinate, list) or len(coordinate) != 2:
                raise ToolError(f"{coordinate} must be a tuple of length 2")
            if not all(isinstance(i, int) and i >= 0 for i in coordinate):
                raise ToolError(f"{coordinate} must be a tuple of non-negative ints")

            # Handle enhanced version with start_coordinate
            if self.api_type == "computer_20250124" and start_coordinate is not None:
                if not isinstance(start_coordinate, list) or len(start_coordinate) != 2:
                    raise ToolError(f"{start_coordinate} must be a tuple of length 2")
                if not all(isinstance(i, int) and i >= 0 for i in start_coordinate):
                    raise ToolError(f"{start_coordinate} must be a tuple of non-negative ints")
                
                start_x, start_y = self.scale_coordinates(ScalingSource.API, start_coordinate[0], start_coordinate[1])
                end_x, end_y = self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])
                
                # Move to start position, press down, drag to end, release
                return await self.shell(f"cliclick m:{start_x},{start_y} dd:{end_x},{end_y}")
            else:
                # Original behavior for older version
                x, y = self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])
                return await self.shell(f"cliclick dd:{x},{y}")

        if action in ("key", "type"):
            if text is None:
                raise ToolError(f"text is required for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            if not isinstance(text, str):
                raise ToolError(output=f"{text} must be a string")

            if action == "key":
                # First, try to normalize the key combination using our Mac shortcuts database
                normalized_keys = normalize_key_combination(text)
                
                # If it's a task name, try to get the shortcut for it
                if not "+" in text and normalized_keys == text.lower():
                    shortcut = get_shortcut_for_task(text.lower())
                    if shortcut:
                        normalized_keys = shortcut
                        print(f"Using Mac shortcut for '{text}': {shortcut}")

                try:
                    if "+" in normalized_keys:
                        # Handle combinations like "cmd+c"
                        keys = normalized_keys.split("+")
                        # Use our enhanced MAC_KEY_MAP for better key mapping
                        mapped_keys = []
                        for k in keys:
                            key_strip = k.strip()
                            mapped = MAC_KEY_MAP.get(key_strip, key_strip)
                            mapped_keys.append(mapped)
                        
                        key_combination = '+'.join(mapped_keys)
                        await asyncio.get_event_loop().run_in_executor(
                            None, keyboard.press_and_release, key_combination
                        )
                    else:
                        # Handle single keys
                        mapped_key = MAC_KEY_MAP.get(normalized_keys, normalized_keys)
                        await asyncio.get_event_loop().run_in_executor(
                            None, keyboard.press_and_release, mapped_key
                        )

                    return ToolResult(
                        output=f"Pressed key combination: {text} (normalized: {normalized_keys})", 
                        error=None, 
                        base64_image=None
                    )

                except Exception as e:
                    return ToolResult(output=None, error=str(e), base64_image=None)
            elif action == "type":
                results: list[ToolResult] = []
                for chunk in chunks(text, TYPING_GROUP_SIZE):
                    cmd = f"cliclick w:{TYPING_DELAY_MS} t:{shlex.quote(chunk)}"
                    results.append(await self.shell(cmd, take_screenshot=False))
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(
                    output="".join(result.output or "" for result in results),
                    error="".join(result.error or "" for result in results),
                    base64_image=screenshot_base64,
                )

        # Handle new actions that require specific parameters
        if action == "hold_key":
            if text is None:
                raise ToolError(f"text is required for {action}")
            if duration is None:
                raise ToolError(f"duration is required for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            
            # Implement hold_key using keyboard library with duration
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, keyboard.press, text
                )
                await asyncio.sleep(duration)
                await asyncio.get_event_loop().run_in_executor(
                    None, keyboard.release, text
                )
                return ToolResult(output=f"Held key: {text} for {duration}s", error=None, base64_image=None)
            except Exception as e:
                return ToolResult(output=None, error=str(e), base64_image=None)

        if action == "wait":
            if duration is None:
                raise ToolError(f"duration is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            
            await asyncio.sleep(duration)
            screenshot_base64 = (await self.screenshot()).base64_image
            return ToolResult(output=f"Waited for {duration}s", error=None, base64_image=screenshot_base64)

        if action == "scroll":
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if scroll_direction is None:
                raise ToolError(f"scroll_direction is required for {action}")
            if scroll_amount is None:
                raise ToolError(f"scroll_amount is required for {action}")
            if text is not None and not isinstance(text, str):
                raise ToolError(f"text must be a string for {action}")

            x, y = self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])
            
            # Implement scroll using pyautogui
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, pyautogui.click, x, y
                )
                
                if scroll_direction in ["up", "down"]:
                    scroll_clicks = scroll_amount if scroll_direction == "up" else -scroll_amount
                    await asyncio.get_event_loop().run_in_executor(
                        None, pyautogui.scroll, scroll_clicks, x, y
                    )
                
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(output=f"Scrolled {scroll_direction} {scroll_amount} clicks at ({x}, {y})", 
                                error=None, base64_image=screenshot_base64)
            except Exception as e:
                return ToolResult(output=None, error=str(e), base64_image=None)

        if action in ("left_mouse_down", "left_mouse_up"):
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            
            try:
                if action == "left_mouse_down":
                    await asyncio.get_event_loop().run_in_executor(
                        None, pyautogui.mouseDown
                    )
                    return ToolResult(output="Left mouse button pressed down", error=None, base64_image=None)
                else:  # left_mouse_up
                    await asyncio.get_event_loop().run_in_executor(
                        None, pyautogui.mouseUp
                    )
                    return ToolResult(output="Left mouse button released", error=None, base64_image=None)
            except Exception as e:
                return ToolResult(output=None, error=str(e), base64_image=None)

        if action in (
            "left_click",
            "right_click",
            "double_click",
            "triple_click",
            "middle_click",
            "screenshot",
            "cursor_position",
        ):
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")

            if action == "screenshot":
                return await self.screenshot()
            elif action == "cursor_position":
                result = await self.shell(
                    "cliclick p",
                    take_screenshot=False,
                )
                if result.output:
                    x, y = map(int, result.output.strip().split(","))
                    x, y = self.scale_coordinates(ScalingSource.COMPUTER, x, y)
                    return result.replace(output=f"X={x},Y={y}")
                return result
            else:
                # Handle click actions with optional coordinates
                if coordinate is not None:
                    if not isinstance(coordinate, list) or len(coordinate) != 2:
                        raise ToolError(f"{coordinate} must be a tuple of length 2")
                    if not all(isinstance(i, int) and i >= 0 for i in coordinate):
                        raise ToolError(f"{coordinate} must be a tuple of non-negative ints")
                    
                    x, y = self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])
                    click_cmd = {
                        "left_click": f"c:{x},{y}",
                        "right_click": f"rc:{x},{y}",
                        "middle_click": f"mc:{x},{y}",
                        "double_click": f"dc:{x},{y}",
                        "triple_click": f"tc:{x},{y}",
                    }[action]
                else:
                    # Click at current cursor position
                    click_cmd = {
                        "left_click": "c:.",
                        "right_click": "rc:.",
                        "middle_click": "mc:.",
                        "double_click": "dc:.",
                        "triple_click": "tc:.",
                    }[action]
                return await self.shell(f"cliclick {click_cmd}")

        raise ToolError(f"Invalid action: {action}")

    async def screenshot(self):
        """Take a screenshot of the current screen and return the base64 encoded image."""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        # Use macOS native screencapture
        screenshot_cmd = f"screencapture -x {path}"
        result = await self.shell(screenshot_cmd, take_screenshot=False)

        if self._scaling_enabled:
            x, y = SCALE_DESTINATION['width'], SCALE_DESTINATION['height']
            await self.shell(
                f"sips -z {y} {x} {path}",  # sips is macOS native image processor
                take_screenshot=False
            )

        if path.exists():
            return result.replace(
                base64_image=base64.b64encode(path.read_bytes()).decode()
            )
        raise ToolError(f"Failed to take screenshot: {result.error}")

    async def shell(self, command: str, take_screenshot=False) -> ToolResult:
        """Run a shell command and return the output, error, and optionally a screenshot."""
        _, stdout, stderr = await run(command)
        base64_image = None

        if take_screenshot:
            # delay to let things settle before taking a screenshot
            await asyncio.sleep(self._screenshot_delay)
            base64_image = (await self.screenshot()).base64_image

        return ToolResult(output=stdout, error=stderr, base64_image=base64_image)

    def scale_coordinates(self, source: ScalingSource, x: int, y: int) -> tuple[int, int]:
        """
        Scale coordinates between original resolution and target resolution (SCALE_DESTINATION).

        Args:
            source: ScalingSource.API for scaling up from SCALE_DESTINATION to original resolution
                   or ScalingSource.COMPUTER for scaling down from original to SCALE_DESTINATION
            x, y: Coordinates to scale

        Returns:
            Tuple of scaled (x, y) coordinates
        """
        if not self._scaling_enabled:
            return x, y

        # Calculate scaling factors
        x_scaling_factor = SCALE_DESTINATION['width'] / self.width
        y_scaling_factor = SCALE_DESTINATION['height'] / self.height

        if source == ScalingSource.API:
            # Scale up from SCALE_DESTINATION to original resolution
            if x > SCALE_DESTINATION['width'] or y > SCALE_DESTINATION['height']:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds for {SCALE_DESTINATION['width']}x{SCALE_DESTINATION['height']}")
            return round(x / x_scaling_factor), round(y / y_scaling_factor)
        else:
            # Scale down from original resolution to SCALE_DESTINATION
            return round(x * x_scaling_factor), round(y * y_scaling_factor)
