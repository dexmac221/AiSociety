#!/usr/bin/env python3
"""
Simple OpenAI Translation Test

Basic test script for validating OpenAI language detection and translation
functionality. Used for debugging translation issues and API connectivity.

Author: AI Society Contributors
License: MIT
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/api_config.env')

# Add the src directory to the Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from routing.openai_meta_router import OpenAIMetaRouter

async def test_simple_translation():
    """Test basic translation functionality"""
    
    print("🧪 Testing OpenAI Language Detection")
    print("=" * 50)
    
    # Create router
    router = OpenAIMetaRouter()
    
    print(f"🔑 OpenAI client initialized: {router.client is not None}")
    print(f"🔑 API key present: {router.api_key is not None}")
    print(f"🤖 Model: {router.model}")
    
    # Test simple Spanish query
    test_query = "¿Cómo estás?"
    print(f"\n📝 Testing query: {test_query}")
    
    try:
        result = await router.detect_and_translate_query(test_query)
        print(f"✅ Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_translation())
