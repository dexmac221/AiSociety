# AI Society - LLM Model Router

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.com/)

## Overview

AI Society is a model routing system that helps select appropriate local LLMs for different types of queries. It provides a web interface and can optionally use OpenAI's API to help with model selection decisions.

### What it does

- **Model Selection**: Analyzes queries and routes them to suitable local models
- **OpenAI Integration**: Can use GPT models for intelligent routing decisions (optional)
- **Web Interface**: Simple chat interface for testing different models
- **Model Discovery**: Scans available Ollama models and manages downloads
- **Performance Tracking**: Basic monitoring of response times and model usage

### What it doesn't do

- This isn't a revolutionary architecture - it's a practical tool for managing multiple local models
- It doesn't magically make models faster or better - just helps pick the right one
- Power savings depend on your usage patterns and hardware setup
- Performance varies based on the models you have available

## Architecture

```
Web Interface ←→ FastAPI Server ←→ Model Router
                                       ↓
                                Model Discovery
                                       ↓
                              Local Ollama Models
```

The system can optionally use OpenAI's API to help make routing decisions, but falls back to local heuristics if that's not available or desired.
- **Linux/macOS/WSL** (recommended)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-society.git
cd ai-society
```

2. **Run the setup script:**
```bash
chmod +x setup.sh
## Quick Start

### Prerequisites

- **Python 3.8+**
- **Ollama** installed and running
- **GPU with sufficient VRAM** (tested on RTX 3090, but should work on other hardware)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dexmac221/AiSociety.git
cd AiSociety
```

2. **Run setup:**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Start the system:**
```bash
chmod +x start.sh
./start.sh
```

4. **Open your browser:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

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

Basic configuration in `config/router_config.json`. Key settings:

```json
{
  "max_model_size": "8GB",
  "openai_meta_routing": {
    "enabled": false,
    "model": "gpt-4o-mini"
  },
  "specialization_weights": {
    "coding": 1.5,
    "math": 1.3,
    "reasoning": 1.4
  }
}
```

## OpenAI Integration (Optional)

If you want to use OpenAI's API to help with routing decisions:

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

This will use OpenAI's API to analyze queries and recommend which local model to use. It's optional - the system works fine without it using local heuristics.

## Supported Models

The system works with any Ollama models. Some examples:

- **llama3.2:3b** - Fast, general purpose
- **qwen2.5-coder:7b** - Good for coding tasks  
- **phi3:mini** - Decent at math
- **mistral:7b** - General reasoning
- **gemma2:9b** - Larger general model

## How It Works

1. **Query comes in** via the web interface
2. **Router analyzes** the query type (coding, math, general, etc.)
3. **Selects a model** based on available models and simple heuristics
4. **Downloads if needed** (if the selected model isn't local)
5. **Runs inference** on the selected model
6. **Returns response** with info about which model was used

Pretty straightforward - nothing fancy, just a practical tool for managing multiple models.

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws` - Real-time chat interface

### REST API
- `GET /api/health` - System health check
- `GET /api/stats` - System statistics  
- `GET /api/models` - Available models
- `POST /api/refresh` - Refresh model registry

## Web Interface

- Real-time chat via WebSocket
- Shows which model handled each query
- Basic performance metrics
- Mobile-friendly design

## Development

To run tests:
```bash
python test_system.py
```

To test OpenAI integration:
```bash
python test_direct_openai.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test them
5. Open a Pull Request

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Notes

This is a simple tool for managing multiple local LLMs. It's not groundbreaking technology, just a practical solution for organizing and routing between different models based on query type. Use it if it's helpful for your workflow.

## 🙏 Acknowledgments

- **Ollama Team** - For the excellent local LLM platform
- **Meta, Google, Mistral, Alibaba** - For open-source models
- **FastAPI Team** - For the amazing web framework
- **Community Contributors** - For feedback and improvements

## 🔮 Future Roadmap

- [ ] **Multi-GPU Support** - Distribute models across multiple GPUs
- [ ] **Fine-tuning Integration** - Custom model training pipeline
- [ ] **Advanced Analytics** - Detailed performance dashboards
- [ ] **Plugin System** - Extensible model integrations
- [ ] **Voice Interface** - Speech-to-text integration
- [ ] **Mobile App** - Native mobile applications

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/ai-society/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-society/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-society/discussions)

---

**Made with ❤️ for the AI community. Democratizing access to powerful AI, one query at a time.**
