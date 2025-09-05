# AI Society - LLM Model Router

## 🎯 Project Overview
A Python-based model routing system that helps select appropriate local LLMs for different types of queries. Features advanced multilingual support, conversation memory, and OpenAI-enhanced routing for intelligent model selection.

## 📁 Project Structure
````instructions
# AI Society - LLM Model Router

## 🎯 Project Overview
A Python-based model routing system that helps select appropriate local LLMs for different types of queries. Features advanced multilingual support, conversation memory, and OpenAI-enhanced routing for intelligent model selection.

## 📁 Project Structure
```
ai-society/
├── src/
│   ├── __init__.py
│   ├── daemon/
│   │   ├── __init__.py
│   │   └── model_discovery.py          # Ollama library scanner
│   ├── memory/
│   │   ├── __init__.py
│   │   └── hybrid_memory.py            # Conversation memory system
│   └── routing/
│       ├── __init__.py
│       ├── intelligent_router.py       # Model selection logic
│       ├── enhanced_intelligent_router.py # OpenAI-enhanced routing
│       └── openai_meta_router.py       # OpenAI API integration + multilingual
├── web/
│   └── app.py                         # FastAPI web application
├── config/
│   ├── router_config.json             # System configuration
│   ├── model_selection.json           # Latest 2025 models (14 total)
│   └── api_config.env                 # API keys and configuration
├── data/                              # Auto-created: model cache & performance data
│   └── memory/                        # Conversation memory storage
├── venv/                              # Auto-created: virtual environment
├── logs/                              # Auto-created: application logs
├── .github/
│   └── copilot-instructions.md        # This file
├── requirements.txt                   # Python dependencies
├── setup.sh                          # Automated setup script (executable)
├── start.sh                          # Quick start script (executable)  
├── test_system.py                     # System testing script (executable)
├── test_multilingual.py              # Multilingual testing script
├── test_direct_openai.py              # OpenAI integration test
├── test_conversation_memory.py        # Conversation memory test
├── test_query_optimization.py         # Query optimization test
└── README.md                         # Documentation
```
├── test_direct_openai.py              # OpenAI integration test
├── main.py                           # Alternative entry point
└── README.md                         # Documentation
```

## 🚀 Quick Start Commands
```bash
# Setup (first time only)
./setup.sh

# Start system
./start.sh

# Test system
./test_system.py

# Manual start
python web/app.py
```

## 🔧 Technical Architecture
- **Model Discovery**: Scans Ollama library for available models (14 latest 2025 models)
- **Multilingual Support**: Automatic language detection and translation using OpenAI
- **Conversation Memory**: Hybrid memory system with FAISS indexing and context awareness
- **Routing Logic**: Analyzes queries and selects appropriate models with confidence scoring
- **OpenAI Integration**: Uses GPT-4.1-mini for routing decisions and query optimization
- **Web Interface**: FastAPI + WebSocket for real-time chat with memory and language indicators
- **Performance Tracking**: Comprehensive monitoring of model usage and response times

## 🎨 Web Interface Features
- Real-time WebSocket chat at http://localhost:8000
- Shows which model handled each query with confidence scores
- Conversation memory indicators and context usage
- Language detection and translation status
- Technical dashboard with performance metrics, memory stats, and model information
- Mobile responsive design with enhanced dark mode
- 8 diverse example categories for easy testing

## 🤖 Model Categories (14 Total)
- **Coding**: Qwen2.5-Coder:7B, DeepSeek-Coder-v2:16B, CodeLlama:7B
- **Math**: Phi-4:14B, Qwen2.5:7B, Phi3:mini
- **Creative**: Hermes-4:14B, Yi:9B, Neural-Chat:7B
- **Multimodal**: Qwen2.5-Omni:7B, Gemma-3:27B/4B, Gemma-3:1B
- **General**: Qwen2.5:7B, Llama3.1:8B, Mistral:7B, OpenAI-OSS:20B
- **Efficiency**: Apple-FastVLM:7B, NVIDIA-Nemotron-Nano:12B

## 🌍 Multilingual Features
- **Language Detection**: Automatic identification of 20+ languages
- **Translation Layer**: OpenAI-powered translation to English for optimal model performance
- **Response Instructions**: Models respond in user's original language
- **Real-time Indicators**: Language panel shows detection and translation status

## 🧠 Memory System
- **Hybrid Architecture**: FAISS vector indexing + OpenAI summarization
- **Context Awareness**: Multi-turn conversations with smart references
- **Session Management**: 10-message memory window with automatic cleanup
- **Performance Tracking**: Memory usage and context effectiveness metrics

## 🔌 API Endpoints
- `ws://localhost:8000/ws` - WebSocket chat
- `GET /api/health` - System health
- `GET /api/stats` - Performance stats
- `GET /api/models` - Available models
- `POST /api/refresh` - Refresh model registry
