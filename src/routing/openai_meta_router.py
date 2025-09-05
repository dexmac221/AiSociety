#!/usr/bin/env python3
"""
OpenAI Meta-Router for AI Society

This module implements a sophisticated routing system that uses OpenAI's GPT models
as a meta-router to analyze queries and select the optimal local open-source model
for response generation. This hybrid approach combines the superior query understanding
of large commercial models with the privacy and cost benefits of local inference.

Features:
- Dynamic prompt generation with current model inventory
- Sophisticated query analysis and intent detection
- Model capability matching and recommendation
- Fallback to local-only routing when needed
- Cost optimization through intelligent API usage

Author: AI Society Contributors
License: MIT
"""

import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime

try:
    from openai import AsyncOpenAI
    openai_available = True
except ImportError:
    AsyncOpenAI = None
    openai_available = False

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIMetaRouter:
    """
    Advanced meta-router using OpenAI models for intelligent model selection.
    
    This class uses OpenAI's GPT models to analyze user queries and recommend
    the most appropriate local model for response generation. It creates dynamic
    prompts that include current model inventory and capabilities.
    
    Attributes:
        api_key (str): OpenAI API key
        model (str): OpenAI model to use for routing decisions
        local_models (Dict): Available local models and their capabilities
        routing_cache (Dict): Cache of recent routing decisions
        fallback_router: Local router for fallback scenarios
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gpt-4.1-mini",
        cache_decisions: bool = True,
        fallback_router = None
    ):
        """
        Initialize the OpenAI Meta-Router.
        
        Args:
            api_key (Optional[str]): OpenAI API key (can also use env var)
            model (str): OpenAI model for routing decisions
            cache_decisions (bool): Whether to cache routing decisions
            fallback_router: Local router for fallback scenarios
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # Skip placeholder API keys
        if self.api_key and (
            self.api_key.startswith('your_') or 
            self.api_key == 'your_openai_api_key_here'
        ):
            self.api_key = None
            
        self.model = model
        self.cache_decisions = cache_decisions
        self.fallback_router = fallback_router
        self.routing_cache: Dict[str, Dict] = {}
        self.local_models: Dict[str, Dict] = {}
        
        # Initialize OpenAI client
        if openai_available and self.api_key:
            # Create client without any organization parameters to avoid conflicts
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"🤖 OpenAI Meta-Router initialized with {model}")
        else:
            self.client = None
            logger.warning("⚠️ OpenAI not available, will use fallback routing only")
    
    async def detect_and_translate_query(self, query: str) -> Dict[str, Any]:
        """
        Detect the language of the query and translate to English if needed.
        
        This enhances model performance since most local models are optimized for English.
        The system will instruct the final model to respond in the original language.
        
        Args:
            query (str): User's input query in any language
            
        Returns:
            Dict[str, Any]: Contains detected language, English translation, and instructions
        """
        if not self.client:
            return {
                "original_language": "unknown",
                "detected_language_name": "Unknown",
                "english_query": query,
                "translation_applied": False,
                "response_instruction": "",
                "translation_confidence": 0.0
            }
        
        translation_prompt = f"""You are a language detection and translation expert. Analyze this query:

"{query}"

Your tasks:
1. Detect the language of this query
2. If it's not English, translate it to clear, natural English
3. Provide instructions for responding in the original language

Respond with JSON only:
{{
    "original_language": "language-code (e.g., 'es', 'fr', 'de', 'zh', 'ja', 'en')",
    "detected_language_name": "Full language name (e.g., 'Spanish', 'French', 'German')",
    "english_query": "Natural English translation (or original if already English)",
    "translation_applied": true/false,
    "response_instruction": "Instruction for final response language (e.g., 'Respond in Spanish', or '' if English)",
    "translation_confidence": 0.95
}}

Rules:
- If the query is already in English, keep it unchanged and set translation_applied to false
- For non-English queries, provide natural, clear English translation
- Preserve the original meaning and intent exactly
- Create appropriate response instructions for the target language
- Be confident in language detection (aim for 0.9+ confidence)"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": translation_prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
                
            translation_result = json.loads(content)
            
            logger.info(f"🌍 Language detection: {translation_result.get('detected_language_name', 'Unknown')} "
                       f"({translation_result.get('original_language', 'unknown')})")
            
            if translation_result.get('translation_applied', False):
                logger.info(f"🔄 Translation: '{query}' → '{translation_result.get('english_query', query)}'")
            
            return translation_result
            
        except Exception as e:
            logger.error(f"❌ Translation error: {e}")
            # Fallback to original query
            return {
                "original_language": "unknown",
                "detected_language_name": "Unknown", 
                "english_query": query,
                "translation_applied": False,
                "response_instruction": "",
                "translation_confidence": 0.0
            }

    def update_model_inventory(self, models: Dict[str, Dict]) -> None:
        """
        Update the current inventory of available local models.
        
        Args:
            models (Dict[str, Dict]): Dictionary of available models with metadata
        """
        self.local_models = models
        logger.info(f"📊 Updated model inventory: {len(models)} models available")
    
    def generate_routing_prompt(self, query: str, language_instruction: str = None) -> str:
        """
        Generate a dynamic prompt for OpenAI model selection and query optimization.
        
        Creates a comprehensive prompt that includes the current model inventory,
        their capabilities, and asks the OpenAI model to both select the best option
        AND optimize the user's query for better results.
        
        Args:
            query (str): User's input query
            language_instruction (str, optional): Instruction for response language
            
        Returns:
            str: Complete prompt for OpenAI model
        """
        
        # Create model inventory description
        model_descriptions = []
        for model_name, model_info in self.local_models.items():
            specs = ", ".join(model_info.get('specializations', []))
            size = model_info.get('size', 'Unknown')
            local = "✅ Local" if model_info.get('local', False) else "📥 Download needed"
            score = model_info.get('performance_score', 0)
            
            model_descriptions.append(
                f"• **{model_name}** ({size})\n"
                f"  - Specializations: {specs}\n"
                f"  - Performance Score: {score}/100\n"
                f"  - Availability: {local}\n"
                f"  - Description: {model_info.get('description', 'General purpose model')}"
            )
        
        models_text = "\n\n".join(model_descriptions)
        
        # Add language instruction if translation was detected
        language_instruction_text = ""
        if language_instruction:
            language_instruction_text = f"\n\n## IMPORTANT - Response Language Instruction:\n{language_instruction}\n"
        
        prompt = f"""You are an expert AI model router AND query optimizer for a local LLM system. Your job is to:
