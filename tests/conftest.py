"""Test configuration and fixtures for Aideck"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_FIXTURES_DIR.mkdir(exist_ok=True)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir(tmp_path) -> Path:
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def test_config():
    """Basic test configuration."""
    return {
        "debug": False,
        "log_level": "INFO",
        "database_url": "sqlite:///:memory:",
        "secret_key": "test-secret-key-for-unit-tests",
    }


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "This is a sample text for testing purposes. It contains multiple sentences and should be long enough for meaningful tests."


@pytest.fixture
def sample_json():
    """Sample JSON data for testing."""
    return {
        "id": "test-123",
        "name": "Test Item",
        "description": "A test item for unit testing",
        "active": True,
        "tags": ["test", "unit", "sample"],
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def mock_model_provider():
    """Mock model provider for testing."""
    provider = Mock()
    provider._provision = AsyncMock()
    return provider


@pytest.fixture
def sample_conversation_messages():
    """Sample conversation messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
    ]


@pytest.fixture
def sample_tool_call():
    """Sample tool call for testing."""
    return {
        "id": "call_123",
        "type": "function",
        "function": {"name": "calculator", "arguments": '{"expression": "2 + 2"}'},
    }


@pytest.fixture
def mock_tool_result():
    """Mock tool result for testing."""
    return {
        "tool_name": "calculator",
        "tool_call_id": "call_123",
        "result": 4,
        "success": True,
        "error": None,
    }
