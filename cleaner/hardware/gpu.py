"""
GPU Monitoring Module für GermanCodeZero-Cleaner
================================================

GPU-Überwachung für NVIDIA, AMD und Intel GPUs.
"""

import sys
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# NVIDIA GPU Support
try:
    import pynvml
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

# AMD GPU Support
try:
    import pyamdgpuinfo
    AMD_AVAILABLE = True
except ImportError:
    AMD_AVAILABLE = False

import psutil


@dataclass
class GPUInfo:
    """GPU-Informationen."""
    index: int
    name: str
    vendor: str
    driver_version: str
    memory_total: int  # Bytes
    compute_capability: tuple
    pcie_generation: int
    power_limit: float  # Watts
    temperature_max: float  # Celsius
    clock_max_graphics: int  # MHz
    clock_max_memory: int  # MHz


@dataclass 
class GPUUsage:
    """Aktuelle GPU-Nutzung."""
    timestamp: datetime
    gpu_utilization: float  # Percent
    memory_used: int  # Bytes
    memory_percent: float
    temperature: float  # Celsius
    power_draw: float  # Watts
    clock_graphics: int  # MHz
    clock_memory: int  # MHz
    fan_speed: float  # Percent
    processes: List[Dict[str, Any]]


class GPUMonitor:
    """GPU-Überwachung."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gpu_count = 0
        self.gpu_info: List[GPUInfo] = []
        self.current_usage: Dict[int, GPUUsage] = {}
        
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0
        
        self._initialize_gpu()
    
    def _initialize_gpu(self):
        """Initialisiert GPU-Überwachung."""
        if NVIDIA_AVAILABLE:
            self._init_nvidia()
        elif AMD_AVAILABLE:
            self._init_amd()
        else:
            self.logger.info("No GPU monitoring available")
    
    def _init_nvidia(self):
        """Initialisiert NVIDIA GPU."""
        try:
            pynvml.nvmlInit()
            self.gpu_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(self.gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                info = GPUInfo(
                    index=i,
                    name=pynvml.nvmlDeviceGetName(handle).decode('utf-8'),
                    vendor="NVIDIA",
                    driver_version=pynvml.nvmlSystemGetDriverVersion().decode('utf-8'),
                    memory_total=pynvml.nvmlDeviceGetMemoryInfo(handle).total,
                    compute_capability=pynvml.nvmlDeviceGetCudaComputeCapability(handle),
                    pcie_generation=pynvml.nvmlDeviceGetMaxPcieLinkGeneration(handle),
                    power_limit=pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000,
                    temperature_max=pynvml.nvmlDeviceGetTemperatureThreshold(
                        handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SHUTDOWN
                    ),
                    clock_max_graphics=pynvml.nvmlDeviceGetMaxClockInfo(
                        handle, pynvml.NVML_CLOCK_GRAPHICS
                    ),
                    clock_max_memory=pynvml.nvmlDeviceGetMaxClockInfo(
                        handle, pynvml.NVML_CLOCK_MEM
                    )
                )
                
                self.gpu_info.append(info)
                
            self.logger.info(f"Initialized {self.gpu_count} NVIDIA GPUs")
            
        except Exception as e:
            self.logger.error(f"NVIDIA init failed: {e}")
    
    def _init_amd(self):
        """Initialisiert AMD GPU."""
        # Placeholder für AMD Support
        pass
    
    def start_monitoring(self, interval: float = 1.0):
        """Startet GPU-Überwachung."""
        if self.monitoring or self.gpu_count == 0:
            return
        
        self.monitoring = True
        self.update_interval = interval
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stoppt GPU-Überwachung."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Überwachungsschleife."""
        while self.monitoring:
            try:
                for i in range(self.gpu_count):
                    usage = self._get_gpu_usage(i)
                    if usage:
                        self.current_usage[i] = usage
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                time.sleep(self.update_interval)
    
    def _get_gpu_usage(self, index: int) -> Optional[GPUUsage]:
        """Holt GPU-Nutzung."""
        if not NVIDIA_AVAILABLE:
            return None
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            
            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            # Memory
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            
            # Power
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # Watts
            
            # Clocks
            clock_graphics = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
            clock_memory = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
            
            # Fan Speed
            try:
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            except:
                fan_speed = 0
            
            # Processes
            processes = []
            try:
                procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                for proc in procs:
                    processes.append({
                        "pid": proc.pid,
                        "memory": proc.usedGpuMemory,
                        "name": psutil.Process(proc.pid).name() if psutil.pid_exists(proc.pid) else "Unknown"
                    })
            except:
                pass
            
            return GPUUsage(
                timestamp=datetime.now(),
                gpu_utilization=util.gpu,
                memory_used=mem_info.used,
                memory_percent=(mem_info.used / mem_info.total) * 100,
                temperature=temp,
                power_draw=power,
                clock_graphics=clock_graphics,
                clock_memory=clock_memory,
                fan_speed=fan_speed,
                processes=processes
            )
            
        except Exception as e:
            self.logger.debug(f"Failed to get GPU usage: {e}")
            return None
    
    def get_current_usage(self, gpu_index: int = 0) -> Optional[GPUUsage]:
        """Gibt aktuelle GPU-Nutzung zurück."""
        return self.current_usage.get(gpu_index)
    
    def cleanup(self):
        """Bereinigt Ressourcen."""
        self.stop_monitoring()
        
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass