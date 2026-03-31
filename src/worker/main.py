"""Worker entry point — run with: python -m src.worker.main"""
import asyncio
import os
import signal
import structlog

from src.worker.processor import JobProcessor

# Configure structured logging (per D-56: structlog)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if os.environ.get("LOG_FORMAT") == "json"
               else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

async def run_worker():
    """Start the worker with graceful shutdown handling."""
    worker_id = os.environ.get("WORKER_ID")
    processor = JobProcessor(worker_id=worker_id)

    loop = asyncio.get_event_loop()

    def shutdown_handler():
        logger.info("shutdown_signal_received")
        processor.running = False

    # Register signal handlers for graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, shutdown_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    try:
        await processor.run(poll_interval=1.0)
    finally:
        logger.info("worker_exited")

if __name__ == "__main__":
    asyncio.run(run_worker())
