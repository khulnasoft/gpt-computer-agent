"""
GPT Agent Tools System

This module provides a comprehensive tool system for GPT agents, including
tool decorators, base classes, and utility functions for tool management.
"""

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from loguru import logger
from pydantic import BaseModel


@dataclass
class ToolConfig:
    """Configuration for a tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    enabled: bool = True
    timeout: int | None = None
    retry_count: int = 0


class ToolResult(BaseModel):
    """Standard result format for tool executions."""

    success: bool
    data: Any = None
    error: str | None = None
    execution_time: float | None = None


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.config = ToolConfig(
            name=name, description=description, parameters=self._get_parameters()
        )

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given parameters."""
        pass

    def _get_parameters(self) -> dict[str, Any]:
        """Get the parameter schema for this tool."""
        signature = inspect.signature(self.execute)
        parameters = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            param_info = {
                "type": self._get_type_string(param.annotation),
                "description": f"Parameter {param_name}",
                "required": param.default == inspect.Parameter.empty,
            }

            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default

            parameters[param_name] = param_info

        return parameters

    def _get_type_string(self, type_annotation) -> str:
        """Convert type annotation to string representation."""
        if type_annotation == inspect.Parameter.empty:
            return "any"
        elif hasattr(type_annotation, "__name__"):
            return type_annotation.__name__
        elif str(type_annotation).startswith("typing."):
            return str(type_annotation).replace("typing.", "")
        else:
            return str(type_annotation)

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert tool to OpenAI function calling schema."""
        properties = {}
        required = []

        for param_name, param_info in self.config.parameters.items():
            prop = {
                "type": param_info["type"],
                "description": param_info["description"],
            }

            if "default" in param_info:
                prop["default"] = param_info["default"]

            properties[param_name] = prop

            if param_info["required"]:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.config.name,
                "description": self.config.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class FunctionTool(BaseTool):
    """Tool that wraps a regular function."""

    def __init__(
        self,
        func: Callable,
        name: str | None = None,
        description: str | None = None,
    ):
        self.func = func
        func_name = name or func.__name__
        func_description = description or func.__doc__ or f"Function {func_name}"
        super().__init__(func_name, func_description)

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the wrapped function."""
        import time

        start_time = time.time()

        try:
            # Handle both sync and async functions
            if inspect.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
            else:
                result = self.func(**kwargs)

            execution_time = time.time() - start_time

            return ToolResult(success=True, data=result, execution_time=execution_time)

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing tool {self.name}: {e}")

            return ToolResult(
                success=False, error=str(e), execution_time=execution_time
            )


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self.tools: dict[str, BaseTool] = {}
        self.enabled_tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool | Callable,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Register a tool."""
        if isinstance(tool, BaseTool):
            self.tools[tool.name] = tool
            if tool.config.enabled:
                self.enabled_tools[tool.name] = tool
        elif callable(tool):
            func_tool = FunctionTool(tool, name, description)
            self.tools[func_tool.name] = func_tool
            if func_tool.config.enabled:
                self.enabled_tools[func_tool.name] = func_tool
        else:
            raise ValueError(f"Cannot register tool of type: {type(tool)}")

        logger.info(
            f"Registered tool: {self.tools[tool.name if isinstance(tool, BaseTool) else name or tool.__name__].name}"
        )

    def unregister(self, name: str) -> None:
        """Unregister a tool."""
        if name in self.tools:
            del self.tools[name]
        if name in self.enabled_tools:
            del self.enabled_tools[name]
        logger.info(f"Unregistered tool: {name}")

    def get_tool(self, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self.enabled_tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self.enabled_tools.keys())

    def enable_tool(self, name: str) -> None:
        """Enable a tool."""
        if name in self.tools:
            tool = self.tools[name]
            tool.config.enabled = True
            self.enabled_tools[name] = tool
            logger.info(f"Enabled tool: {name}")

    def disable_tool(self, name: str) -> None:
        """Disable a tool."""
        if name in self.enabled_tools:
            tool = self.enabled_tools[name]
            tool.config.enabled = False
            del self.enabled_tools[name]
            logger.info(f"Disabled tool: {name}")

    def get_openai_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas in OpenAI format."""
        return [tool.to_openai_schema() for tool in self.enabled_tools.values()]

    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, error=f"Tool '{name}' not found")

        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return ToolResult(success=False, error=str(e))


