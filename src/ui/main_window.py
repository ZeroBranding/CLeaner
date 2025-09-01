"""
🖥️ Holographic Main Window
Modern animated UI with floating islands effect and 3D spatial layout
"""

import asyncio
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QProgressBar, QPushButton, QTextEdit, QLineEdit,
    QTabWidget, QSplitter, QGroupBox, QSlider, QComboBox,
    QFrame, QScrollArea, QListWidget, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QLinearGradient, QPainter, QPen, QBrush,
    QPixmap, QIcon, QMovie, QTransform
)
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QAreaSeries
import logging

from .effects.holographic_renderer import HolographicRenderer
from .components.animated_stats import AnimatedStatsWidget
from .components.ai_chat import AIChatWidget
from .components.system_overview import SystemOverviewWidget

logger = logging.getLogger(__name__)

class FloatingWidget(QWidget):
    """Floating island effect widget with 3D transforms"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.float_offset = 0.0
        self.float_speed = 1.0
        self.float_amplitude = 5.0
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_float_animation)
        self.animation_timer.start(16)  # 60 FPS
        
        # Style with glassmorphism effect
        self.setStyleSheet("""
            QWidget {
                background: rgba(30, 30, 40, 0.8);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
        """)
    
    def _update_float_animation(self):
        """Update floating animation"""
        self.float_offset += 0.02 * self.float_speed
        
        # Calculate floating position
        y_offset = math.sin(self.float_offset) * self.float_amplitude
        
        # Apply transform
        transform = QTransform()
        transform.translate(0, y_offset)
        
        # Update widget position (simplified - real implementation would use 3D transforms)
        self.move(self.x(), int(self.y() + y_offset - self.float_amplitude))

class NeonButton(QPushButton):
    """Neon-styled button with glow effects"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 0.3),
                    stop:1 rgba(255, 0, 255, 0.3));
                border: 2px solid rgba(0, 255, 255, 0.8);
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 0.5),
                    stop:1 rgba(255, 0, 255, 0.5));
                border: 2px solid rgba(0, 255, 255, 1.0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 0.7),
                    stop:1 rgba(255, 0, 255, 0.7));
            }
        """)

class HolographicMainWindow(QMainWindow):
    """Main application window with holographic UI"""
    
    def __init__(self, system_monitor, ai_manager, db_manager):
        super().__init__()
        
        self.system_monitor = system_monitor
        self.ai_manager = ai_manager
        self.db_manager = db_manager
        
        # Window properties
        self.setWindowTitle("🚀 Holographic AI System Monitor")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        self._setup_animations()
        
        # Start monitoring
        self.system_monitor.start_monitoring()
        
        logger.info("Holographic main window initialized")
    
    def _setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitters for flexible arrangement
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Left panel - System monitoring
        left_panel = self._create_left_panel()
        
        # Center panel - Holographic effects and AI chat
        center_panel = self._create_center_panel()
        
        # Right panel - Controls and settings
        right_panel = self._create_right_panel()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 700, 350])
        
        main_layout.addWidget(splitter)
        
        # Apply modern dark theme
        self._apply_modern_theme()
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with system monitoring"""
        panel = FloatingWidget()
        layout = QVBoxLayout(panel)
        
        # System Overview
        self.system_overview = SystemOverviewWidget(self.system_monitor)
        layout.addWidget(self.system_overview)
        
        # Animated Statistics
        self.animated_stats = AnimatedStatsWidget()
        layout.addWidget(self.animated_stats)
        
        # Performance History Chart
        self.performance_chart = self._create_performance_chart()
        layout.addWidget(self.performance_chart)
        
        return panel
    
    def _create_center_panel(self) -> QWidget:
        """Create center panel with holographic effects and AI chat"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        
        # Holographic visualization tab
        holo_tab = QWidget()
        holo_layout = QVBoxLayout(holo_tab)
        
        # Holographic renderer
        self.holographic_renderer = HolographicRenderer()
        self.holographic_renderer.setMinimumHeight(400)
        holo_layout.addWidget(self.holographic_renderer)
        
        # Holographic controls
        holo_controls = self._create_holographic_controls()
        holo_layout.addWidget(holo_controls)
        
        tab_widget.addTab(holo_tab, "🌌 Holographic View")
        
        # AI Chat tab
        self.ai_chat = AIChatWidget(self.ai_manager)
        tab_widget.addTab(self.ai_chat, "🤖 AI Assistant")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with controls and settings"""
        panel = FloatingWidget()
        layout = QVBoxLayout(panel)
        
        # AI Provider Selection
        ai_group = QGroupBox("🤖 AI Providers")
        ai_layout = QVBoxLayout(ai_group)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "Auto Select",
            "Llama3-8B (Local)",
            "Google Gemini 1.5",
            "Deepseek 3.1",
            "Groq (Free)"
        ])
        ai_layout.addWidget(self.provider_combo)
        
        # Provider status indicators
        self.provider_status = QListWidget()
        self.provider_status.setMaximumHeight(150)
        ai_layout.addWidget(self.provider_status)
        
        layout.addWidget(ai_group)
        
        # Visual Effects Controls
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        # Hologram intensity
        intensity_label = QLabel("Hologram Intensity:")
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(0, 200)
        self.intensity_slider.setValue(100)
        self.intensity_slider.valueChanged.connect(self._on_intensity_changed)
        
        effects_layout.addWidget(intensity_label)
        effects_layout.addWidget(self.intensity_slider)
        
        # Particle count
        particle_label = QLabel("Particle Count:")
        self.particle_slider = QSlider(Qt.Orientation.Horizontal)
        self.particle_slider.setRange(100, 5000)
        self.particle_slider.setValue(1000)
        self.particle_slider.valueChanged.connect(self._on_particle_count_changed)
        
        effects_layout.addWidget(particle_label)
        effects_layout.addWidget(self.particle_slider)
        
        layout.addWidget(effects_group)
        
        # System Information
        info_group = QGroupBox("💻 System Info")
        info_layout = QVBoxLayout(info_group)
        
        self.system_info_text = QTextEdit()
        self.system_info_text.setMaximumHeight(200)
        self.system_info_text.setReadOnly(True)
        info_layout.addWidget(self.system_info_text)
        
        layout.addWidget(info_group)
        
        # Performance Metrics
        perf_group = QGroupBox("📊 Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.fps_label = QLabel("FPS: --")
        self.gpu_usage_label = QLabel("GPU: --")
        self.memory_usage_label = QLabel("Memory: --")
        
        perf_layout.addWidget(self.fps_label)
        perf_layout.addWidget(self.gpu_usage_label)
        perf_layout.addWidget(self.memory_usage_label)
        
        layout.addWidget(perf_group)
        
        return panel
    
    def _create_holographic_controls(self) -> QWidget:
        """Create holographic effect controls"""
        controls = QWidget()
        layout = QHBoxLayout(controls)
        
        # Effect toggle buttons
        self.toggle_hologram = NeonButton("Toggle Hologram")
        self.toggle_particles = NeonButton("Toggle Particles")
        self.toggle_glow = NeonButton("Toggle Glow")
        
        layout.addWidget(self.toggle_hologram)
        layout.addWidget(self.toggle_particles)
        layout.addWidget(self.toggle_glow)
        
        return controls
    
    def _create_performance_chart(self) -> QWidget:
        """Create animated performance chart"""
        chart = QChart()
        chart.setTitle("System Performance")
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        
        # CPU series
        self.cpu_series = QLineSeries()
        self.cpu_series.setName("CPU %")
        chart.addSeries(self.cpu_series)
        
        # Memory series
        self.memory_series = QLineSeries()
        self.memory_series.setName("Memory %")
        chart.addSeries(self.memory_series)
        
        # GPU series
        self.gpu_series = QLineSeries()
        self.gpu_series.setName("GPU %")
        chart.addSeries(self.gpu_series)
        
        # Setup axes
        x_axis = QValueAxis()
        x_axis.setRange(0, 60)  # 60 seconds
        x_axis.setTitleText("Time (s)")
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        
        y_axis = QValueAxis()
        y_axis.setRange(0, 100)
        y_axis.setTitleText("Usage (%)")
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        
        # Attach series to axes
        self.cpu_series.attachAxis(x_axis)
        self.cpu_series.attachAxis(y_axis)
        self.memory_series.attachAxis(x_axis)
        self.memory_series.attachAxis(y_axis)
        self.gpu_series.attachAxis(x_axis)
        self.gpu_series.attachAxis(y_axis)
        
        chart_view = QChartView(chart)
        chart_view.setMaximumHeight(200)
        
        return chart_view
    
    def _setup_connections(self):
        """Setup signal connections"""
        # System monitor connections
        self.system_monitor.stats_updated.connect(self._on_stats_updated)
        self.system_monitor.error_occurred.connect(self._on_monitor_error)
        
        # Holographic renderer connections
        self.holographic_renderer.fps_updated.connect(self._on_fps_updated)
        
        # AI manager connections
        if hasattr(self.ai_manager, 'response_ready'):
            self.ai_manager.response_ready.connect(self._on_ai_response)
        if hasattr(self.ai_manager, 'provider_status_changed'):
            self.ai_manager.provider_status_changed.connect(self._on_provider_status_changed)
    
    def _setup_animations(self):
        """Setup UI animations"""
        # Create property animations for smooth transitions
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Window entrance animation
        self.setWindowOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def _apply_modern_theme(self):
        """Apply modern dark theme with neon accents"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f17;
                color: #ffffff;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background: rgba(25, 25, 35, 0.8);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ffff;
            }
            
            QTabWidget::pane {
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 8px;
                background: rgba(25, 25, 35, 0.9);
            }
            
            QTabBar::tab {
                background: rgba(45, 45, 55, 0.8);
                border: 1px solid rgba(0, 255, 255, 0.3);
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            QTabBar::tab:selected {
                background: rgba(0, 255, 255, 0.2);
                border-bottom-color: transparent;
            }
            
            QTabBar::tab:hover {
                background: rgba(0, 255, 255, 0.1);
            }
            
            QSlider::groove:horizontal {
                border: 1px solid rgba(0, 255, 255, 0.3);
                height: 8px;
                background: rgba(25, 25, 35, 0.8);
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ffff, stop:1 #ff00ff);
                border: 1px solid rgba(0, 255, 255, 0.8);
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ffff, stop:1 #ffffff);
            }
            
            QProgressBar {
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 8px;
                text-align: center;
                background: rgba(25, 25, 35, 0.8);
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:0.5 #ff00ff, stop:1 #ffff00);
                border-radius: 6px;
            }
            
            QTextEdit, QLineEdit {
                background: rgba(25, 25, 35, 0.9);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 6px;
                padding: 5px;
                color: #ffffff;
            }
            
            QTextEdit:focus, QLineEdit:focus {
                border: 2px solid rgba(0, 255, 255, 0.8);
            }
            
            QComboBox {
                background: rgba(45, 45, 55, 0.8);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 6px;
                padding: 5px;
                color: #ffffff;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00ffff;
            }
            
            QListWidget {
                background: rgba(25, 25, 35, 0.9);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 6px;
                color: #ffffff;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid rgba(0, 255, 255, 0.1);
            }
            
            QListWidget::item:selected {
                background: rgba(0, 255, 255, 0.2);
            }
        """)
    
    def _on_stats_updated(self, stats):
        """Handle system stats update"""
        # Update animated stats widget
        self.animated_stats.update_stats(stats)
        
        # Update system overview
        self.system_overview.update_stats(stats)
        
        # Update performance chart
        self._update_performance_chart(stats)
        
        # Update right panel labels
        self.gpu_usage_label.setText(f"GPU: {stats.gpu_percent:.1f}%" if stats.gpu_percent else "GPU: N/A")
        self.memory_usage_label.setText(f"Memory: {stats.memory_percent:.1f}%")
        
        # Store stats in database
        if self.db_manager:
            self.db_manager.store_system_stats(stats)
    
    def _update_performance_chart(self, stats):
        """Update performance chart with new data"""
        current_time = time.time()
        
        # Add new data points
        self.cpu_series.append(current_time, stats.cpu_percent)
        self.memory_series.append(current_time, stats.memory_percent)
        if stats.gpu_percent is not None:
            self.gpu_series.append(current_time, stats.gpu_percent)
        
        # Keep only last 60 seconds of data
        cutoff_time = current_time - 60
        
        for series in [self.cpu_series, self.memory_series, self.gpu_series]:
            points = series.pointsVector()
            while points and points[0].x() < cutoff_time:
                series.removePoints(0, 1)
                points = series.pointsVector()
    
    def _on_fps_updated(self, fps):
        """Handle FPS update from holographic renderer"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
        
        # Adjust effects quality based on performance
        if fps < 30:
            # Reduce particle count for better performance
            current_count = self.particle_slider.value()
            if current_count > 500:
                self.particle_slider.setValue(max(500, current_count - 100))
        elif fps > 55:
            # Increase quality if performance allows
            current_count = self.particle_slider.value()
            if current_count < 2000:
                self.particle_slider.setValue(min(2000, current_count + 50))
    
    def _on_intensity_changed(self, value):
        """Handle hologram intensity change"""
        intensity = value / 100.0
        self.holographic_renderer.set_hologram_intensity(intensity)
    
    def _on_particle_count_changed(self, value):
        """Handle particle count change"""
        self.holographic_renderer.set_particle_count(value)
    
    def _on_monitor_error(self, error):
        """Handle system monitor error"""
        logger.error(f"System monitor error: {error}")
    
    def _on_ai_response(self, response):
        """Handle AI response"""
        logger.info(f"AI response received from {response.provider.value}")
    
    def _on_provider_status_changed(self, provider, healthy):
        """Handle AI provider status change"""
        # Update provider status list
        self._update_provider_status_display()
    
    def _update_provider_status_display(self):
        """Update provider status display"""
        self.provider_status.clear()
        
        if hasattr(self.ai_manager, 'get_provider_status'):
            status_dict = self.ai_manager.get_provider_status()
            
            for provider, status in status_dict.items():
                status_text = f"{'🟢' if status['healthy'] else '🔴'} {status['name']}"
                if status['local']:
                    status_text += " (Local)"
                
                self.provider_status.addItem(status_text)
    
    def closeEvent(self, event):
        """Handle application close"""
        # Stop monitoring
        self.system_monitor.stop_monitoring()
        
        # Close database
        if self.db_manager:
            self.db_manager.close()
        
        logger.info("Application closing")
        event.accept()

# Import math for floating widget
import math