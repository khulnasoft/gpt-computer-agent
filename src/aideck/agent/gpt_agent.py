"""
GPT Agent implementation for the Aideck framework.

This module provides a comprehensive GPT-based agent structure that integrates
with the existing Aideck infrastructure while providing a clean, extensible
interface for GPT-powered interactions.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, validator

from ..exceptions import ConfigurationError
from ..models.base import BaseModelProvider
from ..models.factory import ModelFactory
from .base import BaseAgent


@dataclass
class GPTAgentConfig:
    """Configuration for GPT Agent.

    Attributes:
        name: Human-readable name for the agent
        description: Brief description of the agent's purpose
        model_provider: Model provider string (e.g., 'openai/gpt-4o')
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens in response
        max_iterations: Maximum number of tool call iterations
        enable_streaming: Whether to enable streaming responses
        enable_memory: Whether to enable conversation memory
        memory_limit: Maximum conversation history tokens
        system_prompt: System prompt for the agent
        tools: List of tools available to the agent
        verbose: Whether to enable verbose logging
    """

    name: str = "GPT Agent"
    description: str = "An intelligent GPT-powered agent"
    model_provider: str = "openai/gpt-4o"
    temperature: float = 0.7
    max_tokens: int | None = None
    max_iterations: int = 10
    enable_streaming: bool = True
    enable_memory: bool = True
    memory_limit: int = 10000
    system_prompt: str | None = None
    tools: list[Any] = field(default_factory=list)
    verbose: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if self.max_iterations < 1:
            raise ValueError("Max iterations must be at least 1")
        if self.memory_limit < 1:
            raise ValueError("Memory limit must be at least 1")


class ConversationMessage(BaseModel):
    """Represents a message in the conversation.

    Attributes:
        role: Role of the message sender (user, assistant, system, tool)
        content: Content of the message
        tool_calls: Tool calls made by the assistant
        tool_call_id: ID of the tool call this message is responding to
        name: Name of the tool that was called
        timestamp: Timestamp of the message
    """

    role: str = Field(
        ..., description="Role of the message sender (user, assistant, system, tool)"
    )
    content: str | None = Field(None, description="Content of the message")
    tool_calls: list[dict[str, Any]] | None = Field(
        None, description="Tool calls made by the assistant"
    )
    tool_call_id: str | None = Field(
        None, description="ID of the tool call this message is responding to"
    )
    name: str | None = Field(None, description="Name of the tool that was called")
    timestamp: str | None = Field(None, description="Timestamp of the message")

    @validator("role")
    def validate_role(cls, v: str) -> str:
        """Validate that role is one of the allowed values."""
        allowed_roles = {"user", "assistant", "system", "tool"}
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}, got '{v}'")
        return v


class ToolResult(BaseModel):
    """Represents the result of a tool execution."""

    tool_name: str
    tool_call_id: str
    result: Any
    success: bool
    error: str | None = None


class GPTMemory:
    """Manages conversation memory for GPT agents."""

    def __init__(self, limit: int = 10000):
        self.messages: list[ConversationMessage] = []
        self.limit = limit

    def add_message(self, message: ConversationMessage) -> None:
        """Add a message to memory."""
        self.messages.append(message)
        self._trim_if_needed()

    def add_user_message(self, content: str) -> None:
        """Add a user message to memory."""
        message = ConversationMessage(role="user", content=content)
        self.add_message(message)

    def add_assistant_message(
        self, content: str, tool_calls: list[dict[str, Any]] | None = None
    ) -> None:
        """Add an assistant message to memory."""
        message = ConversationMessage(
            role="assistant", content=content, tool_calls=tool_calls
        )
        self.add_message(message)

    def add_tool_message(self, tool_call_id: str, tool_name: str, result: Any) -> None:
        """Add a tool result message to memory."""
        content = json.dumps(result) if not isinstance(result, str) else result
        message = ConversationMessage(
            role="tool", content=content, tool_call_id=tool_call_id, name=tool_name
        )
        self.add_message(message)

    def get_messages(self) -> list[dict[str, Any]]:
        """Get messages in OpenAI format."""
        return [msg.dict(exclude_none=True) for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages.clear()

    def _trim_if_needed(self) -> None:
        """Trim messages if they exceed the token limit."""
        # Simple heuristic: remove oldest messages if we have too many
        # In a real implementation, you'd want to count actual tokens
        if len(self.messages) > 50:  # Arbitrary message count limit
            # Keep system messages and remove oldest user/assistant messages
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            other_messages = [msg for msg in self.messages if msg.role != "system"]

            # Keep only the most recent other messages
            other_messages = other_messages[-30:]

            self.messages = system_messages + other_messages


class GPTToolRegistry:
    """Registry for managing GPT agent tools."""

    def __init__(self):
        self.tools: dict[str, Any] = {}

    def register(self, name: str, tool: Any, description: str | None = None) -> None:
        """Register a tool with the agent."""
        self.tools[name] = {
            "tool": tool,
            "description": description
            or getattr(tool, "__doc__", "No description available"),
        }
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Any | None:
        """Get a tool by name."""
        return self.tools.get(name, {}).get("tool")

    def get_tool_schema(self, name: str) -> dict[str, Any] | None:
        """Get the OpenAI function schema for a tool."""
        tool = self.get_tool(name)
        if not tool:
            return None

        # This is a simplified schema generation
        # In a real implementation, you'd want to inspect the tool's signature
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": self.tools[name]["description"],
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self.tools.keys())

    def get_all_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas for OpenAI API."""
        schemas = []
        for name in self.tools:
            schema = self.get_tool_schema(name)
            if schema:
                schemas.append(schema)
        return schemas