1. Analyze user queries and recommend the BEST local model
2. Optimize the query to get maximum performance from the selected model

## Available Local Models:
{models_text}

## Original User Query:
"{query}"{language_instruction_text}

## Your Dual Task:
1. **Model Selection**: Choose the optimal model for this query
2. **Query Optimization**: Enhance/rephrase the query to get better results from the selected model

## Your Response Format (JSON only):
{{
    "recommended_model": "exact-model-name",
    "confidence": 0.95,
    "reasoning": "Why this model is best for this query",
    "query_type": "coding|math|creative|reasoning|general|conversation",
    "complexity": "simple|moderate|complex",
    "specializations_needed": ["spec1", "spec2"],
    "alternative_models": ["backup-model-1", "backup-model-2"],
    "expected_performance": "excellent|good|fair",
    "download_recommendation": true,
    "optimized_query": "Enhanced version of the user's query optimized for the selected model",
    "optimization_applied": "brief|moderate|extensive|none",
    "optimization_reasoning": "Explanation of how and why the query was optimized"
}}

## Model Selection Criteria (Priority Order):
1. **Specialization Match**: Choose models with specializations matching the query type
2. **Local Availability**: Prefer locally available models (✅ Local) over download needed
3. **Performance Score**: Higher scores indicate better recent performance
4. **Model Size**: Consider complexity vs resource efficiency
5. **Task Complexity**: Match model capability to query complexity

