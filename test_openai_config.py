#!/usr/bin/env python3
"""
Test script to debug OpenAI configuration loading
"""

import json
import os
import sys

# Add src to path
sys.path.append('src')

def test_config_loading():
    """Test configuration loading"""
    
    print("🔍 Testing configuration loading...")
    
    # Test 1: Read config file directly
    config_path = "config/router_config.json"
    print(f"\n1️⃣ Reading config from: {config_path}")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"   ✅ Config loaded successfully")
        print(f"   📋 Config keys: {list(config.keys())}")
        
        openai_config = config.get('openai_meta_routing', {})
        print(f"   🤖 OpenAI section found: {'Yes' if openai_config else 'No'}")
        
        if openai_config:
            print(f"   🔧 Enabled: {openai_config.get('enabled', False)}")
            print(f"   🤖 Model: {openai_config.get('model', 'Not set')}")
            print(f"   🔑 API key: {'Set' if openai_config.get('api_key') else 'Null'}")
    else:
        print(f"   ❌ Config file not found: {config_path}")
    
    # Test 2: Test router loading
    print(f"\n2️⃣ Testing router configuration loading...")
    
    try:
        from routing.intelligent_router import IntelligentModelRouter
        
        # Create router instance
        router = IntelligentModelRouter()
        
        print(f"   ✅ Router created successfully")
        print(f"   📋 Router config keys: {list(router.config.keys())}")
        
        router_openai = router.config.get('openai_meta_routing', {})
        print(f"   🤖 Router OpenAI section: {'Found' if router_openai else 'Empty'}")
        
        if router_openai:
            print(f"   🔧 Router enabled: {router_openai.get('enabled', False)}")
            print(f"   🤖 Router model: {router_openai.get('model', 'Not set')}")
        
    except Exception as e:
        print(f"   ❌ Router loading failed: {e}")
    
    # Test 3: Test enhanced router loading
    print(f"\n3️⃣ Testing enhanced router configuration loading...")
    
    try:
        from routing.enhanced_intelligent_router import EnhancedIntelligentRouter
        
        # Create enhanced router instance
        enhanced_router = EnhancedIntelligentRouter()
        
        print(f"   ✅ Enhanced router created successfully")
        print(f"   📋 Enhanced router config keys: {list(enhanced_router.config.keys())}")
        
        enhanced_openai = enhanced_router.config.get('openai_meta_routing', {})
        print(f"   🤖 Enhanced router OpenAI section: {'Found' if enhanced_openai else 'Empty'}")
        
        if enhanced_openai:
            print(f"   🔧 Enhanced enabled: {enhanced_openai.get('enabled', False)}")
            print(f"   🤖 Enhanced model: {enhanced_openai.get('model', 'Not set')}")
            print(f"   🚀 Meta-router active: {getattr(enhanced_router, 'use_openai_routing', False)}")
        
    except Exception as e:
        print(f"   ❌ Enhanced router loading failed: {e}")
    
    # Test 4: Environment variables
    print(f"\n4️⃣ Testing environment variables...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"   🔑 OPENAI_API_KEY: {'Set' if api_key else 'Not set'}")
    
    if api_key:
        print(f"   📏 Key length: {len(api_key)} characters")
        print(f"   🔢 Key preview: {api_key[:8]}...")

if __name__ == "__main__":
    test_config_loading()
