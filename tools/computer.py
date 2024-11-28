import asyncio
import base64
import os
import shlex
import pyautogui
import keyboard
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict, Optional, Dict, Any
from uuid import uuid4
from loguru import logger

from anthropic.types.beta import BetaToolComputerUse20241022Param, BetaToolUnionParam
from .base import BaseAnthropicTool, ToolError, ToolResult
from .run import run
from .accessibility_integration import AccessibilityIntegration
from .activity_monitor import ActivityMonitor
from .sidecar import SidecarManager

OUTPUT_DIR = "/tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

Action = Literal[
    "key",
    "type",
    "mouse_move", 
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
    "open_app",  # Enhanced action
    "get_window_info",  # Enhanced action
    "monitor_activity",  # Enhanced action
    "sidecar_list",  # List available iPads
    "sidecar_connect",  # Connect to iPad
    "sidecar_configure",  # Configure Sidecar display
]


class Resolution(TypedDict):
    width: int
    height: int


# sizes above XGA/WXGA are not recommended
MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}
SCALE_DESTINATION = MAX_SCALING_TARGETS["FWXGA"]


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerTool(BaseAnthropicTool):
    """Enhanced tool for native macOS computer control"""

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 1.0  # macOS is faster than X11
    _scaling_enabled = True

    def __init__(self):
        super().__init__()
        self.width, self.height = pyautogui.size()
        self.display_num = None  # macOS doesn't use X11 display numbers
        self.accessibility = AccessibilityIntegration()
        self.activity_monitor = ActivityMonitor()
        self.sidecar = SidecarManager()

    async def __call__(
        self,
        action: Action | str,
        text: Optional[str] = None,
        coordinate: Optional[tuple[int, int]] = None,
        **kwargs
    ) -> ToolResult:
        """Execute computer control actions"""
        try:
            # Handle basic actions
            if action == "open_app":
                if not text:
                    raise ToolError("Application name required")
                return await self._open_application(text)
                
            if action == "screenshot":
                return await self.screenshot()
                
            if action in ("mouse_move", "left_click_drag"):
                if not coordinate:
                    raise ToolError(f"coordinate is required for {action}")
                return await self._handle_mouse_movement(action, coordinate)
                
            if action in ("key", "type"):
                if not text:
                    raise ToolError(f"text is required for {action}")
                return await self._handle_keyboard_input(action, text)
                
            if action in ("left_click", "right_click", "double_click", 
                       "middle_click", "cursor_position"):
                return await self._handle_basic_actions(action)
                
            # Handle enhanced actions
            if action == "get_window_info":
                if coordinate:
                    return await self._get_window_info_at_coordinates(coordinate)
                return await self._get_active_window_info()
                
            if action == "monitor_activity":
                return await self._get_system_metrics()
                
            if action == "sidecar_list":
                return await self._handle_sidecar_list()
                
            if action == "sidecar_connect":
                if not text:
                    raise ToolError("iPad name required")
                return await self._handle_sidecar_connect(text, kwargs.get("position"))
                
            if action == "sidecar_configure":
                if not kwargs.get("display_id"):
                    raise ToolError("display_id required")
                return await self._handle_sidecar_configure(**kwargs)
                
            raise ToolError(f"Invalid action: {action}")
            
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
            return ToolResult(error=str(e))

    async def _handle_mouse_movement(
        self, action: Action, coordinate: tuple[int, int] | None
    ) -> ToolResult:
        """Handle mouse movement actions"""
        if coordinate is None:
            raise ToolError(f"coordinate is required for {action}")
        x, y = self.scale_coordinates(ScalingSource.API, coordinate[0], coordinate[1])
        
        if action == "mouse_move":
            return await self.shell(f"cliclick m:{x},{y}")
        return await self.shell(f"cliclick dd:{x},{y}")

    async def _handle_keyboard_input(
        self, action: Action, text: str | None
    ) -> ToolResult:
        """Handle keyboard input actions"""
        if text is None:
            raise ToolError(f"text is required for {action}")
            
        if action == "key":
            return await self._handle_key_press(text)
        return await self._handle_typing(text)

    async def _handle_basic_actions(self, action: Action) -> ToolResult:
        """Handle basic mouse and screenshot actions"""
        if action == "screenshot":
            return await self.screenshot()
            
        if action == "cursor_position":
            return await self._get_cursor_position()
            
        click_cmd = {
            "left_click": "c:.",
            "right_click": "rc:.",
            "middle_click": "mc:.",
            "double_click": "dc:.",
        }[action]
        return await self.shell(f"cliclick {click_cmd}")

    async def _open_application(self, app_name: str) -> ToolResult:
        """Open macOS application"""
        try:
            # Clean up app name
            app_name = app_name.strip()
            
            # Try to open the app using AppleScript first
            script = f'tell application "{app_name}" to activate'
            result = await self.shell(f'osascript -e \'{script}\'', take_screenshot=False)
            
            if result.error:
                # Fallback to open command
                cmd = f'open -a "{app_name}"'
                result = await self.shell(cmd, take_screenshot=False)
            
            if result.error:
                return ToolResult(
                    error=f"Failed to open {app_name}: {result.error}"
                )
                
            # Wait for app to launch
            await asyncio.sleep(2)
            
            # Take screenshot after app opens
            screenshot_result = await self.screenshot()
            
            return ToolResult(
                output=f"Opened {app_name}",
                base64_image=screenshot_result.base64_image
            )
        except Exception as e:
            return ToolResult(error=f"Error opening {app_name}: {str(e)}")

    async def _get_window_info_at_coordinates(
        self, coordinate: tuple[int, int]
    ) -> ToolResult:
        """Get information about window at coordinates"""
        try:
            info = await self.accessibility.get_element_info(coordinate)
            return ToolResult(output=str(info))
        except Exception as e:
            return ToolResult(error=f"Error getting window info: {str(e)}")

    async def _get_active_window_info(self) -> ToolResult:
        """Get information about active window"""
        try:
            info = await self.accessibility.get_active_window_info()
            return ToolResult(output=str(info))
        except Exception as e:
            return ToolResult(error=f"Error getting active window info: {str(e)}")

    async def _get_system_metrics(self) -> ToolResult:
        """Get system performance metrics"""
        try:
            metrics = await self.activity_monitor.get_system_metrics()
            return ToolResult(output=str(metrics))
        except Exception as e:
            return ToolResult(error=f"Error getting system metrics: {str(e)}")

    async def screenshot(self) -> ToolResult:
        """Take native macOS screenshot"""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        # Use macOS screencapture
        result = await self.shell(f"screencapture -x {path}", take_screenshot=False)

        if self._scaling_enabled:
            await self.shell(
                f"sips -z {SCALE_DESTINATION['height']} {SCALE_DESTINATION['width']} {path}",
                take_screenshot=False
            )

        if path.exists():
            return result.replace(
                base64_image=base64.b64encode(path.read_bytes()).decode()
            )
        raise ToolError(f"Failed to take screenshot: {result.error}")

    def _map_key(self, key: str) -> str:
        """Map common key names to system keys"""
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
        return key_map.get(key, key)

    def _chunk_text(self, text: str, size: int) -> list[str]:
        """Split text into chunks for typing"""
        return [text[i:i + size] for i in range(0, len(text), size)]

    def scale_coordinates(self, source: ScalingSource, x: int, y: int) -> tuple[int, int]:
        """Scale coordinates between resolutions"""
        if not self._scaling_enabled:
            return x, y

        x_scale = SCALE_DESTINATION['width'] / self.width
        y_scale = SCALE_DESTINATION['height'] / self.height

        if source == ScalingSource.API:
            if x > SCALE_DESTINATION['width'] or y > SCALE_DESTINATION['height']:
                raise ToolError(f"Coordinates {x}, {y} out of bounds")
            return round(x / x_scale), round(y / y_scale)
        else:
            return round(x * x_scale), round(y * y_scale)

    async def _handle_key_press(self, text: str) -> ToolResult:
        """Handle keyboard key press actions"""
        try:
            if "+" in text:
                keys = text.split("+")
                mapped_keys = [self._map_key(k.strip()) for k in keys]
                await asyncio.get_event_loop().run_in_executor(
                    None, keyboard.press_and_release, '+'.join(mapped_keys)
                )
            else:
                mapped_key = self._map_key(text)
                await asyncio.get_event_loop().run_in_executor(
                    None, keyboard.press_and_release, mapped_key
                )
            return ToolResult(output=f"Pressed key: {text}")
        except Exception as e:
            return ToolResult(error=f"Key press failed: {str(e)}")

    async def _handle_typing(self, text: str) -> ToolResult:
        """Handle text typing actions"""
        try:
            results = []
            for chunk in self._chunk_text(text, TYPING_GROUP_SIZE):
                cmd = f"cliclick w:{TYPING_DELAY_MS} t:{shlex.quote(chunk)}"
                results.append(await self.shell(cmd, take_screenshot=False))
            
            screenshot = await self.screenshot()
            return ToolResult(
                output="".join(r.output or "" for r in results),
                error="".join(r.error or "" for r in results),
                base64_image=screenshot.base64_image
            )
        except Exception as e:
            return ToolResult(error=f"Typing failed: {str(e)}")

    async def _get_cursor_position(self) -> ToolResult:
        """Get current cursor position"""
        try:
            result = await self.shell("cliclick p", take_screenshot=False)
            if result.output:
                x, y = map(int, result.output.strip().split(","))
                x, y = self.scale_coordinates(ScalingSource.COMPUTER, x, y)
                return result.replace(output=f"X={x},Y={y}")
            return result
        except Exception as e:
            return ToolResult(error=f"Failed to get cursor position: {str(e)}")

    async def shell(self, command: str, take_screenshot: bool = True) -> ToolResult:
        """Execute shell command and optionally take screenshot"""
        try:
            _, stdout, stderr = await run(command)
            base64_image = None

            if take_screenshot:
                await asyncio.sleep(self._screenshot_delay)
                base64_image = (await self.screenshot()).base64_image

            return ToolResult(output=stdout, error=stderr, base64_image=base64_image)
        except Exception as e:
            return ToolResult(error=f"Shell command failed: {str(e)}")

    async def _handle_sidecar_list(self) -> ToolResult:
        """List available iPads for Sidecar"""
        try:
            ipads = await self.sidecar.get_available_ipads()
            return ToolResult(output=str(ipads))
        except Exception as e:
            return ToolResult(error=f"Failed to list iPads: {str(e)}")

    async def _handle_sidecar_connect(
        self, ipad_name: str, position: Optional[str] = None
    ) -> ToolResult:
        """Connect to iPad via Sidecar"""
        try:
            success = await self.sidecar.start_sidecar(ipad_name, position)
            if success:
                return ToolResult(
                    output=f"Connected to {ipad_name}",
                    base64_image=(await self.screenshot()).base64_image
                )
            return ToolResult(error=f"Failed to connect to {ipad_name}")
        except Exception as e:
            return ToolResult(error=f"Sidecar connection failed: {str(e)}")

    async def _handle_sidecar_configure(self, **kwargs) -> ToolResult:
        """Configure Sidecar display"""
        try:
            success = await self.sidecar.configure_display(**kwargs)
            if success:
                return ToolResult(
                    output="Display configured successfully",
                    base64_image=(await self.screenshot()).base64_image
                )
            return ToolResult(error="Failed to configure display")
        except Exception as e:
            return ToolResult(error=f"Display configuration failed: {str(e)}")

    def to_params(self) -> BetaToolUnionParam:
        """Convert tool to API parameters."""
        return {
            "type": self.api_type,
            "name": self.name,
        }
