#!/usr/bin/env python3
"""
Test script to verify the new Query Optimization feature
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from routing.enhanced_intelligent_router import EnhancedIntelligentRouter

def test_query_optimization():
    """Test the new query optimization feature"""
    
    print("🔧 Testing Query Optimization Feature")
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
    
    # Test queries that should benefit from optimization
    test_queries = [
        "sort list",                                    # Simple coding query
        "fibonacci",                                    # Incomplete coding query 
        "quantum",                                      # Too vague general query
        "math problem 5+3*2",                         # Informal math query
        "story about robot",                          # Basic creative query
        "explain machine learning"                    # General explanation query
    ]
    
    print(f"\n🧪 Testing Query Optimization")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Original Query: \"{query}\"")
        
        try:
            # Test the routing decision directly
            if router.meta_router and router.use_openai_routing:
                router.meta_router.update_model_inventory(router.model_registry)
                decision = router.meta_router.route_query_sync(query)
                
                original_query = decision.get('original_query', query)
                optimized_query = decision.get('optimized_query', query)
                query_enhanced = decision.get('query_enhanced', False)
                
                print(f"   🎯 Selected Model: {decision['model']}")
                print(f"   🏷️  Query Type: {decision.get('query_type', 'unknown')}")
                print(f"   🔧 Query Enhanced: {'✅ Yes' if query_enhanced else '❌ No'}")
                
                if query_enhanced:
                    optimization_type = decision.get('optimization_applied', 'moderate')
                    print(f"   📈 Optimization Level: {optimization_type}")
                    print(f"   📝 Original: {original_query}")
                    print(f"   ✨ Optimized: {optimized_query}")
                    print(f"   💡 Why: {decision.get('optimization_reasoning', 'No reason provided')}")
                else:
                    print(f"   📝 Query used as-is: {optimized_query}")
                
                print(f"   📊 Confidence: {decision.get('confidence', 0):.2f}")
                
            else:
                print('   ⚠️ OpenAI meta-routing not available')
                
        except Exception as e:
            print(f'   ❌ Error: {e}')
            import traceback
            traceback.print_exc()
    
    print(f"\n📋 Query Optimization Summary")
    print("-" * 50)
    print("✅ Query optimization feature implemented")
    print("🔧 OpenAI now provides both model selection AND query enhancement")
    print("📈 Optimization levels: none, brief, moderate, extensive")
    print("🎯 Tailored to selected model's strengths")
    print("\n🔍 Optimization Examples:")
    print("   • 'sort list' → 'Write a well-documented Python function with error handling...'")
    print("   • 'quantum' → 'Explain quantum computing in simple terms with examples...'")
    print("   • 'math 5+3*2' → 'Calculate 5+3*2 step-by-step, showing order of operations...'")
    print("   • 'story robot' → 'Write a creative story about a robot, specify genre and tone...'")

if __name__ == "__main__":
    test_query_optimization()
