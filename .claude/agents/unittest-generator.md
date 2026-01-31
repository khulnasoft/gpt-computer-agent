# Unit Test Generator Agent

## Purpose
Generate comprehensive unit tests for the GPT Computer Agent framework, focusing on test coverage, edge cases, and best practices.

## Capabilities
- Generate unit tests for Python modules and classes
- Create test fixtures and mock objects
- Write tests for async functions and coroutines
- Generate integration tests for API endpoints
- Create tests for database operations and models
- Write tests for error handling and edge cases
- Generate test data factories
- Create performance and load tests

## Project Structure Understanding
The GPT Computer Agent has the following key modules:
- `/embeddings/` - Multi-provider embedding system
- `/knowledge_base/` - RAG and document processing
- `/audio/` - TTS and STT functionality
- `/api/` - FastAPI web interface
- `/core/` - Core agent functionality
- `/models/` - LLM provider abstractions
- `/storage/` - Data persistence layer
- `/vectordb/` - Vector database integrations
- `/loaders/` - Document loading and parsing
- `/text_splitter/` - Text chunking strategies
- `/safety_engine/` - Content safety and filtering
- `/reliability_layer/` - Error handling and resilience

## Testing Patterns

### 1. Provider Pattern Testing
```python
def test_embedding_provider_initialization():
    """Test embedding provider initialization with valid config."""
    config = OpenAIEmbeddingConfig(
        model_name="text-embedding-3-small",
        api_key="test-key"
    )
    provider = OpenAIEmbedding(config=config)
    assert provider.config.model_name == "text-embedding-3-small"

def test_provider_factory_creation():
    """Test factory method for creating providers."""
    provider = create_embedding_provider("openai", model_name="text-embedding-ada-002")
    assert isinstance(provider, OpenAIEmbedding)
```

### 2. Async Function Testing
```python
@pytest.mark.asyncio
async def test_async_embedding_generation():
    """Test async embedding generation with mocked provider."""
    config = OpenAIEmbeddingConfig(model_name="text-embedding-3-small")
    provider = OpenAIEmbedding(config=config)

    with patch.object(provider, '_embed_batch') as mock_embed:
        mock_embed.return_value = [[0.1, 0.2, 0.3]]

        result = await provider.embed_texts(["test text"])
        assert len(result) == 1
        assert len(result[0]) == 3
```

### 3. API Endpoint Testing
```python
def test_chat_endpoint(client):
    """Test chat API endpoint with valid request."""
    request_data = {
        "message": "Hello, how are you?",
        "model": "gpt-4o",
        "temperature": 0.7
    }

    response = client.post("/chat", json=request_data)
    assert response.status_code == 200
    assert "response" in response.json()
```

### 4. Database Model Testing
```python
def test_user_model_creation(db_session):
    """Test user model creation and persistence."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(User).filter_by(email="test@example.com").first()
    assert saved_user.username == "testuser"
```

### 5. Error Handling Testing
```python
def test_invalid_api_key_handling():
    """Test handling of invalid API keys."""
    config = OpenAIEmbeddingConfig(
        model_name="text-embedding-3-small",
        api_key="invalid-key"
    )
    provider = OpenAIEmbedding(config=config)

    with pytest.raises(ModelConnectionError):
        asyncio.run(provider.validate_connection())
```

## Test Generation Commands

### Generate Basic Unit Tests
```
Generate unit tests for the OpenAIEmbedding class in embeddings/openai_provider.py
- Include initialization tests
- Test embedding generation
- Test error handling
- Test configuration validation
```

### Generate API Tests
```
Create integration tests for the chat API endpoints
- Test successful chat requests
- Test error responses
- Test authentication
- Test rate limiting
```

### Generate Database Tests
```
Generate tests for the storage layer
- Test CRUD operations
- Test connection handling
- Test transaction management
- Test error scenarios
```

### Generate Async Tests
```
Create tests for async functions in the reliability layer
- Test retry mechanisms
- Test circuit breaker patterns
- Test async error handling
- Test concurrent operations
```

## Test Data Generation

### Mock Data Factories
```python
def create_test_embedding_config():
    """Create test configuration for embedding providers."""
    return OpenAIEmbeddingConfig(
        model_name="text-embedding-3-small",
        api_key="test-key",
        batch_size=10
    )

def create_test_document():
    """Create test document for knowledge base testing."""
    return Document(
        content="This is a test document for unit testing.",
        metadata={"source": "test", "type": "text"},
        document_id="test-doc-123"
    )
```

### Fixture Generation
```python
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('openai.AsyncOpenAI') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_texts():
    """Provide sample texts for embedding tests."""
    return [
        "This is a test document.",
        "Another test document for batch processing.",
        "Third document to test edge cases."
    ]
```

