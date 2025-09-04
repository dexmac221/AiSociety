#!/usr/bin/env python3
"""
Simple test to verify OpenAI API calls are working directly.
"""

import os
import asyncio
import logging
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from routing.openai_meta_router import OpenAIMetaRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_direct_openai_call():
    """Test direct OpenAI meta-router call."""
    
    print("🧪 Testing Direct OpenAI API Integration")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Initialize OpenAI meta-router
    meta_router = OpenAIMetaRouter(
        api_key=api_key,
        model="gpt-4.1-mini",
        cache_decisions=False  # Disable cache for testing
    )
    
    # Set up some dummy models
    meta_router.local_models = {
        'qwen2.5-coder:7b': {
            'specializations': ['coding', 'programming', 'debugging'],
            'local': True,
            'performance_score': 85
        },
        'llama3.1:8b': {
            'specializations': ['general', 'reasoning', 'conversation'],
            'local': True,
            'performance_score': 80
        }
    }
    
    # Test query
    test_query = "Write a Python function to calculate fibonacci numbers"
    print(f"\n🔍 Testing query: {test_query}")
    
    try:
        # Make direct OpenAI API call
        result = await meta_router.route_query(test_query)
        
        print("✅ OpenAI API call successful!")
        print(f"🤖 Recommended model: {result.get('model', 'unknown')}")
        print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
        print(f"🎯 Confidence: {result.get('confidence', 0)}")
        print(f"📊 Query type: {result.get('query_type', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    success = asyncio.run(test_direct_openai_call())
    
    if success:
        print("\n🎉 OpenAI integration is working correctly!")
    else:
        print("\n❌ OpenAI integration test failed")

if __name__ == "__main__":
    main()
