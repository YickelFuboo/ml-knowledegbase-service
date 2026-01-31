# Agent Guidelines for Pando Knowledge Base Service

FastAPI-based knowledge base service with multiple LLM providers, vector stores, and document processing. Uses Poetry and modern Python async patterns.

## Build and Development Commands

### Dependency Management
```bash
poetry install           # Install dependencies
poetry add <package>     # Add new dependency
poetry add --group dev <package>  # Add dev dependency
poetry update            # Update dependencies
```

### Running the Service
```bash
poetry run start                               # Start dev server (hot reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # Alternative
uvicorn app.main:app --host 0.0.0.0 --port 8000          # Production
curl http://localhost:8000/health              # Health check
```

### Database Migrations
```bash
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
poetry run alembic downgrade -1
```

### Testing
```bash
poetry run pytest                              # Run all tests (if tests exist)
poetry run pytest path/to/test_file.py::test_function_name  # Single test
poetry run pytest --cov=app --cov-report=html  # Coverage report
poetry run pytest -k "test_chat"               # Run tests matching pattern
```

**Note**: Test directory (`tests/`) not yet implemented. Pytest installed as dev dependency.

### Linting and Formatting (if tools added)
```bash
ruff check .   # Lint (if ruff.toml exists)
black .        # Format (if configured)
isort .        # Sort imports (if configured)
mypy app       # Type checking (if mypy.ini exists)
```

## Code Style Guidelines

- **Import Order**: Standard library → third-party → local imports, separated by blank lines
- **Naming**: `snake_case` variables/functions, `CamelCase` classes, `UPPER_SNAKE_CASE` constants, `_private_method` private members
- **Type Hints**: Required for all function arguments and return values. Async functions must have return type hints.
- **Error Handling**: Use `try/except` for expected errors, raise `HTTPException` with appropriate status codes in API endpoints
- **Logging**: Use `logging` module with custom `ColoredFormatter` from `app/logger.py`
- **Pydantic Models**: Define request/response schemas with `BaseModel`, use `Optional` for optional fields, add Chinese docstrings, include `from_attributes = True` for ORM compatibility
- **FastAPI Endpoints**: Use `@router` decorators, include `summary` and `tags`, use `response_model`, prefer `async def`, document with Chinese docstrings, use `Depends` for dependency injection
- **Async/Await Patterns**: Use `asyncio` for concurrency, `async with` for context managers, avoid blocking I/O, use `asyncio.gather` for parallel operations
- **Configuration**: Use `pydantic-settings` (see `app/config/settings.py`), access via `app.config.settings.settings`, environment variables with sensible defaults

## Common Patterns

### Factory Pattern
```python
from app.infrastructure.llms import llm_factory
model = llm_factory.create_model(provider, model_name)
```

### Dependency Injection
```python
from fastapi import Depends
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/items")
async def get_items(session: AsyncSession = Depends(get_db_session)):
    pass
```

### Middleware
```python
from app.middleware.logging import logging_middleware
app.add_middleware(logging_middleware)
```

## Testing Guidelines

- Place tests in `tests/` directory when implemented
- Use `pytest` with `pytest-asyncio` for async tests
- Mock external dependencies with `unittest.mock`
- Descriptive test names starting with `test_`
- Example async test pattern:
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_chat_endpoint():
    with patch('app.infrastructure.llms.llm_factory.create_model') as mock_create:
        mock_model = AsyncMock()
        mock_create.return_value = mock_model
        mock_model.chat.return_value = ("response", 100)
```

## Security & Performance

- **Security**: Never commit secrets, validate user input, use environment variables, implement proper auth, sanitize file uploads
- **Performance**: Use async I/O, implement Redis caching, batch database queries, use connection pooling

## Troubleshooting

- **Database connection errors**: Check `DATABASE_TYPE` and connection settings
- **Vector store connectivity**: Verify Elasticsearch/OpenSearch is running
- **File storage issues**: Check MinIO/S3 configuration
- **Async context errors**: Ensure proper async/await usage
- **Debugging**: Set `DEBUG=true`, use `ipdb`, check logs in `logs/`, use FastAPI docs at `/docs`

## AI Agent Notes

- **Codebase State**: Disciplined, async-first, Chinese documentation
- **No linting/formatting configs**: No Ruff, Black, or MyPy configurations present
- **No test suite**: Tests not yet implemented
- **No Cursor/Copilot rules**: No `.cursorrules` or `.github/copilot-instructions.md`

## Contributing
When making changes:
1. Follow existing code patterns and conventions
2. Add tests for new functionality
3. Update documentation if needed
4. Run tests before submitting changes
5. Consider backward compatibility

---

*Last updated: January 2026*