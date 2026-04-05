"""Logging configuration"""
import logging
import sys
import os

# Create logger first (before importing settings to avoid circular import)
logger = logging.getLogger("playbook_pulse")


def setup_logging():
    """Configure application logging"""
    from app.config import settings

    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Format based on configuration
    if settings.log_format == "json":
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter(
                "%(timestamp)s %(level)s %(name)s %(message)s",
                rename_fields={"levelname": "level", "asctime": "timestamp"}
            )
        except ImportError:
            # Fall back to standard format if json logger not available
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
            )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    try:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")

    # WebSocket log handler (initialized lazily when first needed)
    # Will be added dynamically when WebSocketManager is available
    logger._ws_handler_enabled = False

    logger.info("Logging configured successfully")

    return logger


def enable_websocket_logging(ws_manager):
    """Enable WebSocket logging handler for real-time log streaming"""
    try:
        from app.utils.log_handler import WebSocketLogHandler

        # Check if already enabled
        if getattr(logger, "_ws_handler_enabled", False):
            return

        ws_log_handler = WebSocketLogHandler(ws_manager)
        formatter = logging.Formatter("%(message)s")
        ws_log_handler.setFormatter(formatter)
        logger.addHandler(ws_log_handler)
        logger._ws_handler_enabled = True
        logger.debug("WebSocket logging handler enabled")

    except Exception as e:
        logger.warning(f"Could not enable WebSocket logging: {e}")
