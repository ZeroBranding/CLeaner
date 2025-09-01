"""
Unit Tests für Database Manager
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import asyncio

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import DatabaseManager, CloudDatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db_manager = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'db_manager') and self.db_manager.conn:
            self.db_manager.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_singleton_pattern(self):
        """Test that DatabaseManager follows singleton pattern"""
        db2 = DatabaseManager(self.db_path)
        self.assertIs(self.db_manager, db2)
    
    def test_create_tables(self):
        """Test table creation"""
        # Tables should be created automatically in __init__
        tables = self.db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [table[0] for table in tables]
        
        expected_tables = ['scan_results', 'cleaning_history', 'user_preferences']
        for table in expected_tables:
            self.assertIn(table, table_names)
    
    def test_save_scan_result(self):
        """Test saving scan results"""
        scan_data = {
            'total_files': 1000,
            'total_size': 1024 * 1024 * 100,  # 100MB
            'categories': {
                'temp_files': {'count': 500, 'size': 50 * 1024 * 1024},
                'cache': {'count': 300, 'size': 30 * 1024 * 1024}
            }
        }
        
        scan_id = self.db_manager.save_scan_result(scan_data)
        self.assertIsNotNone(scan_id)
        self.assertIsInstance(scan_id, int)
    
    def test_get_scan_history(self):
        """Test retrieving scan history"""
        # Save multiple scan results
        for i in range(5):
            self.db_manager.save_scan_result({
                'total_files': 100 * (i + 1),
                'total_size': 1024 * 1024 * (i + 1),
                'categories': {}
            })
        
        # Get history for last 7 days
        history = self.db_manager.get_scan_history(days=7)
        self.assertEqual(len(history), 5)
        
        # Check that results are ordered by timestamp (newest first)
        timestamps = [h['timestamp'] for h in history]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
    
    def test_save_cleaning_result(self):
        """Test saving cleaning results"""
        # First save a scan result
        scan_id = self.db_manager.save_scan_result({
            'total_files': 100,
            'total_size': 1024 * 1024,
            'categories': {}
        })
        
        # Save cleaning result
        cleaning_data = {
            'scan_id': scan_id,
            'files_deleted': 50,
            'bytes_freed': 512 * 1024,
            'duration_seconds': 10.5,
            'error_count': 0
        }
        
        result = self.db_manager.save_cleaning_result(cleaning_data)
        self.assertTrue(result)
    
    def test_get_cleaning_history(self):
        """Test retrieving cleaning history"""
        # Create scan and cleaning results
        scan_id = self.db_manager.save_scan_result({
            'total_files': 100,
            'total_size': 1024 * 1024,
            'categories': {}
        })
        
        for i in range(3):
            self.db_manager.save_cleaning_result({
                'scan_id': scan_id,
                'files_deleted': 10 * (i + 1),
                'bytes_freed': 100 * 1024 * (i + 1),
                'duration_seconds': 5.0,
                'error_count': 0
            })
        
        history = self.db_manager.get_cleaning_history(days=30)
        self.assertEqual(len(history), 3)
    
    def test_save_and_get_preference(self):
        """Test saving and retrieving user preferences"""
        # Save preferences
        self.db_manager.save_preference('auto_scan', 'true')
        self.db_manager.save_preference('scan_interval', '7')
        self.db_manager.save_preference('theme', 'dark')
        
        # Get single preference
        auto_scan = self.db_manager.get_preference('auto_scan')
        self.assertEqual(auto_scan, 'true')
        
        # Get non-existent preference with default
        missing = self.db_manager.get_preference('missing_key', 'default_value')
        self.assertEqual(missing, 'default_value')
    
    def test_get_all_preferences(self):
        """Test getting all preferences"""
        # Save multiple preferences
        prefs = {
            'theme': 'dark',
            'language': 'de',
            'auto_clean': 'false'
        }
        
        for key, value in prefs.items():
            self.db_manager.save_preference(key, value)
        
        all_prefs = self.db_manager.get_all_preferences()
        
        for key, value in prefs.items():
            self.assertEqual(all_prefs[key], value)
    
    def test_cleanup_old_data(self):
        """Test cleanup of old data"""
        # Create old scan results
        old_timestamp = (datetime.now() - timedelta(days=40)).isoformat()
        
        # Insert old data directly
        self.db_manager.execute_update(
            """INSERT INTO scan_results (timestamp, total_files, total_size, categories_json, ai_insights)
               VALUES (?, ?, ?, ?, ?)""",
            (old_timestamp, 100, 1024, '{}', None)
        )
        
        # Create recent scan
        self.db_manager.save_scan_result({
            'total_files': 200,
            'total_size': 2048,
            'categories': {}
        })
        
        # Cleanup data older than 30 days
        self.db_manager.cleanup_old_data(days=30)
        
        # Check that only recent data remains
        history = self.db_manager.get_scan_history(days=60)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['total_files'], 200)
    
    def test_export_import_data(self):
        """Test data export and import"""
        # Create some data
        scan_id = self.db_manager.save_scan_result({
            'total_files': 100,
            'total_size': 1024 * 1024,
            'categories': {'temp': {'count': 50, 'size': 512 * 1024}}
        })
        
        self.db_manager.save_preference('theme', 'dark')
        
        # Export data
        export_path = Path(self.temp_dir) / "export.json"
        result = self.db_manager.export_data(export_path)
        self.assertTrue(result)
        self.assertTrue(export_path.exists())
        
        # Create new database
        new_db_path = Path(self.temp_dir) / "new_test.db"
        new_db = DatabaseManager(new_db_path)
        
        # Import data
        import_result = new_db.import_data(export_path)
        self.assertTrue(import_result)
        
        # Verify imported data
        history = new_db.get_scan_history(days=7)
        self.assertEqual(len(history), 1)
        
        theme = new_db.get_preference('theme')
        self.assertEqual(theme, 'dark')
        
        new_db.close()
    
    def test_thread_safety(self):
        """Test thread safety of database operations"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    self.db_manager.save_preference(f'worker_{worker_id}_{i}', str(i))
                    time.sleep(0.001)  # Small delay to increase chance of conflicts
                results.append(worker_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all operations completed without errors
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 5)
        
        # Verify all preferences were saved
        all_prefs = self.db_manager.get_all_preferences()
        expected_count = 5 * 10  # 5 workers * 10 preferences each
        actual_count = sum(1 for key in all_prefs if key.startswith('worker_'))
        self.assertEqual(actual_count, expected_count)


class TestCloudDatabaseManager(unittest.TestCase):
    """Test cases for CloudDatabaseManager (PostgreSQL)"""
    
    def setUp(self):
        """Set up test environment"""
        # Use test configuration
        self.config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_cleaner_db',
            'user': 'test_user',
            'password': 'test_password'
        }
        
        # Note: These tests require a running PostgreSQL instance
        # They will be skipped if connection fails
        try:
            self.cloud_db = CloudDatabaseManager(self.config)
            self.skip_tests = False
        except Exception:
            self.skip_tests = True
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'cloud_db') and not self.skip_tests:
            self.cloud_db.close()
    
    def test_cloud_sync(self):
        """Test cloud synchronization"""
        if self.skip_tests:
            self.skipTest("PostgreSQL not available")
        
        # This would test cloud sync functionality
        # Implementation depends on actual cloud setup
        pass


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    unittest.main()