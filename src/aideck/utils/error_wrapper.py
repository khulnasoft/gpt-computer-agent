"""
Error wrapper utilities for Aideck.
"""

import functools
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def aideck_error_handler(
    max_retries: int = 3, show_error_details: bool = True
) -> Callable:
    """
    Decorator to handle Aideck-specific errors gracefully.

    Args:
        max_retries: Maximum number of retries for failed operations
        show_error_details: Whether to show detailed error information

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}"
                        )
                        continue
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
                        if show_error_details:
                            logger.exception(f"Error details for {func.__name__}")
                        raise
            raise last_exception

        return wrapper

    return decorator


def async_aideck_error_handler(
    max_retries: int = 3, show_error_details: bool = True
) -> Callable:
    """
    Decorator to handle Aideck-specific errors gracefully for async functions.

    Args:
        max_retries: Maximum number of retries for failed operations
        show_error_details: Whether to show detailed error information

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}"
                        )
                        continue
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
                        if show_error_details:
                            logger.exception(f"Error details for {func.__name__}")
                        raise
            raise last_exception

        return wrapper

    return decorator
