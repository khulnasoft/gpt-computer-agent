"""
GPT Agent Module

This module provides a comprehensive GPT-based agent system for the Aideck framework.
It includes unified agent interfaces, tool management, conversation handling,
response processing, and memory management capabilities.

Key Components:
- GPTAgent: Main agent class with full GPT integration
- GPTAgentBuilder: Fluent builder for creating agents
- ToolManager: Comprehensive tool system with decorators and registry
- ConversationManager: Advanced conversation management with persistence
- ResponseProcessor: Response parsing and tool call handling
- MemoryManager: Multi-tier memory system with semantic search

Example Usage:
    from aideck.agent import GPTAgentBuilder, tool

    @tool(name="calculator", description="Perform calculations")
    def calculate(expression: str) -> float:
        return eval(expression)

    agent = (GPTAgentBuilder()
              .with_name("Math Assistant")
              .with_model("openai/gpt-4o")
              .with_tool(calculate)
              .with_system_prompt("You are a helpful math assistant.")
              .build())

    response = await agent.chat("What is 2 + 2 * 3?")
"""

from .base import BaseAgent
from .conversation import (
    ConversationContext,
    ConversationManager,
    ConversationMetadata,
    MessageRole,
    MessageStatus,
)
from .conversation import ConversationMessage as ConvMessage
from .gpt_agent import (
    ConversationMessage,
    GPTAgent,
    GPTAgentBuilder,
    GPTAgentConfig,
    GPTMemory,
    GPTToolRegistry,
    ToolResult,
)
from .memory import (
    MemoryConfig,
    MemoryItem,
    MemoryManager,
    MemoryPriority,
    MemorySearchResult,
    MemoryType,
)
from .response_processor import (
    ProcessedResponse,
    ResponseProcessor,
    ResponseType,
    StreamingResponseProcessor,
    ToolCall,
)
from .response_processor import ToolExecutionResult as ToolExecResult
from .tools import (
    BaseTool,
    FunctionTool,
    ToolConfig,
    ToolManager,
    calculate,
    get_current_time,
    read_file,
    tool,
    write_file,
)
from .tools import ToolResult as ToolExecutionResult

__version__ = "1.0.0"
__all__ = [
    # Core Agent Classes
    "GPTAgent",
    "GPTAgentConfig",
    "GPTAgentBuilder",
    "BaseAgent",
    # Tool System
    "ToolManager",
    "BaseTool",
    "FunctionTool",
    "ToolConfig",
    "ToolExecutionResult",
    "tool",
    "get_current_time",
    "calculate",
    "read_file",
    "write_file",
    # Conversation Management
    "ConversationManager",
    "ConvMessage",
    "ConversationMetadata",
    "ConversationContext",
    "MessageRole",
    "MessageStatus",
    # Response Processing
    "ResponseProcessor",
    "ProcessedResponse",
    "ToolCall",
    "ToolExecResult",
    "ResponseType",
    "StreamingResponseProcessor",
    # Memory Management
    "MemoryManager",
    "MemoryItem",
    "MemoryType",
    "MemoryPriority",
    "MemorySearchResult",
    "MemoryConfig",
    # Legacy/Compatibility
    "ConversationMessage",
    "ToolResult",
    "GPTMemory",
    "GPTToolRegistry",
]
