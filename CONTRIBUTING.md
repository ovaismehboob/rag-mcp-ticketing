# Contributing to RAG-Based MCP Ticketing System

Thank you for your interest in contributing to this project! This guide will help you get started with contributing to our RAG-based Model Context Protocol (MCP) ticketing system.

## 🎯 Project Goals

This project demonstrates:
- **Model Context Protocol (MCP)** implementation patterns
- **Semantic Kernel** integration with custom tool providers
- **RAG (Retrieval-Augmented Generation)** systems architecture
- **Enterprise-grade AI application** development practices

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- Git
- Azure OpenAI account (for testing)
- Basic knowledge of FastAPI, SQLAlchemy, and async Python

### Quick Setup
1. Fork and clone the repository
2. Run the setup script: `./setup.sh` (Linux/Mac) or `setup.bat` (Windows)
3. Configure your Azure OpenAI credentials in `.env` files
4. Start both services and verify everything works

### Development Environment
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate.bat  # Windows

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# Run tests to verify setup
python -m pytest tests/ -v
```

## 📁 Project Structure

```
ticketingapi/
├── app/                    # Backend MCP Server
│   ├── main.py            # FastAPI application
│   ├── mcp_server.py      # MCP tool implementations
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── models/            # Data models and schemas
│   └── config/            # Configuration management
├── client/                # Frontend Semantic Kernel Client
│   ├── main.py           # Web interface
│   ├── semantic_agent.py # Semantic Kernel integration
│   ├── mcp_client.py     # MCP protocol client
│   └── templates/        # HTML templates
├── tests/                # Test suites
└── docs/                 # Additional documentation
```

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_mcp_server.py -v
python -m pytest tests/test_semantic_kernel.py -v

# Run with coverage
python -m pytest --cov=app tests/
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names that explain the scenario
- Test both success and failure cases
- Mock external dependencies (Azure OpenAI, etc.)
- Include integration tests for MCP protocol compliance

Example test structure:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestMCPTools:
    def test_create_ticket_success(self):
        """Test successful ticket creation via MCP tool."""
        # Test implementation
        
    def test_create_ticket_invalid_priority(self):
        """Test ticket creation with invalid priority."""
        # Test implementation
```

## 🎨 Code Style Guidelines

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable and function names

### Formatting Tools
```bash
# Format code with Black
black app/ client/ tests/

# Check code style with flake8
flake8 app/ client/ tests/

# Type checking with mypy
mypy app/ client/
```

### Documentation Style
- Use docstrings for all classes and functions
- Follow Google docstring format
- Include type information and examples where helpful

```python
async def create_ticket(
    title: str,
    description: str,
    priority: TicketPriority = TicketPriority.MEDIUM
) -> Ticket:
    """Create a new support ticket.
    
    Args:
        title: Brief description of the issue
        description: Detailed description of the problem
        priority: Ticket priority level
        
    Returns:
        Created ticket object with assigned ID
        
    Raises:
        ValidationError: If required fields are missing
        DatabaseError: If ticket creation fails
        
    Example:
        >>> ticket = await create_ticket(
        ...     title="Email server down",
        ...     description="Cannot send or receive emails",
        ...     priority=TicketPriority.HIGH
        ... )
    """
```

## 🔧 Contributing Guidelines

### 1. Choose an Issue
- Check the [Issues](../../issues) page for open tasks
- Look for issues labeled `good first issue` for beginners
- Comment on the issue to indicate you're working on it

### 2. Create a Branch
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 3. Make Changes
- Keep commits small and focused
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes
```bash
# Run tests
python -m pytest tests/ -v

# Check code style
black --check app/ client/ tests/
flake8 app/ client/ tests/

# Verify both services start correctly
python -m app.main &
cd client && python main.py
```

### 5. Submit Pull Request
- Push your branch to your fork
- Create a pull request with a clear description
- Include screenshots for UI changes
- Reference any related issues

## 🎯 Contribution Areas

### High Priority
- **MCP Protocol Enhancements**: Additional tools, better error handling
- **RAG Improvements**: Better embeddings, semantic search optimization
- **Testing Coverage**: More comprehensive test suites
- **Documentation**: API documentation, tutorials, examples

### Medium Priority
- **Performance Optimization**: Caching, async improvements
- **UI/UX Enhancements**: Better web interface, mobile responsiveness
- **Integration Examples**: Connect with external systems
- **Monitoring**: Logging, metrics, health checks

### Future Enhancements
- **Multi-tenant Support**: Organization isolation
- **Advanced Analytics**: Machine learning insights
- **Voice Interface**: Speech-to-text integration
- **Mobile App**: Native mobile clients

## 🐛 Bug Reports

When reporting bugs, please include:
- **Environment**: OS, Python version, dependency versions
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Logs**: Relevant error messages or logs
- **Configuration**: Relevant environment variables (without secrets)

Use this template:
```markdown
## Bug Description
Brief description of the issue

## Environment
- OS: Windows 11 / macOS 13 / Ubuntu 22.04
- Python: 3.11.2
- Semantic Kernel: 1.34.0

## Steps to Reproduce
1. Start the MCP server
2. Send this request: ...
3. Observe the error

## Expected vs Actual Behavior
**Expected**: Should create ticket successfully
**Actual**: Returns 500 error

## Logs
```
[Include relevant logs here]
```

## Configuration
- Azure OpenAI endpoint: [REDACTED]
- MCP server running on: localhost:8000
```

## 💡 Feature Requests

For new features, please:
- Check if similar functionality exists
- Describe the use case and benefits
- Consider backward compatibility
- Propose an implementation approach if possible

## 📋 Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are added/updated and passing
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] All checks pass (CI/CD pipeline)

## 🔍 Code Review Process

1. **Automated Checks**: CI pipeline runs tests and style checks
2. **Peer Review**: At least one maintainer reviews the code
3. **Testing**: Reviewers test the functionality locally
4. **Documentation**: Check that docs are updated appropriately
5. **Merge**: Approved PRs are merged into main branch

## 🎖️ Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes for significant contributions
- Invited to join the maintainer team for consistent contributors

## 📞 Getting Help

- **Documentation**: Check README.md and docs/ folder
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for private concerns

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the RAG-Based MCP Ticketing System! 🚀
