from typing import Any

from pydantic import BaseModel


class ExternalToolCall(BaseModel):
    """Represents a tool call that must be executed externally."""

    tool_name: str
    tool_args: dict[str, Any]
    result: Any | None = None