## Testing Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for shared test data
- Mock external dependencies
- Clean up after tests

### 2. Comprehensive Coverage
- Test happy path scenarios
- Test error conditions
- Test edge cases and boundary values
- Test configuration variations

### 3. Async Testing
- Use pytest-asyncio for async tests
- Mock async functions appropriately
- Test concurrent operations
- Handle async context managers

### 4. Error Testing
- Test exception types and messages
- Test error propagation
- Test fallback mechanisms
- Test retry logic

## Performance Testing

### Load Testing
```python
def test_embedding_provider_throughput():
    """Test embedding generation throughput."""
    config = OpenAIEmbeddingConfig(batch_size=50)
    provider = OpenAIEmbedding(config=config)

    texts = ["test"] * 1000
    start_time = time.time()

    embeddings = asyncio.run(provider.embed_texts(texts))
    end_time = time.time()

    throughput = 1000 / (end_time - start_time)
    assert throughput > 10  # At least 10 embeddings per second
```

### Memory Testing
```python
def test_memory_usage():
    """Test memory usage during embedding generation."""
    config = OpenAIEmbeddingConfig()
    provider = OpenAIEmbedding(config=config)

    import psutil
    process = psutil.Process()

    initial_memory = process.memory_info().rss

    texts = ["test document"] * 100
    embeddings = asyncio.run(provider.embed_texts(texts))

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
```

## Integration Testing

### End-to-End Tests
```python
def test_full_rag_pipeline():
    """Test complete RAG pipeline from document to response."""
    # Setup knowledge base
    embedding_provider = create_embedding_provider("openai")
    vectordb = create_vectordb_provider("chroma")

    kb = KnowledgeBase(
        sources=["test_documents/"],
        embedding_provider=embedding_provider,
        vectordb=vectordb
    )

    # Index documents
    asyncio.run(kb.setup_async())

    # Query knowledge base
    results = asyncio.run(kb.query_async("What is machine learning?"))

    assert len(results) > 0
    assert "machine learning" in results[0].text.lower()
```

### Cross-Module Tests
```python
def test_embedding_to_vectordb_integration():
    """Test integration between embedding and vector database."""
    embedding_provider = create_embedding_provider("openai")
    vectordb = create_vectordb_provider("chroma")

    # Generate embeddings
    texts = ["Machine learning is fascinating"]
    embeddings = asyncio.run(embedding_provider.embed_texts(texts))

    # Store in vector database
    vectordb.create_collection()
    vectordb.upsert(
        vectors=embeddings,
        payloads=[{"source": "test"}],
        ids=["test-1"],
        chunks=texts
    )

    # Query vector database
    query_embedding = asyncio.run(embedding_provider.embed_query("What is ML?"))
    results = vectordb.search(query_embedding)

    assert len(results) > 0
```

## Test Organization

### Directory Structure
```
tests/
├── unit/
│   ├── test_embeddings.py
│   ├── test_knowledge_base.py
│   ├── test_storage.py
│   └── test_models.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_external_services.py
├── fixtures/
│   ├── test_data.py
│   ├── mock_providers.py
│   └── factories.py
└── conftest.py
```

### Naming Conventions
- `test_` prefix for all test functions
- `test_class_method` for testing specific methods
- `test_integration_feature` for integration tests
- `test_unit_component` for unit tests

## CI/CD Integration

### GitHub Actions Configuration
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Coverage Reporting

### Pytest Coverage Configuration
```ini
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### Coverage Goals
- Overall coverage: >85%
- Core modules: >90%
- API endpoints: >80%
- Error handling: >95%

## Debugging Tests

### Common Issues and Solutions
1. **Async Test Issues**: Use `pytest-asyncio` and proper async mocking
2. **Database Connection Issues**: Use test databases and proper cleanup
3. **API Key Issues**: Use environment variable mocking
4. **Memory Issues**: Monitor memory usage in long-running tests

### Debug Commands
```bash
# Run specific test
pytest tests/unit/test_embeddings.py::test_openai_initialization -v

# Run with debugger
pytest tests/unit/test_embeddings.py::test_openai_initialization -v -s --pdb

# Run with coverage
pytest --cov=src/aideck/embeddings --cov-report=html

# Run only failing tests
pytest --lf
```

## Maintenance

### Regular Tasks
- Update test dependencies
- Review and update fixtures
- Add tests for new features
- Remove obsolete tests
- Monitor test performance

### Test Review Process
1. All new features must have tests
2. Tests must pass before merging
3. Code coverage must not decrease
4. Performance tests should not regress

## Conclusion

This unit test generator creates comprehensive, maintainable tests following Python best practices. The tests ensure code quality, catch regressions, and provide documentation of expected behavior. Regular test maintenance and proper CI/CD integration are essential for long-term project health.
