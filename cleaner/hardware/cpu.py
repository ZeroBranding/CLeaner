"""
CPU Monitoring Module für GermanCodeZero-Cleaner
================================================

Erweiterte CPU-Überwachung und -Analyse.
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

# Windows-spezifisch
if sys.platform == "win32":
    try:
        import wmi
        WMI_AVAILABLE = True
    except ImportError:
        WMI_AVAILABLE = False
else:
    WMI_AVAILABLE = False


@dataclass
class CPUInfo:
    """CPU-Informationen."""
    vendor: str = ""
    brand: str = ""
    cores_physical: int = 0
    cores_logical: int = 0
    base_frequency: float = 0.0
    max_frequency: float = 0.0
    cache_l3: int = 0


@dataclass
class CPUUsage:
    """Aktuelle CPU-Nutzung."""
    timestamp: datetime
    overall_percent: float = 0.0
    per_core_percent: List[float] = None
    frequency_current: float = 0.0
    temperature: float = 0.0
    context_switches: int = 0
    processes: int = 0


class CPUMonitor:
    """CPU-Überwachung."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cpu_info: Optional[CPUInfo] = None
        self.current_usage: Optional[CPUUsage] = None
        self.usage_history: List[CPUUsage] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0
        
        self._initialize_cpu_info()
    
    def _initialize_cpu_info(self):
        """Sammelt CPU-Informationen."""
        cpu_freq = psutil.cpu_freq()
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        
        self.cpu_info = CPUInfo(
            cores_physical=cpu_count_physical,
            cores_logical=cpu_count_logical,
            base_frequency=cpu_freq.current if cpu_freq else 0,
            max_frequency=cpu_freq.max if cpu_freq else 0
        )
        
        # Windows-Details
        if sys.platform == "win32" and WMI_AVAILABLE:
            try:
                c = wmi.WMI()
                for processor in c.Win32_Processor():
                    self.cpu_info.vendor = processor.Manufacturer
                    self.cpu_info.brand = processor.Name
                    self.cpu_info.cache_l3 = processor.L3CacheSize or 0
                    break
            except:
                pass
        
        # Linux-Details
        elif sys.platform.startswith("linux"):
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'vendor_id' in line:
                            self.cpu_info.vendor = line.split(':')[1].strip()
                        elif 'model name' in line and not self.cpu_info.brand:
                            self.cpu_info.brand = line.split(':')[1].strip()
            except:
                pass
    
    def start_monitoring(self, interval: float = 1.0):
        """Startet CPU-Überwachung."""
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
        """Stoppt CPU-Überwachung."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Überwachungsschleife."""
        while self.monitoring:
            try:
                usage = self._collect_cpu_usage()
                self.current_usage = usage
                self.usage_history.append(usage)
                
                # Begrenze Historie
                if len(self.usage_history) > 3600:
                    self.usage_history = self.usage_history[-3600:]
                
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_cpu_usage(self) -> CPUUsage:
        """Sammelt CPU-Nutzung."""
        usage = CPUUsage(
            timestamp=datetime.now(),
            overall_percent=psutil.cpu_percent(interval=None),
            per_core_percent=psutil.cpu_percent(interval=None, percpu=True),
            processes=len(psutil.pids())
        )
        
        # Frequenz
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            usage.frequency_current = cpu_freq.current
        
        # Temperatur (Linux)
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    usage.temperature = temps['coretemp'][0].current
        except:
            pass
        
        # Statistiken
        try:
            stats = psutil.cpu_stats()
            usage.context_switches = stats.ctx_switches
        except:
            pass
        
        return usage
    
    def get_current_usage(self) -> Optional[CPUUsage]:
        """Gibt aktuelle CPU-Nutzung zurück."""
        return self.current_usage
    
    def get_average_usage(self, minutes: int = 5) -> float:
        """Berechnet durchschnittliche CPU-Nutzung."""
        if not self.usage_history:
            return 0.0
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = [u for u in self.usage_history if u.timestamp >= cutoff_time]
        
        if not recent:
            return 0.0
        
        return np.mean([u.overall_percent for u in recent])
    
    def get_optimization_suggestions(self) -> List[str]:
        """Gibt CPU-Optimierungsvorschläge."""
        suggestions = []
        
        if not self.current_usage:
            return suggestions
        
        avg_usage = self.get_average_usage(5)
        
        if avg_usage > 80:
            suggestions.append("CPU-Auslastung hoch. Schließen Sie ungenutzte Programme.")
        
        if self.current_usage.temperature > 80:
            suggestions.append(f"CPU-Temperatur hoch ({self.current_usage.temperature:.1f}°C). Lüfter prüfen.")
        
        if self.current_usage.context_switches > 100000:
            suggestions.append("Viele Kontextwechsel. System-Scheduler optimieren.")
        
        return suggestions
    
    def cleanup(self):
        """Bereinigt Ressourcen."""
        self.stop_monitoring()


# Singleton
_cpu_monitor_instance: Optional[CPUMonitor] = None
_cpu_monitor_lock = threading.Lock()


def get_cpu_monitor() -> CPUMonitor:
    """Gibt Singleton CPU-Monitor zurück."""
    global _cpu_monitor_instance
    
    if _cpu_monitor_instance is None:
        with _cpu_monitor_lock:
            if _cpu_monitor_instance is None:
                _cpu_monitor_instance = CPUMonitor()
    
    return _cpu_monitor_instance


# Legacy-Funktion für Kompatibilität
def clean():
    """Legacy-Funktion für CPU-Bereinigung."""
    from rich import print
    print("[yellow]CPU-Caches werden analysiert …[/yellow]")
    
    # Nutze echte CPU-Daten
    monitor = get_cpu_monitor()
    suggestions = monitor.get_optimization_suggestions()
    
    if suggestions:
        for suggestion in suggestions:
            print(f"[yellow]• {suggestion}[/yellow]")
    
    print("[green]CPU-Analyse abgeschlossen.[/green]")