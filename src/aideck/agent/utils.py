"""
Utility functions for the GPT Agent module.

This module provides helper functions and utilities used across
the GPT agent system.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from loguru import logger


def generate_id() -> str:
    """Generate a unique identifier.

    Returns:
        A unique string identifier
    """
    import uuid

    return str(uuid.uuid4())


def generate_hash(content: str) -> str:
    """Generate a hash for content.

    Args:
        content: Content to hash

    Returns:
        SHA-256 hash of the content
    """
    return hashlib.sha256(content.encode()).hexdigest()


def safe_json_dumps(data: Any, default: str | None = None) -> str:
    """Safely serialize data to JSON.

    Args:
        data: Data to serialize
        default: Default value for unserializable objects

    Returns:
        JSON string
    """
    try:
        return json.dumps(data, default=default)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize data to JSON: {e}")
        return json.dumps({"error": "Serialization failed", "data": str(data)})


def safe_json_loads(data: str) -> Any:
    """Safely deserialize JSON data.

    Args:
        data: JSON string to deserialize

    Returns:
        Deserialized data or None if failed
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to deserialize JSON: {e}")
        return None


def format_timestamp(dt: datetime | None = None) -> str:
    """Format datetime to ISO string.

    Args:
        dt: Datetime to format, defaults to now

    Returns:
        ISO formatted timestamp
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()


def parse_timestamp(timestamp: str) -> datetime:
    """Parse ISO timestamp to datetime.

    Args:
        timestamp: ISO formatted timestamp

    Returns:
        Datetime object

    Raises:
        ValueError: If timestamp is invalid
    """
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp}") from e


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitize_string(text: str) -> str:
    """Sanitize string for safe processing.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Remove control characters except newlines and tabs
    sanitized = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")
    # Remove excessive whitespace
    sanitized = " ".join(sanitized.split())
    return sanitized


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    # Rough estimation: ~1.3 tokens per word
    words = len(text.split())
    return int(words * 1.3)


class Timer:
    """Context manager for timing operations."""

    def __init__(self, name: str = "operation") -> None:
        """Initialize timer.

        Args:
            name: Name of the operation being timed
        """
        self.name = name
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.duration: float | None = None

    def __enter__(self) -> Timer:
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop timing."""
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
            logger.debug(f"Timer '{self.name}': {self.duration:.3f}s")

    @property
    def elapsed(self) -> float:
        """Get elapsed time."""
        if self.duration is not None:
            return self.duration
        if self.start_time:
            return time.time() - self.start_time
        return 0.0


async def run_with_timeout(
    coro, timeout: float, timeout_message: str = "Operation timed out"
) -> Any:
    """Run coroutine with timeout.

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        timeout_message: Message to log on timeout

    Returns:
        Result of the coroutine

    Raises:
        asyncio.TimeoutError: If operation times out
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"{timeout_message} after {timeout}s")
        raise


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator for retrying async functions.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Multiplier for delay after each attempt
        exceptions: Exception types to retry on
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} attempt {attempt + 1} failed: {e}, retrying in {current_delay}s"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def validate_config(config: dict[str, Any], required_keys: list[str]) -> None:
    """Validate configuration dictionary.

    Args:
        config: Configuration to validate
        required_keys: List of required keys

    Raises:
        ValueError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """Split list into chunks.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i : i + chunk_size])
    return chunks


def flatten_dict(
    d: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested items
        sep: Separator between keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
