"""
SSD/HDD Monitoring Module für GermanCodeZero-Cleaner
====================================================

Festplatten-Überwachung mit Performance-Metriken.
"""

import sys
import os
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

import psutil


@dataclass
class DiskInfo:
    """Festplatten-Informationen."""
    device: str
    model: str
    size: int
    type: str  # SSD, HDD, NVMe
    partitions: List[Dict[str, Any]]
    health_status: str


@dataclass
class DiskUsage:
    """Festplatten-Nutzung."""
    timestamp: datetime
    device: str
    total: int
    used: int
    free: int
    percent: float
    read_bytes: int
    write_bytes: int


class SSDMonitor:
    """SSD/HDD-Überwachung."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.disks: Dict[str, DiskInfo] = {}
        self.current_usage: Dict[str, DiskUsage] = {}
        
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 5.0
        
        self._initialize_disks()
    
    def _initialize_disks(self):
        """Initialisiert Festplatten-Informationen."""
        try:
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    disk_info = DiskInfo(
                        device=partition.device,
                        model="Unknown",
                        size=usage.total,
                        type=self._detect_disk_type(partition.device),
                        partitions=[{
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent
                        }],
                        health_status="Good"
                    )
                    
                    self.disks[partition.device] = disk_info
                    
                except PermissionError:
                    continue
            
            self.logger.info(f"Initialized {len(self.disks)} disks")
            
        except Exception as e:
            self.logger.error(f"Disk initialization failed: {e}")
    
    def _detect_disk_type(self, device: str) -> str:
        """Erkennt Festplattentyp."""
        device_lower = device.lower()
        
        if 'nvme' in device_lower:
            return "NVMe"
        elif 'ssd' in device_lower:
            return "SSD"
        else:
            return "HDD"
    
    def start_monitoring(self, interval: float = 5.0):
        """Startet Disk-Überwachung."""
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
        """Stoppt Disk-Überwachung."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitor_loop(self):
        """Überwachungsschleife."""
        last_io = psutil.disk_io_counters(perdisk=True)
        
        while self.monitoring:
            try:
                current_io = psutil.disk_io_counters(perdisk=True)
                
                for device, disk_info in self.disks.items():
                    if disk_info.partitions:
                        partition = disk_info.partitions[0]
                        usage_stats = psutil.disk_usage(partition['mountpoint'])
                        
                        usage = DiskUsage(
                            timestamp=datetime.now(),
                            device=device,
                            total=usage_stats.total,
                            used=usage_stats.used,
                            free=usage_stats.free,
                            percent=usage_stats.percent,
                            read_bytes=0,
                            write_bytes=0
                        )
                        
                        # I/O-Statistiken
                        device_name = os.path.basename(device.rstrip('\\'))
                        if device_name in current_io and device_name in last_io:
                            curr = current_io[device_name]
                            last = last_io[device_name]
                            
                            usage.read_bytes = curr.read_bytes - last.read_bytes
                            usage.write_bytes = curr.write_bytes - last.write_bytes
                        
                        self.current_usage[device] = usage
                
                last_io = current_io
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(self.update_interval)
    
    def get_current_usage(self) -> Dict[str, DiskUsage]:
        """Gibt aktuelle Disk-Nutzung zurück."""
        return self.current_usage.copy()
    
    def get_optimization_suggestions(self) -> List[str]:
        """Gibt Disk-Optimierungsvorschläge."""
        suggestions = []
        
        for device, disk_info in self.disks.items():
            if device in self.current_usage:
                usage = self.current_usage[device]
                
                if usage.percent > 90:
                    suggestions.append(f"{device}: Kritisch wenig Speicherplatz ({usage.percent:.1f}% belegt)")
                elif usage.percent > 80:
                    suggestions.append(f"{device}: Speicherplatz wird knapp ({usage.percent:.1f}% belegt)")
        
        return suggestions
    
    def cleanup(self):
        """Bereinigt Ressourcen."""
        self.stop_monitoring()