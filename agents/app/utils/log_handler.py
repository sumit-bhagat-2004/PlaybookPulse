"""WebSocket logging handler for real-time log streaming"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import contextvars
import asyncio

# Context variable to store analysis_id in logging context
analysis_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "analysis_id", default=None
)


class WebSocketLogHandler(logging.Handler):
    """Custom logging handler that sends logs to WebSocket clients"""

    def __init__(self, ws_manager=None):
        """
        Initialize the WebSocket log handler

        Args:
            ws_manager: WebSocketManager instance for broadcasting logs
        """
        super().__init__()
        self.ws_manager = ws_manager
        self.setLevel(logging.DEBUG)

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to WebSocket clients

        Args:
            record: LogRecord to emit
        """
        if not self.ws_manager:
            return

        try:
            # Get analysis_id from context
            analysis_id = analysis_id_var.get()
            if not analysis_id:
                return

            # Format log message
            message = self.format(record)

            # Extract agent name if present (format: "[AgentName] message")
            agent_name = "system"
            if message.startswith("[") and "]" in message:
                agent_name = message.split("]")[0].strip("[")
                # Remove agent name from message if it exists
                message = message.split("]", 1)[1].strip() if "]" in message else message

            log_data = {
                "type": "log",
                "analysis_id": analysis_id,
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "agent_name": agent_name,
                "message": message,
            }

            # Queue the async operation to send log message
            # This avoids blocking the logging system
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, create a task
                    asyncio.create_task(self.ws_manager.send_log_message(analysis_id, log_data))
                else:
                    # Otherwise, run it synchronously
                    loop.run_until_complete(self.ws_manager.send_log_message(analysis_id, log_data))
            except RuntimeError:
                # No event loop available, skip sending
                pass

        except Exception as e:
            # Avoid recursion - don't log errors from this handler
            self.handleError(record)


def set_analysis_context(analysis_id: str):
    """Set the current analysis_id in logging context"""
    analysis_id_var.set(analysis_id)


def clear_analysis_context():
    """Clear the analysis_id from logging context"""
    analysis_id_var.set(None)


def get_analysis_context() -> Optional[str]:
    """Get the current analysis_id from logging context"""
    return analysis_id_var.get()
