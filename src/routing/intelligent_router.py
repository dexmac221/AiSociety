#!/usr/bin/env python3
"""
Intelligent Model Router for AI Society

This module provides intelligent routing of queries to specialized LLM models
based on query analysis and model capabilities. It optimizes for performance,
specialization, and resource efficiency.

Author: AI Society Contributors
License: MIT
"""

import ollama
from typing import List, Dict, Optional, Tuple, Any, Union
import json
import os
from datetime import datetime
import numpy as np
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from daemon.model_discovery import OllamaLibraryScanner, ModelDiscoveryDaemon

class IntelligentModelRouter:
    """
    Intelligent Model Router for dynamic LLM routing.
    
    This class provides intelligent routing of user queries to the most appropriate
    specialized models based on query analysis, model capabilities, and performance
    history. It optimizes for both quality and efficiency.
    
    Attributes:
        config_file (str): Path to the configuration file
        model_registry (Dict): Registry of available models and their metadata
        performance_history (List): Historical performance data for optimization
        scanner (OllamaLibraryScanner): Model discovery scanner
        discovery_daemon (ModelDiscoveryDaemon): Background model discovery daemon
        ollama_client: Ollama client instance
    """
    def __init__(self, config_file: str = "config/router_config.json") -> None:
        """
        Initialize the Intelligent Model Router.
        
        Args:
            config_file (str): Path to the router configuration file
            
        Raises:
            FileNotFoundError: If required configuration cannot be created
            ConnectionError: If Ollama service is not accessible
        """
        self.config_file = config_file
        self.model_registry: Dict[str, Any] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.scanner = OllamaLibraryScanner()
        self.discovery_daemon = ModelDiscoveryDaemon()
        self.ollama_client: Optional[Any] = None
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        logger.info("🔄 Initializing Intelligent Model Router...")
        self.load_config()
        self._setup_ollama_client()
        self.refresh_model_registry()
        self.discovery_daemon.start()
        logger.info("✅ Router initialization complete")
    
    def load_config(self) -> None:
        """
        Load router configuration from file or create default configuration.
        
        Creates a default configuration optimized for RTX 3090 if no config exists.
        Validates and applies configuration settings.
        
        Raises:
            json.JSONDecodeError: If configuration file is malformed
            PermissionError: If unable to write default configuration
        """
        """Load router configuration"""
        default_config = {
            'max_model_size': '8GB',  # Optimal for RTX 3090
            'preferred_quantization': 'Q4_K_M',
            'specialization_weights': {
                'coding': 1.5,
                'programming': 1.5,
                'debugging': 1.4,
                'general': 1.0,
                'math': 1.3,
                'reasoning': 1.4,
                'conversation': 1.1,
                'chat': 1.1,
                'multilingual': 1.2,
                'vision': 1.3,
                'multimodal': 1.3
            },
            'gpu_constraints': {
                'max_vram_gb': 24,  # RTX 3090
                'preferred_model_sizes': ['3b', '7b', '8b', '9b', '13b'],
                'avoid_sizes': ['70b', '72b', '90b', '405b']  # Too large for single GPU
            },
            'performance_tracking': True,
            'auto_download': True,
            'refresh_interval_hours': 24
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults, but preserve existing settings
                    self.config = {**default_config, **loaded_config}
                    logger.info(f"✅ Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Error loading config: {e}, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            logger.info(f"📄 Creating default configuration at {self.config_file}")
            # Save config only if it doesn't exist
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
    
    def _setup_ollama_client(self):
        """Setup Ollama client with configured host"""
        # Check for new ollama_config format first, then fallback to old ollama_host
        ollama_host = self.config.get('ollama_config', {}).get('host') or self.config.get('ollama_host', 'http://localhost:11434')
        
        # Configure Ollama client to use the specified host
        self.ollama_client = ollama.Client(host=ollama_host)
        
        # Update the global ollama client as well for backward compatibility
        ollama._client._base_url = ollama_host
        
        print(f"🔗 Configured Ollama client for: {ollama_host}")
    
    def refresh_model_registry(self):
        """Refresh the model registry from Ollama library"""
        print("🔄 Refreshing model registry from Ollama library...")
        
        # Fetch latest models from library
        library_models = self.scanner.fetch_library_models()
        
        # Get locally available models
        local_models = self._get_local_models()
        
        # Build comprehensive registry
        for model_data in library_models:
            model_name = model_data['name']
            
            # Find best tag for RTX 3090 (prefer 7B-13B models)
            best_tag = self._select_best_tag(model_data.get('tags', []))
            
            if best_tag:
                # Construct proper full model name using the actual model name
                tag = best_tag['tag']
                if tag.lower() == 'latest':
                    full_name = model_name
                else:
                    full_name = f"{model_name}:{tag}"
                
                # Update the best_tag with correct full_name
                best_tag['full_name'] = full_name
                
                self.model_registry[model_name] = {
                    'full_name': full_name,
                    'base_name': model_name,
                    'tag': best_tag['tag'],
                    'specializations': model_data.get('specializations', ['general']),
                    'performance_score': model_data.get('performance_score', 50),
                    'size': best_tag.get('size', 'unknown'),
                    'parameter_count': best_tag.get('parameter_count', 'unknown'),
                    'quantization': best_tag.get('quantization', 'Q4_K_M'),
                    'is_local': full_name in local_models,
                    'last_updated': model_data.get('last_updated', datetime.now().isoformat()),
                    'description': model_data.get('description', ''),
                    'download_priority': self._calculate_download_priority(model_data, best_tag)
                }
        
        # Save registry to file
        self._save_registry()
        print(f"✅ Registry updated with {len(self.model_registry)} models")
        
        # Show some stats
        local_count = sum(1 for m in self.model_registry.values() if m['is_local'])
        print(f"📊 {local_count} models available locally, {len(self.model_registry) - local_count} available for download")
    
    def _get_local_models(self) -> List[str]:
        """Get list of locally installed models"""
        try:
            models = self.ollama_client.list()
            if isinstance(models, dict) and 'models' in models:
                return [model['name'] for model in models['models']]
            elif isinstance(models, list):
                # Handle case where models might be returned directly as a list
                result = []
                for model in models:
                    if isinstance(model, dict):
                        result.append(model.get('name', str(model)))
                    elif isinstance(model, str):
                        result.append(model)
                    else:
                        result.append(str(model))
                return result
            else:
                return []
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {e}")
            return []
    
    def _select_best_tag(self, tags: List) -> Optional[Dict]:
        """Select best tag based on GPU constraints"""
        if not tags:
            return None
        
        preferred_sizes = self.config['gpu_constraints']['preferred_model_sizes']
        avoid_sizes = self.config['gpu_constraints']['avoid_sizes']
        
        # Convert string tags to dict format
        processed_tags = []
        for tag in tags:
            if isinstance(tag, str):
                # For the _select_best_tag context, we need the base model name
                # This will be passed from the calling function
                tag_dict = {
                    'tag': tag,
                    'size': self._estimate_size_from_tag(tag),
                    'parameter_count': self._get_parameter_count_from_tag(tag),
                    'quantization': 'Q4_K_M'
                }
                processed_tags.append(tag_dict)
            elif isinstance(tag, dict):
                processed_tags.append(tag)
            else:
                continue
        
        # Filter out too-large models
        suitable_tags = []
        for tag in processed_tags:
            tag_name = tag.get('tag', '').lower()
            if not any(avoid in tag_name for avoid in avoid_sizes):
                suitable_tags.append(tag)
        
        if not suitable_tags:
            suitable_tags = processed_tags  # Fallback to all tags
        
        # Prefer optimal sizes
        for pref_size in preferred_sizes:
            for tag in suitable_tags:
                if pref_size in tag.get('tag', '').lower():
                    return tag
        
        # Default to first suitable tag or 'latest'
        for tag in suitable_tags:
            if tag.get('tag', '').lower() == 'latest':
                return tag
        
        return suitable_tags[0] if suitable_tags else None
    
    def _estimate_size_from_tag(self, tag: str) -> str:
        """Estimate model size from tag name"""
        size_map = {
            '0.5b': '0.3GB', '1b': '0.6GB', '1.5b': '0.9GB', '2b': '1.2GB',
            '3b': '2.0GB', '3.8b': '2.3GB', '6b': '3.5GB', '7b': '4.0GB',
            '8b': '4.5GB', '9b': '5.5GB', '11b': '6.5GB', '13b': '7.5GB',
            '14b': '8.0GB', '16b': '9.0GB', '27b': '16GB', '32b': '18GB',
            '34b': '20GB', '35b': '20GB', '70b': '40GB', '72b': '42GB',
            'mini': '2.0GB', 'small': '4.0GB', 'medium': '8.0GB', 'latest': '4.0GB'
        }
        
        tag_lower = tag.lower()
        for size_key, size_value in size_map.items():
            if size_key in tag_lower:
                return size_value
        return '4.0GB'  # Default
    
    def _get_parameter_count_from_tag(self, tag: str) -> str:
        """Get parameter count from tag name"""
        tag_lower = tag.lower()
        if 'b' in tag_lower and tag_lower not in ['latest', 'stable']:
            return tag.upper().replace('B', 'B parameters')
        elif tag_lower == 'mini':
            return '3.8B parameters'
        elif tag_lower == 'small':
            return '7B parameters'
        elif tag_lower == 'medium':
            return '14B parameters'
        return '7B parameters'  # Default
    
    def _calculate_download_priority(self, model_data: Dict, tag_info: Dict) -> int:
        """Calculate download priority (higher = more important to download)"""
        priority = 0
        
        # Base priority from performance score
        priority += int(model_data.get('performance_score', 50))
        
        # Higher priority for coding models (common use case)
        if 'coding' in model_data.get('specializations', []):
            priority += 20
        
        # Higher priority for general models (versatile)
        if 'general' in model_data.get('specializations', []):
            priority += 15
        
        # Lower priority for very large models
        size_gb = self._extract_size_gb(tag_info.get('size', ''))
        if size_gb > 10:
            priority -= 10
        elif size_gb < 5:
            priority += 5
        
        return priority
    
    def _extract_size_gb(self, size_str: str) -> float:
        """Extract size in GB from size string"""
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', size_str)
            if match:
                return float(match.group(1))
        except:
            pass
        return 5.0  # Default assumption
    
    def _save_registry(self):
        """Save model registry to file"""
        registry_file = "data/model_registry.json"
        try:
            with open(registry_file, 'w') as f:
                json.dump(self.model_registry, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save registry: {e}")
    
    def select_model(self, query: str, context: Optional[Dict] = None) -> str:
        """Intelligently select the best model for a query"""
        
        # Analyze query to determine required specializations
        required_specs = self._analyze_query(query)
        print(f"🔍 Query analysis - Required specializations: {required_specs}")
        
        # Score each model
        model_scores = {}
        for model_name, model_info in self.model_registry.items():
            score = self._calculate_model_score(
                model_info, 
                required_specs,
                context
            )
            model_scores[model_name] = score
            print(f"📊 {model_name}: {score:.2f} (local: {model_info.get('is_local', False)}, specs: {model_info.get('specializations', [])})")
        
        # Select best model
        if model_scores:
            best_model = max(model_scores, key=model_scores.get)
            selected_info = self.model_registry[best_model]
            
            print(f"🎯 Selected: {selected_info['full_name']} (specializations: {', '.join(selected_info['specializations'])})")
            
            # Download if not local and download_on_request is enabled
            if not selected_info['is_local'] and self.config.get('download_on_request', True):
                print(f"📥 Model not available locally, downloading {selected_info['full_name']}...")
                self._download_model(selected_info['full_name'])
            elif not selected_info['is_local']:
                print(f"⚠️  Model {selected_info['full_name']} not available locally (auto-download disabled)")
            
            return selected_info['full_name']
        
        # Fallback to a safe default
        fallback_models = ["llama3.2:3b", "gemma2:2b", "phi3:mini"]
        for fallback in fallback_models:
            try:
                self.ollama_client.pull(fallback)
                return fallback
            except:
                continue
        
        raise Exception("No suitable model found and fallback failed")
    
    def _analyze_query(self, query: str) -> List[str]:
        """Analyze query to determine required specializations"""
        query_lower = query.lower()
        specs = []
        
        # Coding indicators
        coding_keywords = [
            'code', 'function', 'program', 'debug', 'error', 'implement', 
            'class', 'method', 'variable', 'algorithm', 'script', 'syntax',
            'python', 'javascript', 'java', 'c++', 'html', 'css', 'sql',
            'api', 'database', 'framework', 'library', 'package', 'import'
        ]
        if any(kw in query_lower for kw in coding_keywords):
            specs.append('coding')
        
        # Math indicators
        math_keywords = [
            'calculate', 'math', 'equation', 'solve', 'formula', 'derivative',
            'integral', 'statistics', 'probability', 'algebra', 'geometry',
            'calculus', 'number', 'sum', 'average', 'percentage'
        ]
        if any(kw in query_lower for kw in math_keywords):
            specs.append('math')
        
        # Creative/Story indicators (high priority)
        creative_keywords = [
            'story', 'creative', 'write', 'poem', 'fiction', 'narrative',
            'character', 'plot', 'dialogue', 'scene', 'chapter', 'novel',
            'imagination', 'fantasy', 'adventure', 'romance', 'mystery',
            'once upon', 'tell a story', 'write a', 'create a', 'imagine',
            'tale', 'legend', 'fairy tale', 'short story', 'creative writing'
        ]
        if any(kw in query_lower for kw in creative_keywords):
            specs.append('creative')
        
        # Reasoning indicators
        reasoning_keywords = [
            'explain', 'why', 'analyze', 'reason', 'because', 'therefore',
            'compare', 'contrast', 'evaluate', 'assess', 'conclude',
            'infer', 'deduce', 'logic', 'argument', 'evidence'
        ]
        if any(kw in query_lower for kw in reasoning_keywords):
            specs.append('reasoning')
        
        # Conversation indicators
        chat_keywords = [
            'chat', 'talk', 'hello', 'hi', 'how are', 'conversation',
            'discuss', 'tell me', 'what do you think', 'opinion'
        ]
        if any(kw in query_lower for kw in chat_keywords):
            specs.append('conversation')
        
        # Vision/multimodal indicators
        vision_keywords = [
            'image', 'picture', 'visual', 'see', 'look', 'photo',
            'diagram', 'chart', 'graph', 'describe image'
        ]
        if any(kw in query_lower for kw in vision_keywords):
            specs.append('vision')
        
        # Default to general if no specific indicators
        if not specs:
            specs.append('general')
        
        print(f"🔍 Query: '{query[:50]}...' -> Specializations: {specs}")
        return specs
    
    def _calculate_model_score(self, model_info: Dict, required_specs: List[str], context: Optional[Dict]) -> float:
        """Calculate score for a model based on requirements"""
        score = model_info.get('performance_score', 50)
        
        # Boost score for matching specializations
        for spec in required_specs:
            if spec in model_info.get('specializations', []):
                weight = self.config['specialization_weights'].get(spec, 1.0)
                score *= weight
        
        # Prefer local models (but make this configurable and less aggressive)
        if model_info.get('is_local'):
            local_boost = self.config.get('local_model_boost', 1.1)
            score *= local_boost
        
        # Consider model size (prefer optimal sizes for RTX 3090)
        size_gb = self._extract_size_gb(model_info.get('size', ''))
        if 3 <= size_gb <= 8:  # Sweet spot for RTX 3090
            score *= 1.2
        elif size_gb > 15:  # Too large, penalize
            score *= 0.7
        
        # Consider context history if available
        if context and context.get('previous_model'):
            # Slight preference for consistency (reduce model switching overhead)
            if context['previous_model'] == model_info['full_name']:
                score *= 1.05
        
        # Boost newer models (strongly prefer recent models)
        model_name = model_info.get('full_name', '').lower()
        last_updated = model_info.get('last_updated', '2023-01-01')
        
        # 2024-2025 models get significant boost
        if '2024-11' in last_updated or '2024-10' in last_updated:
            score *= 1.25  # Latest models
        elif '2024-0' in last_updated or '2024-1' in last_updated:
            score *= 1.2   # Recent 2024 models
        elif '2024' in last_updated:
            score *= 1.15  # 2024 models
        elif '2023' in last_updated:
            score *= 1.05  # 2023 models
        
        # Specific model version bonuses
        if any(version in model_name for version in ['3.2', '2.5']):
            score *= 1.1
        elif any(version in model_name for version in ['3.1', '2.0']):
            score *= 1.05
        
        return score
    
    def _download_model(self, model_name: str):
        """Download model if not available locally"""
        print(f"📥 Downloading {model_name}...")
        try:
            self.ollama_client.pull(model_name)
            
            # Update registry to mark as local
            for model_data in self.model_registry.values():
                if model_data.get('full_name') == model_name:
                    model_data['is_local'] = True
                    break
            
            print(f"✅ Successfully downloaded {model_name}")
            
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
            raise
    
    def get_model_recommendations(self, limit: int = 5) -> List[Dict]:
        """Get recommended models to download based on priority"""
        available_models = [
            model for model in self.model_registry.values()
            if not model.get('is_local', False)
        ]
        
        # Sort by download priority
        available_models.sort(key=lambda x: x.get('download_priority', 0), reverse=True)
        
        return available_models[:limit]
    
    def query_model(self, query: str, model_name: str = None, context: Optional[Dict] = None) -> Dict:
        """Query the selected model and return response with metadata"""
        start_time = datetime.now()
        
        if not model_name:
            model_name = self.select_model(query, context)
        
        try:
            print(f"🤖 Generating response with {model_name}...")
            response = self.ollama_client.generate(
                model=model_name,
                prompt=query,
                options={
                    'temperature': 0.7,
                    'top_k': 40,
                    'top_p': 0.9,
                    'num_predict': 2048,  # Limit response length
                }
            )
            print(f"✅ Response generated successfully")
            print(f"🔍 Response type: {type(response)}")
            print(f"🔍 Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            # Handle different response formats
            if isinstance(response, dict):
                if 'response' in response:
                    response_text = response['response']
                elif 'message' in response:
                    response_text = response['message']
                elif 'content' in response:
                    response_text = response['content']
                else:
                    response_text = str(response)
                    print(f"⚠️ Unexpected response format, using string conversion")
            else:
                response_text = str(response)
                print(f"⚠️ Response is not a dict: {type(response)}")
            
            print(f"📝 Response text length: {len(response_text)} characters")
            
            end_time = datetime.now()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Track performance if enabled
            if self.config.get('performance_tracking', True):
                self._track_performance(model_name, query, response_time, len(response_text))
            
            result = {
                'response': response_text,
                'message': response_text,  # For backward compatibility
                'model': model_name,
                'response_time_ms': response_time,
                'timestamp': end_time.isoformat(),
                'specializations_used': self.model_registry.get(model_name.split(':')[0], {}).get('specializations', [])
            }
            
            print(f"📤 Returning result with {len(result['response'])} characters")
            return result
            
        except Exception as e:
            print(f"❌ Error querying {model_name}: {e}")
            # Try fallback model
            if model_name != "llama3.2:3b":
                return self.query_model(query, "llama3.2:3b", context)
            else:
                raise
    
    def _track_performance(self, model_name: str, query: str, response_time: int, response_length: int):
        """Track model performance for future optimization"""
        performance_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model_name,
            'query_length': len(query),
            'response_time_ms': response_time,
            'response_length': response_length,
            'tokens_per_second': response_length / max(response_time / 1000, 0.001)
        }
        
        self.performance_history.append(performance_entry)
        
        # Keep only recent history (last 1000 entries)
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        # Save to file periodically
        if len(self.performance_history) % 50 == 0:  # Every 50 queries
            try:
                with open('data/performance_history.json', 'w') as f:
                    json.dump(self.performance_history, f)
            except:
                pass  # Silent fail for performance tracking
    
    def get_stats(self) -> Dict:
        """Get router statistics"""
        total_models = len(self.model_registry)
        local_models = sum(1 for m in self.model_registry.values() if m.get('is_local', False))
        
        stats = {
            'total_models_available': total_models,
            'local_models': local_models,
            'downloadable_models': total_models - local_models,
            'queries_processed': len(self.performance_history),
            'average_response_time': 0,
            'most_used_specializations': {}
        }
        
        if self.performance_history:
            avg_time = sum(entry['response_time_ms'] for entry in self.performance_history) / len(self.performance_history)
            stats['average_response_time'] = round(avg_time, 2)
        
        return stats

if __name__ == "__main__":
    # Test the router
    router = IntelligentModelRouter()
    
    # Test queries
    test_queries = [
        "Write a Python function to calculate fibonacci numbers",
        "Explain quantum computing in simple terms",
        "What's 15 * 23 + 47?",
        "Hello, how are you today?"
    ]
    
    for query in test_queries:
        print(f"\n🤖 Query: {query}")
        try:
            result = router.query_model(query)
            print(f"📝 Response: {result['response'][:100]}...")
            print(f"⚡ Model: {result['model']} | Time: {result['response_time_ms']}ms")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Show stats
    print(f"\n📊 Router Stats: {router.get_stats()}")
