"""
Custom exceptions for the GPT Agent module.

This module defines custom exceptions that provide specific error handling
for the GPT agent system.
"""

from typing import Any


class GPTAgentError(Exception):
    """Base exception for all GPT agent related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AgentInitializationError(GPTAgentError):
    """Raised when agent initialization fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, "AGENT_INIT_ERROR", details)


class ToolExecutionError(GPTAgentError):
    """Raised when tool execution fails."""

    def __init__(
        self, tool_name: str, message: str, details: dict[str, Any] | None = None
    ) -> None:
        self.tool_name = tool_name
        details = details or {}
        details["tool_name"] = tool_name
        super().__init__(message, "TOOL_EXECUTION_ERROR", details)


class ConversationError(GPTAgentError):
    """Raised when conversation operations fail."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, "CONVERSATION_ERROR", details)


class MemoryError(GPTAgentError):
    """Raised when memory operations fail."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, "MEMORY_ERROR", details)


class ModelProviderError(GPTAgentError):
    """Raised when model provider operations fail."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, "MODEL_PROVIDER_ERROR", details)


class ResponseProcessingError(GPTAgentError):
    """Raised when response processing fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, "RESPONSE_PROCESSING_ERROR", details)


class ConfigurationError(GPTAgentError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, "CONFIGURATION_ERROR", details)


class ValidationError(GPTAgentError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)
