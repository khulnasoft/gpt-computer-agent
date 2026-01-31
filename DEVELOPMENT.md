# Aideck Development Guide

This guide will help you set up and contribute to the Aideck project.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/KhulnaSoft/aideck.git
cd aideck
./setup.sh
```

### 2. Configure Environment

Edit the `.env` file with your API keys:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
```

### 3. Start Development Server

```bash
./dev.sh
```

The application will be available at:
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🛠 Development Workflow

### Environment Management

The project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

```bash
# Install dependencies
uv sync

# Install with optional dependencies
uv sync --extra dev --extra rag --extra storage

# Add new dependency
uv add package-name

# Remove dependency
uv remove package-name
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_file.py

# Run with coverage
uv run pytest --cov=src/aideck

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Run linting
uv run pre-commit run --all-files

# Format code
uv run black src/aideck
uv run isort src/aideck

# Type checking
uv run mypy src/aideck
```

### Database Management

```bash
# Initialize database
uv run python -c "from src.aideck.db.session import engine; from src.aideck.db.base import Base; Base.metadata.create_all(bind=engine)"

# Run migrations (if using Alembic)
uv run alembic upgrade head
```

## 📁 Project Structure

```
aideck/
├── src/aideck/           # Main source code
│   ├── api/             # FastAPI routes
│   ├── agent/           # Agent implementations
│   ├── core/            # Core functionality
│   ├── gui/             # GUI components
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── tools/           # Tool implementations
│   └── utils/           # Utility functions
├── tests/               # Test files
├── .github/workflows/   # CI/CD workflows
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | No | - |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `DATABASE_URL` | Database connection | No | sqlite:///./aideck.db |
| `DEBUG` | Debug mode | No | false |
| `LOG_LEVEL` | Logging level | No | INFO |

### LLM Providers

The application supports multiple LLM providers:

```python
# In your code
from aideck.llm import LLMManager

llm = LLMManager.get_provider("openai")  # or "anthropic"
```

## 🧪 Testing

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient
from src.aideck.api import app

def test_example():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

### Test Categories

- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test API endpoints
- **E2E Tests**: Test complete user workflows

## 🔀 Git Workflow

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-issue` - Critical fixes
- `docs/documentation-update` - Documentation

### Commit Messages

```
type(scope): description

Examples:
feat(api): add new user endpoint
fix(db): resolve connection timeout
docs: update installation guide
```

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Run full test suite
4. Create pull request
5. Address review comments
6. Merge after approval

## 📚 API Development

### Adding New Endpoints

```python
# src/aideck/api/router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    return {"message": "Hello World"}
```

### Adding Middleware

```python
# src/aideck/api/middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)
        # Process response
        return response
```

## 🚀 Deployment

### Local Development

```bash
# Development mode
uv run uvicorn src.aideck.api:app --reload

# Production mode
uv run uvicorn src.aideck.api:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build image
docker build -t aideck .

# Run container
docker run -p 8000:8000 -v $(pwd)/.env:/app/.env aideck
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the full test suite
6. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/KhulnaSoft/aideck/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KhulnaSoft/aideck/discussions)
- **Discord**: [Join our community](https://discord.gg/qApFmWMt8x)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
