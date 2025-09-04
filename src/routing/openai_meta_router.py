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
        self.model = model
        self.cache_decisions = cache_decisions
        self.fallback_router = fallback_router
        self.routing_cache: Dict[str, Dict] = {}
        self.local_models: Dict[str, Dict] = {}
        
        # Initialize OpenAI client
        if openai_available and self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"🤖 OpenAI Meta-Router initialized with {model}")
        else:
            self.client = None
            logger.warning("⚠️ OpenAI not available, will use fallback routing only")
    
    def update_model_inventory(self, models: Dict[str, Dict]) -> None:
        """
        Update the current inventory of available local models.
        
        Args:
            models (Dict[str, Dict]): Dictionary of available models with metadata
        """
        self.local_models = models
        logger.info(f"📊 Updated model inventory: {len(models)} models available")
    
    def generate_routing_prompt(self, query: str) -> str:
        """
        Generate a dynamic prompt for OpenAI model selection.
        
        Creates a comprehensive prompt that includes the current model inventory,
        their capabilities, and asks the OpenAI model to select the best option.
        
        Args:
            query (str): User's input query
            
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
        
        prompt = f"""You are an expert AI model router for a local LLM system. Your job is to analyze user queries and recommend the BEST local model for response generation.

## Available Local Models:
{models_text}

## Query Analysis Task:
Analyze this user query and recommend the optimal model: "{query}"

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
    "download_recommendation": true
}}

## Selection Criteria (Priority Order):
1. **Specialization Match**: Choose models with specializations matching the query type
2. **Local Availability**: Prefer locally available models (✅ Local) over download needed
3. **Performance Score**: Higher scores indicate better recent performance
4. **Model Size**: Consider complexity vs resource efficiency
5. **Task Complexity**: Match model capability to query complexity

## Query Types & Best Models:
- **Coding/Programming**: qwen2.5-coder, deepseek-coder-v2, codellama
- **Mathematics**: phi3, qwen2.5, mistral
- **Creative Writing**: llama3.2, gemma2, neural-chat
- **Reasoning/Analysis**: mistral, llama3.1, command-r
- **General Questions**: llama3.2, gemma2, qwen2.5
- **Conversation**: neural-chat, vicuna, llama3.2

## Important Notes:
- If no local models are available, recommend the best model even if download is needed
- Consider download time vs performance trade-offs
- Provide 2-3 alternative models in case the primary choice fails
- Be specific about why you chose this model over others

Analyze the query and respond with JSON only:"""

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
                
                # Handle event loop properly
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, can't use run_until_complete
                    logger.warning("⚠️ Cannot run async OpenAI call in sync context, using fallback")
                    if self.fallback_router:
                        return self.fallback_router.route_query(query)
                    else:
                        return self._basic_fallback_routing(query)
                except RuntimeError:
                    # No event loop running, safe to create one
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
        Perform routing using OpenAI API.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: OpenAI routing recommendation
        """
        
        prompt = self.generate_routing_prompt(query)
        
        logger.info(f"🤖 Sending routing request to {self.model}")
        
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
            
            # Validate the decision
            validated_decision = self._validate_routing_decision(routing_decision, query)
            
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
    
    def _validate_routing_decision(self, decision: Dict, query: str) -> Dict[str, Any]:
        """
        Validate and enhance the routing decision from OpenAI.
        
        Args:
            decision (Dict): Raw decision from OpenAI
            query (str): Original user query
            
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
            'timestamp': datetime.now().isoformat()
        }
        
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
