#!/usr/bin/env python3
"""
Test script to verify OpenAI integration is working properly.
"""

import os
import sys
import asyncio
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from routing.enhanced_intelligent_router import EnhancedIntelligentRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openai_integration():
    """Test OpenAI integration with actual API calls."""
    
    print("🧪 Testing OpenAI Integration")
    print("=" * 50)
    
    # Initialize the enhanced router
    try:
        router = EnhancedIntelligentRouter()
        print("✅ Enhanced router initialized")
        
        # Test if OpenAI meta-routing is enabled
        if router.use_openai_routing and router.meta_router:
            print("✅ OpenAI meta-routing is enabled")
            print(f"🤖 Using model: {router.meta_router.model}")
            
            # Test query to see if we get real OpenAI API call
            test_query = "Write a Python function to calculate fibonacci numbers"
            print(f"\n🔍 Testing query: {test_query}")
            
            # This should trigger a real OpenAI API call
            result = router.query_model(test_query)
            
            print(f"✅ Query completed!")
            print(f"🤖 Selected model: {result.get('model', 'unknown')}")
            print(f"🎯 Routing method: {result.get('routing_method', 'unknown')}")
            print(f"⏱️  Response time: {result.get('response_time_ms', 0)}ms")
            
            if 'routing_reasoning' in result:
                print(f"💭 OpenAI reasoning: {result['routing_reasoning']}")
            
            if 'meta_model' in result:
                print(f"🧠 Meta model used: {result['meta_model']}")
                
        else:
            print("❌ OpenAI meta-routing is not enabled")
            if not router.use_openai_routing:
                print("   - OpenAI routing flag is False")
            if not router.meta_router:
                print("   - Meta router is None")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Run the async test
    asyncio.run(test_openai_integration())

if __name__ == "__main__":
    main()
