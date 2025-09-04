# AI Society - LLM Model Router

## 🎯 Project Overview
A Python-based model routing system that helps select appropriate local LLMs for different types of queries. Provides a web interface and can optionally use OpenAI's API for routing decisions.

## 📁 Project Structure
```
ai-society/
├── src/
│   ├── __init__.py
│   ├── daemon/
│   │   ├── __init__.py
│   │   └── model_discovery.py          # Ollama library scanner
│   └── routing/
│       ├── __init__.py
│       ├── intelligent_router.py       # Model selection logic
│       ├── enhanced_intelligent_router.py # OpenAI-enhanced routing
│       └── openai_meta_router.py       # OpenAI API integration
├── web/
│   └── app.py                         # FastAPI web application
├── config/
│   └── router_config.json             # System configuration
├── data/                              # Auto-created: model cache & performance data
├── venv/                              # Auto-created: virtual environment
├── logs/                              # Auto-created: application logs
├── .github/
│   └── copilot-instructions.md        # This file
├── requirements.txt                   # Python dependencies
├── setup.sh                          # Automated setup script (executable)
├── start.sh                          # Quick start script (executable)  
├── test_system.py                     # System testing script (executable)
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
- **Model Discovery**: Scans Ollama library for available models
- **Routing Logic**: Analyzes queries and selects appropriate models  
- **Optional OpenAI Integration**: Uses GPT models for routing decisions
- **Web Interface**: FastAPI + WebSocket for real-time chat
- **Performance Tracking**: Basic monitoring of model usage

## 🎨 Web Interface Features
- Real-time WebSocket chat at http://localhost:8000
- Shows which model handled each query
- Basic performance metrics and response times
- Mobile responsive design
- API documentation at http://localhost:8000/docs

## 🤖 Model Types
- **Coding**: qwen2.5-coder:7b, codellama:7b
- **Math**: phi3:mini, qwen2.5:7b  
- **General**: llama3.2:3b, gemma2:9b
- **Reasoning**: mistral:7b, yi:9b
- **Conversation**: neural-chat:7b, vicuna:7b

## 🔌 API Endpoints
- `ws://localhost:8000/ws` - WebSocket chat
- `GET /api/health` - System health
- `GET /api/stats` - Performance stats
- `GET /api/models` - Available models
- `POST /api/refresh` - Refresh model registry
