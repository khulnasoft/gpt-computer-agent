"""
Basic tests for the GPT Agent module.

These tests cover the core functionality of the GPT agent system.
"""

import pytest

from aideck.agent import (
    ConversationMessage,
    GPTAgentBuilder,
    GPTAgentConfig,
    MemoryPriority,
    MemoryType,
    ToolResult,
)
from aideck.agent.exceptions import ConfigurationError, GPTAgentError, ValidationError


class TestGPTAgentConfig:
    """Test cases for GPTAgentConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = GPTAgentConfig()

        assert config.name == "GPT Agent"
        assert config.description == "An intelligent GPT-powered agent"
        assert config.model_provider == "openai/gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.max_iterations == 10
        assert config.enable_streaming is True
        assert config.enable_memory is True
        assert config.memory_limit == 10000
        assert config.system_prompt is None
        assert config.tools == []
        assert config.verbose is False

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = GPTAgentConfig(
            name="Custom Agent", temperature=0.5, max_tokens=500, enable_streaming=False
        )

        assert config.name == "Custom Agent"
        assert config.temperature == 0.5
        assert config.max_tokens == 500
        assert config.enable_streaming is False

    def test_temperature_validation(self) -> None:
        """Test temperature validation."""
        # Valid temperatures
        GPTAgentConfig(temperature=0.0)
        GPTAgentConfig(temperature=1.0)
        GPTAgentConfig(temperature=2.0)

        # Invalid temperatures
        with pytest.raises(ValueError, match="Temperature must be between 0.0 and 2.0"):
            GPTAgentConfig(temperature=-0.1)

        with pytest.raises(ValueError, match="Temperature must be between 0.0 and 2.0"):
            GPTAgentConfig(temperature=2.1)

    def test_max_iterations_validation(self) -> None:
        """Test max_iterations validation."""
        # Valid values
        GPTAgentConfig(max_iterations=1)
        GPTAgentConfig(max_iterations=10)

        # Invalid values
        with pytest.raises(ValueError, match="Max iterations must be at least 1"):
            GPTAgentConfig(max_iterations=0)

        with pytest.raises(ValueError, match="Max iterations must be at least 1"):
            GPTAgentConfig(max_iterations=-1)

    def test_memory_limit_validation(self) -> None:
        """Test memory_limit validation."""
        # Valid values
        GPTAgentConfig(memory_limit=1)
        GPTAgentConfig(memory_limit=5000)

        # Invalid values
        with pytest.raises(ValueError, match="Memory limit must be at least 1"):
            GPTAgentConfig(memory_limit=0)

        with pytest.raises(ValueError, match="Memory limit must be at least 1"):
            GPTAgentConfig(memory_limit=-1)


class TestConversationMessage:
    """Test cases for ConversationMessage."""

    def test_valid_message(self) -> None:
        """Test creating a valid message."""
        message = ConversationMessage(role="user", content="Hello, world!")

        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.tool_calls is None
        assert message.tool_call_id is None
        assert message.name is None

    def test_message_with_tool_calls(self) -> None:
        """Test creating a message with tool calls."""
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "calculator",
                    "arguments": '{"expression": "2 + 2"}',
                },
            }
        ]

        message = ConversationMessage(
            role="assistant",
            content="I'll calculate that for you.",
            tool_calls=tool_calls,
        )

        assert message.role == "assistant"
        assert message.tool_calls == tool_calls
        assert message.content == "I'll calculate that for you."

    def test_role_validation(self) -> None:
        """Test role validation."""
        valid_roles = ["user", "assistant", "system", "tool"]

        for role in valid_roles:
            message = ConversationMessage(role=role)
            assert message.role == role

        # Invalid role
        with pytest.raises(ValueError, match="Role must be one of"):
            ConversationMessage(role="invalid")

    def test_tool_message(self) -> None:
        """Test creating a tool response message."""
        message = ConversationMessage(
            role="tool", content="4", tool_call_id="call_123", name="calculator"
        )

        assert message.role == "tool"
        assert message.content == "4"
        assert message.tool_call_id == "call_123"
        assert message.name == "calculator"


class TestToolResult:
    """Test cases for ToolResult."""

    def test_successful_result(self) -> None:
        """Test creating a successful tool result."""
        result = ToolResult(
            tool_name="calculator", tool_call_id="call_123", result=4, success=True
        )

        assert result.tool_name == "calculator"
        assert result.tool_call_id == "call_123"
        assert result.result == 4
        assert result.success is True
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test creating a failed tool result."""
        result = ToolResult(
            tool_name="calculator",
            tool_call_id="call_123",
            result=None,
            success=False,
            error="Invalid expression",
        )

        assert result.tool_name == "calculator"
        assert result.tool_call_id == "call_123"
        assert result.result is None
        assert result.success is False
        assert result.error == "Invalid expression"


class TestGPTAgentBuilder:
    """Test cases for GPTAgentBuilder."""

    def test_builder_defaults(self) -> None:
        """Test builder with default values."""
        builder = GPTAgentBuilder()
        config = builder.config

        assert config.name == "GPT Agent"
        assert config.temperature == 0.7
        assert config.enable_streaming is True

    def test_builder_chaining(self) -> None:
        """Test builder method chaining."""
        builder = (
            GPTAgentBuilder()
            .with_name("Test Agent")
            .with_temperature(0.5)
            .with_model("openai/gpt-3.5-turbo")
            .with_streaming(False)
        )

        config = builder.config

        assert config.name == "Test Agent"
        assert config.temperature == 0.5
        assert config.model_provider == "openai/gpt-3.5-turbo"
        assert config.enable_streaming is False

    def test_builder_build(self) -> None:
        """Test building an agent."""
        # Mock the model provider to avoid actual API calls
        with pytest.MonkeyPatch().context():
            # This would need proper mocking in a real test
            pass


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_gpt_agent_error(self) -> None:
        """Test base GPTAgentError."""
        error = GPTAgentError("Test error", "TEST_ERROR", {"detail": "test"})

        assert str(error) == "[TEST_ERROR] Test error"
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"detail": "test"}

    def test_gpt_agent_error_no_code(self) -> None:
        """Test GPTAgentError without error code."""
        error = GPTAgentError("Test error")

        assert str(error) == "Test error"
        assert error.error_code is None

    def test_configuration_error(self) -> None:
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid config", {"field": "temperature"})

        assert str(error) == "[CONFIGURATION_ERROR] Invalid config"
        assert error.error_code == "CONFIGURATION_ERROR"
        assert error.details["field"] == "temperature"

    def test_validation_error(self) -> None:
        """Test ValidationError."""
        error = ValidationError("Invalid value", field="temperature")

        assert str(error) == "[VALIDATION_ERROR] Invalid value"
        assert error.field == "temperature"
        assert error.details["field"] == "temperature"


@pytest.mark.unit
class TestMemoryTypes:
    """Test cases for memory types and priorities."""

    def test_memory_type_values(self) -> None:
        """Test MemoryType enum values."""
        assert MemoryType.SHORT_TERM.value == "short_term"
        assert MemoryType.LONG_TERM.value == "long_term"
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.SEMANTIC.value == "semantic"
        assert MemoryType.WORKING.value == "working"

    def test_memory_priority_values(self) -> None:
        """Test MemoryPriority enum values."""
        assert MemoryPriority.LOW.value == "low"
        assert MemoryPriority.MEDIUM.value == "medium"
        assert MemoryPriority.HIGH.value == "high"
        assert MemoryPriority.CRITICAL.value == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
