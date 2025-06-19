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
                # Convert common key names to pyautogui format
                key_map = {
                    "Return": "enter",
                    "space": "space",
                    "Tab": "tab",
                    "Left": "left",
                    "Right": "right",
                    "Up": "up",
                    "Down": "down",
                    "Escape": "esc",
                    "command": "command",
                    "cmd": "command",
                    "alt": "alt",
                    "shift": "shift",
                    "ctrl": "ctrl"
                }

                try:
                    if "+" in text:
                        # Handle combinations like "ctrl+c"
                        keys = text.split("+")
                        mapped_keys = [key_map.get(k.strip(), k.strip()) for k in keys]
                        await asyncio.get_event_loop().run_in_executor(
                            None, keyboard.press_and_release, '+'.join(mapped_keys)
                        )
                    else:
                        # Handle single keys
                        mapped_key = key_map.get(text, text)
                        await asyncio.get_event_loop().run_in_executor(
                            None, keyboard.press_and_release, mapped_key
                        )

                    return ToolResult(output=f"Pressed key: {text}", error=None, base64_image=None)

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
