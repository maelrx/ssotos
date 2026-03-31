"""structlog configuration — per D-56 (structlog for logging).

Configures structured logging with:
- JSON output in production (LOG_FORMAT=json)
- Console output in development
- Context propagation across async boundaries
- Timestamps in ISO format
"""
import os
import structlog
from structlog.stdlib import ProcessorFormatter


def configure_logging() -> None:
    """Configure structlog based on environment.

    Call this once at application startup.
    """
    log_format = os.environ.get("LOG_FORMAT", "console")  # json or console

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Usage:
        logger = get_logger(__name__)
        logger.info("job_started", job_id="123")
    """
    logger = structlog.get_logger(name) if name else structlog.get_logger()
    return logger


# Convenience function for loggers
log = get_logger
