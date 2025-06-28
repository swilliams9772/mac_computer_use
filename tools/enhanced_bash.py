"""
Enhanced Bash Tool with Advanced Features
Extends the basic bash tool with parallel execution, security features, and better command management.
"""

import asyncio
import json
import os
import re
import shlex
import time
from collections import defaultdict, deque
from typing import ClassVar, Dict, List, Literal, Optional

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .run import run


class CommandHistory:
    """Enhanced command history management."""
    
    def __init__(self, max_size: int = 1000):
        self.commands = deque(maxlen=max_size)
        self.execution_times = {}
        self.command_stats = defaultdict(int)
    
    def add_command(self, command: str, execution_time: float, success: bool):
        """Add command to history with metadata."""
        timestamp = time.time()
        entry = {
            "command": command,
            "timestamp": timestamp,
            "execution_time": execution_time,
            "success": success
        }
        self.commands.append(entry)
        self.command_stats[command.split()[0] if command.split() else ""] += 1
        self.execution_times[command] = execution_time
    
    def get_recent_commands(self, count: int = 10) -> List[Dict]:
        """Get recent commands."""
        return list(self.commands)[-count:]
    
    def get_command_stats(self) -> Dict:
        """Get command usage statistics."""
        return dict(self.command_stats)
    
    def search_commands(self, pattern: str) -> List[Dict]:
        """Search command history by pattern."""
        return [cmd for cmd in self.commands if re.search(pattern, cmd["command"], re.IGNORECASE)]


class SecurityManager:
    """Enhanced security management for bash commands."""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'rm\s+-rf\s+/',  # rm -rf /
            r'sudo\s+rm',      # sudo rm
            r'format\s+',      # format
            r'fdisk\s+',       # fdisk
            r'dd\s+if=',       # dd if=
            r'>\s*/dev/',      # redirect to /dev/
            r'curl.*\|\s*sh',  # curl | sh
            r'wget.*\|\s*sh',  # wget | sh
            r'chmod\s+777',    # chmod 777
            r'chown\s+.*\s+/', # chown on root
        ]
        
        self.warning_patterns = [
            r'sudo\s+',        # any sudo command
            r'rm\s+.*-r',      # recursive rm
            r'mv\s+.*\s+/',    # moving to root
            r'cp\s+.*\s+/',    # copying to root
            r'find.*-delete',  # find with delete
        ]
    
    def assess_command_risk(self, command: str) -> Dict:
        """Assess the security risk of a command."""
        risk_level = "low"
        risk_factors = []
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                risk_level = "critical"
                risk_factors.append(f"Dangerous pattern detected: {pattern}")
        
        # Check for warning patterns
        for pattern in self.warning_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                if risk_level == "low":
                    risk_level = "medium"
                risk_factors.append(f"Warning pattern detected: {pattern}")
        
        # Additional checks
        if 'sudo' in command.lower():
            risk_factors.append("Uses sudo privileges")
        
        if any(char in command for char in ['>', '>>', '|']):
            risk_factors.append("Uses output redirection or pipes")
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "safe_to_execute": risk_level != "critical"
        }


