from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VectorSearchResult:
    """
    A standardized data structure for a single search result.
    All provider implementations must return a list of these objects.
    """

    id: str | int
    score: float
    payload: dict[str, Any] | None = None
    vector: list[float] | None = None
    text: str | None = None
