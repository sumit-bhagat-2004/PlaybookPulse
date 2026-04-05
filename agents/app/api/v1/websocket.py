"""WebSocket endpoints for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

from app.services.websocket_manager import WebSocketManager
from app.utils.logger import logger, enable_websocket_logging

router = APIRouter()

# Global WebSocket manager
ws_manager = WebSocketManager()

# Enable WebSocket logging on startup
enable_websocket_logging(ws_manager)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time analysis updates

    Clients connect with a unique client_id to receive:
    - Analysis progress updates
    - Agent status changes
    - Completion notifications
    - Real-time logs
    - Slack messages
    """
    await ws_manager.connect(client_id, websocket)

    try:
        logger.info(f"WebSocket client connected: {client_id}")

        # Send welcome message
        await ws_manager.send_personal_message(
            client_id,
            {
                "type": "connection",
                "message": "Connected to PlaybookPulse Agents",
                "client_id": client_id
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "ping":
                await ws_manager.send_personal_message(
                    client_id,
                    {"type": "pong", "timestamp": data.get("timestamp")}
                )

            elif message_type == "subscribe":
                # Subscribe to specific analysis updates
                analysis_id = data.get("analysis_id")
                if analysis_id:
                    ws_manager.subscribe_client(client_id, analysis_id)

                    # Send existing logs for this analysis
                    existing_logs = ws_manager.get_analysis_logs(analysis_id)
                    for log in existing_logs[-20:]:  # Send last 20 logs
                        await ws_manager.send_personal_message(client_id, log)

                    await ws_manager.send_personal_message(
                        client_id,
                        {
                            "type": "subscribed",
                            "analysis_id": analysis_id,
                            "message": f"Subscribed to analysis {analysis_id}"
                        }
                    )

            elif message_type == "get_slack_messages":
                # Request Slack messages for a specific analysis
                analysis_id = data.get("analysis_id")
                if analysis_id:
                    # Import here to avoid circular imports
                    from app.services.analysis_service import get_analysis

                    try:
                        analysis = get_analysis(analysis_id)

                        slack_messages = analysis.get("slack_messages", []) if analysis else []
                        slack_thread_id = analysis.get("slack_thread_id", "") if analysis else ""

                        await ws_manager.send_personal_message(
                            client_id,
                            {
                                "type": "slack_messages",
                                "analysis_id": analysis_id,
                                "slack_thread_id": slack_thread_id,
                                "messages": slack_messages,
                                "participant_count": len(set(m.get("user") for m in slack_messages if m.get("user")))
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error retrieving Slack messages: {e}")
                        await ws_manager.send_personal_message(
                            client_id,
                            {
                                "type": "error",
                                "message": f"Could not retrieve Slack messages: {str(e)}"
                            }
                        )

            elif message_type == "unsubscribe":
                # Unsubscribe from analysis updates
                ws_manager.unsubscribe_client(client_id)
                await ws_manager.send_personal_message(
                    client_id,
                    {
                        "type": "unsubscribed",
                        "message": "Unsubscribed from analysis updates"
                    }
                )

            else:
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
        ws_manager.disconnect(client_id)

    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        ws_manager.disconnect(client_id)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": ws_manager.get_connection_count(),
        "status": "operational"
    }
