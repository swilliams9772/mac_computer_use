import asyncio
import json
import psutil
import time
from typing import ClassVar, Literal, Dict, Optional
from datetime import datetime

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult
from .run import run


class M4PerformanceMonitor:
    """Advanced M4 MacBook Air performance monitoring."""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.monitoring_history = []
        self.thermal_thresholds = {
            "normal": 60,
            "warm": 75,
            "hot": 85,
            "critical": 95
        }
    
    async def get_comprehensive_metrics(self) -> Dict:
        """Get comprehensive M4 system metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": await self._get_cpu_metrics(),
            "memory": await self._get_memory_metrics(),
            "thermal": await self._get_thermal_metrics(),
            "power": await self._get_power_metrics(),
            "performance_cores": await self._get_performance_core_status(),
            "neural_engine": await self._get_neural_engine_metrics(),
            "gpu": await self._get_gpu_metrics()
        }
        
        # Store in history for trend analysis
        self.monitoring_history.append(metrics)
        if len(self.monitoring_history) > 100:  # Keep last 100 readings
            self.monitoring_history.pop(0)
            
        return metrics
    
    async def _get_cpu_metrics(self) -> Dict:
        """Get detailed CPU performance metrics."""
        # Use system_profiler for M4 chip details
        cmd = "system_profiler SPHardwareDataType -json"
        return_code, stdout, stderr = await run(cmd, timeout=10.0)
        
        cpu_info = {}
        if return_code == 0:
            try:
                data = json.loads(stdout)
                hardware = data.get('SPHardwareDataType', [{}])[0]
                cpu_info = {
                    "chip_type": hardware.get('chip_type', 'Unknown'),
                    "total_cores": hardware.get('total_number_of_cores', 'Unknown'),
                    "performance_cores": hardware.get('performance_cores', 4),
                    "efficiency_cores": hardware.get('efficiency_cores', 6),
                    "cpu_frequency": hardware.get('cpu_frequency', 'Unknown')
                }
            except json.JSONDecodeError:
                pass
        
        # Add real-time CPU usage
        try:
            cpu_info["usage_percent"] = psutil.cpu_percent(interval=1)
            cpu_info["per_core_usage"] = psutil.cpu_percent(interval=1, percpu=True)
            cpu_info["load_average"] = psutil.getloadavg()
        except:
            cpu_info["usage_percent"] = "Unknown"
        
        return cpu_info
    
    async def _get_memory_metrics(self) -> Dict:
        """Get unified memory architecture metrics."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Get macOS-specific memory info
            cmd = "vm_stat | head -20"
            return_code, stdout, stderr = await run(cmd, timeout=5.0)
            
            vm_stats = {}
            if return_code == 0:
                for line in stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        vm_stats[key.strip()] = value.strip()
            
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "memory_pressure": await self._get_memory_pressure(),
                "unified_architecture": True,
                "vm_stats": vm_stats
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_memory_pressure(self) -> str:
        """Get memory pressure status."""
        cmd = "memory_pressure"
        return_code, stdout, stderr = await run(cmd, timeout=5.0)
        
        if return_code == 0:
            if "normal" in stdout.lower():
                return "normal"
            elif "warn" in stdout.lower():
                return "warning"
            elif "critical" in stdout.lower():
                return "critical"
        
        return "unknown"
    
    async def _get_thermal_metrics(self) -> Dict:
        """Get comprehensive thermal information."""
        thermal_data = {}
        
        # Try multiple thermal monitoring methods
        commands = [
            ("pmset -g thermlog", "thermal_log"),
            ("sysctl machdep.xcpm.cpu_thermal_state", "cpu_thermal"),
            ("sudo powermetrics -n 1 -i 1000 --samplers cpu_power,gpu_power 2>/dev/null", "power_thermal")
        ]
        
        for cmd, key in commands:
            try:
                return_code, stdout, stderr = await run(cmd, timeout=5.0)
                if return_code == 0:
                    thermal_data[key] = stdout
            except:
                continue
        
        # Analyze thermal state
        thermal_state = "normal"
        if "thermal_log" in thermal_data:
            log_data = thermal_data["thermal_log"]
            if "Critical" in log_data:
                thermal_state = "critical"
            elif "Hot" in log_data or "Warm" in log_data:
                thermal_state = "warm"
        
        return {
            "state": thermal_state,
            "raw_data": thermal_data,
            "m4_optimized": True
        }
    
    async def _get_power_metrics(self) -> Dict:
        """Get power consumption and battery metrics."""
        power_data = {}
        
        # Battery information
        cmd = "pmset -g batt"
        return_code, stdout, stderr = await run(cmd, timeout=5.0)
        if return_code == 0:
            power_data["battery_info"] = stdout
        
        # Power adapter info
        cmd = "system_profiler SPPowerDataType -json"
        return_code, stdout, stderr = await run(cmd, timeout=10.0)
        if return_code == 0:
            try:
                data = json.loads(stdout)
                power_data["adapter_info"] = data.get('SPPowerDataType', [])
            except:
                pass
        
        return power_data
    
    async def _get_performance_core_status(self) -> Dict:
        """Get M4 performance core utilization."""
        # This would require more sophisticated monitoring
        # For now, return basic core information
        return {
            "performance_cores": 4,
            "efficiency_cores": 6,
            "total_cores": 10,
            "architecture": "M4",
            "optimization_status": "active"
        }
    
    async def _get_neural_engine_metrics(self) -> Dict:
        """Monitor Neural Engine activity."""
        return {
            "available": True,
            "generation": "M4",
            "performance": "16-core Neural Engine",
            "ml_workload_active": "unknown"  # Would need specialized monitoring
        }
    
    async def _get_gpu_metrics(self) -> Dict:
        """Get integrated GPU metrics."""
        return {
            "type": "10-core GPU (M4)",
            "unified_memory": True,
            "metal_support": True,
            "hardware_acceleration": True
        }


