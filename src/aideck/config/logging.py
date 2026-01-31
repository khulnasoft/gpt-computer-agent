import sys
from pathlib import Path

from loguru import logger


def configure_logging(
    log_level: str = "INFO",
    log_format: str | None = None,
    log_file: str | None = None,
    rotation: str = "100 MB",
    retention: str = "30 days",
    serialize: bool = False,
) -> None:
    """
    Configure logging with loguru.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        log_file: Path to log file. If None, logs only to stderr
        rotation: Rotation condition (e.g., "100 MB", "1 day")
        retention: Retention period (e.g., "30 days")
        serialize: Whether to output logs as JSON
    """
    # Default log format
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

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

    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure file logging
        logger.add(
            str(log_path),
            rotation=rotation,
            retention=retention,
            level=log_level,
            format=log_format,
            enqueue=True,  # For async logging
            backtrace=True,
            diagnose=True,
            serialize=serialize,
        )


class InterceptHandler:
    """Intercept standard logging and redirect to loguru."""

    @staticmethod
    def setup():
        import logging

        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        # Disable uvicorn access logs by default
        logging.getLogger("uvicorn.access").handlers = []
        logging.getLogger("uvicorn").handlers = []
        logging.getLogger("uvicorn.error").handlers = []

    def emit(self, record):
        from loguru import logger

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logging call was made
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def get_logger(name: str = None) -> logger:
    """Get a logger instance with the given name."""
    if name is None:
        import inspect

        name = inspect.currentframe().f_back.f_globals.get("__name__")

    return logger.bind(logger_name=name)


# Initialize logging when module is imported
configure_logging()
