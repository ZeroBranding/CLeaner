"""
Unit Tests für API Server
"""

import unittest
import asyncio
import json
from pathlib import Path
import sys
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from api_server import app, get_system_monitor, get_ai_manager, get_database_manager


class TestAPIServer(unittest.TestCase):
    """Test cases for API Server endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("name", data)
        self.assertEqual(data["name"], "GermanCodeZero Cleaner API")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("uptime", data)
    
    def test_system_info_endpoint(self):
        """Test system info endpoint"""
        response = self.client.get("/api/system/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check required fields
        self.assertIn("platform", data)
        self.assertIn("processor", data)
        self.assertIn("cpu_count", data)
        self.assertIn("total_memory", data)
    
    def test_system_metrics_endpoint(self):
        """Test system metrics endpoint"""
        response = self.client.get("/api/system/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check required metrics
        self.assertIn("cpu_percent", data)
        self.assertIn("memory_percent", data)
        self.assertIn("disk_usage", data)
        
        # Check value ranges
        self.assertGreaterEqual(data["cpu_percent"], 0)
        self.assertLessEqual(data["cpu_percent"], 100)
    
    @patch('api_server.scanner.scan_system')
    async def test_start_scan_endpoint(self, mock_scan):
        """Test scan initiation endpoint"""
        # Setup mock
        mock_scan.return_value = {
            "scan_id": 1,
            "status": "started",
            "total_files": 0
        }
        
        # Start scan
        response = self.client.post("/api/scan/start", json={
            "categories": ["temp_files", "cache"],
            "enable_ai": False
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("scan_id", data)
        self.assertIn("status", data)
    
    def test_scan_status_endpoint(self):
        """Test scan status endpoint"""
        # Try to get status of non-existent scan
        response = self.client.get("/api/scan/status/999")
        self.assertEqual(response.status_code, 404)
    
    def test_scan_history_endpoint(self):
        """Test scan history endpoint"""
        response = self.client.get("/api/scan/history?days=7")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    @patch('api_server.cleaner.perform_cleaning')
    async def test_perform_cleaning_endpoint(self, mock_clean):
        """Test cleaning endpoint"""
        # Setup mock
        mock_clean.return_value = {
            "success": True,
            "files_deleted": 100,
            "bytes_freed": 1024 * 1024 * 50
        }
        
        # Perform cleaning
        response = self.client.post("/api/clean", json={
            "scan_id": 1,
            "items": ["C:\\Temp\\file1.tmp", "C:\\Temp\\file2.tmp"],
            "create_backup": True
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("files_deleted", data)
    
    def test_cleaning_history_endpoint(self):
        """Test cleaning history endpoint"""
        response = self.client.get("/api/clean/history?days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    @patch('api_server.ai_manager.generate_response')
    async def test_ai_chat_endpoint(self, mock_ai):
        """Test AI chat endpoint"""
        # Setup mock
        mock_ai.return_value = "Dies ist eine KI-Antwort"
        
        # Send chat message
        response = self.client.post("/api/ai/chat", json={
            "message": "Wie bereinige ich meinen PC?",
            "context": "system_cleaning"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertIn("model_used", data)
    
    def test_ai_recommendations_endpoint(self):
        """Test AI recommendations endpoint"""
        scan_results = {
            "total_files": 1000,
            "total_size": 1024 * 1024 * 500,
            "categories": {
                "temp_files": {"count": 500, "size": 250 * 1024 * 1024}
            }
        }
        
        response = self.client.post("/api/ai/recommendations", json=scan_results)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_settings_endpoints(self):
        """Test settings management endpoints"""
        # Get all settings
        response = self.client.get("/api/settings")
        self.assertEqual(response.status_code, 200)
        settings = response.json()
        self.assertIsInstance(settings, dict)
        
        # Update a setting
        response = self.client.put("/api/settings", json={
            "key": "theme",
            "value": "dark"
        })
        self.assertEqual(response.status_code, 200)
        
        # Get specific setting
        response = self.client.get("/api/settings/theme")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["value"], "dark")
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = self.client.options("/api/health")
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertIn("access-control-allow-methods", response.headers)
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Invalid JSON
        response = self.client.post(
            "/api/scan/start",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 422)
        
        # Missing required fields
        response = self.client.post("/api/scan/start", json={})
        self.assertEqual(response.status_code, 422)
    
    def test_rate_limiting(self):
        """Test rate limiting (if implemented)"""
        # Make many requests quickly
        responses = []
        for _ in range(20):
            response = self.client.get("/api/system/metrics")
            responses.append(response.status_code)
        
        # All should succeed for now (rate limiting not yet implemented)
        self.assertTrue(all(code == 200 for code in responses))


class TestWebSocket(unittest.TestCase):
    """Test cases for WebSocket connections"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        with self.client.websocket_connect("/ws") as websocket:
            # Send a message
            websocket.send_json({"type": "ping"})
            
            # Receive response
            data = websocket.receive_json()
            self.assertIn("type", data)
    
    def test_websocket_system_updates(self):
        """Test receiving system updates via WebSocket"""
        with self.client.websocket_connect("/ws") as websocket:
            # Request system updates
            websocket.send_json({"type": "subscribe", "channel": "system"})
            
            # Should receive acknowledgment
            data = websocket.receive_json()
            self.assertEqual(data["type"], "subscribed")
            self.assertEqual(data["channel"], "system")


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_scan_to_clean_workflow(self):
        """Test complete scan to clean workflow"""
        # 1. Start a scan
        scan_response = self.client.post("/api/scan/start", json={
            "categories": ["temp_files"],
            "enable_ai": False
        })
        self.assertEqual(scan_response.status_code, 200)
        scan_id = scan_response.json().get("scan_id")
        
        if scan_id:
            # 2. Check scan status
            status_response = self.client.get(f"/api/scan/status/{scan_id}")
            # Might be 404 if scan completes too quickly or hasn't started
            self.assertIn(status_response.status_code, [200, 404])
            
            # 3. Get scan results (would need to wait for completion in real scenario)
            # results_response = self.client.get(f"/api/scan/results/{scan_id}")
            
            # 4. Perform cleaning (with mock data)
            clean_response = self.client.post("/api/clean", json={
                "scan_id": scan_id,
                "items": [],
                "create_backup": False
            })
            self.assertIn(clean_response.status_code, [200, 400])
    
    def test_metrics_monitoring(self):
        """Test continuous metrics monitoring"""
        # Get initial metrics
        response1 = self.client.get("/api/system/metrics")
        self.assertEqual(response1.status_code, 200)
        metrics1 = response1.json()
        
        # Get metrics again
        response2 = self.client.get("/api/system/metrics")
        self.assertEqual(response2.status_code, 200)
        metrics2 = response2.json()
        
        # Metrics should be present and possibly different
        self.assertIn("cpu_percent", metrics1)
        self.assertIn("cpu_percent", metrics2)
    
    def test_settings_persistence(self):
        """Test that settings changes persist"""
        # Set a preference
        self.client.put("/api/settings", json={
            "key": "test_setting",
            "value": "test_value"
        })
        
        # Retrieve the preference
        response = self.client.get("/api/settings/test_setting")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["value"], "test_value")
        
        # Get all preferences
        all_response = self.client.get("/api/settings")
        self.assertEqual(all_response.status_code, 200)
        settings = all_response.json()
        self.assertEqual(settings.get("test_setting"), "test_value")


class TestAPIPerformance(unittest.TestCase):
    """Performance tests for API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_endpoint_response_times(self):
        """Test that endpoints respond within acceptable time"""
        import time
        
        endpoints = [
            ("/api/health", "GET"),
            ("/api/system/info", "GET"),
            ("/api/system/metrics", "GET"),
            ("/api/scan/history?days=7", "GET"),
            ("/api/settings", "GET")
        ]
        
        for endpoint, method in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint, json={})
            
            elapsed_time = time.time() - start_time
            
            # Check response time is under 1 second
            self.assertLess(elapsed_time, 1.0, 
                          f"Endpoint {endpoint} took {elapsed_time:.2f}s")
            
            # Check successful response
            self.assertLess(response.status_code, 500)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        
        def make_request():
            response = self.client.get("/api/system/metrics")
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        self.assertTrue(all(code == 200 for code in results))


if __name__ == '__main__':
    unittest.main()