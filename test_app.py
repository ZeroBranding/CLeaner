#!/usr/bin/env python3
"""
🧪 Test Script for Holographic AI System Monitor
Comprehensive testing of all components
"""

import sys
import asyncio
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / "src"))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        # Core imports
        from src.core.system_monitor import SystemMonitor, SystemStats
        from src.core.database import DatabaseManager
        print("✅ Core modules")
        
        # AI imports
        from src.ai.ai_manager import AIManager, AIProvider
        print("✅ AI modules")
        
        # UI imports (may fail without display)
        try:
            from PyQt6.QtWidgets import QApplication
            from src.ui.main_window import HolographicMainWindow
            print("✅ UI modules")
        except Exception as e:
            print(f"⚠️  UI modules (expected if no display): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_monitor():
    """Test system monitoring functionality"""
    print("\n🔧 Testing system monitor...")
    
    try:
        from src.core.system_monitor import SystemMonitor
        
        monitor = SystemMonitor()
        
        # Test system info
        info = monitor.get_system_info()
        print(f"✅ System info: {info['platform']}")
        print(f"   CPU: {info['processor']}")
        print(f"   Memory: {info['total_memory']}")
        print(f"   GPU: {info['gpu_info']}")
        
        # Test stats collection
        stats = monitor._collect_system_stats()
        print(f"✅ Stats collection:")
        print(f"   CPU: {stats.cpu_percent:.1f}%")
        print(f"   Memory: {stats.memory_percent:.1f}%")
        print(f"   GPU: {stats.gpu_percent or 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ System monitor test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n💾 Testing database...")
    
    try:
        from src.core.database import DatabaseManager
        
        db = DatabaseManager("test_holographic.db")
        
        # Test preferences
        db.store_preference("test_key", "test_value")
        value = db.get_preference("test_key")
        assert value == "test_value"
        print("✅ Preferences storage")
        
        # Test API key encryption
        db.store_api_key("test_provider", "test_api_key_12345")
        retrieved_key = db.get_api_key("test_provider")
        assert retrieved_key == "test_api_key_12345"
        print("✅ API key encryption")
        
        # Test conversation storage
        db.store_conversation(
            session_id="test_session",
            user_message="Test message",
            ai_response="Test response",
            ai_provider="test_provider",
            tokens_used=100,
            response_time=1.5
        )
        
        history = db.get_conversation_history("test_session")
        assert len(history) == 1
        print("✅ Conversation storage")
        
        db.close()
        
        # Clean up test database
        Path("test_holographic.db").unlink(missing_ok=True)
        Path(".encryption_key").unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_manager():
    """Test AI manager (without actual API calls)"""
    print("\n🤖 Testing AI manager...")
    
    try:
        from src.ai.ai_manager import AIManager, AIProvider
        
        ai_manager = AIManager()
        
        # Test provider configuration
        configs = ai_manager.provider_configs
        print(f"✅ Provider configs: {len(configs)} providers")
        
        for provider, config in configs.items():
            print(f"   {config.name}: Quality {config.quality_score}/100")
        
        # Test provider selection
        try:
            best_provider = ai_manager.select_best_provider("test prompt", "quality")
            print(f"✅ Provider selection: {best_provider.value}")
        except:
            print("⚠️  No healthy providers (expected without API keys)")
        
        # Test status
        status = ai_manager.get_provider_status()
        print(f"✅ Provider status: {len(status)} providers tracked")
        
        return True
        
    except Exception as e:
        print(f"❌ AI manager test failed: {e}")
        return False

def test_opengl_support():
    """Test OpenGL support for holographic effects"""
    print("\n🎮 Testing OpenGL support...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtOpenGL import QOpenGLWidget
        import OpenGL.GL as gl
        
        # Create minimal QApplication for OpenGL context
        app = QApplication([])
        
        # Test OpenGL widget creation
        widget = QOpenGLWidget()
        widget.show()
        
        # Process events to initialize OpenGL
        app.processEvents()
        
        print("✅ OpenGL context created")
        
        # Test OpenGL version
        try:
            widget.makeCurrent()
            version = gl.glGetString(gl.GL_VERSION)
            renderer = gl.glGetString(gl.GL_RENDERER)
            print(f"✅ OpenGL Version: {version.decode() if version else 'Unknown'}")
            print(f"   Renderer: {renderer.decode() if renderer else 'Unknown'}")
        except:
            print("⚠️  OpenGL version check failed")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"⚠️  OpenGL test failed (expected without display): {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Holographic AI System Monitor Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("System Monitor", test_system_monitor),
        ("Database", test_database),
        ("AI Manager", test_ai_manager),
        ("OpenGL Support", test_opengl_support)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Ready to launch the application.")
        print("   Run: python main.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        print("   Try running: python setup.py")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())