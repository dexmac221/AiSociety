#!/usr/bin/env python3
"""
Enhanced Intelligent Router with OpenAI Meta-Routing

This module extends the original intelligent router to support OpenAI-powered
meta-routing for superior query analysis and model selection.

Integration Architecture:
1. User Query → OpenAI Meta-Router (Analysis) → Local Model Selection → Response
2. Falls back to local-only routing when OpenAI is not available
3. Caches routing decisions to minimize API calls and costs

Author: AI Society Contributors
License: MIT
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Add local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from intelligent_router import IntelligentModelRouter

try:
    from openai_meta_router import OpenAIMetaRouter
except ImportError:
    OpenAIMetaRouter = None

logger = logging.getLogger(__name__)

class EnhancedIntelligentRouter(IntelligentModelRouter):
    """
    Enhanced router that combines OpenAI meta-routing with local model execution.
    
    This class extends the base IntelligentModelRouter to add OpenAI-powered
    query analysis and model selection while maintaining full fallback capability
    to local-only routing.
    
    Features:
    - OpenAI GPT-4o-mini for superior query understanding
    - Dynamic prompt generation with current model inventory
    - Cost-optimized API usage with intelligent caching
    - Seamless fallback to local routing
    - Enhanced model selection accuracy
    """
    
    def __init__(self, config_file: str = "config/router_config.json"):
        """
        Initialize the Enhanced Intelligent Router.
        
        Args:
            config_file (str): Path to router configuration file
        """
        # Initialize base router first
        super().__init__(config_file)
        
        # Initialize OpenAI meta-router if available
        self.meta_router = None
        self.use_openai_routing = False
        
        self._setup_meta_router()
        logger.info("🚀 Enhanced Intelligent Router initialized")
    
    def _setup_meta_router(self) -> None:
        """Set up OpenAI meta-router if available and configured."""
        
        # Debug: Print the entire config
        logger.info(f"🔍 Full config keys: {list(self.config.keys())}")
        logger.info(f"🔍 Config file path: {getattr(self, 'config_file', 'Unknown')}")
        
        # Check if OpenAI integration is enabled in config
        openai_config = self.config.get('openai_meta_routing', {})
        
        logger.info(f"🔍 OpenAI config section: {openai_config}")
        logger.info(f"🔍 OpenAI config found: {openai_config.get('enabled', False)}")
        logger.info(f"🔍 API key from config: {'SET' if openai_config.get('api_key') else 'NULL'}")
        logger.info(f"🔍 API key from env: {'SET' if os.getenv('OPENAI_API_KEY') else 'NULL'}")
        
        if not openai_config.get('enabled', False):
            logger.info("📝 OpenAI meta-routing disabled in configuration")
            return
        
        # Check for API key
        api_key = (
            openai_config.get('api_key') or 
            os.getenv('OPENAI_API_KEY') or
            os.getenv('OPENAI_API_KEY_META_ROUTING')
        )
        
        if not api_key:
            logger.warning("⚠️ OpenAI API key not found - using local routing only")
            return
        
        if not OpenAIMetaRouter:
            logger.warning("⚠️ OpenAI meta-router not available - install openai package")
            return
        
        try:
            self.meta_router = OpenAIMetaRouter(
                api_key=api_key,
                model=openai_config.get('model', 'gpt-4o-mini'),
                cache_decisions=openai_config.get('cache_decisions', True),
                fallback_router=self  # Use self as fallback
            )
            
            self.use_openai_routing = True
            logger.info(f"✅ OpenAI meta-routing enabled with {openai_config.get('model', 'gpt-4o-mini')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI meta-router: {e}")
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Compatibility method for OpenAI meta-router fallback.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: Routing decision compatible with meta-router
        """
        
        # Use local routing (base router) for fallback
        result = super().query_model(query, model_name=None, context=None)
        
        # Convert to meta-router compatible format
        return {
            'model': result.get('model', 'unknown'),
            'confidence': 0.7,  # Standard confidence for local routing
            'reasoning': 'Local intelligent routing fallback',
            'query_type': 'general',
            'complexity': 'moderate'
        }
    
    def query_model(self, query: str, model_name: str = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enhanced query processing with OpenAI meta-routing.
        
        Args:
            query (str): User's query
            model_name (str, optional): Specific model to use (overrides routing)
            context (Optional[Dict]): Additional context for routing
            
        Returns:
            Dict[str, Any]: Response with model information and performance metrics
        """
        
        start_time = time.time()
        
        # If specific model is requested, use it directly
        if model_name:
            logger.info(f"🎯 Using specifically requested model: {model_name}")
            return super().query_model(query, model_name, context)
        
        try:
            # Update meta-router with current model inventory
            if self.meta_router and self.use_openai_routing:
                self.meta_router.update_model_inventory(self.model_registry)
                
                # Get routing decision from OpenAI
                routing_decision = self._get_meta_routing_decision(query)
                
                if routing_decision:
                    selected_model = routing_decision['model']
                    reasoning = routing_decision.get('reasoning', 'OpenAI meta-routing')
                    
                    logger.info(f"🤖 OpenAI selected: {selected_model}")
                    logger.info(f"💭 Reasoning: {reasoning}")
                    
                    # Generate response using selected model
                    response = self._generate_response_with_model(
                        query, selected_model, context, routing_decision
                    )
                    
                    # Add meta-routing information
                    response.update({
                        'routing_method': 'openai_meta',
                        'meta_model': self.meta_router.model,
                        'routing_confidence': routing_decision.get('confidence', 0.0),
                        'routing_reasoning': reasoning,
                        'query_type_detected': routing_decision.get('query_type', 'unknown'),
                        'alternatives_considered': routing_decision.get('alternatives', [])
                    })
                    
                    return response
            
            # Fallback to original local routing
            logger.info("🔄 Using local routing method")
            return super().query_model(query, model_name, context)
            
        except Exception as e:
            logger.error(f"❌ Enhanced routing failed: {e}")
            # Always fallback to base router on error
            return super().query_model(query, model_name, context)
    
    def _get_meta_routing_decision(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get routing decision from OpenAI meta-router.
        
        Args:
            query (str): User query
            
        Returns:
            Optional[Dict[str, Any]]: Routing decision or None if failed
        """
        
        try:
            if self.meta_router:
                # Use the synchronous wrapper to avoid async issues
                result = self.meta_router.route_query_sync(query)
                return result
            else:
                # Fallback to simulation if meta-router not available
                logger.warning("⚠️ OpenAI meta-router not available, using simulation")
                return self._simulate_openai_routing(query)
                
        except Exception as e:
            logger.error(f"❌ Meta-routing failed: {e}")
            # Fallback to simulation on error
            return self._simulate_openai_routing(query)
    
    def _simulate_openai_routing(self, query: str) -> Dict[str, Any]:
        """
        Simulate OpenAI routing decision (for demonstration).
        
        In a real implementation, this would call the OpenAI API.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: Simulated routing decision
        """
        
        query_lower = query.lower()
        
        # Enhanced query analysis simulation
        if any(keyword in query_lower for keyword in ['code', 'function', 'python', 'debug', 'programming']):
            return {
                'model': 'qwen2.5-coder:7b',
                'confidence': 0.95,
                'reasoning': 'Query contains programming keywords, qwen2.5-coder excels at code generation',
                'query_type': 'coding',
                'complexity': 'moderate',
                'specializations_needed': ['coding', 'programming'],
                'alternatives': ['deepseek-coder-v2', 'codellama:7b'],
                'expected_performance': 'excellent'
            }
        
        elif any(keyword in query_lower for keyword in ['math', 'calculate', 'equation', 'solve']):
            return {
                'model': 'phi3:mini',
                'confidence': 0.88,
                'reasoning': 'Mathematical query detected, phi3 optimized for mathematical reasoning',
                'query_type': 'math',
                'complexity': 'moderate',
                'specializations_needed': ['math', 'reasoning'],
                'alternatives': ['qwen2.5:7b', 'mistral:7b'],
                'expected_performance': 'excellent'
            }
        
        elif any(keyword in query_lower for keyword in ['story', 'creative', 'write', 'poem', 'imagine']):
            return {
                'model': 'llama3.2:3b',
                'confidence': 0.82,
                'reasoning': 'Creative writing task identified, llama3.2 has strong creative capabilities',
                'query_type': 'creative',
                'complexity': 'moderate',
                'specializations_needed': ['creative', 'conversation'],
                'alternatives': ['gemma2:9b', 'neural-chat:7b'],
                'expected_performance': 'good'
            }
        
        else:
            return {
                'model': 'llama3.2:3b',
                'confidence': 0.75,
                'reasoning': 'General query, llama3.2 provides good balance of speed and quality',
                'query_type': 'general',
                'complexity': 'moderate',
                'specializations_needed': ['general', 'conversation'],
                'alternatives': ['gemma2:9b', 'qwen2.5:7b'],
                'expected_performance': 'good'
            }
    
    def _generate_response_with_model(
        self, 
        query: str, 
        model_name: str, 
        context: Optional[Dict],
        routing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate response using the specified model with routing context.
        
        Args:
            query (str): User query (original)
            model_name (str): Selected model name
            context (Optional[Dict]): Query context
            routing_info (Dict[str, Any]): Information from routing decision
            
        Returns:
            Dict[str, Any]: Response with metadata
        """
        
        # Check if model is available locally
        if model_name not in self.model_registry:
            logger.warning(f"⚠️ Model {model_name} not in registry, falling back to local selection")
            return super().query_model(query, model_name=None, context=context)
        
        model_info = self.model_registry[model_name]
        
        # Download model if needed
        if not model_info.get('local', False):
            logger.info(f"📥 Downloading {model_name} as recommended by OpenAI...")
            try:
                self._download_model(model_name)
            except Exception as e:
                logger.error(f"❌ Failed to download {model_name}: {e}")
                return super().query_model(query, model_name=None, context=context)
        
        # Use optimized query if available, otherwise use original
        actual_query = routing_info.get('optimized_query', query)
        
        # Generate response using the selected model
        try:
            start_response_time = time.time()
            
            # Use the base router's ollama client directly
            if actual_query != query:
                logger.info(f"🔧 Using optimized query for {model_name}")
                logger.info(f"📝 Original: {query[:80]}...")
                logger.info(f"✨ Enhanced: {actual_query[:80]}...")
            else:
                logger.info(f"🤖 Generating response with {model_name}...")
            
            response = self.ollama_client.generate(
                model=model_name,
                prompt=actual_query,  # Use the optimized query here
                options={
                    'temperature': 0.7,
                    'top_k': 40,
                    'top_p': 0.9,
                    'num_predict': 2048,
                }
            )
            
            response_time = time.time() - start_response_time
            logger.info(f"✅ Response generated successfully in {response_time:.2f}s")
            
            # Prepare enhanced response with routing metadata
            result = {
                'response': response.get('response', ''),
                'model': model_name,
                'routing_method': 'openai_meta',
                'meta_model': self.meta_router.model if self.meta_router else 'none',
                'response_time': response_time,
                'reasoning': routing_info.get('reasoning', 'OpenAI meta-routing'),
                'confidence': routing_info.get('confidence', 0.0),
                'query_type': routing_info.get('query_type', 'unknown'),
                'specializations': routing_info.get('specializations_needed', []),
                'alternatives': routing_info.get('alternatives', []),
                'model_info': model_info,
                'timestamp': datetime.now().isoformat(),
                # Query optimization metadata
                'original_query': query,
                'optimized_query': actual_query,
                'query_enhanced': routing_info.get('query_enhanced', False),
                'optimization_applied': routing_info.get('optimization_applied', 'none'),
                'optimization_reasoning': routing_info.get('optimization_reasoning', 'No optimization applied')
            }
            
            # Update performance tracking
            self._update_performance_stats(model_name, response_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating response with {model_name}: {e}")
            # Fallback to base router
            return super().query_model(query, model_name, context)
    
    def _update_performance_stats(self, model_name: str, response_time: float, success: bool) -> None:
        """Update performance statistics for the model."""
        try:
            if hasattr(self, 'performance_history'):
                self.performance_history.append({
                    'model': model_name,
                    'response_time': response_time,
                    'success': success,
                    'timestamp': datetime.now().isoformat(),
                    'routing_method': 'openai_meta'
                })
                
                # Keep only last 1000 entries
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
        except Exception as e:
            logger.warning(f"⚠️ Failed to update performance stats: {e}")
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """
        Get enhanced statistics including meta-routing information.
        
        Returns:
            Dict[str, Any]: Enhanced system statistics
        """
        
        base_stats = self.get_stats()
        
        enhanced_stats = {
            **base_stats,
            'meta_routing_enabled': self.use_openai_routing,
            'meta_router_model': self.meta_router.model if self.meta_router else None,
            'routing_methods': {
                'openai_meta': 'Available' if self.use_openai_routing else 'Not available',
                'local_analysis': 'Always available',
                'fallback': 'Always available'
            }
        }
        
        # Add meta-router specific stats if available
        if self.meta_router:
            meta_stats = self.meta_router.get_routing_stats()
            enhanced_stats['meta_routing_stats'] = meta_stats
        
        return enhanced_stats

# Configuration example for OpenAI meta-routing
ENHANCED_CONFIG_EXAMPLE = {
    "openai_meta_routing": {
        "enabled": True,
        "model": "gpt-4o-mini",  # or "gpt-4" for even better analysis
        "api_key": None,  # Will use OPENAI_API_KEY environment variable
        "cache_decisions": True,
        "cache_duration_hours": 1,
        "cost_optimization": {
            "max_requests_per_hour": 100,
            "fallback_on_rate_limit": True,
            "use_local_for_simple_queries": True
        }
    },
    "max_model_size": "8GB",
    "preferred_quantization": "Q4_K_M",
    "specialization_weights": {
        "coding": 1.5,
        "math": 1.3,
        "reasoning": 1.4,
        "conversation": 1.1,
        "creative": 1.2
    }
}

if __name__ == "__main__":
    # Example usage
    import time
    from datetime import datetime
    
    router = EnhancedIntelligentRouter()
    
    # Test queries
    test_queries = [
        "Write a Python function to sort a list using quicksort",
        "What is the square root of 144?",
        "Tell me a creative story about a robot",
        "Explain the concept of machine learning"
    ]
    
    print("🧪 Testing Enhanced Intelligent Router")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = router.query_model(query)
        print(f"🤖 Model: {result['model']}")
        print(f"⏱️  Time: {result['response_time_ms']}ms")
        print(f"🎯 Method: {result.get('routing_method', 'local')}")
        if 'routing_reasoning' in result:
            print(f"💭 Reasoning: {result['routing_reasoning']}")
        print(f"📝 Response: {result['response'][:100]}...")
    
    print(f"\n📊 System Statistics:")
    stats = router.get_enhanced_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
