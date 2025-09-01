"""
📊 Animated Statistics Widget
Floating islands effect with depth-aware UI layers
"""

import math
import time
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QLinearGradient
import logging

logger = logging.getLogger(__name__)

class AnimatedProgressBar(QProgressBar):
    """Custom animated progress bar with neon effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_offset = 0.0
        self.glow_intensity = 1.0
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(16)  # 60 FPS
        
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 8px;
                text-align: center;
                background: rgba(25, 25, 35, 0.8);
                font-weight: bold;
                color: white;
            }
        """)
    
    def _update_animation(self):
        """Update progress bar animation"""
        self.animation_offset += 0.05
        self.glow_intensity = (math.sin(self.animation_offset) + 1.0) / 2.0 * 0.3 + 0.7
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event for animated effects"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw animated glow effect
        rect = self.rect()
        
        # Create gradient based on current value
        gradient = QLinearGradient(0, 0, rect.width(), 0)
        
        if self.value() < 30:
            # Low usage - cyan to blue
            gradient.setColorAt(0, QColor(0, 255, 255, int(255 * self.glow_intensity)))
            gradient.setColorAt(1, QColor(0, 150, 255, int(255 * self.glow_intensity)))
        elif self.value() < 70:
            # Medium usage - cyan to magenta
            gradient.setColorAt(0, QColor(0, 255, 255, int(255 * self.glow_intensity)))
            gradient.setColorAt(1, QColor(255, 0, 255, int(255 * self.glow_intensity)))
        else:
            # High usage - magenta to red
            gradient.setColorAt(0, QColor(255, 0, 255, int(255 * self.glow_intensity)))
            gradient.setColorAt(1, QColor(255, 100, 100, int(255 * self.glow_intensity)))
        
        # Draw progress fill
        fill_width = int((rect.width() - 4) * self.value() / self.maximum())
        if fill_width > 0:
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(2, 2, fill_width, rect.height() - 4, 6, 6)

class FloatingStatsCard(QFrame):
    """Individual stats card with floating animation"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.float_offset = 0.0
        self.float_speed = 1.0 + hash(title) % 100 / 100.0  # Unique speed per card
        self.base_y = 0
        
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #00ffff; margin-bottom: 5px;")
        layout.addWidget(self.title_label)
        
        # Value label
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(self.value_label)
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Card styling
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 30, 40, 0.9),
                    stop:1 rgba(40, 40, 50, 0.9));
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 12px;
                margin: 5px;
            }
        """)
    
    def _setup_animation(self):
        """Setup floating animation"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_float)
        self.animation_timer.start(16)  # 60 FPS
    
    def _update_float(self):
        """Update floating animation"""
        self.float_offset += 0.02 * self.float_speed
        
        # Calculate floating offset
        y_offset = math.sin(self.float_offset) * 3.0
        
        # Apply floating effect (simplified - would use 3D transforms in full implementation)
        current_geometry = self.geometry()
        new_y = self.base_y + int(y_offset)
        self.setGeometry(current_geometry.x(), new_y, current_geometry.width(), current_geometry.height())
    
    def update_value(self, value: float, suffix: str = "%"):
        """Update card value with animation"""
        self.value_label.setText(f"{value:.1f}{suffix}")
        self.progress_bar.setValue(int(value))
        
        # Pulse animation on significant changes
        if hasattr(self, 'last_value') and abs(value - self.last_value) > 10:
            self._pulse_animation()
        
        self.last_value = value
    
    def _pulse_animation(self):
        """Create pulse animation for significant changes"""
        # Simple scale animation
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        current_rect = self.geometry()
        expanded_rect = QRect(
            current_rect.x() - 5,
            current_rect.y() - 5,
            current_rect.width() + 10,
            current_rect.height() + 10
        )
        
        animation.setStartValue(current_rect)
        animation.setKeyValueAt(0.5, expanded_rect)
        animation.setEndValue(current_rect)
        animation.start()

class AnimatedStatsWidget(QWidget):
    """Main animated statistics widget with floating islands effect"""
    
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_cards: Dict[str, FloatingStatsCard] = {}
        self._setup_ui()
        
        # Animation state
        self.animation_time = 0.0
        self.master_timer = QTimer()
        self.master_timer.timeout.connect(self._update_master_animation)
        self.master_timer.start(16)  # 60 FPS
        
        logger.info("Animated stats widget initialized")
    
    def _setup_ui(self):
        """Setup the stats widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📊 System Statistics")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Stats container with grid layout
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setSpacing(8)
        
        # Create stats cards
        self._create_stats_cards()
        
        layout.addWidget(self.stats_container)
        layout.addStretch()
    
    def _create_stats_cards(self):
        """Create floating stats cards"""
        cards_config = [
            ("🔥 CPU Usage", "cpu"),
            ("🧠 Memory Usage", "memory"),
            ("🎮 GPU Usage", "gpu"),
            ("🌡️ CPU Temperature", "cpu_temp"),
            ("💾 Disk Usage", "disk"),
            ("🌐 Network I/O", "network")
        ]
        
        for title, key in cards_config:
            card = FloatingStatsCard(title)
            self.stats_cards[key] = card
            self.stats_layout.addWidget(card)
            
            # Set unique base position for floating effect
            card.base_y = len(self.stats_cards) * 120
    
    def update_stats(self, stats):
        """Update all stats cards with new data"""
        try:
            # CPU stats
            if 'cpu' in self.stats_cards:
                self.stats_cards['cpu'].update_value(stats.cpu_percent)
            
            # Memory stats
            if 'memory' in self.stats_cards:
                self.stats_cards['memory'].update_value(stats.memory_percent)
            
            # GPU stats
            if 'gpu' in self.stats_cards and stats.gpu_percent is not None:
                self.stats_cards['gpu'].update_value(stats.gpu_percent)
            
            # CPU Temperature
            if 'cpu_temp' in self.stats_cards and stats.cpu_temp is not None:
                self.stats_cards['cpu_temp'].update_value(stats.cpu_temp, "°C")
            
            # Disk usage (average)
            if 'disk' in self.stats_cards and stats.disk_usage:
                avg_disk = sum(stats.disk_usage.values()) / len(stats.disk_usage)
                self.stats_cards['disk'].update_value(avg_disk)
            
            # Network I/O (combined rate in MB/s)
            if 'network' in self.stats_cards and stats.network_io:
                total_rate = (stats.network_io.get('bytes_sent_rate', 0) + 
                            stats.network_io.get('bytes_recv_rate', 0)) / (1024 * 1024)
                self.stats_cards['network'].update_value(total_rate, " MB/s")
            
            self.stats_updated.emit({
                'cpu': stats.cpu_percent,
                'memory': stats.memory_percent,
                'gpu': stats.gpu_percent,
                'timestamp': stats.timestamp
            })
            
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    def _update_master_animation(self):
        """Update master animation timing"""
        self.animation_time += 0.016  # 60 FPS
        
        # Create wave effect across cards
        for i, card in enumerate(self.stats_cards.values()):
            wave_offset = math.sin(self.animation_time + i * 0.5) * 2.0
            card.float_speed = 1.0 + wave_offset * 0.1
    
    def set_theme_colors(self, primary_color: str, secondary_color: str):
        """Set custom theme colors for stats cards"""
        for card in self.stats_cards.values():
            card.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {primary_color},
                        stop:1 {secondary_color});
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    border-radius: 12px;
                    margin: 5px;
                }}
            """)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        metrics = {}
        for key, card in self.stats_cards.items():
            if hasattr(card, 'last_value'):
                metrics[key] = card.last_value
        return metrics