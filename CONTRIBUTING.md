# Contributing to AI Society

Thank you for your interest in contributing to AI Society! This guide will help you get started.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - GPU model and VRAM
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Feature Requests

1. **Check the roadmap** in README.md first
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with implementation details
4. **Consider backwards compatibility**

### Code Contributions

#### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/ai-society.git
   cd ai-society
   ```

3. **Set up development environment**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Code Style

- **Follow PEP 8** for Python code style
- **Use type hints** where appropriate
- **Write docstrings** for all functions and classes
- **Add logging** for important operations
- **Include error handling** with meaningful messages

#### Example Code Style:

```python
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def analyze_query(query: str, context: Optional[Dict] = None) -> List[str]:
    """
    Analyze a user query to determine required specializations.
    
    Args:
        query: The user's input query
        context: Optional context from previous interactions
        
    Returns:
        List of specialization tags required for this query
        
    Raises:
        ValueError: If query is empty or invalid
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
        
    logger.info(f"Analyzing query: {query[:50]}...")
    
    # Your implementation here
    return specializations
```

#### Testing

1. **Write tests** for new functionality:
   ```bash
   # Run existing tests
   python -m pytest tests/
   
   # Add your tests in tests/ directory
   ```

2. **Test with different scenarios**:
   - Various query types
   - Different model availability
   - Error conditions
   - Edge cases

#### Documentation

1. **Update README.md** if needed
2. **Add docstrings** to new functions
3. **Update configuration examples**
4. **Add API documentation** for new endpoints

#### Commit Guidelines

**Use conventional commits**:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples**:
```bash
git commit -m "feat: add support for custom specializations"
git commit -m "fix: resolve model download timeout issue"
git commit -m "docs: update configuration guide"
```

### Pull Request Process

1. **Update documentation** as needed
2. **Add tests** for new functionality
3. **Ensure CI passes** (when available)
4. **Request review** from maintainers
5. **Address feedback** promptly

#### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested locally
- [ ] Added unit tests
- [ ] Updated integration tests

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors
```

## 🏗️ Development Areas

### High Priority
- **Performance optimizations**
- **Model integration improvements**
- **Error handling enhancements**
- **Testing coverage**

### Medium Priority
- **Web interface improvements**
- **Configuration enhancements**
- **Logging and monitoring**
- **Documentation improvements**

### Future Features
- **Multi-GPU support**
- **Custom model training**
- **Advanced analytics**
- **Mobile applications**

## 🔧 Technical Guidelines

### Model Integration

When adding support for new models:

1. **Update model database** in `model_discovery.py`
2. **Add specialization mappings**
3. **Consider resource requirements**
4. **Test with various query types**

### API Changes

For API modifications:

1. **Maintain backwards compatibility**
2. **Update OpenAPI documentation**
3. **Add proper error responses**
4. **Include request/response examples**

### Configuration

When adding configuration options:

1. **Provide sensible defaults**
2. **Add validation**
3. **Update documentation**
4. **Consider environment variables**

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes
- **Minor**: New features
- **Patch**: Bug fixes

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Test on multiple platforms
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release

## 📞 Getting Help

- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check the wiki first

## 🙏 Recognition

Contributors will be:
- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Credited in documentation**

Thank you for helping make AI Society better for everyone! 🚀
