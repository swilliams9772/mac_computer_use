import asyncio
import json
from typing import ClassVar, Literal

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .run import run


class SiliconTool(BaseAnthropicTool):
    """
    A tool for Apple Silicon specific monitoring and hardware information.
    Provides access to M-series chip features and system optimization data.
    """

    name: ClassVar[Literal["silicon"]] = "silicon"
    api_type: str = "custom"  # Always use "custom" for custom tools

    def __init__(self, api_version: str = "custom"):
        # Custom tools always use "custom" type for API calls
        self.api_version = api_version
        super().__init__()

    async def __call__(
        self,
        action: str,
        target: str | None = None,
        **kwargs
    ):
        """
        Execute Apple Silicon specific operations.
        
        Args:
            action: The action to perform ('performance', 'thermal', 'memory', 'system_info')
            target: Optional target for the action
        """
        if action not in ["performance", "thermal", "memory", "system_info"]:
            raise ToolError("action must be one of: performance, thermal, memory, system_info")

        try:
            if action == "performance":
                return await self._get_performance_info()
            elif action == "thermal":
                return await self._get_thermal_info()
            elif action == "memory":
                return await self._get_memory_info()
            elif action == "system_info":
                return await self._get_system_info()
            
        except Exception as e:
            return CLIResult(error=f"Silicon tool error: {str(e)}")

    async def _get_performance_info(self):
        """Get Apple Silicon performance information."""
        cmd = "system_profiler SPHardwareDataType -json"
        return_code, stdout, stderr = await run(cmd, timeout=30.0)
        
        if return_code == 0:
            try:
                data = json.loads(stdout)
                hardware = data.get('SPHardwareDataType', [{}])[0]
                
                info = f"""Apple Silicon Performance Information:
Chip: {hardware.get('chip_type', 'Unknown')}
Cores: {hardware.get('total_number_of_cores', 'Unknown')}
Memory: {hardware.get('physical_memory', 'Unknown')}
Model: {hardware.get('machine_model', 'Unknown')}"""
                
                return CLIResult(output=info)
            except json.JSONDecodeError:
                return CLIResult(output=stdout, error="Could not parse JSON output")
        else:
            return CLIResult(error=f"Command failed: {stderr}")

    async def _get_thermal_info(self):
        """Get thermal information."""
        cmd = "pmset -g thermlog"
        return_code, stdout, stderr = await run(cmd, timeout=10.0)
        
        if return_code == 0:
            return CLIResult(output=f"Thermal Status:\n{stdout}")
        else:
            # Fallback to basic thermal info
            cmd2 = "sysctl machdep.xcpm.cpu_thermal_state"
            return_code2, stdout2, stderr2 = await run(cmd2, timeout=10.0)
            return CLIResult(output=f"CPU Thermal State:\n{stdout2}", error=stderr2 if stderr2 else None)

    async def _get_memory_info(self):
        """Get unified memory information."""
        cmd = "vm_stat && echo '---' && memory_pressure"
        return_code, stdout, stderr = await run(cmd, timeout=10.0)
        
        return CLIResult(output=f"Memory Status:\n{stdout}", error=stderr if stderr else None)

    async def _get_system_info(self):
        """Get comprehensive Apple Silicon system information."""
        cmd = "sw_vers && echo '---' && uname -a && echo '---' && sysctl hw.model hw.ncpu hw.memsize"
        return_code, stdout, stderr = await run(cmd, timeout=20.0)
        
        return CLIResult(output=f"Apple Silicon System Info:\n{stdout}", 
                        error=stderr if stderr else None)

    def to_params(self):
        return {
            "type": self.api_type,
            "name": self.name,
            "description": "Monitor Apple Silicon hardware performance, thermal status, and system information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["performance", "thermal", "memory", "system_info"],
                        "description": "The Apple Silicon specific action to perform"
                    },
                    "target": {
                        "type": "string",
                        "description": "Optional target parameter for specific actions"
                    }
                },
                "required": ["action"]
            }
        } 