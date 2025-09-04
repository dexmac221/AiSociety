# AI Society - Dynamic LLM Routing System

## 🎯 Project Overview
A Python-based dynamic LLM routing system that democratizes AI access by intelligently routing queries to specialized local models. Uses 40-50% less power than monolithic models while maintaining excellent performance.

## 📁 Complete Project Structure
```
ai-society/
├── src/
│   ├── __init__.py
│   ├── daemon/
│   │   ├── __init__.py
│   │   └── model_discovery.py          # Ollama library scanner & daemon
│   └── routing/
│       ├── __init__.py
│       └── intelligent_router.py       # Smart model selection logic
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
├── main.py                           # Alternative entry point
└── README.md                         # Complete documentation
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
- **Model Discovery Daemon**: Automatically scans Ollama library for latest models
- **Intelligent Router**: Analyzes queries and selects optimal specialized models  
- **Dynamic Downloads**: Automatically downloads best models on-demand
- **Power Optimization**: Targets 7B-13B models optimized for RTX 3090
- **Performance Tracking**: Monitors model performance for better future selections

## 🎨 Web Interface Features
- Real-time WebSocket chat at http://localhost:8000
- Model transparency showing which model handled each query
- Performance metrics and response times
- Mobile responsive design
- API documentation at http://localhost:8000/docs

## 🤖 Supported Model Types
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
