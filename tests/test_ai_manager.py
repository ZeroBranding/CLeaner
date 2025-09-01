"""
Unit Tests für AI Manager
"""

import unittest
import asyncio
from pathlib import Path
import sys
from unittest.mock import Mock, patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.ai_manager import AIManager, ModelType


class TestAIManager(unittest.TestCase):
    """Test cases for AIManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.ai_manager = AIManager()
    
    def test_singleton_pattern(self):
        """Test that AIManager follows singleton pattern"""
        ai2 = AIManager()
        self.assertIs(self.ai_manager, ai2)
    
    def test_model_selection(self):
        """Test model selection logic"""
        # Test local model selection
        model = self.ai_manager._select_model(ModelType.LOCAL)
        self.assertIn(model, ['ollama', 'llama_cpp', None])
        
        # Test cloud model selection  
        model = self.ai_manager._select_model(ModelType.CLOUD)
        self.assertIn(model, ['claude', None])
    
    @patch('src.ai.ai_manager.AIManager._call_ollama')
    async def test_generate_response_with_ollama(self, mock_ollama):
        """Test response generation with Ollama"""
        # Setup mock
        mock_ollama.return_value = "Dies ist eine Test-Antwort von Ollama"
        
        # Force Ollama as available
        self.ai_manager.ollama_available = True
        
        # Generate response
        response = await self.ai_manager.generate_response(
            "Was ist der beste Weg, temporäre Dateien zu bereinigen?"
        )
        
        # Check response
        self.assertIsNotNone(response)
        self.assertIn("Test-Antwort", response)
        mock_ollama.assert_called_once()
    
    @patch('src.ai.ai_manager.AIManager._call_claude')
    async def test_generate_response_with_claude(self, mock_claude):
        """Test response generation with Claude API"""
        # Setup mock
        mock_claude.return_value = "Claude empfiehlt regelmäßige Bereinigung"
        
        # Force Claude as available
        self.ai_manager.claude_available = True
        self.ai_manager.ollama_available = False
        
        # Generate response
        response = await self.ai_manager.generate_response(
            "Wie optimiere ich meinen PC?",
            prefer_cloud=True
        )
        
        # Check response
        self.assertIsNotNone(response)
        self.assertIn("Claude", response)
        mock_claude.assert_called_once()
    
    def test_explain_cleaning_item(self):
        """Test cleaning item explanation"""
        item = {
            'path': 'C:\\Windows\\Temp\\test.tmp',
            'size': 1024 * 1024,  # 1MB
            'type': 'temp_file',
            'created': '2024-01-01'
        }
        
        explanation = self.ai_manager.explain_cleaning_item(item)
        
        # Check explanation structure
        self.assertIsInstance(explanation, dict)
        self.assertIn('description', explanation)
        self.assertIn('safety_level', explanation)
        self.assertIn('recommendation', explanation)
        
        # Check safety level
        self.assertIn(explanation['safety_level'], ['safe', 'caution', 'danger'])
    
    def test_get_cleaning_recommendations(self):
        """Test cleaning recommendations"""
        scan_results = {
            'total_files': 1000,
            'total_size': 1024 * 1024 * 500,  # 500MB
            'categories': {
                'temp_files': {
                    'count': 500,
                    'size': 250 * 1024 * 1024
                },
                'cache': {
                    'count': 300,
                    'size': 150 * 1024 * 1024
                },
                'duplicates': {
                    'count': 50,
                    'size': 100 * 1024 * 1024
                }
            }
        }
        
        recommendations = self.ai_manager.get_cleaning_recommendations(scan_results)
        
        # Check recommendations structure
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check recommendation format
        for rec in recommendations:
            self.assertIn('category', rec)
            self.assertIn('priority', rec)
            self.assertIn('action', rec)
            self.assertIn('reason', rec)
    
    def test_cache_functionality(self):
        """Test response caching"""
        prompt = "Test-Prompt für Cache"
        response = "Gecachte Antwort"
        
        # Add to cache
        self.ai_manager._add_to_cache(prompt, response)
        
        # Check cache hit
        cached = self.ai_manager._get_from_cache(prompt)
        self.assertEqual(cached, response)
        
        # Check cache miss
        missing = self.ai_manager._get_from_cache("Nicht im Cache")
        self.assertIsNone(missing)
    
    def test_cache_size_limit(self):
        """Test cache size limitation"""
        # Add many items to cache
        for i in range(150):  # More than cache limit (100)
            self.ai_manager._add_to_cache(f"prompt_{i}", f"response_{i}")
        
        # Check cache size doesn't exceed limit
        self.assertLessEqual(len(self.ai_manager.response_cache), 100)
        
        # Check that recent items are in cache
        self.assertIsNotNone(self.ai_manager._get_from_cache("prompt_149"))
        
        # Check that old items were removed
        self.assertIsNone(self.ai_manager._get_from_cache("prompt_0"))
    
    @patch('requests.post')
    def test_fallback_mechanism(self, mock_post):
        """Test fallback from cloud to local models"""
        # Simulate Claude API failure
        mock_post.side_effect = Exception("API Error")
        
        # Set up models availability
        self.ai_manager.claude_available = True
        self.ai_manager.ollama_available = False
        
        # Try to generate response
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(
            self.ai_manager.generate_response("Test", prefer_cloud=True)
        )
        loop.close()
        
        # Should fallback to default response
        self.assertIsNotNone(response)
        self.assertIn("KI-Modell", response)  # Default response indicator
    
    def test_get_model_status(self):
        """Test getting model status"""
        status = self.ai_manager.get_model_status()
        
        # Check status structure
        self.assertIsInstance(status, dict)
        self.assertIn('ollama', status)
        self.assertIn('llama_cpp', status)
        self.assertIn('claude', status)
        
        # Check status values
        for model, info in status.items():
            self.assertIn('available', info)
            self.assertIn('loaded', info)
            self.assertIsInstance(info['available'], bool)
            self.assertIsInstance(info['loaded'], bool)
    
    async def test_async_response_generation(self):
        """Test asynchronous response generation"""
        # Create multiple async tasks
        tasks = []
        for i in range(5):
            task = self.ai_manager.generate_response(f"Frage {i}")
            tasks.append(task)
        
        # Wait for all responses
        responses = await asyncio.gather(*tasks)
        
        # Check all responses
        self.assertEqual(len(responses), 5)
        for response in responses:
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
    
    def test_analyze_system_performance(self):
        """Test system performance analysis"""
        metrics = {
            'cpu_percent': 85,
            'memory_percent': 75,
            'disk_usage': 90,
            'running_processes': 150
        }
        
        analysis = self.ai_manager.analyze_system_performance(metrics)
        
        # Check analysis structure
        self.assertIsInstance(analysis, dict)
        self.assertIn('status', analysis)
        self.assertIn('issues', analysis)
        self.assertIn('recommendations', analysis)
        
        # With high usage, should detect issues
        self.assertGreater(len(analysis['issues']), 0)
        self.assertGreater(len(analysis['recommendations']), 0)
    
    def test_suggest_optimization_priority(self):
        """Test optimization priority suggestions"""
        scan_results = {
            'categories': {
                'system_cache': {'size': 5 * 1024 * 1024 * 1024},  # 5GB
                'temp_files': {'size': 100 * 1024 * 1024},  # 100MB
                'browser_cache': {'size': 2 * 1024 * 1024 * 1024},  # 2GB
            }
        }
        
        priorities = self.ai_manager.suggest_optimization_priority(scan_results)
        
        # Check priorities structure
        self.assertIsInstance(priorities, list)
        self.assertGreater(len(priorities), 0)
        
        # Check that largest category has highest priority
        self.assertEqual(priorities[0]['category'], 'system_cache')
        
        # Check priority values
        for item in priorities:
            self.assertIn('category', item)
            self.assertIn('priority', item)
            self.assertIn('size', item)
            self.assertIn(item['priority'], ['high', 'medium', 'low'])


class TestAIIntegration(unittest.TestCase):
    """Integration tests for AI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.ai_manager = AIManager()
    
    @unittest.skipUnless(
        AIManager().ollama_available or AIManager().claude_available,
        "No AI models available for integration testing"
    )
    async def test_real_model_response(self):
        """Test with real AI model if available"""
        response = await self.ai_manager.generate_response(
            "Liste 3 wichtige Windows-Temp-Ordner auf"
        )
        
        # Check that we get a meaningful response
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 50)  # Should be substantial response
    
    def test_end_to_end_cleaning_workflow(self):
        """Test complete cleaning workflow with AI"""
        # Simulate scan results
        scan_results = {
            'total_files': 2500,
            'total_size': 2 * 1024 * 1024 * 1024,  # 2GB
            'categories': {
                'temp_files': {
                    'count': 1000,
                    'size': 500 * 1024 * 1024,
                    'items': [
                        {'path': 'C:\\Temp\\file1.tmp', 'size': 1024},
                        {'path': 'C:\\Temp\\file2.tmp', 'size': 2048},
                    ]
                },
                'cache': {
                    'count': 1500,
                    'size': 1.5 * 1024 * 1024 * 1024,
                    'items': []
                }
            }
        }
        
        # Get AI recommendations
        recommendations = self.ai_manager.get_cleaning_recommendations(scan_results)
        self.assertGreater(len(recommendations), 0)
        
        # Explain items
        for category_data in scan_results['categories'].values():
            for item in category_data.get('items', []):
                explanation = self.ai_manager.explain_cleaning_item(item)
                self.assertIsNotNone(explanation)
                self.assertIn('safety_level', explanation)
        
        # Analyze performance impact
        metrics = {'cpu_percent': 60, 'memory_percent': 70}
        analysis = self.ai_manager.analyze_system_performance(metrics)
        self.assertIn('status', analysis)


def run_async_test(test_func):
    """Helper to run async tests"""
    def wrapper(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_func(self))
        finally:
            loop.close()
    return wrapper


# Apply async wrapper to async test methods
for attr_name in dir(TestAIManager):
    attr = getattr(TestAIManager, attr_name)
    if callable(attr) and attr_name.startswith('test_') and asyncio.iscoroutinefunction(attr):
        setattr(TestAIManager, attr_name, run_async_test(attr))

for attr_name in dir(TestAIIntegration):
    attr = getattr(TestAIIntegration, attr_name)
    if callable(attr) and attr_name.startswith('test_') and asyncio.iscoroutinefunction(attr):
        setattr(TestAIIntegration, attr_name, run_async_test(attr))


if __name__ == '__main__':
    unittest.main()