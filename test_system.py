#!/usr/bin/env python3
"""
AI Society System Test Suite

Comprehensive test script for validating all core system components and
functionality. Tests imports, configuration, model discovery, routing,
and basic system integration.

Features:
- Module import testing
- Configuration validation
- Model discovery verification
- Routing system testing
- Database connectivity testing
- Basic integration validation

Author: AI Society Contributors
License: MIT
"""

import sys
import os
import json

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from daemon.model_discovery import OllamaLibraryScanner, ModelDiscoveryDaemon
        print("✅ Model discovery modules imported successfully")
    except Exception as e:
        print(f"❌ Failed to import model discovery: {e}")
        return False
    
    try:
        from routing.intelligent_router import IntelligentModelRouter
        print("✅ Intelligent router imported successfully")
    except Exception as e:
        print(f"❌ Failed to import intelligent router: {e}")
        return False
    
    return True

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🔌 Testing Ollama connection...")
    
    try:
        import ollama
        models = ollama.list()
        model_count = len(models['models'])
        print(f"✅ Ollama connected - {model_count} models available")
        
        # List first few models
        if model_count > 0:
            print("📋 Available models:")
            for i, model in enumerate(models['models'][:3]):  # Show first 3
                print(f"   - {model['name']}")
            if model_count > 3:
                print(f"   ... and {model_count - 3} more")
        
        return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_model_discovery():
    """Test model discovery system"""
    print("\n🔍 Testing model discovery...")
    
    try:
        from daemon.model_discovery import OllamaLibraryScanner
        scanner = OllamaLibraryScanner()
        models = scanner.fetch_library_models()
        print(f"✅ Model discovery working - found {len(models)} models in library")
        
        # Show some model info
        if models:
            print("📊 Sample discovered models:")
            for model in models[:3]:  # Show first 3
                specializations = ', '.join(model.get('specializations', []))
                print(f"   - {model['name']}: {specializations}")
        
        return True
    except Exception as e:
        print(f"❌ Model discovery failed: {e}")
        return False

def test_router():
    """Test intelligent router"""
    print("\n🎯 Testing intelligent router...")
    
    try:
        from routing.intelligent_router import IntelligentModelRouter
        router = IntelligentModelRouter()
        
        # Test model selection (without actual query)
        test_query = "Write a Python function"
        selected_model = router.select_model(test_query)
        print(f"✅ Router working - selected '{selected_model}' for coding query")
        
        # Show some stats
        stats = router.get_stats()
        print(f"📈 Router stats: {stats['total_models_available']} total, {stats['local_models']} local")
        
        return True
    except Exception as e:
        print(f"❌ Router test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    config_file = "config/router_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✅ Configuration file loaded successfully")
            print(f"   - Max model size: {config.get('max_model_size', 'unknown')}")
            print(f"   - GPU constraints: {config.get('gpu_constraints', {}).get('max_vram_gb', 'unknown')}GB VRAM")
            return True
        except Exception as e:
            print(f"❌ Configuration file error: {e}")
            return False
    else:
        print("❌ Configuration file not found")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Society System Test")
    print("="*40)
    
    tests = [
        test_imports,
        test_configuration,
        test_ollama_connection,
        test_model_discovery,
        test_router
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "="*40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the web interface:")
        print("   ./start.sh")
        print("   or: python web/app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Try running setup first:")
        print("   ./setup.sh")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
