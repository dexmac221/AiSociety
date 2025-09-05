# Development Setup Guide

This guide will help you set up a development environment for contributing to AI Society.

## 🛠️ Prerequisites

### Required Software

- **Python 3.8+** - Programming language
- **Git** - Version control
- **Ollama** - Local LLM management
- **GPU with 8GB+ VRAM** - For model inference (RTX 3090 recommended)

### Required Python Packages
- **FastAPI** - Web framework
- **uvicorn** - ASGI server
- **ollama** - Ollama client library
- **openai** - OpenAI API client (optional, for enhanced routing)
- **sentence-transformers** - For conversation memory embeddings
- **faiss-cpu** - Vector similarity search for memory system
- **python-dotenv** - Environment variable management

### Optional Development Tools

- **VS Code** - Recommended IDE with Python extension
- **Docker** - For containerized development
- **Postman** - For API testing

## 🚀 Quick Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/AiSociety.git
cd AiSociety

# Add upstream remote
git remote add upstream https://github.com/dexmac221/AiSociety.git
```

### 2. Environment Setup

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 3. Configure OpenAI API (Optional but Recommended)

For enhanced routing and multilingual support:

```bash
# Copy and edit API configuration
cp config/api_config.env config/.env
nano config/.env

# Add your OpenAI API key:
OPENAI_API_KEY=your_actual_openai_api_key_here
# Remove or comment out the placeholder org ID:
# OPENAI_ORG_ID=your_org_id_here_optional
```

### 4. Install Development Dependencies

```bash
# Install additional development tools
pip install pytest pytest-asyncio black flake8 mypy pre-commit

# Setup pre-commit hooks
pre-commit install
```

### 4. Verify Installation

```bash
# Test the system
python test_system.py

# Start development server
python web/app.py
```

## 🏗️ Development Workflow

### Branch Management

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Keep your fork updated
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### Code Quality

We use several tools to maintain code quality:

#### Formatting with Black
```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

#### Linting with Flake8
```bash
# Run linter
flake8 src/ web/ --max-line-length=88

# With specific error codes
flake8 src/ --select=E9,F63,F7,F82
```

#### Type Checking with MyPy
```bash
# Check types
mypy src/ --ignore-missing-imports
```

### Testing

#### Unit Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_router.py

# Run with verbose output
pytest -v
```

#### Integration Tests
```bash
# Test with actual models (requires Ollama)
python test_system.py

# Test specific components
python -m src.routing.intelligent_router
python -m src.daemon.model_discovery
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

## 🧪 Testing Guidelines

### Writing Tests

Create tests in the `tests/` directory:

```python
# tests/test_router.py
import pytest
from src.routing.intelligent_router import IntelligentModelRouter

class TestIntelligentRouter:
    def test_query_analysis(self):
        router = IntelligentModelRouter()
        specializations = router._analyze_query("Write a Python function")
        assert "coding" in specializations
    
    @pytest.mark.asyncio
    async def test_model_selection(self):
        router = IntelligentModelRouter()
        # Add your async tests here
```

### Test Categories

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test component interactions
3. **System Tests** - Test complete workflows
4. **Performance Tests** - Test response times and resource usage

## 📁 Project Structure

```
ai-society/
├── src/                          # Core application code
│   ├── daemon/                   # Model discovery daemon
│   │   ├── __init__.py
│   │   └── model_discovery.py
│   └── routing/                  # Intelligent routing logic
│       ├── __init__.py
│       └── intelligent_router.py
├── web/                          # Web application
│   └── app.py                    # FastAPI application
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_router.py
│   └── test_discovery.py
├── config/                       # Configuration files
│   └── router_config.json
├── docs/                         # Documentation
├── .github/                      # GitHub workflows and templates
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.sh                      # Setup script
├── start.sh                      # Start script
└── README.md                     # Project documentation
```

## 🔧 Configuration

### Development Configuration

Create a development configuration file:

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "auto_reload": true,
  "max_model_size": "8GB",
  "development_mode": true,
  "mock_models": false
}
```

### Environment Variables

Create a `.env` file for development:

```bash
# .env
DEBUG=true
LOG_LEVEL=DEBUG
OLLAMA_HOST=http://localhost:11434
DEVELOPMENT_MODE=true
```

## 🤖 Model Development

### Adding New Models

1. **Update Model Database** in `src/daemon/model_discovery.py`:
```python
models = [
    {
        'name': 'your-new-model',
        'tags': ['latest', '7b'],
        'specializations': ['your-specialization'],
        'performance_score': 90.0,
        # ... other metadata
    }
]
```

2. **Add Specialization Logic** in `src/routing/intelligent_router.py`:
```python
def _analyze_query(self, query: str) -> List[str]:
    if 'your_keyword' in query.lower():
        specializations.append('your-specialization')
