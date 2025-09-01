"""
Unit Tests für System Monitor
"""

import unittest
import time
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.system_monitor import SystemMonitor, PerformanceAnalyzer
from cleaner.hardware.cpu import CPUMonitor
from cleaner.hardware.ram import RAMMonitor
from cleaner.hardware.ssd import SSDMonitor
from cleaner.hardware.gpu import GPUMonitor


class TestSystemMonitor(unittest.TestCase):
    """Test cases for SystemMonitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.monitor = SystemMonitor()
    
    def test_singleton_pattern(self):
        """Test that SystemMonitor follows singleton pattern"""
        monitor2 = SystemMonitor()
        self.assertIs(self.monitor, monitor2)
    
    def test_get_system_info(self):
        """Test getting system information"""
        info = self.monitor.get_system_info()
        
        # Check required fields
        self.assertIn('platform', info)
        self.assertIn('processor', info)
        self.assertIn('cpu_count', info)
        self.assertIn('total_memory', info)
        self.assertIn('total_disk', info)
        
        # Check data types
        self.assertIsInstance(info['cpu_count'], int)
        self.assertIsInstance(info['total_memory'], int)
        self.assertIsInstance(info['total_disk'], int)
        
        # Check reasonable values
        self.assertGreater(info['cpu_count'], 0)
        self.assertGreater(info['total_memory'], 0)
        self.assertGreater(info['total_disk'], 0)
    
    def test_get_current_metrics(self):
        """Test getting current system metrics"""
        metrics = self.monitor.get_current_metrics()
        
        # Check required fields
        required_fields = [
            'cpu_percent', 'memory_percent', 'disk_usage',
            'disk_io', 'network_io', 'temperature'
        ]
        
        for field in required_fields:
            self.assertIn(field, metrics)
        
        # Check value ranges
        self.assertGreaterEqual(metrics['cpu_percent'], 0)
        self.assertLessEqual(metrics['cpu_percent'], 100)
        
        self.assertGreaterEqual(metrics['memory_percent'], 0)
        self.assertLessEqual(metrics['memory_percent'], 100)
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        # Start monitoring
        self.monitor.start_monitoring(interval=0.1)
        self.assertTrue(self.monitor.is_monitoring)
        
        # Let it run for a short time
        time.sleep(0.5)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring)
    
    def test_get_metrics_history(self):
        """Test getting metrics history"""
        # Start monitoring with short interval
        self.monitor.start_monitoring(interval=0.1)
        
        # Let it collect some data
        time.sleep(0.5)
        
        # Get history
        history = self.monitor.get_metrics_history(seconds=1)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Check that we have some history
        self.assertGreater(len(history), 0)
        
        # Check history structure
        if len(history) > 0:
            first_entry = history[0]
            self.assertIn('timestamp', first_entry)
            self.assertIn('cpu_percent', first_entry)
            self.assertIn('memory_percent', first_entry)
    
    def test_get_alerts(self):
        """Test alert generation"""
        alerts = self.monitor.get_alerts()
        
        # Check that alerts is a list
        self.assertIsInstance(alerts, list)
        
        # If there are alerts, check their structure
        if len(alerts) > 0:
            alert = alerts[0]
            self.assertIn('type', alert)
            self.assertIn('severity', alert)
            self.assertIn('message', alert)
            self.assertIn('timestamp', alert)
    
    def test_get_optimization_suggestions(self):
        """Test optimization suggestions"""
        suggestions = self.monitor.get_optimization_suggestions()
        
        # Check that suggestions is a list
        self.assertIsInstance(suggestions, list)
        
        # If there are suggestions, check their structure
        if len(suggestions) > 0:
            suggestion = suggestions[0]
            self.assertIn('category', suggestion)
            self.assertIn('description', suggestion)
            self.assertIn('potential_gain', suggestion)


class TestCPUMonitor(unittest.TestCase):
    """Test cases for CPUMonitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.cpu_monitor = CPUMonitor()
    
    def test_singleton_pattern(self):
        """Test that CPUMonitor follows singleton pattern"""
        cpu2 = CPUMonitor()
        self.assertIs(self.cpu_monitor, cpu2)
    
    def test_get_info(self):
        """Test getting CPU information"""
        info = self.cpu_monitor.get_info()
        
        # Check required fields
        self.assertIn('vendor', info)
        self.assertIn('model', info)
        self.assertIn('cores', info)
        self.assertIn('threads', info)
        self.assertIn('frequency', info)
        
        # Check data types and values
        self.assertIsInstance(info['cores'], int)
        self.assertIsInstance(info['threads'], int)
        self.assertGreater(info['cores'], 0)
        self.assertGreater(info['threads'], 0)
    
    def test_get_usage(self):
        """Test getting CPU usage"""
        usage = self.cpu_monitor.get_usage()
        
        # Check value range
        self.assertGreaterEqual(usage, 0)
        self.assertLessEqual(usage, 100)
    
    def test_get_per_core_usage(self):
        """Test getting per-core CPU usage"""
        per_core = self.cpu_monitor.get_per_core_usage()
        
        # Check that we have data for each core
        self.assertIsInstance(per_core, list)
        self.assertGreater(len(per_core), 0)
        
        # Check value ranges
        for usage in per_core:
            self.assertGreaterEqual(usage, 0)
            self.assertLessEqual(usage, 100)
    
    def test_get_temperature(self):
        """Test getting CPU temperature"""
        temp = self.cpu_monitor.get_temperature()
        
        # Temperature might not be available on all systems
        if temp is not None:
            self.assertIsInstance(temp, (int, float))
            # Reasonable temperature range (Celsius)
            self.assertGreater(temp, 0)
            self.assertLess(temp, 150)


