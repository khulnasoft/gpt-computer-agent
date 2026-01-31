"""
Response Processing and Tool Call Handling for GPT Agents

This module provides comprehensive response processing capabilities including
tool call parsing, execution, result formatting, and error handling.
"""

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from .conversation import ConversationManager, MessageRole
from .tools import ToolManager, ToolResult


class ResponseType(str, Enum):
    """Types of responses from GPT models."""

    TEXT = "text"
    TOOL_CALL = "tool_call"
    MULTI_TOOL_CALL = "multi_tool_call"
    ERROR = "error"
    STREAMING = "streaming"


@dataclass
class ToolCall:
    """Represents a tool call from the model."""

    id: str
    name: str
    arguments: dict[str, Any]
    raw_call: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": json.dumps(self.arguments)},
        }


class ProcessedResponse(BaseModel):
    """A processed response from the GPT model."""

    response_type: ResponseType
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    execution_time: float | None = None
    token_usage: dict[str, int] | None = None


class ToolExecutionResult(BaseModel):
    """Result of tool execution."""

    tool_call: ToolCall
    result: ToolResult
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


class ResponseProcessor:
    """
    Processes responses from GPT models, handles tool calls, and manages
    the execution flow for agent interactions.
    """

    def __init__(
        self, tool_manager: ToolManager, conversation_manager: ConversationManager
    ):
        self.tool_manager = tool_manager
        self.conversation_manager = conversation_manager
        self.execution_history: list[ToolExecutionResult] = []
        self.response_handlers: dict[ResponseType, Callable] = {
            ResponseType.TEXT: self._handle_text_response,
            ResponseType.TOOL_CALL: self._handle_tool_call_response,
            ResponseType.MULTI_TOOL_CALL: self._handle_multi_tool_call_response,
            ResponseType.ERROR: self._handle_error_response,
        }

    async def process_response(
        self, raw_response: dict[str, Any], conversation_id: str | None = None
    ) -> ProcessedResponse:
        """
        Process a raw response from the GPT model.

        Args:
            raw_response: Raw response from the model
            conversation_id: Optional conversation ID for context

        Returns:
            Processed response with parsed content and tool calls
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Determine response type and extract content
            response_type, content, tool_calls = self._parse_response(raw_response)

            # Create processed response
            processed_response = ProcessedResponse(
                response_type=response_type,
                content=content,
                tool_calls=tool_calls,
                raw_response=raw_response,
                execution_time=asyncio.get_event_loop().time() - start_time,
                token_usage=self._extract_token_usage(raw_response),
            )

            # Add to conversation if provided
            if conversation_id:
                await self._add_response_to_conversation(
                    conversation_id, processed_response
                )

            logger.debug(
                f"Processed {response_type.value} response in {processed_response.execution_time:.3f}s"
            )
            return processed_response

        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return ProcessedResponse(
                response_type=ResponseType.ERROR,
                content=f"Error processing response: {str(e)}",
                raw_response=raw_response,
                execution_time=asyncio.get_event_loop().time() - start_time,
            )

    def _parse_response(
        self, raw_response: dict[str, Any]
    ) -> tuple[ResponseType, str | None, list[ToolCall] | None]:
        """Parse raw response and determine type, content, and tool calls."""
        # Handle different response formats
        if "choices" in raw_response:
            # OpenAI format
            choice = raw_response["choices"][0]
            message = choice.get("message", {})

            content = message.get("content")
            tool_calls_data = message.get("tool_calls")

            if tool_calls_data:
                tool_calls = []
                for tool_call_data in tool_calls_data:
                    tool_call = ToolCall(
                        id=tool_call_data["id"],
                        name=tool_call_data["function"]["name"],
                        arguments=json.loads(tool_call_data["function"]["arguments"]),
                        raw_call=tool_call_data,
                    )
                    tool_calls.append(tool_call)

                if len(tool_calls) == 1:
                    return ResponseType.TOOL_CALL, content, tool_calls
                else:
                    return ResponseType.MULTI_TOOL_CALL, content, tool_calls
            elif content:
                return ResponseType.TEXT, content, None
            else:
                return (
                    ResponseType.ERROR,
                    "Empty response with no content or tool calls",
                    None,
                )

        elif "content" in raw_response:
            # Simple content response
            return ResponseType.TEXT, raw_response["content"], None

        else:
            return ResponseType.ERROR, "Unknown response format", None

    def _extract_token_usage(
        self, raw_response: dict[str, Any]
    ) -> dict[str, int] | None:
        """Extract token usage information from response."""
        if "usage" in raw_response:
            usage = raw_response["usage"]
            return {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }
        return None

    async def _add_response_to_conversation(
        self, conversation_id: str, response: ProcessedResponse
    ) -> None:
        """Add the processed response to the conversation."""
        # Add assistant message
        tool_calls_data = None
        if response.tool_calls:
            tool_calls_data = [tool_call.to_dict() for tool_call in response.tool_calls]

        self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response.content,
            tool_calls=tool_calls_data,
            metadata={
                "response_type": response.response_type.value,
                "token_usage": response.token_usage,
                "execution_time": response.execution_time,
            },
        )

    async def execute_tool_calls(
        self,
        tool_calls: list[ToolCall],
        conversation_id: str | None = None,
        parallel_execution: bool = True,
    ) -> list[ToolExecutionResult]:
        """
        Execute a list of tool calls.

        Args:
            tool_calls: List of tool calls to execute
            conversation_id: Optional conversation ID for context
            parallel_execution: Whether to execute tools in parallel

        Returns:
            List of execution results
        """
        if not tool_calls:
            return []

        start_time = asyncio.get_event_loop().time()

        if parallel_execution and len(tool_calls) > 1:
            # Execute tools in parallel
            tasks = [
                self._execute_single_tool_call(tool_call, conversation_id)
                for tool_call in tool_calls
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to error results
            execution_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    execution_results.append(
                        ToolExecutionResult(
                            tool_call=tool_calls[i],
                            result=ToolResult(success=False, error=str(result)),
                            execution_time=0.0,
                        )
                    )
                else:
                    execution_results.append(result)
        else:
            # Execute tools sequentially
            execution_results = []
            for tool_call in tool_calls:
                result = await self._execute_single_tool_call(
                    tool_call, conversation_id
                )
                execution_results.append(result)

        total_time = asyncio.get_event_loop().time() - start_time

        # Add to execution history
        self.execution_history.extend(execution_results)

        # Add tool results to conversation
        if conversation_id:
            for exec_result in execution_results:
                self.conversation_manager.add_message(
                    conversation_id=conversation_id,
                    role=MessageRole.TOOL,
                    content=(
                        json.dumps(exec_result.result.data)
                        if exec_result.result.success
                        else exec_result.result.error
                    ),
                    tool_call_id=exec_result.tool_call.id,
                    name=exec_result.tool_call.name,
                    metadata={
                        "tool_success": exec_result.result.success,
                        "execution_time": exec_result.execution_time,
                    },
                )

        logger.info(f"Executed {len(tool_calls)} tool calls in {total_time:.3f}s")
        return execution_results

    async def _execute_single_tool_call(
        self, tool_call: ToolCall, conversation_id: str | None = None
    ) -> ToolExecutionResult:
        """Execute a single tool call."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Execute the tool
            result = await self.tool_manager.execute_tool_call(
                tool_call.name, tool_call.arguments
            )

            execution_time = asyncio.get_event_loop().time() - start_time

            execution_result = ToolExecutionResult(
                tool_call=tool_call, result=result, execution_time=execution_time
            )

            if result.success:
                logger.debug(
                    f"Tool {tool_call.name} executed successfully in {execution_time:.3f}s"
                )
            else:
                logger.error(f"Tool {tool_call.name} failed: {result.error}")

            return execution_result

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Error executing tool {tool_call.name}: {e}")

            return ToolExecutionResult(
                tool_call=tool_call,
                result=ToolResult(success=False, error=str(e)),
                execution_time=execution_time,
            )

    async def handle_response(
        self,
        processed_response: ProcessedResponse,
        conversation_id: str | None = None,
        auto_execute_tools: bool = True,
    ) -> tuple[str, list[ToolExecutionResult] | None]:
        """
        Handle a processed response based on its type.

        Args:
            processed_response: The processed response to handle
            conversation_id: Optional conversation ID
            auto_execute_tools: Whether to automatically execute tool calls

        Returns:
            Tuple of (response_content, tool_execution_results)
        """
        handler = self.response_handlers.get(processed_response.response_type)
        if not handler:
            raise ValueError(
                f"No handler for response type: {processed_response.response_type}"
            )

        return await handler(processed_response, conversation_id, auto_execute_tools)

    async def _handle_text_response(
        self,
        response: ProcessedResponse,
        conversation_id: str | None = None,
        auto_execute_tools: bool = True,
    ) -> tuple[str, list[ToolExecutionResult] | None]:
        """Handle a text response."""
        return response.content or "", None

    async def _handle_tool_call_response(
        self,
        response: ProcessedResponse,
        conversation_id: str | None = None,
        auto_execute_tools: bool = True,
    ) -> tuple[str, list[ToolExecutionResult] | None]:
        """Handle a single tool call response."""
        if not auto_execute_tools:
            return "", None

        tool_calls = response.tool_calls or []
        execution_results = await self.execute_tool_calls(tool_calls, conversation_id)

        # Format tool results as response
        results_text = self._format_tool_results(execution_results)

        return results_text, execution_results

    async def _handle_multi_tool_call_response(
        self,
        response: ProcessedResponse,
        conversation_id: str | None = None,
        auto_execute_tools: bool = True,
    ) -> tuple[str, list[ToolExecutionResult] | None]:
        """Handle a multi-tool call response."""
        return await self._handle_tool_call_response(
            response, conversation_id, auto_execute_tools
        )

    async def _handle_error_response(
        self,
        response: ProcessedResponse,
        conversation_id: str | None = None,
        auto_execute_tools: bool = True,
    ) -> tuple[str, list[ToolExecutionResult] | None]:
        """Handle an error response."""
        return f"Error: {response.content}", None

    def _format_tool_results(self, execution_results: list[ToolExecutionResult]) -> str:
        """Format tool execution results into a readable string."""
        if not execution_results:
            return ""

        results = []
        for exec_result in execution_results:
            tool_name = exec_result.tool_call.name

            if exec_result.result.success:
                result_data = exec_result.result.data
                if isinstance(result_data, str):
                    result_str = result_data
                else:
                    result_str = json.dumps(result_data, indent=2)

                results.append(f"✅ {tool_name}: {result_str}")
            else:
                results.append(f"❌ {tool_name}: {exec_result.result.error}")

        return "\n\n".join(results)

    def get_execution_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get the tool execution history."""
        history = []
        for result in self.execution_history[-limit:]:
            history.append(
                {
                    "tool_name": result.tool_call.name,
                    "arguments": result.tool_call.arguments,
                    "success": result.result.success,
                    "result": (
                        result.result.data
                        if result.result.success
                        else result.result.error
                    ),
                    "execution_time": result.execution_time,
                    "timestamp": result.timestamp.isoformat(),
                }
            )
        return history

    def clear_execution_history(self) -> None:
        """Clear the execution history."""
        self.execution_history.clear()

    def get_tool_usage_stats(self) -> dict[str, Any]:
        """Get statistics about tool usage."""
        if not self.execution_history:
            return {}

        tool_counts = {}
        total_executions = 0
        successful_executions = 0
        total_time = 0.0

        for result in self.execution_history:
            tool_name = result.tool_call.name
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            total_executions += 1

            if result.result.success:
                successful_executions += 1

            total_time += result.execution_time

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": (
                successful_executions / total_executions if total_executions > 0 else 0
            ),
            "total_execution_time": total_time,
            "average_execution_time": (
                total_time / total_executions if total_executions > 0 else 0
            ),
            "tool_counts": tool_counts,
            "most_used_tool": (
                max(tool_counts.items(), key=lambda x: x[1])[0] if tool_counts else None
            ),
        }


class StreamingResponseProcessor:
    """Handles streaming responses from GPT models."""

    def __init__(self, response_processor: ResponseProcessor):
        self.response_processor = response_processor
        self.buffer = ""
        self.current_tool_calls: list[dict[str, Any]] = []

    async def process_stream_chunk(
        self, chunk: dict[str, Any], conversation_id: str | None = None
    ) -> str | None:
        """
        Process a streaming chunk and return any text content.

        Args:
            chunk: Streaming chunk from the model
            conversation_id: Optional conversation ID

        Returns:
            Text content from the chunk, or None if no content
        """
        try:
            if "choices" in chunk:
                choice = chunk["choices"][0]
                delta = choice.get("delta", {})

                # Handle text content
                if "content" in delta and delta["content"]:
                    content = delta["content"]
                    self.buffer += content
                    return content

                # Handle tool calls
                if "tool_calls" in delta:
                    for tool_call_delta in delta["tool_calls"]:
                        self._update_tool_call(tool_call_delta)

            return None

        except Exception as e:
            logger.error(f"Error processing stream chunk: {e}")
            return None

    def _update_tool_call(self, tool_call_delta: dict[str, Any]) -> None:
        """Update the current tool calls with delta data."""
        index = tool_call_delta.get("index", 0)

        # Ensure we have enough slots in current_tool_calls
        while len(self.current_tool_calls) <= index:
            self.current_tool_calls.append(
                {"id": "", "function": {"name": "", "arguments": ""}}
            )

        tool_call = self.current_tool_calls[index]

        if "id" in tool_call_delta:
            tool_call["id"] = tool_call_delta["id"]

        if "function" in tool_call_delta:
            func_delta = tool_call_delta["function"]

            if "name" in func_delta:
                tool_call["function"]["name"] = func_delta["name"]

            if "arguments" in func_delta:
                tool_call["function"]["arguments"] += func_delta["arguments"]

    async def finalize_stream(
        self, conversation_id: str | None = None
    ) -> ProcessedResponse:
        """
        Finalize the streaming response and create a processed response.

        Args:
            conversation_id: Optional conversation ID

        Returns:
            Final processed response
        """
        # Create a mock response object
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": self.buffer if self.buffer else None,
                        "tool_calls": (
                            self.current_tool_calls if self.current_tool_calls else None
                        ),
                    }
                }
            ]
        }

        # Process the final response
        processed_response = await self.response_processor.process_response(
            mock_response, conversation_id
        )

        # Reset state
        self.buffer = ""
        self.current_tool_calls = []

        return processed_response