def tool(name: str | None = None, description: str | None = None, enabled: bool = True):
    """
    Decorator to convert a function into a tool.

    Args:
        name: Name of the tool (defaults to function name)
        description: Description of the tool (defaults to function docstring)
        enabled: Whether the tool is enabled by default
    """

    def decorator(func: Callable) -> FunctionTool:
        func_tool = FunctionTool(func, name, description)
        func_tool.config.enabled = enabled

        # Store the tool in the function for later registration
        func._aideck_tool = func_tool

        return func

    return decorator


class ToolManager:
    """High-level tool manager for GPT agents."""

    def __init__(self):
        self.registry = ToolRegistry()
        self.execution_history: list[dict[str, Any]] = []

    def register_function(
        self,
        func: Callable,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Register a function as a tool."""
        self.registry.register(func, name, description)

    def register_class_method(
        self, instance: Any, method_name: str, tool_name: str | None = None
    ) -> None:
        """Register a class method as a tool."""
        method = getattr(instance, method_name)
        if not callable(method):
            raise ValueError(f"{method_name} is not callable")

        name = tool_name or f"{instance.__class__.__name__}_{method_name}"
        description = (
            method.__doc__ or f"Method {method_name} from {instance.__class__.__name__}"
        )

        # Bind the method to the instance
        bound_method = getattr(instance, method_name)
        self.register_function(bound_method, name, description)

    def register_module_functions(self, module, prefix: str = "") -> None:
        """Register all functions from a module."""
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                tool_name = f"{prefix}_{name}" if prefix else name
                self.register_function(obj, tool_name)

    async def execute_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> ToolResult:
        """Execute a tool call and log the result."""
        import time

        start_time = time.time()

        result = await self.registry.execute_tool(tool_name, **arguments)

        # Log the execution
        execution_record = {
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result.dict(),
            "timestamp": time.time(),
            "execution_time": time.time() - start_time,
        }

        self.execution_history.append(execution_record)

        if result.success:
            logger.info(f"Tool {tool_name} executed successfully")
        else:
            logger.error(f"Tool {tool_name} execution failed: {result.error}")

        return result

    def get_execution_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get the execution history."""
        return self.execution_history[-limit:]

    def clear_execution_history(self) -> None:
        """Clear the execution history."""
        self.execution_history.clear()


# Predefined common tools
@tool(name="get_current_time", description="Get the current time and date")
def get_current_time() -> str:
    """Get the current time and date."""
    from datetime import datetime

    return datetime.now().isoformat()


@tool(name="calculate", description="Perform basic mathematical calculations")
def calculate(expression: str) -> float | str:
    """
    Calculate the result of a mathematical expression.

    Args:
        expression: A mathematical expression as a string (e.g., "2 + 3 * 4")

    Returns:
        The result of the calculation or an error message
    """
    try:
        # Safe evaluation of mathematical expressions
        import ast
        import operator

        # Define allowed operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
        }

        def eval_node(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                op_type = type(node.op)
                if op_type in operators:
                    return operators[op_type](left, right)
                else:
                    raise ValueError(f"Unsupported operator: {op_type}")
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                op_type = type(node.op)
                if op_type in operators:
                    return operators[op_type](operand)
                else:
                    raise ValueError(f"Unsupported unary operator: {op_type}")
            else:
                raise ValueError(f"Unsupported expression: {type(node)}")

        tree = ast.parse(expression, mode="eval")
        result = eval_node(tree.body)
        return result

    except Exception as e:
        return f"Error: {str(e)}"


@tool(name="read_file", description="Read the contents of a file")
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        The contents of the file or an error message
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool(name="write_file", description="Write content to a file")
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success message or an error message
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"
