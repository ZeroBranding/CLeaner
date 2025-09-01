"""
System Monitor für GermanCodeZero-Cleaner
=========================================

Echtzeit-Überwachung von System-Ressourcen mit Hardware-Beschleunigung.
"""

import os
import sys
import time
import threading
import asyncio
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json
import logging

# System-Monitoring
import psutil

# Hardware-spezifische Bibliotheken
try:
    import pynvml
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# Performance Counter (Windows)
if sys.platform == "win32":
    try:
        import win32pdh
        import win32pdhutil
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

# Numpy für Berechnungen
import numpy as np

from ..core.database import get_database, PerformanceMetric


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SystemInfo:
    """System-Informationen."""
    os_name: str = ""
    os_version: str = ""
    architecture: str = ""
    hostname: str = ""
    boot_time: datetime = None
    cpu_model: str = ""
    cpu_cores: int = 0
    cpu_threads: int = 0
    cpu_frequency: float = 0.0
    memory_total: int = 0
    memory_available: int = 0
    disk_total: int = 0
    disk_free: int = 0
    gpu_info: List[Dict[str, Any]] = field(default_factory=list)
    network_interfaces: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ResourceUsage:
    """Aktuelle Ressourcen-Nutzung."""
    timestamp: datetime = None
    cpu_percent: float = 0.0
    cpu_per_core: List[float] = field(default_factory=list)
    memory_percent: float = 0.0
    memory_used: int = 0
    memory_available: int = 0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    network_sent: float = 0.0
    network_recv: float = 0.0
    gpu_usage: float = 0.0
    gpu_memory: float = 0.0
    gpu_temperature: float = 0.0
    process_count: int = 0
    thread_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ProcessInfo:
    """Informationen über einen Prozess."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    num_threads: int
    status: str
    create_time: datetime
    cmdline: str = ""
    username: str = ""


@dataclass
class DiskInfo:
    """Informationen über Festplatten."""
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float
    read_count: int = 0
    write_count: int = 0
    read_bytes: int = 0
    write_bytes: int = 0


@dataclass
class NetworkInfo:
    """Netzwerk-Informationen."""
    interface: str
    is_up: bool
    speed: int  # Mbps
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drop_in: int
    drop_out: int


# ============================================================================
# SYSTEM MONITOR
# ============================================================================

class SystemMonitor:
    """Hauptklasse für System-Überwachung."""
    
    def __init__(self):
        """Initialisiert den System Monitor."""
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0  # Sekunden
        
        # Data storage
        self.system_info: Optional[SystemInfo] = None
        self.current_usage: Optional[ResourceUsage] = None
        self.usage_history: deque = deque(maxlen=3600)  # 1 Stunde bei 1s Intervall
        
        # Callbacks
        self.usage_callbacks: List[Callable[[ResourceUsage], None]] = []
        self.alert_callbacks: List[Callable[[str, str], None]] = []
        
        # Alert thresholds
        self.alert_thresholds = {
            "cpu_percent": 90.0,
            "memory_percent": 90.0,
            "disk_percent": 95.0,
            "gpu_temperature": 85.0
        }
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize hardware monitoring
        self._initialize_hardware_monitoring()
        
        # Collect initial system info
        self._collect_system_info()
    
    def _initialize_hardware_monitoring(self):
        """Initialisiert Hardware-spezifische Überwachung."""
        # NVIDIA GPU Monitoring
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_count = pynvml.nvmlDeviceGetCount()
                self.logger.info(f"NVIDIA monitoring initialized: {self.gpu_count} GPUs found")
            except Exception as e:
                self.logger.warning(f"NVIDIA monitoring failed: {e}")
                self.gpu_count = 0
        else:
            self.gpu_count = 0
        
        # Windows WMI
        if WMI_AVAILABLE and sys.platform == "win32":
            try:
                self.wmi = wmi.WMI()
                self.logger.info("WMI monitoring initialized")
            except Exception as e:
                self.logger.warning(f"WMI initialization failed: {e}")
                self.wmi = None
        else:
            self.wmi = None
    
    def _collect_system_info(self):
        """Sammelt statische System-Informationen."""
        import platform
        
        try:
            # Basis-Informationen
            uname = platform.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            # CPU-Informationen
            cpu_freq = psutil.cpu_freq()
            cpu_info = self._get_cpu_info()
            
            # Memory-Informationen
            memory = psutil.virtual_memory()
            
            # Disk-Informationen
            disk_usage = psutil.disk_usage('/')
            
            # GPU-Informationen
            gpu_info = self._get_gpu_info()
            
            # Netzwerk-Interfaces
            network_interfaces = self._get_network_interfaces()
            
            self.system_info = SystemInfo(
                os_name=uname.system,
                os_version=uname.release,
                architecture=uname.machine,
                hostname=uname.node,
                boot_time=boot_time,
                cpu_model=cpu_info.get("model", "Unknown"),
                cpu_cores=psutil.cpu_count(logical=False),
                cpu_threads=psutil.cpu_count(logical=True),
                cpu_frequency=cpu_freq.max if cpu_freq else 0,
                memory_total=memory.total,
                memory_available=memory.available,
                disk_total=disk_usage.total,
                disk_free=disk_usage.free,
                gpu_info=gpu_info,
                network_interfaces=network_interfaces
            )
            
            self.logger.info("System information collected successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to collect system info: {e}")
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Holt detaillierte CPU-Informationen."""
        cpu_info = {
            "model": "Unknown",
            "vendor": "Unknown",
            "features": []
        }
        
        if sys.platform == "win32" and self.wmi:
            try:
                for cpu in self.wmi.Win32_Processor():
                    cpu_info["model"] = cpu.Name
                    cpu_info["vendor"] = cpu.Manufacturer
                    cpu_info["max_clock"] = cpu.MaxClockSpeed
                    cpu_info["l2_cache"] = cpu.L2CacheSize
                    cpu_info["l3_cache"] = cpu.L3CacheSize
                    break
            except Exception as e:
                self.logger.debug(f"WMI CPU info failed: {e}")
        
        elif sys.platform == "linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            cpu_info["model"] = line.split(":")[1].strip()
                        elif "vendor_id" in line:
                            cpu_info["vendor"] = line.split(":")[1].strip()
                        elif "flags" in line:
                            cpu_info["features"] = line.split(":")[1].strip().split()
                            break
            except Exception as e:
                self.logger.debug(f"Linux CPU info failed: {e}")
        
        return cpu_info
    
    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Holt GPU-Informationen."""
        gpu_list = []
        
        if NVIDIA_AVAILABLE and self.gpu_count > 0:
            try:
                for i in range(self.gpu_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    
                    gpu_info = {
                        "index": i,
                        "name": pynvml.nvmlDeviceGetName(handle).decode('utf-8'),
                        "driver": pynvml.nvmlSystemGetDriverVersion().decode('utf-8'),
                        "memory_total": pynvml.nvmlDeviceGetMemoryInfo(handle).total,
                        "compute_capability": pynvml.nvmlDeviceGetCudaComputeCapability(handle),
                        "pcie_gen": pynvml.nvmlDeviceGetMaxPcieLinkGeneration(handle),
                        "power_limit": pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000  # Watts
                    }
                    
                    gpu_list.append(gpu_info)
                    
            except Exception as e:
                self.logger.debug(f"NVIDIA GPU info failed: {e}")
        
        # Fallback für AMD/Intel GPUs über WMI (Windows)
        if sys.platform == "win32" and self.wmi and not gpu_list:
            try:
                for gpu in self.wmi.Win32_VideoController():
                    gpu_info = {
                        "name": gpu.Name,
                        "driver": gpu.DriverVersion,
                        "memory_total": gpu.AdapterRAM if gpu.AdapterRAM else 0,
                        "vendor": gpu.AdapterCompatibility
                    }
                    gpu_list.append(gpu_info)
            except Exception as e:
                self.logger.debug(f"WMI GPU info failed: {e}")
        
        return gpu_list
    
    def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Holt Netzwerk-Interface-Informationen."""
        interfaces = []
        
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            for interface, stat in stats.items():
                interface_info = {
                    "name": interface,
                    "is_up": stat.isup,
                    "speed": stat.speed,
                    "mtu": stat.mtu,
                    "addresses": []
                }
                
                if interface in addrs:
                    for addr in addrs[interface]:
                        addr_info = {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        }
                        interface_info["addresses"].append(addr_info)
                
                interfaces.append(interface_info)
                
        except Exception as e:
            self.logger.debug(f"Network interface info failed: {e}")
        
        return interfaces
    
    # ========================================================================
    # MONITORING METHODS
    # ========================================================================
    
    def start_monitoring(self, interval: float = 1.0):
        """Startet die System-Überwachung."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.update_interval = interval
        
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info(f"System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stoppt die System-Überwachung."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            self.monitor_thread = None
        
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Haupt-Überwachungsschleife."""
        last_net_io = psutil.net_io_counters()
        last_disk_io = psutil.disk_io_counters()
        last_time = time.time()
        
        while self.monitoring:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # Sammle aktuelle Nutzungsdaten
                usage = ResourceUsage(timestamp=datetime.now())
                
                # CPU
                usage.cpu_percent = psutil.cpu_percent(interval=None)
                usage.cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
                
                # Memory
                memory = psutil.virtual_memory()
                usage.memory_percent = memory.percent
                usage.memory_used = memory.used
                usage.memory_available = memory.available
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                if disk_io and last_disk_io:
                    usage.disk_io_read = (disk_io.read_bytes - last_disk_io.read_bytes) / time_delta
                    usage.disk_io_write = (disk_io.write_bytes - last_disk_io.write_bytes) / time_delta
                last_disk_io = disk_io
                
                # Network I/O
                net_io = psutil.net_io_counters()
                if net_io and last_net_io:
                    usage.network_sent = (net_io.bytes_sent - last_net_io.bytes_sent) / time_delta
                    usage.network_recv = (net_io.bytes_recv - last_net_io.bytes_recv) / time_delta
                last_net_io = net_io
                
                # GPU (if available)
                if NVIDIA_AVAILABLE and self.gpu_count > 0:
                    gpu_usage, gpu_memory, gpu_temp = self._get_gpu_usage()
                    usage.gpu_usage = gpu_usage
                    usage.gpu_memory = gpu_memory
                    usage.gpu_temperature = gpu_temp
                
                # Process & Thread count
                usage.process_count = len(psutil.pids())
                
                # Update current usage
                self.current_usage = usage
                self.usage_history.append(usage)
                
                # Check for alerts
                self._check_alerts(usage)
                
                # Call callbacks
                for callback in self.usage_callbacks:
                    try:
                        callback(usage)
                    except Exception as e:
                        self.logger.error(f"Usage callback error: {e}")
                
                # Save to database periodically (every 60 seconds)
                if int(current_time) % 60 == 0:
                    self._save_metrics_to_database(usage)
                
                last_time = current_time
                
                # Sleep
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.update_interval)
    
    def _get_gpu_usage(self) -> Tuple[float, float, float]:
        """Holt aktuelle GPU-Nutzung."""
        if not NVIDIA_AVAILABLE or self.gpu_count == 0:
            return 0.0, 0.0, 0.0
        
        try:
            # Verwende erste GPU
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # GPU Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_usage = util.gpu
            
            # Memory Usage
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory = (mem_info.used / mem_info.total) * 100
            
            # Temperature
            gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            
            return gpu_usage, gpu_memory, gpu_temp
            
        except Exception as e:
            self.logger.debug(f"GPU usage collection failed: {e}")
            return 0.0, 0.0, 0.0
    
    def _check_alerts(self, usage: ResourceUsage):
        """Prüft auf Alert-Bedingungen."""
        alerts = []
        
        # CPU Alert
        if usage.cpu_percent > self.alert_thresholds["cpu_percent"]:
            alerts.append(("cpu_high", f"CPU-Auslastung hoch: {usage.cpu_percent:.1f}%"))
        
        # Memory Alert
        if usage.memory_percent > self.alert_thresholds["memory_percent"]:
            alerts.append(("memory_high", f"Speicher-Auslastung hoch: {usage.memory_percent:.1f}%"))
        
        # GPU Temperature Alert
        if usage.gpu_temperature > self.alert_thresholds["gpu_temperature"]:
            alerts.append(("gpu_temp_high", f"GPU-Temperatur hoch: {usage.gpu_temperature:.1f}°C"))
        
        # Trigger alert callbacks
        for alert_type, message in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert_type, message)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
    
    def _save_metrics_to_database(self, usage: ResourceUsage):
        """Speichert Metriken in der Datenbank."""
        try:
            db = get_database()
            
            metric = PerformanceMetric(
                timestamp=usage.timestamp,
                metric_type="system_usage",
                cpu_usage=usage.cpu_percent,
                memory_usage=usage.memory_percent,
                disk_io=(usage.disk_io_read + usage.disk_io_write) / (1024 * 1024),  # MB/s
                gpu_usage=usage.gpu_usage,
                operation="monitoring",
                duration_ms=self.update_interval * 1000
            )
            
            db.save_performance_metric(metric)
            
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    # ========================================================================
    # QUERY METHODS
    # ========================================================================
    
    def get_current_usage(self) -> Optional[ResourceUsage]:
        """Gibt aktuelle Ressourcen-Nutzung zurück."""
        return self.current_usage
    
    def get_usage_history(self, minutes: int = 60) -> List[ResourceUsage]:
        """Gibt Nutzungshistorie zurück."""
        if not self.usage_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            usage for usage in self.usage_history
            if usage.timestamp >= cutoff_time
        ]
    
    def get_average_usage(self, minutes: int = 5) -> Optional[ResourceUsage]:
        """Berechnet durchschnittliche Nutzung."""
        history = self.get_usage_history(minutes)
        
        if not history:
            return None
        
        avg_usage = ResourceUsage(timestamp=datetime.now())
        
        avg_usage.cpu_percent = np.mean([u.cpu_percent for u in history])
        avg_usage.memory_percent = np.mean([u.memory_percent for u in history])
        avg_usage.disk_io_read = np.mean([u.disk_io_read for u in history])
        avg_usage.disk_io_write = np.mean([u.disk_io_write for u in history])
        avg_usage.network_sent = np.mean([u.network_sent for u in history])
        avg_usage.network_recv = np.mean([u.network_recv for u in history])
        avg_usage.gpu_usage = np.mean([u.gpu_usage for u in history])
        avg_usage.gpu_memory = np.mean([u.gpu_memory for u in history])
        
        return avg_usage
    
    def get_top_processes(self, count: int = 10, sort_by: str = "cpu") -> List[ProcessInfo]:
        """Gibt Top-Prozesse zurück."""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 
                                            'memory_percent', 'memory_info',
                                            'num_threads', 'status', 'create_time']):
                try:
                    pinfo = proc.info
                    
                    process = ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        cpu_percent=pinfo['cpu_percent'] or 0.0,
                        memory_percent=pinfo['memory_percent'] or 0.0,
                        memory_rss=pinfo['memory_info'].rss if pinfo.get('memory_info') else 0,
                        num_threads=pinfo['num_threads'] or 0,
                        status=pinfo['status'],
                        create_time=datetime.fromtimestamp(pinfo['create_time'])
                    )
                    
                    processes.append(process)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sortiere Prozesse
            if sort_by == "cpu":
                processes.sort(key=lambda p: p.cpu_percent, reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda p: p.memory_percent, reverse=True)
            
            return processes[:count]
            
        except Exception as e:
            self.logger.error(f"Failed to get top processes: {e}")
            return []
    
    def get_disk_usage(self) -> List[DiskInfo]:
        """Gibt Festplatten-Nutzung zurück."""
        disks = []
        
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    io_counters = psutil.disk_io_counters(perdisk=True)
                    
                    disk = DiskInfo(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        fstype=partition.fstype,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent
                    )
                    
                    # Add I/O stats if available
                    device_name = partition.device.replace('\\', '').replace('/', '')
                    if device_name in io_counters:
                        io = io_counters[device_name]
                        disk.read_count = io.read_count
                        disk.write_count = io.write_count
                        disk.read_bytes = io.read_bytes
                        disk.write_bytes = io.write_bytes
                    
                    disks.append(disk)
                    
                except PermissionError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
        
        return disks
    
    def get_network_usage(self) -> List[NetworkInfo]:
        """Gibt Netzwerk-Nutzung zurück."""
        networks = []
        
        try:
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, stat in stats.items():
                network = NetworkInfo(
                    interface=interface,
                    is_up=stat.isup,
                    speed=stat.speed
                )
                
                if interface in io_counters:
                    io = io_counters[interface]
                    network.bytes_sent = io.bytes_sent
                    network.bytes_recv = io.bytes_recv
                    network.packets_sent = io.packets_sent
                    network.packets_recv = io.packets_recv
                    network.errors_in = io.errin
                    network.errors_out = io.errout
                    network.drop_in = io.dropin
                    network.drop_out = io.dropout
                
                networks.append(network)
                
        except Exception as e:
            self.logger.error(f"Failed to get network usage: {e}")
        
        return networks
    
    # ========================================================================
    # CALLBACK MANAGEMENT
    # ========================================================================
    
    def add_usage_callback(self, callback: Callable[[ResourceUsage], None]):
        """Fügt einen Usage-Callback hinzu."""
        if callback not in self.usage_callbacks:
            self.usage_callbacks.append(callback)
    
    def remove_usage_callback(self, callback: Callable[[ResourceUsage], None]):
        """Entfernt einen Usage-Callback."""
        if callback in self.usage_callbacks:
            self.usage_callbacks.remove(callback)
    
    def add_alert_callback(self, callback: Callable[[str, str], None]):
        """Fügt einen Alert-Callback hinzu."""
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[str, str], None]):
        """Entfernt einen Alert-Callback."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Setzt einen Alert-Schwellwert."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    def cleanup(self):
        """Bereinigt Ressourcen."""
        self.stop_monitoring()
        
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


# ============================================================================
# PERFORMANCE TRACKER
# ============================================================================

class PerformanceTracker:
    """Trackt Performance-Metriken für Operationen."""
    
    def __init__(self):
        self.operations = {}
        self.lock = threading.Lock()
    
    def start_operation(self, operation_name: str):
        """Startet Tracking für eine Operation."""
        with self.lock:
            self.operations[operation_name] = {
                "start_time": time.time(),
                "start_cpu": psutil.cpu_percent(),
                "start_memory": psutil.virtual_memory().percent
            }
    
    def end_operation(self, operation_name: str) -> Dict[str, float]:
        """Beendet Tracking und gibt Metriken zurück."""
        with self.lock:
            if operation_name not in self.operations:
                return {}
            
            op_data = self.operations[operation_name]
            end_time = time.time()
            
            metrics = {
                "duration_ms": (end_time - op_data["start_time"]) * 1000,
                "cpu_delta": psutil.cpu_percent() - op_data["start_cpu"],
                "memory_delta": psutil.virtual_memory().percent - op_data["start_memory"]
            }
            
            del self.operations[operation_name]
            
            return metrics


# ============================================================================
# SYSTEM MONITOR SINGLETON
# ============================================================================

_monitor_instance: Optional[SystemMonitor] = None
_monitor_lock = threading.Lock()


def get_system_monitor() -> SystemMonitor:
    """Gibt die Singleton-Monitor-Instanz zurück."""
    global _monitor_instance
    
    if _monitor_instance is None:
        with _monitor_lock:
            if _monitor_instance is None:
                _monitor_instance = SystemMonitor()
    
    return _monitor_instance


def cleanup_system_monitor():
    """Bereinigt den globalen System Monitor."""
    global _monitor_instance
    
    if _monitor_instance:
        with _monitor_lock:
            _monitor_instance.cleanup()
            _monitor_instance = None