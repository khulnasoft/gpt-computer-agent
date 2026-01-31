import inspect
from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
from typing import Any, Union

from loguru import logger


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


@dataclass
class Tool:
    """A tool that can be used by the agent."""

    name: str
    description: str
    parameters: dict
    func: Callable

    def __post_init__(self):
        # Validate the function signature against the parameters
        self._validate_signature()

    def _validate_signature(self):
        """Validate that the function signature matches the parameters."""
        sig = signature(self.func)
        param_names = set(sig.parameters.keys())
        schema_params = set(self.parameters.get("properties", {}).keys())

        # Check for missing parameters
        missing = schema_params - param_names
        if missing:
            raise ToolError(
                f"Function '{self.name}' is missing parameters: {', '.join(missing)}"
            )

        # Check for extra parameters
        extra = param_names - schema_params
        if extra and "**" not in str(sig):
            raise ToolError(
                f"Function '{self.name}' has extra parameters not in schema: {', '.join(extra)}"
            )

    def run(self, **kwargs) -> Any:
        """Run the tool with the given arguments."""
        try:
            return self.func(**kwargs)
        except Exception as e:
            logger.error(f"Error running tool '{self.name}': {e}")
            raise ToolError(f"Error running tool '{self.name}': {e}")

    def to_dict(self) -> dict[str, Any]:
        """Convert the tool to a dictionary for the OpenAI API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    @classmethod
    def from_function(
        cls,
        func: Callable,
        name: str | None = None,
        description: str | None = None,
        parameters: dict | None = None,
    ) -> "Tool":
        """Create a tool from a function."""
        if name is None:
            name = func.__name__

        if description is None:
            description = func.__doc__ or ""

        # Generate parameters from type hints if not provided
        if parameters is None:
            parameters = cls._parameters_from_type_hints(func)

        return cls(name=name, description=description, parameters=parameters, func=func)

    @staticmethod
    def _parameters_from_type_hints(func: Callable) -> dict:
        """Generate parameters from function type hints."""
        type_mapping = {
            "str": {"type": "string"},
            "int": {"type": "integer"},
            "float": {"type": "number"},
            "bool": {"type": "boolean"},
            "list": {"type": "array", "items": {"type": "string"}},
            "dict": {"type": "object"},
        }

        sig = signature(func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            param_type = param.annotation
            param_type_name = getattr(param_type, "__name__", str(param_type))

            # Handle Optional types
            if hasattr(param_type, "__origin__") and param_type.__origin__ is Union:
                # Get the non-None type from Optional[T] = Union[T, None]
                non_none_types = [
                    t for t in param_type.__args__ if t is not type(None)
                ]  # noqa
                if len(non_none_types) == 1:
                    param_type = non_none_types[0]
                    param_type_name = getattr(param_type, "__name__", str(param_type))

            # Handle basic types
            if param_type_name in type_mapping:
                param_schema = type_mapping[param_type_name].copy()
            # Handle List, Dict, etc.
            elif hasattr(param_type, "__origin__"):
                origin = param_type.__origin__
                if origin is list and hasattr(param_type, "__args__"):
                    item_type = param_type.__args__[0]
                    item_type_name = getattr(item_type, "__name__", str(item_type))
                    param_schema = {
                        "type": "array",
                        "items": type_mapping.get(item_type_name, {"type": "string"}),
                    }
                elif origin is dict and hasattr(param_type, "__args__"):
                    key_type, value_type = param_type.__args__
                    value_type_name = getattr(value_type, "__name__", str(value_type))
                    param_schema = {
                        "type": "object",
                        "additionalProperties": type_mapping.get(
                            value_type_name, {"type": "string"}
                        ),
                    }
                else:
                    param_schema = {"type": "string"}
            else:
                param_schema = {"type": "string"}

            # Add description from docstring if available
            if func.__doc__:
                # Simple extraction of parameter descriptions from docstring
                docstring = inspect.cleandoc(func.__doc__)
                for line in docstring.split("\n"):
                    if line.strip().startswith(f"{name}:"):
                        param_schema["description"] = line.split(":", 1)[1].strip()

            parameters["properties"][name] = param_schema

            # Add to required if no default value
            if param.default == param.empty:
                parameters["required"].append(name)

        return parameters


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool | Callable, **kwargs) -> None:
        """Register a tool with the registry."""
        if not isinstance(tool, Tool):
            tool = Tool.from_function(tool, **kwargs)

        if tool.name in self.tools:
            logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")

        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [tool.to_dict() for tool in self.tools.values()]

    def clear(self) -> None:
        """Clear all registered tools."""
        self.tools.clear()

    def __len__(self) -> int:
        return len(self.tools)

    def __contains__(self, name: str) -> bool:
        return name in self.tools


# Decorator for registering functions as tools
def tool(
    name: str | None = None,
    description: str | None = None,
    parameters: dict | None = None,
):
    """Decorator to register a function as a tool."""

    def decorator(func):
        tool = Tool.from_function(
            func=func, name=name, description=description, parameters=parameters
        )
        # The actual registration happens when the tool is added to an agent
        return tool

    return decorator
