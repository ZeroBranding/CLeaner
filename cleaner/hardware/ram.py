"""
RAM Monitoring Module für GermanCodeZero-Cleaner
================================================

Erweiterte RAM-Überwachung und -Analyse.
"""

import sys
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

import psutil
import numpy as np


@dataclass
class RAMInfo:
    """RAM-Informationen."""
    total: int  # Bytes
    type: str  # DDR3, DDR4, DDR5
    speed: int  # MHz
    slots_total: int
    slots_used: int
    modules: List[Dict[str, Any]]
    ecc: bool
    form_factor: str


@dataclass
class RAMUsage:
    """Aktuelle RAM-Nutzung."""
    timestamp: datetime
    total: int
    available: int
    used: int
    free: int
    percent: float
    active: int
    inactive: int
    buffers: int
    cached: int
    shared: int
    slab: int
    swap_total: int
    swap_used: int
    swap_free: int
    swap_percent: float


@dataclass
class ProcessMemoryInfo:
    """Speicher-Info für Prozess."""
    pid: int
    name: str
    memory_rss: int  # Resident Set Size
    memory_vms: int  # Virtual Memory Size
    memory_percent: float
    memory_shared: int
    memory_unique: int


class RAMMonitor:
    """RAM-Überwachung."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ram_info: Optional[RAMInfo] = None
        self.current_usage: Optional[RAMUsage] = None
        self.usage_history: List[RAMUsage] = []
        self.max_history = 3600
        
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0
        self.lock = threading.Lock()
        
        self._initialize_ram_info()
    
    def _initialize_ram_info(self):
        """Initialisiert RAM-Informationen."""
        memory = psutil.virtual_memory()
        
        self.ram_info = RAMInfo(
            total=memory.total,
            type="Unknown",
            speed=0,
            slots_total=0,
            slots_used=0,
            modules=[],
            ecc=False,
            form_factor="Unknown"
        )
        
        # Platform-spezifische Details
        if sys.platform == "win32":
            self._get_windows_ram_info()
        elif sys.platform.startswith("linux"):
            self._get_linux_ram_info()
    
    def _get_windows_ram_info(self):
        """Holt Windows RAM-Details."""
        try:
            import wmi
            c = wmi.WMI()
            
            for mem in c.Win32_PhysicalMemory():
                module = {
                    "capacity": int(mem.Capacity),
                    "speed": int(mem.Speed) if mem.Speed else 0,
                    "manufacturer": mem.Manufacturer,
                    "part_number": mem.PartNumber,
                    "serial": mem.SerialNumber,
                    "form_factor": self._decode_form_factor(mem.FormFactor),
                    "type": self._decode_memory_type(mem.MemoryType)
                }
                self.ram_info.modules.append(module)
                
                if mem.Speed:
                    self.ram_info.speed = int(mem.Speed)
                    
                self.ram_info.type = module["type"]
            
            self.ram_info.slots_used = len(self.ram_info.modules)
            
        except Exception as e:
            self.logger.debug(f"Windows RAM info failed: {e}")
    
    def _get_linux_ram_info(self):
        """Holt Linux RAM-Details."""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        self.ram_info.total = int(line.split()[1]) * 1024
                        
            # dmidecode für Details (benötigt sudo)
            import subprocess
            try:
                result = subprocess.run(['sudo', 'dmidecode', '-t', 'memory'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse dmidecode output
                    pass
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Linux RAM info failed: {e}")
    
    def _decode_form_factor(self, code):
        """Dekodiert Form Factor Code."""
        form_factors = {
            8: "DIMM",
            12: "SODIMM",
            13: "RIMM",
            14: "SRIMM"
        }
        return form_factors.get(code, "Unknown")
    
    def _decode_memory_type(self, code):
        """Dekodiert Memory Type Code."""
        memory_types = {
            20: "DDR",
            21: "DDR2",
            24: "DDR3",
            26: "DDR4",
            30: "DDR5"
        }
        return memory_types.get(code, "Unknown")
    
    def start_monitoring(self, interval: float = 1.0):
        """Startet RAM-Überwachung."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.update_interval = interval
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stoppt RAM-Überwachung."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Überwachungsschleife."""
        while self.monitoring:
            try:
                usage = self._collect_ram_usage()
                
                with self.lock:
                    self.current_usage = usage
                    self.usage_history.append(usage)
                    
                    if len(self.usage_history) > self.max_history:
                        self.usage_history = self.usage_history[-self.max_history:]
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_ram_usage(self) -> RAMUsage:
        """Sammelt RAM-Nutzung."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        usage = RAMUsage(
            timestamp=datetime.now(),
            total=mem.total,
            available=mem.available,
            used=mem.used,
            free=mem.free,
            percent=mem.percent,
            active=getattr(mem, 'active', 0),
            inactive=getattr(mem, 'inactive', 0),
            buffers=getattr(mem, 'buffers', 0),
            cached=getattr(mem, 'cached', 0),
            shared=getattr(mem, 'shared', 0),
            slab=getattr(mem, 'slab', 0),
            swap_total=swap.total,
            swap_used=swap.used,
            swap_free=swap.free,
            swap_percent=swap.percent
        )
        
        return usage
    
    def get_current_usage(self) -> Optional[RAMUsage]:
        """Gibt aktuelle RAM-Nutzung zurück."""
        with self.lock:
            return self.current_usage
    
    def get_usage_history(self, minutes: int = 60) -> List[RAMUsage]:
        """Gibt RAM-Nutzungshistorie zurück."""
        with self.lock:
            if not self.usage_history:
                return []
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            return [u for u in self.usage_history if u.timestamp >= cutoff_time]
    
    def get_average_usage(self, minutes: int = 5) -> float:
        """Berechnet durchschnittliche RAM-Nutzung."""
        history = self.get_usage_history(minutes)
        
        if not history:
            return 0.0
        
        return np.mean([u.percent for u in history])
    
    def get_memory_pressure(self) -> Dict[str, Any]:
        """Analysiert Speicherdruck."""
        if not self.current_usage:
            return {"level": "unknown"}
        
        percent = self.current_usage.percent
        swap_percent = self.current_usage.swap_percent
        
        if percent < 60:
            level = "low"
        elif percent < 80:
            level = "moderate"
        elif percent < 90:
            level = "high"
        else:
            level = "critical"
        
        return {
            "level": level,
            "ram_percent": percent,
            "swap_percent": swap_percent,
            "available_mb": self.current_usage.available // (1024 * 1024),
            "recommendation": self._get_memory_recommendation(level)
        }
    
    def _get_memory_recommendation(self, level: str) -> str:
        """Gibt Speicher-Empfehlung."""
        recommendations = {
            "low": "Speicher ausreichend verfügbar.",
            "moderate": "Speichernutzung normal. Beobachten Sie große Anwendungen.",
            "high": "Speicher wird knapp. Schließen Sie ungenutzte Programme.",
            "critical": "Kritischer Speichermangel! Sofort Programme schließen."
        }
        return recommendations.get(level, "")
    
    def get_top_memory_processes(self, count: int = 10) -> List[ProcessMemoryInfo]:
        """Gibt Top Speicher-verbrauchende Prozesse."""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
                try:
                    pinfo = proc.info
                    mem_info = pinfo.get('memory_info')
                    
                    if mem_info:
                        process = ProcessMemoryInfo(
                            pid=pinfo['pid'],
                            name=pinfo['name'],
                            memory_rss=mem_info.rss,
                            memory_vms=mem_info.vms,
                            memory_percent=pinfo.get('memory_percent', 0),
                            memory_shared=getattr(mem_info, 'shared', 0),
                            memory_unique=getattr(mem_info, 'unique', 0)
                        )
                        processes.append(process)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processes.sort(key=lambda p: p.memory_rss, reverse=True)
            return processes[:count]
            
        except Exception as e:
            self.logger.error(f"Failed to get memory processes: {e}")
            return []
    
    def predict_out_of_memory(self, minutes_ahead: int = 5) -> Dict[str, Any]:
        """Prognostiziert Speichermangel."""
        history = self.get_usage_history(10)
        
        if len(history) < 3:
            return {"risk": "unknown"}
        
        # Trend-Analyse
        usage_values = [u.percent for u in history]
        x = np.arange(len(usage_values))
        coeffs = np.polyfit(x, usage_values, 1)
        
        # Extrapoliere
        future_value = coeffs[0] * (len(usage_values) + minutes_ahead * 60) + coeffs[1]
        
        risk = "low"
        if future_value > 95:
            risk = "high"
        elif future_value > 85:
            risk = "medium"
        
        return {
            "risk": risk,
            "predicted_percent": min(100, max(0, future_value)),
            "minutes_to_critical": (95 - usage_values[-1]) / coeffs[0] / 60 if coeffs[0] > 0 else float('inf')
        }
    
    def cleanup(self):
        """Bereinigt Ressourcen."""
        self.stop_monitoring()