## Query Optimization Guidelines:
- **Coding Queries**: Add context, specify language, include expected output format
- **Math Queries**: Clarify what type of solution is needed, add step-by-step requests
- **Creative Queries**: Add style preferences, length requirements, tone specifications  
- **General Queries**: Add context for better understanding, specify desired detail level
- **Complex Queries**: Break down into clear sub-components, add examples if helpful

## Query Types & Optimization Examples:
- **Coding**: "Write Python function" → "Write a well-documented Python function with error handling that..."
- **Math**: "Calculate X" → "Calculate X step-by-step, showing all work and explaining each step"
- **Creative**: "Write story" → "Write a [genre] story of [length] with [tone] about [specific topic]"
- **General**: "Explain X" → "Explain X in simple terms with examples, suitable for [audience level]"

## Optimization Rules:
- Keep the core intent unchanged
- Add helpful context and specificity
- Don't over-complicate simple queries
- Enhance clarity and reduce ambiguity
- Tailor to the selected model's strengths

Analyze the query, select the best model, optimize the query, and respond with JSON only:"""

        return prompt
    
    async def route_query(self, query: str) -> Dict[str, Any]:
        """
        Use OpenAI model to analyze query and recommend local model.
        
        Args:
            query (str): User's input query
            
        Returns:
            Dict[str, Any]: Routing decision with model recommendation
        """
        
        # Check cache first
        if self.cache_decisions and query in self.routing_cache:
            cached = self.routing_cache[query]
            if time.time() - cached['timestamp'] < 3600:  # 1 hour cache
                logger.info("🎯 Using cached routing decision")
                return cached['decision']
        
        # Try OpenAI routing first
        if self.client and self.api_key:
            try:
                return await self._route_with_openai(query)
            except Exception as e:
                logger.warning(f"⚠️ OpenAI routing failed: {e}")
        
        # Fallback to local routing
        if self.fallback_router:
            logger.info("🔄 Falling back to local routing")
            return self.fallback_router.route_query(query)
        
        # Basic fallback
        return self._basic_fallback_routing(query)
    
    def route_query_sync(self, query: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for route_query to avoid async/await issues.
        
        Args:
            query (str): User's input query
            
        Returns:
            Dict[str, Any]: Routing decision with model recommendation
        """
        
        # Check cache first
        if self.cache_decisions and query in self.routing_cache:
            cached = self.routing_cache[query]
            if time.time() - cached['timestamp'] < 3600:  # 1 hour cache
                logger.info("🎯 Using cached routing decision")
                return cached['decision']
        
        # Try OpenAI routing first
        if self.client and self.api_key:
            try:
                import asyncio
                import threading
                
                # Handle event loop properly for different contexts
                try:
                    # Check if we're in an async context
                    loop = asyncio.get_running_loop()
                    
                    # We're in an async context (like FastAPI), run in thread
                    logger.info("🔄 Running OpenAI call in thread to avoid async context issues")
                    
                    result_container = {"result": None, "error": None}
                    
                    def run_openai_in_thread():
                        """Run OpenAI call in a separate thread with its own event loop"""
                        try:
                            # Create new event loop for this thread
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                result = new_loop.run_until_complete(self._route_with_openai(query))
                                result_container["result"] = result
                            finally:
                                new_loop.close()
                        except Exception as e:
                            result_container["error"] = e
                    
                    # Run in thread and wait for completion
                    thread = threading.Thread(target=run_openai_in_thread)
                    thread.start()
                    thread.join(timeout=30)  # 30 second timeout
                    
                    if result_container["result"]:
                        logger.info("🤖 Successfully got OpenAI routing decision via thread")
                        return result_container["result"]
                    elif result_container["error"]:
                        logger.warning(f"⚠️ OpenAI routing failed in thread: {result_container['error']}")
                    else:
                        logger.warning("⚠️ OpenAI routing timed out")
                        
                except RuntimeError:
                    # No event loop running, safe to create one directly
                    logger.info("🔄 No event loop found, creating one for OpenAI call")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(self._route_with_openai(query))
                        logger.info("🤖 Successfully got OpenAI routing decision")
                        return result
                    finally:
                        loop.close()
                        asyncio.set_event_loop(None)
                        
            except Exception as e:
                logger.warning(f"⚠️ OpenAI routing failed: {e}")
        
        # Fallback to local routing
        if self.fallback_router:
            logger.info("🔄 Falling back to local routing")
            return self.fallback_router.route_query(query)
        
        # Final fallback
        return self._basic_fallback_routing(query)
    
    async def _route_with_openai(self, query: str) -> Dict[str, Any]:
        """
        Perform routing using OpenAI API with multilingual support.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: OpenAI routing recommendation with translation details
        """
        
        # Check if translation is needed
        translation_result = await self.detect_and_translate_query(query)
        
        # Use translated query for routing if translation was applied
        routing_query = translation_result.get('translated_query', query)
        language_instruction = translation_result.get('language_instruction')
        
        # Generate prompt with language instruction if needed
        prompt = self.generate_routing_prompt(routing_query, language_instruction)
        
        logger.info(f"🤖 Sending routing request to {self.model}")
        if translation_result.get('translated'):
            logger.info(f"🌍 Using translated query for better model performance")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert AI model router. Respond only with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent routing
                max_tokens=500,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            routing_decision = json.loads(response.choices[0].message.content)
            
            # Validate the decision and include translation information
            validated_decision = self._validate_routing_decision(routing_decision, query, translation_result)
            
            # Cache the decision
            if self.cache_decisions:
                self.routing_cache[query] = {
                    'decision': validated_decision,
                    'timestamp': time.time()
                }
            
            logger.info(f"✅ OpenAI recommended: {validated_decision['model']}")
            return validated_decision
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON response from OpenAI: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            raise
    
    def _validate_routing_decision(self, decision: Dict, query: str, translation_result: Dict = None) -> Dict[str, Any]:
        """
        Validate and enhance the routing decision from OpenAI.
        
        Args:
            decision (Dict): Raw decision from OpenAI
            query (str): Original user query
            translation_result (Dict, optional): Translation details if applied
            
        Returns:
            Dict[str, Any]: Validated and enhanced decision
        """
        
        # Ensure recommended model exists
        recommended = decision.get('recommended_model', '')
        if recommended not in self.local_models:
            # Find closest match
            available_models = list(self.local_models.keys())
            if available_models:
                recommended = available_models[0]  # Fallback to first available
                logger.warning(f"⚠️ Recommended model not found, using {recommended}")
        
        # Get optimized query or fallback to original
        optimized_query = decision.get('optimized_query', query)
        if not optimized_query or optimized_query.strip() == "":
            optimized_query = query
            
        # Create standardized response
        validated = {
            'model': recommended,
            'confidence': min(max(decision.get('confidence', 0.5), 0.0), 1.0),
            'reasoning': decision.get('reasoning', 'OpenAI model recommendation'),
            'query_type': decision.get('query_type', 'general'),
            'complexity': decision.get('complexity', 'moderate'),
            'specializations_used': decision.get('specializations_needed', []),
            'alternatives': decision.get('alternative_models', []),
            'expected_performance': decision.get('expected_performance', 'good'),
            'download_needed': not self.local_models.get(recommended, {}).get('local', False),
            'routing_method': 'openai_meta',
            'meta_model_used': self.model,
            'timestamp': datetime.now().isoformat(),
            # New query optimization fields
            'original_query': query,
            'optimized_query': optimized_query,
            'optimization_applied': decision.get('optimization_applied', 'none'),
            'optimization_reasoning': decision.get('optimization_reasoning', 'No optimization applied'),
            'query_enhanced': optimized_query != query,
            # Translation information
            'translation': translation_result if translation_result else None,
            'multilingual_enhanced': bool(translation_result and translation_result.get('translated'))
        }
        
        # Log optimization info
        if optimized_query != query:
            logger.info(f"🔧 Query optimized: {decision.get('optimization_applied', 'moderate')} enhancement applied")
            logger.info(f"📝 Original: {query[:100]}...")
            logger.info(f"✨ Optimized: {optimized_query[:100]}...")
            
        # Log translation info
        if translation_result and translation_result.get('translated'):
            logger.info(f"🌍 Multilingual support: Query translated from {translation_result.get('detected_language', 'unknown')}")
            logger.info(f"📋 Response instruction: {translation_result.get('language_instruction', 'N/A')}")
        
        return validated
    
    def _basic_fallback_routing(self, query: str) -> Dict[str, Any]:
        """
        Basic fallback routing when OpenAI is not available.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: Basic routing decision
        """
        
        # Simple keyword-based routing
        query_lower = query.lower()
        
        # Try to find a local model
        local_models = [name for name, info in self.local_models.items() 
                       if info.get('local', False)]
        
        if not local_models and self.local_models:
            # No local models, pick highest scored
            best_model = max(self.local_models.keys(), 
                           key=lambda x: self.local_models[x].get('performance_score', 0))
        elif local_models:
            # Pick first local model (could be enhanced)
            best_model = local_models[0]
        else:
            best_model = 'llama3.2:3b'  # Default fallback
        
        return {
            'model': best_model,
            'confidence': 0.6,
            'reasoning': 'Fallback routing - OpenAI not available',
            'query_type': 'general',
            'complexity': 'moderate',
            'specializations_used': ['general'],
            'alternatives': local_models[:2],
            'expected_performance': 'fair',
            'download_needed': not self.local_models.get(best_model, {}).get('local', False),
            'routing_method': 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about routing decisions.
        
        Returns:
            Dict[str, Any]: Routing statistics
        """
        
        total_decisions = len(self.routing_cache)
        openai_decisions = sum(1 for d in self.routing_cache.values() 
                              if d['decision'].get('routing_method') == 'openai_meta')
        
        return {
            'total_routing_decisions': total_decisions,
            'openai_meta_decisions': openai_decisions,
            'fallback_decisions': total_decisions - openai_decisions,
            'cache_hit_rate': f"{(openai_decisions / max(total_decisions, 1)) * 100:.1f}%",
            'available_models': len(self.local_models),
            'local_models': sum(1 for m in self.local_models.values() if m.get('local', False)),
            'meta_model': self.model if self.client and self.api_key else 'Not available'
        }

# Example usage and testing
async def example_usage():
    """Example of how to use the OpenAI Meta-Router."""
    
    # Initialize with local fallback
    from intelligent_router import IntelligentModelRouter
    fallback = IntelligentModelRouter()
    
    # Create meta-router
    meta_router = OpenAIMetaRouter(
        api_key="your-openai-api-key",  # or set OPENAI_API_KEY env var
        fallback_router=fallback
    )
    
    # Update with current model inventory
    models = {
        'qwen2.5-coder:7b': {
            'specializations': ['coding', 'programming'],
            'size': '7B',
            'local': True,
            'performance_score': 95,
            'description': 'Advanced coding model with excellent Python support'
        },
        'llama3.2:3b': {
            'specializations': ['general', 'conversation'],
            'size': '3B', 
            'local': True,
            'performance_score': 88,
            'description': 'Fast general-purpose conversational model'
        },
        'deepseek-coder-v2': {
            'specializations': ['coding', 'debugging', 'reasoning'],
            'size': '16B',
            'local': False,
            'performance_score': 98,
            'description': 'State-of-the-art coding model with advanced reasoning'
        }
    }
    
    meta_router.update_model_inventory(models)
    
    # Test queries
    test_queries = [
        "Write a Python function to calculate fibonacci numbers",
        "What is the capital of France?",
        "Debug this code: def func(x): return x + y",
        "Explain quantum computing in simple terms"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        decision = await meta_router.route_query(query)
        print(f"📍 Recommended Model: {decision['model']}")
        print(f"🎯 Confidence: {decision['confidence']:.2f}")
        print(f"💭 Reasoning: {decision['reasoning']}")
        print(f"🏷️ Query Type: {decision['query_type']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
