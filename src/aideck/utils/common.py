"""Common utility functions for the GPT Computer Agent."""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from loguru import logger


def load_config(config_path: str | Path) -> dict[str, Any]:
    """
    Load configuration from a JSON or YAML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Dict containing the configuration.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, encoding="utf-8") as f:
            if config_path.suffix.lower() == ".json":
                return json.load(f)
            elif config_path.suffix.lower() in (".yaml", ".yml"):
                return yaml.safe_load(f)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}"
                )
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        raise


def save_config(config: dict[str, Any], config_path: str | Path) -> None:
    """
    Save configuration to a JSON or YAML file.

    Args:
        config: Configuration dictionary to save.
        config_path: Path to save the configuration to.
    """
    config_path = Path(config_path)
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            if config_path.suffix.lower() == ".json":
                json.dump(config, f, indent=2, ensure_ascii=False)
            elif config_path.suffix.lower() in (".yaml", ".yml"):
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}"
                )
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")
        raise


def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as a formatted string.

    Args:
        fmt: Format string for the timestamp.

    Returns:
        Formatted timestamp string.
    """
    return datetime.now().strftime(fmt)


def is_url(string: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        string: String to check.

    Returns:
        True if the string is a valid URL, False otherwise.
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def calculate_checksum(file_path: str | Path, algorithm: str = "sha256") -> str:
    """
    Calculate the checksum of a file.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm to use (default: 'sha256').

    Returns:
        Hexadecimal digest of the file's hash.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    hash_func = getattr(hashlib, algorithm, None)
    if hash_func is None:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    h = hash_func()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)

    return h.hexdigest()


def ensure_directory(path: str | Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory.

    Returns:
        Path object for the directory.
    """
    path = Path(path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.

    Args:
        filename: Name of the file.

    Returns:
        File extension (without the dot), or an empty string if no extension.
    """
    return Path(filename).suffix.lstrip(".").lower()


def format_bytes(size: int) -> str:
    """
    Format a size in bytes to a human-readable string.

    Args:
        size: Size in bytes.

    Returns:
        Formatted string with appropriate unit (e.g., '1.2 MB').
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def setup_logging(
    log_dir: str | Path = "logs",
    log_level: str = "INFO",
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    retention: str = "30 days",
    rotation: str = "100 MB",
    serialize: bool = False,
) -> None:
    """
    Configure logging with loguru.

    Args:
        log_dir: Directory to store log files.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Log format string.
        retention: Log retention period.
        rotation: Log rotation condition.
        serialize: Whether to output logs as JSON.
    """
    import sys

    from loguru import logger

    # Remove default handler
    logger.remove()

    # Add stderr handler
    logger.add(
        sys.stderr,
        level=log_level,
        format=log_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Add file handler
    log_dir = ensure_directory(log_dir)
    log_file = log_dir / f"gpt_agent_{get_timestamp('%Y%m%d')}.log"

    logger.add(
        str(log_file),
        level=log_level,
        format=log_format,
        rotation=rotation,
        retention=retention,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        serialize=serialize,
    )

    logger.info(f"Logging configured. Log file: {log_file}")


def get_environment_info() -> dict[str, str]:
    """
    Get information about the current environment.

    Returns:
        Dictionary containing environment information.
    """
    import platform
    import sys

    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler(),
        "working_directory": os.getcwd(),
        "executable": sys.executable,
        "pid": os.getpid(),
        "cpu_count": os.cpu_count(),
        "user": os.getenv("USER", "unknown"),
        "home": os.path.expanduser("~"),
    }
