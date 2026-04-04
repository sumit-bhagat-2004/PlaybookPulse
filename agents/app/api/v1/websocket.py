"""WebSocket endpoints for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

from app.services.websocket_manager import WebSocketManager
from app.utils.logger import logger

router = APIRouter()

# Global WebSocket manager
ws_manager = WebSocketManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time analysis updates
    
    Clients connect with a unique client_id to receive:
    - Analysis progress updates
    - Agent status changes
    - Completion notifications
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
                    await ws_manager.send_personal_message(
                        client_id,
                        {
                            "type": "subscribed",
                            "analysis_id": analysis_id,
                            "message": f"Subscribed to analysis {analysis_id}"
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
