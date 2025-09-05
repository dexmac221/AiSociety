# AI Society - LLM Model Router

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Enhanced-orange.svg)](https://openai.com/)

> 🎯 **Democratizing AI Access with Intelligent Routing**  
> A Python-based model routing system that intelligently selects appropriate local LLMs for different types of queries. Features advanced multilingual support, conversation memory, and OpenAI-enhanced routing for superior query analysis and optimization.

![AI Society Web Interface](web_interface.png)

##  What is AI Society?

AI Society is an advanced model routing system that combines **dual AI intelligence** - using OpenAI's superior query analysis with efficient local model execution. It features conversation memory for extended interactions and **multilingual support** for global accessibility.

### ✨ Core Features

- **🌍 Multilingual Intelligence** - Automatic language detection and translation for optimal performance
- **🧠 Dual AI Architecture** - OpenAI meta-routing + Local model execution  
- **🔧 Query Optimization** - Automatically enhances queries for dramatically better results
- **💬 Conversation Memory** - Multi-turn conversations with hybrid FAISS indexing
- **🎯 Smart Model Selection** - AI-powered routing to specialized models
- **⚡ Performance Tracking** - Comprehensive monitoring and analytics

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Ollama** installed and running
- **GPU with 8GB+ VRAM** (tested on RTX 3090)
- **OpenAI API key** (optional, for enhanced routing)

### Installation
```bash
# Clone and setup
git clone https://github.com/dexmac221/AiSociety.git
cd AiSociety

# Automated setup
chmod +x setup.sh && ./setup.sh

# Quick start
chmod +x start.sh && ./start.sh
```

### Access
- **Web Interface**: http://localhost:8000
- **WebSocket API**: ws://localhost:8000/ws
- **REST API**: http://localhost:8000/api/health

## ✅ Current Status (September 2025)

🎯 **System is LIVE and fully operational!**

**Latest Features:**
- ✅ 14 cutting-edge 2025 models integrated
- ✅ Enhanced UI with dark mode and 8+ example categories  
- ✅ Multilingual support with OpenAI translation framework
- ✅ Hybrid memory system with conversation context
- ✅ Real-time technical dashboard with performance metrics

## 🎯 Model Inventory (14 Latest 2025 Models)

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

### 🎯 **General Purpose**
- **Llama3.1:8B** - Meta's latest reasoning and code model
- **Mistral:7B** - Advanced reasoning and function calling

## 🏗️ System Architecture

![System Architecture](schema_color.png)

### Dual AI Intelligence Flow

1. **Query Reception** - User sends message in any supported language
2. **Language Detection** - OpenAI automatically detects query language  
3. **Translation Layer** - Non-English queries translated for optimal performance
4. **Memory Integration** - System builds context from conversation history
5. **OpenAI Analysis** - GPT-4.1-mini analyzes and optimizes query
6. **Model Selection** - AI recommends optimal local model
7. **Local Execution** - Enhanced query runs on selected model
8. **Response Enhancement** - Results include optimization details and context

## 🌍 Multilingual AI Enhancement

- **Universal Language Support** - Spanish, French, German, Italian, Portuguese, Japanese, Chinese, and more
- **Intelligent Translation** - OpenAI detects language and translates for optimal comprehension
- **Native Response Language** - Models receive instructions to respond in original language
- **Real-time Indicators** - Language panel shows detection and translation status

## 💬 Conversation Memory System

- **Multi-turn Conversations** - "Write a function" → "Explain that code" → "Make it more efficient"
- **Context Awareness** - Remembers previous messages and maintains flow
- **Smart References** - Understands "that code", "the previous example"
- **Hybrid Architecture** - FAISS indexing with OpenAI summarization

## 🔧 Query Optimization

### Before vs After
| Original Query | OpenAI Enhancement |
|---|---|
| "sort list" | "Write a well-documented Python function with error handling..." |
| "quantum" | "Explain quantum computing in simple terms with examples..." |
| "5+3*2" | "Calculate step-by-step showing order of operations..." |

## ⚙️ Configuration

### OpenAI Integration (Recommended)
```bash
# Set API key for enhanced routing
export OPENAI_API_KEY="your-api-key-here"
```

### Configuration File (`config/router_config.json`)
```json
{
  "max_model_size": "8GB",
  "openai_meta_routing": {
    "enabled": true,
    "model": "gpt-4.1-mini",
    "cache_decisions": true
  },
  "specialization_weights": {
    "coding": 1.5,
    "math": 1.3,
    "creative": 1.2
  }
}
```

##  Testing & Validation

```bash
# Run comprehensive tests
./test_system.py

# Test specific components
python test_multilingual.py
python test_conversation_memory.py
python test_query_optimization.py
```

## 🌟 Example Usage

### Coding Query
```
👤 "Debug this Python code: def fibonacci(n): return n + fibonacci(n-1)"
🔧 Enhanced: "Analyze and debug this recursive Python function..."
🤖 qwen2.5-coder → Identifies missing base case and infinite recursion
```

### Conversation Memory
```
👤 "Write a Python sorting function"
🤖 [Provides function] 🧠 2 messages

👤 "Explain how that works"  
🤖 [Explains previous function] 🧠 4 messages

👤 "Make it more efficient"
🤖 [Improves with optimizations] 🧠 6 messages
```

## 📁 Project Structure

```
AiSociety/
├── src/
│   ├── daemon/          # Model discovery
│   ├── memory/          # Conversation memory  
│   └── routing/         # Intelligent routing
├── web/
│   └── app.py          # FastAPI web interface
├── config/             # Configuration files
├── docs/               # Documentation
├── requirements.txt    # Dependencies
├── setup.sh           # Setup script
└── start.sh           # Start script
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting issues and feature requests
- Development setup and workflow
- Code style and testing requirements
- Pull request process

## 📚 Documentation

- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development guide and architecture
- **[OPENAI_META_ROUTING.md](docs/OPENAI_META_ROUTING.md)** - Technical deep dive on meta-routing
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates
- **[SECURITY.md](SECURITY.md)** - Security policy and reporting

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama team** for excellent local LLM infrastructure
- **OpenAI** for API integration capabilities  
- **FastAPI** for the robust web framework
- **FAISS** for efficient vector similarity search

## 📞 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/dexmac221/AiSociety/issues)
- **Discussions**: [Community discussions and questions](https://github.com/dexmac221/AiSociety/discussions)