```

3. **Test the New Model**:
```bash
# Test model discovery
python -c "from src.daemon.model_discovery import OllamaLibraryScanner; scanner = OllamaLibraryScanner(); print(scanner.fetch_library_models())"

# Test routing
python -c "from src.routing.intelligent_router import IntelligentModelRouter; router = IntelligentModelRouter(); print(router.query_model('test query'))"
```

### Performance Testing

Test model performance:

```python
import time
from src.routing.intelligent_router import IntelligentModelRouter

router = IntelligentModelRouter()

# Test different query types
queries = [
    "Write a Python function to sort a list",
    "What is 15 * 23 + 89?",
    "Explain quantum computing"
]

for query in queries:
    start_time = time.time()
    result = router.query_model(query)
    end_time = time.time()
    
    print(f"Query: {query[:30]}...")
    print(f"Model: {result['model']}")
    print(f"Time: {end_time - start_time:.2f}s")
    print("-" * 50)
```

## 🐛 Debugging

### Debug Mode

Run in debug mode:

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug
python web/app.py
```

### Common Issues

1. **Import Errors**:
   - Ensure `__init__.py` files exist
   - Check Python path configuration
   - Verify virtual environment activation

2. **Ollama Connection**:
   - Check if Ollama is running: `ollama list`
   - Verify host configuration
   - Check firewall settings

3. **Model Download Issues**:
   - Check disk space
   - Verify network connection
   - Check Ollama logs

### Debugging Tools

```python
# Add debugging to your code
import logging
import pdb

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Debug message")
    pdb.set_trace()  # Breakpoint
    # Your code here
```

## 📊 Performance Monitoring

### Profiling

Profile your code:

```bash
# Profile with cProfile
python -m cProfile -o profile.stats web/app.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

### Memory Monitoring

Monitor memory usage:

```python
import psutil
import GPUtil

# Monitor system resources
def monitor_resources():
    # CPU and RAM
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    # GPU
    gpus = GPUtil.getGPUs()
    gpu_usage = gpus[0].load * 100 if gpus else 0
    gpu_memory = gpus[0].memoryUsed if gpus else 0
    
    print(f"CPU: {cpu_percent}%")
    print(f"RAM: {memory.percent}%")
    print(f"GPU: {gpu_usage}%")
    print(f"GPU Memory: {gpu_memory}MB")
```

## 🚀 Deployment

### Local Development Server

```bash
# Development server with auto-reload
uvicorn web.app:app --reload --host 0.0.0.0 --port 8000

# With custom configuration
uvicorn web.app:app --reload --env-file .env
```

### Production Build

```bash
# Create production build
python setup.py sdist bdist_wheel

# Install from build
pip install dist/ai-society-*.whl
```

## 📝 Documentation

### Updating Documentation

1. **Code Documentation**:
   - Add docstrings to all functions and classes
   - Use type hints consistently
   - Include examples in docstrings

2. **API Documentation**:
   - FastAPI auto-generates docs at `/docs`
   - Add descriptions to endpoints
   - Include request/response examples

3. **User Documentation**:
   - Update README.md for user-facing changes
   - Add configuration examples
   - Include troubleshooting guides

### Documentation Format

```python
def example_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Brief description of the function.
    
    Longer description with more details about what the function does,
    how it works, and any important considerations.
    
    Args:
        param1 (str): Description of param1
        param2 (int, optional): Description of param2. Defaults to 10.
    
    Returns:
        Dict[str, Any]: Description of return value
    
    Raises:
        ValueError: When param1 is empty
        ConnectionError: When unable to connect to service
    
    Example:
        >>> result = example_function("test", 20)
        >>> print(result)
        {'status': 'success', 'data': '...'}
    """
    pass
```

## 🤝 Contributing Guidelines

### Pull Request Process

1. **Create Feature Branch**: Always work on a feature branch
2. **Write Tests**: Add tests for new functionality
3. **Update Documentation**: Keep docs current
4. **Code Review**: Request review from maintainers
5. **Address Feedback**: Respond to review comments

### Code Style Guidelines

- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Document all public functions and classes
- **Comments**: Explain complex logic
- **Naming**: Use descriptive variable and function names

## 📞 Getting Help

- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Development Chat**: Join our development discussions

Happy coding! 🚀