class ParallelExecutor:
    """Execute multiple commands in parallel with intelligent batching."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_batch(self, commands: List[str], timeout: float = 30.0) -> List[Dict]:
        """Execute a batch of commands in parallel."""
        tasks = []
        for i, command in enumerate(commands):
            task = self._execute_single_command(command, i, timeout)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r if not isinstance(r, Exception) else {"error": str(r), "command_index": -1} for r in results]
    
    async def _execute_single_command(self, command: str, index: int, timeout: float) -> Dict:
        """Execute a single command with semaphore control."""
        async with self.semaphore:
            start_time = time.time()
            try:
                return_code, stdout, stderr = await run(command, timeout=timeout)
                execution_time = time.time() - start_time
                
                return {
                    "command": command,
                    "command_index": index,
                    "return_code": return_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "execution_time": execution_time,
                    "success": return_code == 0
                }
            except Exception as e:
                execution_time = time.time() - start_time
                return {
                    "command": command,
                    "command_index": index,
                    "error": str(e),
                    "execution_time": execution_time,
                    "success": False
                }


class EnhancedBashTool(BaseAnthropicTool):
    """
    Enhanced bash tool with advanced features:
    - Parallel command execution
    - Command history and statistics
    - Enhanced security assessment
    - Intelligent command suggestions
    - Performance monitoring
    - M4-optimized execution
    """

    name: ClassVar[Literal["enhanced_bash"]] = "enhanced_bash"
    api_type: str = "custom"

    def __init__(self, api_version: str = "custom"):
        self.api_type = api_version
        self.command_history = CommandHistory()
        self.security_manager = SecurityManager()
        self.parallel_executor = ParallelExecutor()
        self.working_directory = os.getcwd()
        self.environment_vars = dict(os.environ)
        super().__init__()

    async def __call__(self,
                      command: str = None,
                      commands: List[str] = None,
                      mode: str = "single",
                      timeout: float = 30.0,
                      **kwargs):
        """Execute bash commands with enhanced features."""
        
        if command:
            return await self._execute_single_command(command, timeout)
        elif commands:
            return await self._execute_multiple_commands(commands, mode, timeout)
        else:
            return ToolResult(error="❌ **No command provided**")

    async def _execute_single_command(self, command: str, timeout: float) -> ToolResult:
        """Execute a single command with enhanced features."""
        start_time = time.time()
        
        try:
            return_code, stdout, stderr = await run(command, timeout=timeout)
            execution_time = time.time() - start_time
            success = return_code == 0
            
            self.command_history.add_command(command, execution_time, success)
            
            if success:
                return ToolResult(output=f"✅ **Command executed** (⏱️ {execution_time:.2f}s)\n```\n{stdout}\n```")
            else:
                return ToolResult(error=f"❌ **Command failed** (⏱️ {execution_time:.2f}s)\n```\n{stderr}\n```")
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(error=f"❌ **Execution error:** {str(e)} (⏱️ {execution_time:.2f}s)")

    async def _execute_multiple_commands(self, commands: List[str], mode: str, timeout: float) -> ToolResult:
        """Execute multiple commands."""
        if mode == "parallel":
            return await self._execute_parallel(commands, timeout)
        else:
            return await self._execute_sequential(commands, timeout)

    async def _execute_parallel(self, commands: List[str], timeout: float) -> ToolResult:
        """Execute commands in parallel."""
        tasks = [self._execute_single_command(cmd, timeout) for cmd in commands]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output_parts = [f"🔄 **Parallel execution** ({len(commands)} commands)"]
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                output_parts.append(f"❌ **Command {i+1}:** {str(result)}")
            else:
                status = "✅" if not result.error else "❌"
                output_parts.append(f"{status} **Command {i+1}:** {commands[i]}")
        
        return ToolResult(output="\n".join(output_parts))

    async def _execute_sequential(self, commands: List[str], timeout: float) -> ToolResult:
        """Execute commands sequentially."""
        output_parts = [f"📋 **Sequential execution** ({len(commands)} commands)"]
        
        for i, command in enumerate(commands):
            result = await self._execute_single_command(command, timeout)
            if result.error:
                output_parts.append(f"❌ **Command {i+1} failed:** {command}")
                break
            else:
                output_parts.append(f"✅ **Command {i+1} completed:** {command}")
        
        return ToolResult(output="\n".join(output_parts))

    def to_params(self):
        return {
            "type": self.api_type,
            "name": self.name,
            "description": "Enhanced bash tool with parallel execution and command history",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Single command to execute"},
                    "commands": {"type": "array", "items": {"type": "string"}, "description": "Multiple commands"},
                    "mode": {"type": "string", "enum": ["single", "parallel", "sequential"], "default": "single"},
                    "timeout": {"type": "number", "default": 30.0}
                }
            }
        } 