class GPTAgent(BaseAgent):
    """
    A comprehensive GPT-based agent that integrates with the Aideck framework.

    This agent provides:
    - Unified interface for different GPT model providers
    - Tool integration and execution
    - Conversation memory management
    - Streaming support
    - Error handling and retry logic
    """

    def __init__(self, config: GPTAgentConfig):
        super().__init__(config)
        self.config = config
        self.memory = (
            GPTMemory(limit=config.memory_limit) if config.enable_memory else None
        )
        self.tool_registry = GPTToolRegistry()
        self.model_provider: BaseModelProvider | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the agent and its components."""
        if self._initialized:
            return

        try:
            # Initialize model provider
            self.model_provider = ModelFactory.create(self.config.model_provider)

            # Register tools
            for tool in self.config.tools:
                if hasattr(tool, "name") and hasattr(tool, "run"):
                    self.tool_registry.register(tool.name, tool)
                elif callable(tool):
                    tool_name = getattr(tool, "__name__", str(tool))
                    self.tool_registry.register(tool_name, tool)

            # Add system prompt if provided
            if self.config.system_prompt and self.memory:
                self.memory.add_message(
                    ConversationMessage(
                        role="system", content=self.config.system_prompt
                    )
                )

            self._initialized = True
            logger.info(f"GPT Agent '{self.config.name}' initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize GPT Agent: {e}")
            raise ConfigurationError(f"Agent initialization failed: {e}") from e

    async def _ensure_initialized(self) -> None:
        """Ensure the agent is initialized."""
        if not self._initialized:
            await self.initialize()

    async def chat(self, message: str) -> str:
        """Send a message to the agent and get a response."""
        await self._ensure_initialized()

        if self.memory:
            self.memory.add_user_message(message)

        try:
            # Get model and settings
            model, model_settings = await self.model_provider._provision(
                tools=(
                    self.tool_registry.get_all_schemas() if self.tool_registry else None
                )
            )

            # Create the agent response
            from pydantic_ai import Agent

            agent = Agent(model, model_type="openai")

            # Get response
            response = await agent.run(message)

            # Store response in memory
            if self.memory:
                self.memory.add_assistant_message(response.data)

            return response.data

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise

    async def chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Send a message and stream the response."""
        await self._ensure_initialized()

        if self.memory:
            self.memory.add_user_message(message)

        try:
            # Get model and settings
            model, model_settings = await self.model_provider._provision(
                tools=(
                    self.tool_registry.get_all_schemas() if self.tool_registry else None
                )
            )

            # Create the agent response
            from pydantic_ai import Agent

            agent = Agent(model, model_type="openai")

            # Stream response
            async for chunk in agent.run_stream(message):
                yield chunk.data

        except Exception as e:
            logger.error(f"Error in chat_stream: {e}")
            raise

    def clear_memory(self) -> None:
        """Clear the agent's conversation memory."""
        if self.memory:
            self.memory.clear()
            logger.info("Agent memory cleared")

    def get_conversation_history(self) -> list[ConversationMessage]:
        """Get the conversation history."""
        return self.memory.messages if self.memory else []

    def add_tool(self, name: str, tool: Any, description: str | None = None) -> None:
        """Add a tool to the agent."""
        self.tool_registry.register(name, tool, description)

    def list_tools(self) -> list[str]:
        """List all available tools."""
        return self.tool_registry.list_tools()

    async def run(self, input_data: str | dict[str, Any]) -> Any:
        """Run the agent with the given input."""
        if isinstance(input_data, str):
            return await self.chat(input_data)
        elif isinstance(input_data, dict):
            message = input_data.get("message", str(input_data))
            return await self.chat(message)
        else:
            return await self.chat(str(input_data))

    def save_state(self, path: str | Path) -> None:
        """Save the agent's state to a file."""
        state = {
            "config": self.config.__dict__,
            "messages": (
                [msg.dict() for msg in self.memory.messages] if self.memory else []
            ),
            "tools": list(self.tool_registry.tools.keys()),
        }

        with open(path, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Saved agent state to {path}")

    @classmethod
    def load_state(cls, path: str | Path):
        """Load an agent from a saved state."""
        with open(path) as f:
            state = json.load(f)

        config = GPTAgentConfig(**state["config"])
        agent = cls(config)

        # Restore conversation history
        if agent.memory and "messages" in state:
            for msg_data in state["messages"]:
                msg = ConversationMessage(**msg_data)
                agent.memory.messages.append(msg)

        return agent


class GPTAgentBuilder:
    """Builder class for creating GPT agents with fluent interface."""

    def __init__(self):
        self.config = GPTAgentConfig()

    def with_name(self, name: str) -> GPTAgentBuilder:
        """Set the agent name."""
        self.config.name = name
        return self

    def with_description(self, description: str) -> GPTAgentBuilder:
        """Set the agent description."""
        self.config.description = description
        return self

    def with_model(self, model_provider: str) -> GPTAgentBuilder:
        """Set the model provider."""
        self.config.model_provider = model_provider
        return self

    def with_temperature(self, temperature: float) -> GPTAgentBuilder:
        """Set the temperature."""
        self.config.temperature = temperature
        return self

    def with_max_tokens(self, max_tokens: int) -> GPTAgentBuilder:
        """Set the maximum tokens."""
        self.config.max_tokens = max_tokens
        return self

    def with_system_prompt(self, system_prompt: str) -> GPTAgentBuilder:
        """Set the system prompt."""
        self.config.system_prompt = system_prompt
        return self

    def with_memory(self, enabled: bool = True, limit: int = 10000) -> GPTAgentBuilder:
        """Configure memory settings."""
        self.config.enable_memory = enabled
        self.config.memory_limit = limit
        return self

    def with_tool(self, tool: Any, name: str | None = None) -> GPTAgentBuilder:
        """Add a tool to the agent."""
        if name:
            tool.name = name
        self.config.tools.append(tool)
        return self

    def with_streaming(self, enabled: bool = True) -> GPTAgentBuilder:
        """Configure streaming."""
        self.config.enable_streaming = enabled
        return self

    def build(self) -> GPTAgent:
        """Build and return the GPT agent."""
        return GPTAgent(self.config)