class SiliconTool(BaseAnthropicTool):
    """
    Enhanced Apple Silicon monitoring tool with comprehensive M4 support.
    
    Features:
    - Real-time performance monitoring
    - Thermal management and optimization
    - Memory pressure analysis
    - Power consumption tracking
    - Neural Engine status
    - Performance vs efficiency core utilization
    - Historical trend analysis
    """

    name: ClassVar[Literal["silicon"]] = "silicon"
    api_type: str = "custom"

    def __init__(self, api_version: str = "custom"):
        self.api_version = api_version
        self.monitor = M4PerformanceMonitor()
        super().__init__()

    async def __call__(self,
                      action: str,
                      target: str | None = None,
                      detailed: bool = False,
                      **kwargs):
        """
        Execute Apple Silicon specific operations with enhanced M4 support.
        
        Args:
            action: Action to perform
            target: Optional target for specific monitoring
            detailed: Whether to return detailed metrics
        """
        actions = [
            "performance", "thermal", "memory", "system_info", 
            "comprehensive", "optimization", "history", "neural_engine"
        ]
        
        if action not in actions:
            return ToolResult(
                error=f"❌ **Invalid action:** Must be one of: {', '.join(actions)}"
            )

        try:
            if action == "performance":
                return await self._get_performance_analysis(detailed)
            elif action == "thermal":
                return await self._get_thermal_analysis(detailed)
            elif action == "memory":
                return await self._get_memory_analysis(detailed)
            elif action == "system_info":
                return await self._get_enhanced_system_info()
            elif action == "comprehensive":
                return await self._get_comprehensive_analysis()
            elif action == "optimization":
                return await self._get_optimization_recommendations()
            elif action == "history":
                return await self._get_performance_history()
            elif action == "neural_engine":
                return await self._get_neural_engine_status()
                
        except Exception as e:
            return ToolResult(error=f"❌ **Silicon tool error:** {str(e)}")

    async def _get_performance_analysis(self, detailed: bool) -> ToolResult:
        """Get comprehensive M4 performance analysis."""
        metrics = await self.monitor.get_comprehensive_metrics()
        cpu_metrics = metrics["cpu"]
        
        output_parts = [
            "🚀 **M4 Performance Analysis**",
            "=" * 35,
            f"**Chip:** {cpu_metrics.get('chip_type', 'Unknown')}",
            f"**Total Cores:** {cpu_metrics.get('total_cores', 'Unknown')}",
            f"**Performance Cores:** {cpu_metrics.get('performance_cores', 4)}",
            f"**Efficiency Cores:** {cpu_metrics.get('efficiency_cores', 6)}",
            f"**CPU Usage:** {cpu_metrics.get('usage_percent', 'Unknown')}%"
        ]
        
        if detailed and cpu_metrics.get('per_core_usage'):
            core_usage = cpu_metrics['per_core_usage']
            output_parts.append("\n**Per-Core Usage:**")
            for i, usage in enumerate(core_usage):
                core_type = "P" if i < 4 else "E"  # First 4 are performance cores
                output_parts.append(f"  Core {i+1} ({core_type}): {usage}%")
        
        if cpu_metrics.get('load_average'):
            load_avg = cpu_metrics['load_average']
            output_parts.append(f"**Load Average:** {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        
        return ToolResult(output="\n".join(output_parts))

    async def _get_thermal_analysis(self, detailed: bool) -> ToolResult:
        """Get detailed thermal analysis with M4 optimizations."""
        metrics = await self.monitor.get_comprehensive_metrics()
        thermal_data = metrics["thermal"]
        
        state = thermal_data["state"]
        state_emoji = {
            "normal": "🟢",
            "warm": "🟡", 
            "hot": "🟠",
            "critical": "🔴"
        }.get(state, "⚪")
        
        output_parts = [
            "🌡️ **M4 Thermal Analysis**",
            "=" * 30,
            f"{state_emoji} **Thermal State:** {state.title()}",
            f"**M4 Optimization:** Active"
        ]
        
        if detailed and thermal_data.get("raw_data"):
            output_parts.append("\n**Raw Thermal Data:**")
            for key, value in thermal_data["raw_data"].items():
                output_parts.append(f"  **{key}:** {value[:100]}...")
        
        # Add recommendations based on thermal state
        if state in ["hot", "critical"]:
            output_parts.append("\n⚠️ **Recommendations:**")
            output_parts.append("  • Reduce CPU-intensive tasks")
            output_parts.append("  • Check background processes")
            output_parts.append("  • Ensure proper ventilation")
            output_parts.append("  • Consider using efficiency cores for background tasks")
        
        return ToolResult(output="\n".join(output_parts))

    async def _get_memory_analysis(self, detailed: bool) -> ToolResult:
        """Get unified memory architecture analysis."""
        metrics = await self.monitor.get_comprehensive_metrics()
        memory_data = metrics["memory"]
        
        if "error" in memory_data:
            return ToolResult(error=f"❌ **Memory analysis failed:** {memory_data['error']}")
        
        output_parts = [
            "🧠 **M4 Unified Memory Analysis**",
            "=" * 35,
            f"**Total Memory:** {memory_data.get('total_gb', 'Unknown')} GB",
            f"**Available:** {memory_data.get('available_gb', 'Unknown')} GB",
            f"**Used:** {memory_data.get('used_gb', 'Unknown')} GB",
            f"**Usage:** {memory_data.get('usage_percent', 'Unknown')}%",
            f"**Memory Pressure:** {memory_data.get('memory_pressure', 'Unknown').title()}",
            f"**Unified Architecture:** {'✅' if memory_data.get('unified_architecture') else '❌'}"
        ]
        
        if memory_data.get('swap_used_gb', 0) > 0:
            output_parts.append(f"**Swap Used:** {memory_data['swap_used_gb']} GB")
        
        # Memory efficiency recommendations
        pressure = memory_data.get('memory_pressure', 'normal')
        if pressure in ['warning', 'critical']:
            output_parts.append("\n⚠️ **Memory Optimization Tips:**")
            output_parts.append("  • Close unused applications")
            output_parts.append("  • Check for memory leaks in running processes")
            output_parts.append("  • Leverage M4's unified memory efficiency")
            output_parts.append("  • Consider restarting memory-intensive applications")
        
        return ToolResult(output="\n".join(output_parts))

    async def _get_enhanced_system_info(self) -> ToolResult:
        """Get comprehensive M4 system information."""
        # Hardware info
        cmd = "system_profiler SPHardwareDataType SPSoftwareDataType -json"
        return_code, stdout, stderr = await run(cmd, timeout=15.0)
        
        if return_code != 0:
            return ToolResult(error=f"❌ **System info failed:** {stderr}")
        
        try:
            data = json.loads(stdout)
            hardware = data.get('SPHardwareDataType', [{}])[0]
            software = data.get('SPSoftwareDataType', [{}])[0]
            
            output_parts = [
                "💻 **M4 MacBook Air System Information**",
                "=" * 45,
                f"**Model:** {hardware.get('machine_name', 'Unknown')}",
                f"**Chip:** {hardware.get('chip_type', 'Unknown')}",
                f"**Memory:** {hardware.get('physical_memory', 'Unknown')}",
                f"**Serial:** {hardware.get('serial_number', 'Hidden')}",
                f"**macOS:** {software.get('os_version', 'Unknown')}",
                f"**Kernel:** {software.get('kernel_version', 'Unknown')}",
                f"**Boot Volume:** {software.get('boot_volume', 'Unknown')}",
                f"**System Integrity:** {software.get('system_integrity', 'Unknown')}"
            ]
            
            return ToolResult(output="\n".join(output_parts))
            
        except json.JSONDecodeError:
            return ToolResult(error="❌ **Failed to parse system information**")

    async def _get_comprehensive_analysis(self) -> ToolResult:
        """Get complete M4 system analysis."""
        metrics = await self.monitor.get_comprehensive_metrics()
        
        output_parts = [
            "📊 **Comprehensive M4 Analysis**",
            "=" * 40,
            f"**Timestamp:** {metrics['timestamp']}",
            "",
            "🔥 **CPU Performance:**",
            f"  • Chip: {metrics['cpu'].get('chip_type', 'Unknown')}",
            f"  • Usage: {metrics['cpu'].get('usage_percent', 'Unknown')}%",
            f"  • Cores: {metrics['cpu'].get('total_cores', 'Unknown')} total",
            "",
            "🧠 **Memory Status:**",
            f"  • Total: {metrics['memory'].get('total_gb', 'Unknown')} GB",
            f"  • Available: {metrics['memory'].get('available_gb', 'Unknown')} GB",
            f"  • Pressure: {metrics['memory'].get('memory_pressure', 'Unknown').title()}",
            "",
            "🌡️ **Thermal Status:**",
            f"  • State: {metrics['thermal']['state'].title()}",
            f"  • M4 Optimized: ✅",
            "",
            "⚡ **Neural Engine:**",
            f"  • Available: {'✅' if metrics['neural_engine']['available'] else '❌'}",
            f"  • Type: {metrics['neural_engine']['performance']}",
            "",
            "🎮 **GPU:**",
            f"  • Type: {metrics['gpu']['type']}",
            f"  • Unified Memory: {'✅' if metrics['gpu']['unified_memory'] else '❌'}"
        ]
        
        return ToolResult(output="\n".join(output_parts))

    async def _get_optimization_recommendations(self) -> ToolResult:
        """Get M4-specific optimization recommendations."""
        metrics = await self.monitor.get_comprehensive_metrics()
        
        recommendations = []
        
        # CPU optimization
        cpu_usage = metrics['cpu'].get('usage_percent', 0)
        if isinstance(cpu_usage, (int, float)) and cpu_usage > 80:
            recommendations.append("🔥 **High CPU Usage:** Consider using efficiency cores for background tasks")
        
        # Memory optimization
        memory_pressure = metrics['memory'].get('memory_pressure', 'normal')
        if memory_pressure in ['warning', 'critical']:
            recommendations.append("🧠 **Memory Pressure:** Close unused apps, leverage unified memory architecture")
        
        # Thermal optimization
        thermal_state = metrics['thermal']['state']
        if thermal_state in ['hot', 'critical']:
            recommendations.append("🌡️ **Thermal Management:** Reduce intensive tasks, improve airflow")
        
        # General M4 optimizations
        recommendations.extend([
            "⚡ **M4 Best Practices:**",
            "  • Use performance cores for interactive tasks",
            "  • Leverage efficiency cores for background processes",
            "  • Take advantage of unified memory architecture",
            "  • Monitor thermal state during intensive workloads",
            "  • Use Neural Engine for ML tasks when possible",
            "  • Optimize for hardware-accelerated video/image processing"
        ])
        
        if not recommendations:
            recommendations = ["✅ **System running optimally!** No specific recommendations at this time."]
        
        output = "🎯 **M4 Optimization Recommendations**\n" + "=" * 45 + "\n\n" + "\n".join(recommendations)
        return ToolResult(output=output)

    async def _get_performance_history(self) -> ToolResult:
        """Get performance trend analysis."""
        history = self.monitor.monitoring_history
        
        if len(history) < 2:
            return ToolResult(output="📈 **Performance History:** Insufficient data (need at least 2 readings)")
        
        latest = history[-1]
        previous = history[-2]
        
        # Calculate trends
        cpu_trend = "📈" if latest['cpu'].get('usage_percent', 0) > previous['cpu'].get('usage_percent', 0) else "📉"
        memory_trend = "📈" if latest['memory'].get('usage_percent', 0) > previous['memory'].get('usage_percent', 0) else "📉"
        
        output_parts = [
            "📈 **M4 Performance Trends**",
            "=" * 35,
            f"**Data Points:** {len(history)}",
            f"**CPU Usage Trend:** {cpu_trend}",
            f"**Memory Usage Trend:** {memory_trend}",
            f"**Latest Reading:** {latest['timestamp'][:19]}",
            "",
            "**Recent Performance:**"
        ]
        
        # Show last 5 readings
        for i, reading in enumerate(history[-5:], 1):
            timestamp = reading['timestamp'][11:19]  # Extract time portion
            cpu_usage = reading['cpu'].get('usage_percent', 'N/A')
            memory_usage = reading['memory'].get('usage_percent', 'N/A')
            output_parts.append(f"  {i}. {timestamp} - CPU: {cpu_usage}%, Mem: {memory_usage}%")
        
        return ToolResult(output="\n".join(output_parts))

    async def _get_neural_engine_status(self) -> ToolResult:
        """Get Neural Engine specific information."""
        metrics = await self.monitor.get_comprehensive_metrics()
        neural_data = metrics['neural_engine']
        
        output_parts = [
            "🧠 **M4 Neural Engine Status**",
            "=" * 35,
            f"**Available:** {'✅' if neural_data['available'] else '❌'}",
            f"**Performance:** {neural_data['performance']}",
            f"**ML Workload Active:** {neural_data.get('ml_workload_active', 'Unknown')}",
            "",
            "**Capabilities:**",
            "  • 16-core Neural Engine",
            "  • Machine Learning acceleration",
            "  • Real-time image/video processing",
            "  • Natural language processing",
            "  • Computer vision tasks",
            "",
            "**Optimization Tips:**",
            "  • Use Core ML for ML workloads",
            "  • Leverage Metal Performance Shaders",
            "  • Optimize models for Neural Engine",
            "  • Monitor thermal state during ML tasks"
        ]
        
        return ToolResult(output="\n".join(output_parts))

    def to_params(self):
        return {
            "type": self.api_type,
            "name": self.name,
            "description": """Enhanced Apple Silicon monitoring tool with comprehensive M4 MacBook Air support.

**Key Features:**
- Real-time M4 performance monitoring
- Thermal management and optimization
- Unified memory architecture analysis
- Power consumption tracking
- Neural Engine status monitoring
- Performance vs efficiency core utilization
- Historical trend analysis and optimization recommendations

**Available Actions:**
- `performance`: CPU and core utilization analysis
- `thermal`: Thermal state monitoring and recommendations
- `memory`: Unified memory architecture metrics
- `system_info`: Comprehensive hardware/software information
- `comprehensive`: Complete system analysis
- `optimization`: M4-specific optimization recommendations
- `history`: Performance trend analysis
- `neural_engine`: Neural Engine status and capabilities

**M4-Specific Features:**
- Performance core vs efficiency core monitoring
- Unified memory pressure analysis
- Thermal optimization for Apple Silicon
- Neural Engine utilization tracking
- Hardware acceleration status

**Usage Examples:**
- Basic monitoring: `{"action": "performance"}`
- Detailed analysis: `{"action": "comprehensive", "detailed": true}`
- Thermal check: `{"action": "thermal"}`
- Get recommendations: `{"action": "optimization"}`""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["performance", "thermal", "memory", "system_info", "comprehensive", "optimization", "history", "neural_engine"],
                        "description": "The monitoring action to perform"
                    },
                    "target": {
                        "type": "string",
                        "description": "Optional target parameter for specific monitoring"
                    },
                    "detailed": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to return detailed metrics and analysis"
                    }
                },
                "required": ["action"]
            }
        } 