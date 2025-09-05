# AI Society - LLM Model Router

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Enhanced-orange.svg)](https://openai.com/)

> 🎯 **Democratizing AI Access with Intelligent Routing**  
> A Python-based model routing system that intelligently selects appropriate local LLMs for different types of queries. Features advanced multilingual support, conversation memory, and OpenAI-enhanced routing for superior query analysis and optimization.

![AI Society Web Interface](web_interface.png)

![System Architecture](schema_color.png)

## ✅ Current Status (September 2025)

🎯 **System is LIVE and fully operational!**
- ✅ Web interface running at: http://localhost:8000 
- ✅ 14 latest 2025 models integrated and tested
- ✅ Enhanced UI with dark mode, 8+ example categories
- ✅ Multilingual support with OpenAI translation framework
- ✅ Hybrid memory system with conversation context
- ✅ Real-time technical dashboard with performance metrics
- ✅ Professional visual documentation with schema diagrams

**Latest Models Available:**
- **Coding**: Qwen2.5-Coder:7B, DeepSeek-Coder-v2:16B, CodeLlama:7B
- **Math**: Phi-4:14B, Qwen2.5:7B, Phi3:mini
- **Creative**: Hermes-4:14B, Yi:9B, Neural-Chat:7B  
- **Multimodal**: Qwen2.5-Omni:7B, Gemma-3:27B/4B
- **Efficiency**: Gemma-3:1B, Apple-FastVLM:7B, NVIDIA-Nemotron-Nano:12B
- **General**: Qwen2.5:7B, Llama3.1:8B, Mistral:7B, OpenAI-OSS:20B

## 🌟 What is AI Society?

AI Society is an advanced model routing system that intelligently selects and optimizes queries for local LLMs. It features dual AI intelligence combining OpenAI's superior query analysis with efficient local model execution, plus conversation memory for extended interactions, and **multilingual support** for global accessibility.

### Core Capabilities

- **🌍 Multilingual Intelligence**: Automatic language detection and translation for optimal local model performance
- **🧠 Dual AI Intelligence**: OpenAI for smart routing + Local models for execution
- **🔧 Query Optimization**: Automatically enhances queries for dramatically better results
- **💬 Conversation Memory**: Maintains context across multi-turn conversations with hybrid FAISS indexing
- **🎯 Smart Model Selection**: Analyzes queries and routes to optimal local models with confidence scoring
- **🌐 Modern Web Interface**: Real-time chat with optimization, memory, and language indicators
- **📊 Model Discovery**: Scans available Ollama models and manages downloads automatically
- **⚡ Performance Tracking**: Comprehensive monitoring of response times and model usage

## 🎉 Latest Updates (September 2025)

### **🌍 Multilingual AI Enhancement**
- **Intelligent Language Detection** - Automatically detects queries in Spanish, French, German, Italian, Portuguese, Japanese, Chinese, and more
- **OpenAI Translation Layer** - Translates non-English queries to English for optimal local model performance
- **Response Language Instructions** - Local models receive instructions to respond in the user's original language
- **Enhanced Performance** - Local models work better with English queries but respond in user's preferred language
- **Real-time Language Panel** - Technical dashboard shows detection status, translation applied, and multilingual enhancement active

### **🚀 2025 Model Optimization & Enhanced UI**
- **14 cutting-edge models** optimized for RTX 3090 and similar hardware
- **Phi-4** (14B) - Microsoft's latest reasoning model
- **Gemma-3** series - Google's enhanced efficiency models
- **OpenAI OSS 20B** - RTX 3090 optimized open source model
- **Dark mode UI fixes** - Perfect text visibility in all themes
- **Enhanced example queries** - 8 diverse categories including debugging, translation, and data analysis
- **Real-time technical panel** - Memory stats, model info, performance metrics, and language detection
- **Improved model selection** - Better visibility in both light/dark modes

### **🧠 Conversation Memory System**
- **Multi-turn conversations** with full context awareness
- **Smart references** - "explain that code", "improve my function"  
- **Session management** with automatic cleanup
- **Context visualization** in the web interface
- **Hybrid FAISS indexing** with OpenAI summarization

### **🔧 Query Optimization with Dual AI**
- **OpenAI-powered enhancement** of user queries for better results
- **Transparent process** showing original vs optimized queries
- **Dramatic improvements** - "sort list" → "Write a well-documented Python function..."
- **Model-specific optimization** tailored to selected AI capabilities

## 🎯 Model Inventory (2025 Latest)

Our system features **14 cutting-edge models** optimized for RTX 3090 and similar hardware:

### 💻 **Coding Specialists**
- **Qwen2.5-Coder:7B** - Advanced multilingual coding with debugging
- **DeepSeek-Coder-v2:16B** - Complex algorithms and system programming
- **CodeLlama:7B** - General coding, documentation, refactoring

### 🧮 **Math & Reasoning**  
- **Phi-4:14B** - Microsoft's latest math reasoning model
- **Qwen2.5:7B** - Algebra, calculus, statistics, problem solving
- **Phi3:mini** - Quick calculations and basic math

### 🎨 **Creative Specialists**
- **Hermes-4:14B** - NousResearch's latest uncensored creative model
- **Yi:9B** - Long-form content, poetry, fiction
- **Neural-Chat:7B** - Dialogue, conversation, roleplay

### 🌐 **Multimodal & Efficiency**
- **Qwen2.5-Omni:7B** - Real-time voice, text, image, audio, video
- **Gemma-3:27B/4B** - Google's latest multimodal models  
- **Gemma-3:1B** - Ultra-efficient edge deployment
- **Apple-FastVLM:7B** - Mobile-optimized multimodal
- **NVIDIA-Nemotron-Nano:12B** - Enterprise-grade efficiency

### 🎯 **General Purpose**
- **Qwen2.5:7B** - Excellent instruction following and multilingual
- **Llama3.1:8B** - Meta's latest reasoning and code model
- **Mistral:7B** - Advanced reasoning and function calling
- **OpenAI-OSS:20B** - Advanced reasoning, RTX 3090 compatible

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Ollama** installed and running
- **GPU with sufficient VRAM** (tested on RTX 3090, but should work on other hardware)
- **OpenAI API key** (optional, for enhanced routing)

### Installation
```bash
# Clone the repository
git clone https://github.com/dexmac221/AiSociety.git
cd AiSociety

# Automated setup (recommended)
chmod +x setup.sh
./setup.sh

# Quick start
chmod +x start.sh  
./start.sh

# Or manual start
python web/app.py
```

### Access Points
- **Web Interface**: http://localhost:8000 (main chat interface)
- **WebSocket API**: ws://localhost:8000/ws
- **REST API**: http://localhost:8000/api/health

## 🌟 Core Features

### 🌍 **Multilingual AI Enhancement**
- **Universal Language Support**: Ask questions in Spanish, French, German, Italian, Portuguese, Japanese, Chinese, and more
- **Intelligent Translation**: OpenAI automatically detects language and translates to English for optimal local model comprehension
- **Native Response Language**: Local models receive instructions to respond in your original language
- **Performance Boost**: Combines English query optimization with multilingual response capability
- **Real-time Indicators**: Language panel shows detection status and translation activity

### 🔧 **Query Optimization with Dual AI**
- **Before**: "sort list" → Basic response
- **After**: OpenAI enhances to "Write a well-documented Python function with error handling that sorts a list..." → Superior response
- **Transparency**: See both original and optimized queries in the interface
- **Intelligence**: OpenAI analyzes intent and optimizes for the selected model's strengths

### 💬 **Conversation Memory & Context**
- **Multi-turn Conversations**: "Write a function" → "Explain that code" → "Make it more complex"
- **Context Awareness**: Remembers previous messages and maintains conversation flow
- **Smart References**: Understands "that code", "the previous example", "my function"
- **Session Management**: 10-message memory window with automatic cleanup

### 🎯 **Enhanced Model Routing**
- **Specialized Selection**: Coding → qwen2.5-coder, Math → phi3, Creative → llama3.2
- **Performance Optimization**: Tracks model success rates and response times
- **Auto-downloads**: Fetches recommended models as needed
- **Fallback Logic**: Graceful degradation when preferred models unavailable

## 🏗️ System Architecture

![AI Society Architecture](schema_color.png)

The system employs a sophisticated dual AI architecture combining commercial AI intelligence with local model execution:

### Dual AI Intelligence Flow

1. **Query Reception**: User sends message in any supported language via WebSocket
2. **Language Detection**: OpenAI automatically detects the query language
3. **Translation Layer**: Non-English queries translated to English for optimal local model performance
4. **Memory Integration**: System adds to conversation history and builds context
5. **OpenAI Analysis**: GPT-4.1-mini analyzes query and optimizes it for better results
6. **Model Selection**: AI recommends optimal local model based on query type and available models
7. **Response Instructions**: Local model receives query with instruction to respond in original language
8. **Local Execution**: Enhanced query runs on selected local model with language instructions
9. **Response Enhancement**: Results include optimization details, memory context, and language info
10. **Memory Update**: Conversation history updated for future context

This hybrid approach combines the intelligence of commercial AI with the privacy and efficiency of local models, while supporting global users through intelligent multilingual processing.

## 🔧 Configuration & Setup

### Configuration File
Enhanced configuration in `config/router_config.json`:

```json
{
  "max_model_size": "8GB",
  "openai_meta_routing": {
    "enabled": true,
    "model": "gpt-4.1-mini",
    "cache_decisions": true,
    "cost_optimization": {
      "max_requests_per_hour": 200,
      "max_daily_cost_usd": 5.0,
      "fallback_on_rate_limit": true
    },
    "prompt_optimization": {
      "include_model_specs": true,
      "include_previous_success": true,
      "format_structured_response": true
    }
  },
  "specialization_weights": {
    "coding": 1.5,
    "math": 1.3,
    "reasoning": 1.4,
    "creative": 1.2,
    "conversation": 1.1
  },
  "performance_tracking": {
    "enabled": true,
    "track_optimization_impact": true,
    "conversation_analytics": true
  }
}
```

### OpenAI Integration (Recommended)

For optimal performance with query optimization and intelligent routing:

1. **Set your API key:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. **Enable in config:**
```json
{
  "openai_meta_routing": {
    "enabled": true,
    "model": "gpt-4o-mini"
  }
}
```

### **What OpenAI Integration Provides:**

- **🔧 Query Optimization**: Transforms vague queries into specific, effective prompts
- **🎯 Smart Model Selection**: AI-powered analysis of query requirements
- **📈 Better Results**: Dramatically improved response quality through enhanced prompts
- **💰 Cost Efficient**: Uses gpt-4o-mini for analysis (~$0.01 per 1000 requests)
- **🔄 Fallback Safe**: System works without OpenAI, but with reduced optimization

### **Example Optimizations:**

| Original Query | OpenAI Enhancement |
|---|---|
| "sort list" | "Write a well-documented Python function with error handling..." |
| "quantum" | "Explain quantum computing in simple terms with examples..." |
| "5+3*2" | "Calculate step-by-step showing order of operations..." |

## 📋 Testing & Validation

### Test System
```bash
# Run comprehensive system tests
./test_system.py

# Test multilingual capabilities
python test_multilingual.py

# Test individual components
python test_conversation_memory.py
python test_query_optimization.py
```

### Example Usage Scenarios

#### **Query Optimization in Action**
```
👤 User Input: "sort list"

🔧 OpenAI Enhancement: "Write a well-documented Python function with error handling 
   that sorts a list of integers in ascending order using an efficient algorithm. 
   Include type hints, docstring, and example usage."

🤖 Selected Model: qwen2.5-coder (specialized for coding)
⚡ Result: High-quality, comprehensive code with documentation
```

#### **Conversation Memory in Action**
```
👤 "Write a Python function to calculate fibonacci"
🤖 [Provides fibonacci function] 🧠 2 messages

👤 "Can you explain how that algorithm works?"  
🤖 [Explains the fibonacci algorithm from previous message] 🧠 4 messages

👤 "Make it more efficient using memoization"
🤖 [Improves the previous function with memoization] 🧠 6 messages
```

#### **Web Interface Features**
- **🌍 Language Panel**: Real-time language detection and translation status
- **🧠 Memory Indicators**: Shows conversation length and context usage
- **🔧 Query Optimization**: Displays original vs enhanced queries
- **🎯 Model Selection**: Shows reasoning for model choice
- **⚡ Performance Metrics**: Real-time response times and confidence scores
- **📊 Status Updates**: Live updates with optimization, memory, and language info

## 📁 Project Structure

```
ai-society/
├── src/
│   ├── daemon/                     # Model discovery
│   │   ├── model_discovery.py
│   │   └── model_discovery_new.py
│   ├── memory/                     # Conversation memory
│   │   └── hybrid_memory.py
│   └── routing/                    # Routing logic
│       ├── intelligent_router.py
│       ├── enhanced_intelligent_router.py
│       └── openai_meta_router.py
├── web/
│   └── app.py                      # FastAPI web interface
├── config/
│   ├── router_config.json          # System configuration
│   ├── model_selection.json        # Latest 2025 models
│   └── api_config.env              # API keys
├── data/                           # Auto-created directories
│   └── memory/                     # Conversation storage
├── docs/                           # Documentation
│   ├── DEVELOPMENT.md
│   └── OPENAI_META_ROUTING.md
├── requirements.txt                # Dependencies
├── setup.sh                       # Setup script
├── start.sh                       # Start script
└── test_*.py                      # Test scripts
```

## 📚 Development & Contributing

For detailed development information, see:
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development guide and architecture
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

### Development Commands
```bash
# System testing
./test_system.py

# Component testing  
python test_multilingual.py
python test_conversation_memory.py
python test_query_optimization.py

# Direct OpenAI testing
python test_direct_openai.py
```

## 📄 License & Credits

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Acknowledgments
- **Ollama team** for excellent local LLM infrastructure
- **OpenAI** for API integration capabilities  
- **FastAPI** for the robust web framework
- **FAISS** for efficient vector similarity search
- **Community contributors** for feedback and improvements

### Support & Community
- **GitHub Issues**: [Report bugs and request features](https://github.com/dexmac221/AiSociety/issues)
- **Documentation**: [Full documentation](docs/)
- **Changelog**: [Version history](CHANGELOG.md)

---

*AI Society - Democratizing access to intelligent AI routing for everyone* 🚀

![AI Society Web Interface](web_interface.png)

![System Architecture](schema_color.png)

## ✅ Current Status (September 2025)

🎯 **System is LIVE and fully operational!**
- ✅ Web interface running at: http://localhost:8000 
- ✅ 14 latest 2025 models integrated and tested
- ✅ Enhanced UI with dark mode, 8+ example categories
- ✅ Multilingual support with OpenAI translation framework
- ✅ Hybrid memory system with conversation context
- ✅ Real-time technical dashboard with performance metrics
- ✅ Professional visual documentation with schema diagrams

**Latest Models Available:**
- **Coding**: Qwen2.5-Coder:7B, DeepSeek-Coder-v2:16B, CodeLlama:7B
- **Math**: Phi-4:14B, Qwen2.5:7B, Phi3:mini
- **Creative**: Hermes-4:14B, Yi:9B, Neural-Chat:7B  
- **Multimodal**: Qwen2.5-Omni:7B, Gemma-3:27B/4B
- **Efficiency**: Gemma-3:1B, Apple-FastVLM:7B, NVIDIA-Nemotron-Nano:12B
- **General**: Qwen2.5:7B, Llama3.1:8B, Mistral:7B, OpenAI-OSS:20B

## 🌟 What is AI Society?

AI Society is an advanced model routing system that intelligently selects and optimizes queries for local LLMs. It features dual AI intelligence combining OpenAI's superior query analysis with efficient local model execution, plus conversation memory for extended interactions, and **multilingual support** for global accessibility.

### � Core Capabilities

- **🌍 Multilingual Intelligence**: Automatic language detection and translation for optimal local model performance
- **🧠 Dual AI Intelligence**: OpenAI for smart routing + Local models for execution
- **🔧 Query Optimization**: Automatically enhances queries for dramatically better results
- **💬 Conversation Memory**: Maintains context across multi-turn conversations with hybrid FAISS indexing
- **🎯 Smart Model Selection**: Analyzes queries and routes to optimal local models with confidence scoring
- **🌐 Modern Web Interface**: Real-time chat with optimization, memory, and language indicators
- **📊 Model Discovery**: Scans available Ollama models and manages downloads automatically
- **⚡ Performance Tracking**: Comprehensive monitoring of response times and model usage

## 🎉 Latest Updates (September 2025)

### **🌍 Multilingual AI Enhancement**
- **Intelligent Language Detection** - Automatically detects queries in Spanish, French, German, Italian, Portuguese, Japanese, Chinese, and more
- **OpenAI Translation Layer** - Translates non-English queries to English for optimal local model performance
- **Response Language Instructions** - Local models receive instructions to respond in the user's original language
- **Enhanced Performance** - Local models work better with English queries but respond in user's preferred language
- **Real-time Language Panel** - Technical dashboard shows detection status, translation applied, and multilingual enhancement active

### **🚀 2025 Model Optimization & Enhanced UI**
- **14 cutting-edge models** optimized for RTX 3090 and similar hardware
- **Phi-4** (14B) - Microsoft's latest reasoning model
- **Gemma-3** series - Google's enhanced efficiency models
- **OpenAI OSS 20B** - RTX 3090 optimized open source model
- **Dark mode UI fixes** - Perfect text visibility in all themes
- **Enhanced example queries** - 8 diverse categories including debugging, translation, and data analysis
- **Real-time technical panel** - Memory stats, model info, performance metrics, and language detection
- **Improved model selection** - Better visibility in both light/dark modes

### **🧠 Conversation Memory System**
- **Multi-turn conversations** with full context awareness
- **Smart references** - "explain that code", "improve my function"  
- **Session management** with automatic cleanup
- **Context visualization** in the web interface
- **Hybrid FAISS indexing** with OpenAI summarization

### **🔧 Query Optimization with Dual AI**
- **OpenAI-powered enhancement** of user queries for better results
- **Transparent process** showing original vs optimized queries
- **Dramatic improvements** - "sort list" → "Write a well-documented Python function..."
- **Model-specific optimization** tailored to selected AI capabilities

## 🎯 Model Inventory (2025 Latest)

Our system features **14 cutting-edge models** optimized for RTX 3090 and similar hardware:

### 💻 **Coding Specialists**
- **Qwen2.5-Coder:7B** - Advanced multilingual coding with debugging
- **DeepSeek-Coder-v2:16B** - Complex algorithms and system programming
- **CodeLlama:7B** - General coding, documentation, refactoring

### 🧮 **Math & Reasoning**  
- **Phi-4:14B** - Microsoft's latest math reasoning model
- **Qwen2.5:7B** - Algebra, calculus, statistics, problem solving
- **Phi3:mini** - Quick calculations and basic math

### 🎨 **Creative Specialists**
- **Hermes-4:14B** - NousResearch's latest uncensored creative model
- **Yi:9B** - Long-form content, poetry, fiction
- **Neural-Chat:7B** - Dialogue, conversation, roleplay

### 🌐 **Multimodal & Efficiency**
- **Qwen2.5-Omni:7B** - Real-time voice, text, image, audio, video
- **Gemma-3:27B/4B** - Google's latest multimodal models  
- **Gemma-3:1B** - Ultra-efficient edge deployment
- **Apple-FastVLM:7B** - Mobile-optimized multimodal
- **NVIDIA-Nemotron-Nano:12B** - Enterprise-grade efficiency

### 🎯 **General Purpose**
- **Qwen2.5:7B** - Excellent instruction following and multilingual
- **Llama3.1:8B** - Meta's latest reasoning and code model
- **Mistral:7B** - Advanced reasoning and function calling
- **OpenAI-OSS:20B** - Advanced reasoning, RTX 3090 compatible

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Ollama** installed and running
- **GPU with sufficient VRAM** (tested on RTX 3090, but should work on other hardware)
- **OpenAI API key** (optional, for enhanced routing)

### Installation
```bash
# Clone the repository
git clone https://github.com/dexmac221/AiSociety.git
cd AiSociety

# Automated setup (recommended)
chmod +x setup.sh
./setup.sh

# Quick start
chmod +x start.sh  
./start.sh

# Or manual start
python web/app.py
```

### Access Points
- **Web Interface**: http://localhost:8000 (main chat interface)
- **WebSocket API**: ws://localhost:8000/ws
- **REST API**: http://localhost:8000/api/health

## 🌟 Core Features

### 🌍 **Multilingual AI Enhancement**
- **Universal Language Support**: Ask questions in Spanish, French, German, Italian, Portuguese, Japanese, Chinese, and more
- **Intelligent Translation**: OpenAI automatically detects language and translates to English for optimal local model comprehension
- **Native Response Language**: Local models receive instructions to respond in your original language
- **Performance Boost**: Combines English query optimization with multilingual response capability
- **Real-time Indicators**: Language panel shows detection status and translation activity

### 🔧 **Query Optimization with Dual AI**
- **Before**: "sort list" → Basic response
- **After**: OpenAI enhances to "Write a well-documented Python function with error handling that sorts a list..." → Superior response
- **Transparency**: See both original and optimized queries in the interface
- **Intelligence**: OpenAI analyzes intent and optimizes for the selected model's strengths

### 💬 **Conversation Memory & Context**
- **Multi-turn Conversations**: "Write a function" → "Explain that code" → "Make it more complex"
- **Context Awareness**: Remembers previous messages and maintains conversation flow
- **Smart References**: Understands "that code", "the previous example", "my function"
- **Session Management**: 10-message memory window with automatic cleanup

### 🎯 **Enhanced Model Routing**
- **Specialized Selection**: Coding → qwen2.5-coder, Math → phi3, Creative → llama3.2
- **Performance Optimization**: Tracks model success rates and response times
- **Auto-downloads**: Fetches recommended models as needed
- **Fallback Logic**: Graceful degradation when preferred models unavailable

## 🏗️ System Architecture

![AI Society Architecture](schema_color.png)

The system employs a sophisticated dual AI architecture combining commercial AI intelligence with local model execution:

### Dual AI Intelligence Flow

1. **Query Reception**: User sends message in any supported language via WebSocket
2. **Language Detection**: OpenAI automatically detects the query language
3. **Translation Layer**: Non-English queries translated to English for optimal local model performance
4. **Memory Integration**: System adds to conversation history and builds context
5. **OpenAI Analysis**: GPT-4.1-mini analyzes query and optimizes it for better results
6. **Model Selection**: AI recommends optimal local model based on query type and available models
7. **Response Instructions**: Local model receives query with instruction to respond in original language
8. **Local Execution**: Enhanced query runs on selected local model with language instructions
9. **Response Enhancement**: Results include optimization details, memory context, and language info
10. **Memory Update**: Conversation history updated for future context

This hybrid approach combines the intelligence of commercial AI with the privacy and efficiency of local models, while supporting global users through intelligent multilingual processing.

## 📋 Testing & Validation

### Test System
```bash
# Run comprehensive system tests
./test_system.py

# Test multilingual capabilities
python test_multilingual.py

# Test individual components
python test_conversation_memory.py
python test_query_optimization.py
```

### Example Usage Scenarios

#### **Query Optimization in Action**
```
👤 User Input: "sort list"

🔧 OpenAI Enhancement: "Write a well-documented Python function with error handling 
   that sorts a list of integers in ascending order using an efficient algorithm. 
   Include type hints, docstring, and example usage."

🤖 Selected Model: qwen2.5-coder (specialized for coding)
⚡ Result: High-quality, comprehensive code with documentation
```

#### **Conversation Memory in Action**
```
👤 "Write a Python function to calculate fibonacci"
🤖 [Provides fibonacci function] 🧠 2 messages

👤 "Can you explain how that algorithm works?"  
🤖 [Explains the fibonacci algorithm from previous message] 🧠 4 messages

👤 "Make it more efficient using memoization"
🤖 [Improves the previous function with memoization] 🧠 6 messages
```

#### **Web Interface Features**
- **🌍 Language Panel**: Real-time language detection and translation status
- **🧠 Memory Indicators**: Shows conversation length and context usage
- **🔧 Query Optimization**: Displays original vs enhanced queries
- **🎯 Model Selection**: Shows reasoning for model choice
- **⚡ Performance Metrics**: Real-time response times and confidence scores
- **📊 Status Updates**: Live updates with optimization, memory, and language info

## 📁 Project Structure

```
ai-society/
├── src/
│   ├── daemon/                     # Model discovery
│   └── routing/                    # Routing logic
├── web/
│   └── app.py                      # Web interface
├── config/
│   └── router_config.json          # Configuration
├── requirements.txt                # Dependencies
├── setup.sh                       # Setup script
└── start.sh                       # Start script
```

## Configuration

Enhanced configuration in `config/router_config.json` with new AI features:

```json
{
  "max_model_size": "8GB",
  "openai_meta_routing": {
    "enabled": true,
    "model": "gpt-4.1-mini",
    "cache_decisions": true,
    "cost_optimization": {
      "max_requests_per_hour": 200,
      "max_daily_cost_usd": 5.0,
      "fallback_on_rate_limit": true
    },
    "prompt_optimization": {
      "include_model_specs": true,
      "include_previous_success": true,
      "format_structured_response": true
    }
  },
  "specialization_weights": {
    "coding": 1.5,
    "math": 1.3,
    "reasoning": 1.4,
    "creative": 1.2,
    "conversation": 1.1
  },
  "performance_tracking": {
    "enabled": true,
    "track_optimization_impact": true,
    "conversation_analytics": true
  }
}
```

## OpenAI Integration (Recommended)

For optimal performance with query optimization and intelligent routing:

1. **Set your API key:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. **Enable in config:**
```json
{
  "openai_meta_routing": {
    "enabled": true,
    "model": "gpt-4o-mini"
  }
}
```

### **What OpenAI Integration Provides:**

- **🔧 Query Optimization**: Transforms vague queries into specific, effective prompts
- **🎯 Smart Model Selection**: AI-powered analysis of query requirements
- **📈 Better Results**: Dramatically improved response quality through enhanced prompts
- **💰 Cost Efficient**: Uses gpt-4o-mini for analysis (~$0.01 per 1000 requests)
- **🔄 Fallback Safe**: System works without OpenAI, but with reduced optimization

### **Example Optimizations:**

| Original Query | OpenAI Enhancement |
|---|---|
| "sort list" | "Write a well-documented Python function with error handling..." |
| "quantum" | "Explain quantum computing in simple terms with examples..." |
| "5+3*2" | "Calculate step-by-step showing order of operations..." |

## � Configuration & Setup

### **Enhanced Workflow with Dual AI Intelligence**

## 📚 Development & Contributing

For detailed development information, see:
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development guide and architecture
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

### Development Commands
```bash
# System testing
./test_system.py

# Component testing  
python test_multilingual.py
python test_conversation_memory.py
python test_query_optimization.py

# Direct OpenAI testing
python test_direct_openai.py
```

## 📄 License & Credits

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Acknowledgments
- **Ollama team** for excellent local LLM infrastructure
- **OpenAI** for API integration capabilities  
- **FastAPI** for the robust web framework
- **FAISS** for efficient vector similarity search
- **Community contributors** for feedback and improvements

### Support & Community
- **GitHub Issues**: [Report bugs and request features](https://github.com/dexmac221/AiSociety/issues)
- **Documentation**: [Full documentation](docs/)
- **Changelog**: [Version history](CHANGELOG.md)

---

*AI Society - Democratizing access to intelligent AI routing for everyone* 🚀
