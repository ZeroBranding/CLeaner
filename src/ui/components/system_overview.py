"""
💻 System Overview Widget
Comprehensive system information display with real-time updates
"""

from typing import Dict, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon
import logging

logger = logging.getLogger(__name__)

class SystemOverviewWidget(QWidget):
    """System overview with hardware information and real-time stats"""
    
    def __init__(self, system_monitor, parent=None):
        super().__init__(parent)
        self.system_monitor = system_monitor
        self._setup_ui()
        self._load_system_info()
        
    def _setup_ui(self):
        """Setup system overview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("💻 System Overview")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Hardware info group
        hw_group = QGroupBox("Hardware Information")
        hw_layout = QVBoxLayout(hw_group)
        
        self.hw_info_text = QTextEdit()
        self.hw_info_text.setMaximumHeight(150)
        self.hw_info_text.setReadOnly(True)
        self.hw_info_text.setStyleSheet("""
            QTextEdit {
                background: rgba(25, 25, 35, 0.9);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 6px;
                color: white;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        hw_layout.addWidget(self.hw_info_text)
        
        layout.addWidget(hw_group)
        
        # Real-time stats group
        stats_group = QGroupBox("Real-time Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        # Current stats labels
        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("Memory: --")
        self.gpu_label = QLabel("GPU: --")
        self.temp_label = QLabel("Temperature: --")
        
        for label in [self.cpu_label, self.memory_label, self.gpu_label, self.temp_label]:
            label.setStyleSheet("color: white; font-size: 11px; margin: 2px;")
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_group)
    
    def _load_system_info(self):
        """Load static system information"""
        try:
            system_info = self.system_monitor.get_system_info()
            
            info_text = f"""🖥️ Platform: {system_info.get('platform', 'Unknown')}
🔧 Processor: {system_info.get('processor', 'Unknown')}
🏗️ Architecture: {system_info.get('architecture', 'Unknown')}
🐍 Python: {system_info.get('python_version', 'Unknown')}
⚡ CPU Cores: {system_info.get('cpu_count', 'Unknown')} physical, {system_info.get('cpu_count_logical', 'Unknown')} logical
💾 Total Memory: {system_info.get('total_memory', 'Unknown')}
🎮 GPU: {system_info.get('gpu_info', 'Unknown')}"""
            
            self.hw_info_text.setPlainText(info_text)
            
        except Exception as e:
            logger.error(f"Failed to load system info: {e}")
            self.hw_info_text.setPlainText("Failed to load system information")
    
    def update_stats(self, stats):
        """Update real-time statistics"""
        try:
            # Update CPU info
            cpu_text = f"CPU: {stats.cpu_percent:.1f}%"
            if stats.cpu_freq:
                cpu_text += f" @ {stats.cpu_freq:.0f} MHz"
            self.cpu_label.setText(cpu_text)
            
            # Update memory info
            memory_text = f"Memory: {stats.memory_percent:.1f}% ({stats.memory_used:.1f}/{stats.memory_total:.1f} GB)"
            self.memory_label.setText(memory_text)
            
            # Update GPU info
            if stats.gpu_percent is not None:
                gpu_text = f"GPU: {stats.gpu_percent:.1f}%"
                if stats.gpu_memory_used and stats.gpu_memory_total:
                    gpu_text += f" ({stats.gpu_memory_used:.0f}/{stats.gpu_memory_total:.0f} MB)"
                self.gpu_label.setText(gpu_text)
            else:
                self.gpu_label.setText("GPU: Not available")
            
            # Update temperature info
            temp_text = "Temperature: "
            if stats.cpu_temp is not None:
                temp_text += f"CPU {stats.cpu_temp:.1f}°C"
            if stats.gpu_temp is not None:
                if stats.cpu_temp is not None:
                    temp_text += f", GPU {stats.gpu_temp:.1f}°C"
                else:
                    temp_text += f"GPU {stats.gpu_temp:.1f}°C"
            if stats.cpu_temp is None and stats.gpu_temp is None:
                temp_text += "Not available"
            
            self.temp_label.setText(temp_text)
            
        except Exception as e:
            logger.error(f"Failed to update stats display: {e}")