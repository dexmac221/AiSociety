#!/usr/bin/env python3
"""
Routing Debug Tool

Debug script for testing and troubleshooting the routing behavior of AI Society.
Helps diagnose model selection, query optimization, and routing logic issues.

Features:
- Web interface query testing
- Model selection debugging
- Routing logic validation
- Performance troubleshooting
- Configuration verification

Author: AI Society Contributors
License: MIT
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from routing.enhanced_intelligent_router import EnhancedIntelligentRouter

def test_web_interface_queries():
    """Test the exact queries used in the web interface suggestion buttons"""
    
    print("🔍 DEBUG: Testing Web Interface Routing Behavior")
    print("=" * 60)
    
    # Initialize router
    try:
        router = EnhancedIntelligentRouter()
        print(f"✅ Router initialized successfully")
        print(f"🤖 OpenAI meta-routing enabled: {router.use_openai_routing}")
        
        if router.meta_router:
            print(f"🧠 Meta-router model: {router.meta_router.model}")
        
    except Exception as e:
        print(f"❌ Failed to initialize router: {e}")
        return
    
    # The exact queries from the web interface suggestion buttons
    web_queries = [
        "Write a Python function to sort a list",      # Coding Help button
        "Explain quantum computing simply",            # Complex Topics button  
        "What is 15 * 23 + 89?",                      # Math Problems button
        "Tell me a creative story"                     # Creative Writing button
    ]
    
    # Test multiple times to check for consistency
    for round_num in range(1, 4):  # Test 3 rounds
        print(f"\n🔄 ROUND {round_num} - Testing Routing Consistency")
        print("-" * 50)
        
        for i, query in enumerate(web_queries, 1):
            print(f"\n{round_num}.{i} Query: \"{query}\"")
            
            try:
                # Simulate exactly what the web interface does
                result = router.query_model(query, model_name=None, context=None)
                
                print(f"   🎯 Selected Model: {result['model']}")
                print(f"   ⏱️  Response Time: {result.get('response_time_ms', 'N/A')}ms")
                print(f"   🔀 Routing Method: {result.get('routing_method', 'unknown')}")
                
                if 'routing_reasoning' in result:
                    reasoning = result['routing_reasoning'][:100] + "..." if len(result['routing_reasoning']) > 100 else result['routing_reasoning']
                    print(f"   💭 Reasoning: {reasoning}")
                
                if 'query_type_detected' in result:
                    print(f"   🏷️  Query Type: {result['query_type_detected']}")
                
                if 'routing_confidence' in result:
                    print(f"   📊 Confidence: {result['routing_confidence']:.2f}")
                
            except Exception as e:
                print(f"   ❌ Error processing query: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n⏳ Waiting before next round...")
        import time
        time.sleep(2)  # Wait 2 seconds between rounds
    
    # Test cache behavior
    print(f"\n🗄️  CACHE TEST - Same Query Multiple Times")
    print("-" * 50)
    
    test_query = "Write a Python function to sort a list"
    for i in range(1, 4):
        print(f"\n🔄 Cache Test {i}: \"{test_query}\"")
        
        try:
            start_time = time.time()
            result = router.query_model(test_query, model_name=None, context=None)
            end_time = time.time()
            
            print(f"   🎯 Model: {result['model']}")
            print(f"   ⏱️  Processing Time: {(end_time - start_time) * 1000:.1f}ms")
            print(f"   🔀 Method: {result.get('routing_method', 'unknown')}")
            
            # Check if this was cached
            if hasattr(router.meta_router, 'routing_cache'):
                cached_entries = len(router.meta_router.routing_cache)
                print(f"   🗄️  Cache Entries: {cached_entries}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 SUMMARY")
    print("-" * 50)
    print(f"✅ Test completed")
    
    if router.meta_router:
        stats = router.meta_router.get_routing_stats()
        print(f"📈 Routing Stats:")
        for key, value in stats.items():
            print(f"   • {key}: {value}")

if __name__ == "__main__":
    test_web_interface_queries()