class TestRAMMonitor(unittest.TestCase):
    """Test cases for RAMMonitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.ram_monitor = RAMMonitor()
    
    def test_get_info(self):
        """Test getting RAM information"""
        info = self.ram_monitor.get_info()
        
        # Check required fields
        self.assertIn('total', info)
        self.assertIn('available', info)
        self.assertIn('used', info)
        self.assertIn('free', info)
        self.assertIn('percent', info)
        
        # Check values
        self.assertGreater(info['total'], 0)
        self.assertGreaterEqual(info['percent'], 0)
        self.assertLessEqual(info['percent'], 100)
    
    def test_get_usage_percent(self):
        """Test getting RAM usage percentage"""
        usage = self.ram_monitor.get_usage_percent()
        
        self.assertGreaterEqual(usage, 0)
        self.assertLessEqual(usage, 100)
    
    def test_get_top_processes(self):
        """Test getting top memory-consuming processes"""
        processes = self.ram_monitor.get_top_processes(limit=5)
        
        # Check that we get a list
        self.assertIsInstance(processes, list)
        self.assertLessEqual(len(processes), 5)
        
        # Check process structure
        if len(processes) > 0:
            process = processes[0]
            self.assertIn('pid', process)
            self.assertIn('name', process)
            self.assertIn('memory_mb', process)
            self.assertIn('memory_percent', process)


class TestSSDMonitor(unittest.TestCase):
    """Test cases for SSDMonitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.ssd_monitor = SSDMonitor()
    
    def test_get_info(self):
        """Test getting SSD information"""
        info = self.ssd_monitor.get_info()
        
        # Check that we have disk information
        self.assertIsInstance(info, list)
        self.assertGreater(len(info), 0)
        
        # Check first disk structure
        disk = info[0]
        self.assertIn('device', disk)
        self.assertIn('mountpoint', disk)
        self.assertIn('total', disk)
        self.assertIn('used', disk)
        self.assertIn('free', disk)
        self.assertIn('percent', disk)
    
    def test_get_io_stats(self):
        """Test getting I/O statistics"""
        stats = self.ssd_monitor.get_io_stats()
        
        # Check required fields
        self.assertIn('read_bytes', stats)
        self.assertIn('write_bytes', stats)
        self.assertIn('read_count', stats)
        self.assertIn('write_count', stats)
        
        # Check values are non-negative
        self.assertGreaterEqual(stats['read_bytes'], 0)
        self.assertGreaterEqual(stats['write_bytes'], 0)


class TestGPUMonitor(unittest.TestCase):
    """Test cases for GPUMonitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.gpu_monitor = GPUMonitor()
    
    def test_is_available(self):
        """Test GPU availability check"""
        available = self.gpu_monitor.is_available()
        self.assertIsInstance(available, bool)
    
    def test_get_info(self):
        """Test getting GPU information"""
        info = self.gpu_monitor.get_info()
        
        if self.gpu_monitor.is_available():
            # If GPU is available, check structure
            self.assertIn('name', info)
            self.assertIn('driver_version', info)
            self.assertIn('cuda_version', info)
            self.assertIn('total_memory', info)
        else:
            # If no GPU, should return None or empty dict
            self.assertTrue(info is None or info == {})
    
    def test_get_usage(self):
        """Test getting GPU usage"""
        usage = self.gpu_monitor.get_usage()
        
        if self.gpu_monitor.is_available():
            self.assertIsInstance(usage, (int, float))
            self.assertGreaterEqual(usage, 0)
            self.assertLessEqual(usage, 100)
        else:
            self.assertEqual(usage, 0)


class TestPerformanceAnalyzer(unittest.TestCase):
    """Test cases for PerformanceAnalyzer"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = PerformanceAnalyzer()
    
    def test_analyze_system_bottlenecks(self):
        """Test system bottleneck analysis"""
        # Get current metrics
        monitor = SystemMonitor()
        metrics = monitor.get_current_metrics()
        
        # Analyze bottlenecks
        bottlenecks = self.analyzer.analyze_bottlenecks(metrics)
        
        # Check structure
        self.assertIsInstance(bottlenecks, list)
        
        if len(bottlenecks) > 0:
            bottleneck = bottlenecks[0]
            self.assertIn('component', bottleneck)
            self.assertIn('severity', bottleneck)
            self.assertIn('description', bottleneck)
    
    def test_generate_optimization_plan(self):
        """Test optimization plan generation"""
        # Get current metrics
        monitor = SystemMonitor()
        metrics = monitor.get_current_metrics()
        
        # Generate plan
        plan = self.analyzer.generate_optimization_plan(metrics)
        
        # Check structure
        self.assertIsInstance(plan, dict)
        self.assertIn('immediate_actions', plan)
        self.assertIn('scheduled_tasks', plan)
        self.assertIn('long_term_recommendations', plan)


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    unittest.main()