#!/usr/bin/env python3
"""
Multilingual Translation System Test

Test script for validating the multilingual capabilities of AI Society.
Tests language detection, translation, and response language instructions
across multiple languages including Spanish, French, German, Italian,
Portuguese, Japanese, and Chinese.

Author: AI Society Contributors
License: MIT
"""

import asyncio
import json
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from routing.openai_meta_router import OpenAIMetaRouter

async def test_multilingual_routing():
    """Test the multilingual routing with various languages"""
    
    # Create router instance
    router = OpenAIMetaRouter()
    
    # Test queries in different languages
    test_queries = [
        # Spanish
        "¿Cómo puedo crear una función en Python que calcule números fibonacci?",
        
        # French  
        "Comment puis-je optimiser les performances de mon code JavaScript?",
        
        # German
        "Wie kann ich eine REST API mit FastAPI erstellen?",
        
        # Italian
        "Come posso risolvere questo problema di matematica: calcolare l'integrale di x²?",
        
        # Portuguese
        "Qual é a melhor maneira de aprender algoritmos de machine learning?",
        
        # English (should not be translated)
        "Write a Python function to sort a list of numbers",
        
        # Japanese
        "Pythonでデータ分析をするための最良の方法は何ですか？",
        
        # Chinese
        "如何用Python创建一个简单的web应用程序？"
    ]
    
    print("🌍 Testing Multilingual Translation System")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            # Test translation detection
            translation_result = await router.detect_and_translate_query(query)
            
            print(f"🔍 Detected language: {translation_result.get('detected_language', 'unknown')}")
            print(f"🌐 Translation needed: {translation_result.get('translated', False)}")
            
            if translation_result.get('translated'):
                print(f"📖 Original: {query}")
                print(f"🔄 Translated: {translation_result.get('translated_query', 'N/A')}")
                print(f"💬 Response instruction: {translation_result.get('language_instruction', 'N/A')}")
            else:
                print("✅ No translation needed - query in English")
                
            # Test full routing if OpenAI is available
            if router.client and router.api_key:
                print("\n🤖 Testing full routing...")
                routing_result = await router._route_with_openai(query)
                
                print(f"🎯 Recommended model: {routing_result.get('model')}")
                print(f"🔧 Query optimized: {routing_result.get('query_enhanced', False)}")
                print(f"🌍 Multilingual enhanced: {routing_result.get('multilingual_enhanced', False)}")
                
                if routing_result.get('translation'):
                    trans_info = routing_result['translation']
                    print(f"📋 Translation info: {trans_info.get('detected_language', 'N/A')} → English")
            else:
                print("⚠️ OpenAI not configured - skipping full routing test")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()

    print("🎉 Multilingual testing complete!")

if __name__ == "__main__":
    asyncio.run(test_multilingual_routing())
