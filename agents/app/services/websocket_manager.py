"""WebSocket Manager for handling real-time connections"""
from fastapi import WebSocket
from typing import Dict, Any
import json
from datetime import datetime

from app.utils.logger import logger


class WebSocketManager:
    """Manages WebSocket connections and broadcasting"""

    def __init__(self):
        # Store active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Track client subscriptions: client_id -> analysis_id
        self.client_subscriptions: Dict[str, str] = {}
        # Store log queues per analysis: analysis_id -> list of logs
        self.analysis_logs: Dict[str, list] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id} (total: {len(self.active_connections)})")

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
            logger.info(f"WebSocket disconnected: {client_id} (total: {len(self.active_connections)})")

    def subscribe_client(self, client_id: str, analysis_id: str):
        """Subscribe a client to analysis updates"""
        self.client_subscriptions[client_id] = analysis_id
        logger.info(f"Client {client_id} subscribed to analysis {analysis_id}")

    def unsubscribe_client(self, client_id: str):
        """Unsubscribe a client from analysis updates"""
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]

    def get_interested_clients(self, analysis_id: str) -> list:
        """Get all client IDs subscribed to a specific analysis"""
        return [
            client_id
            for client_id, sub_analysis_id in self.client_subscriptions.items()
            if sub_analysis_id == analysis_id
        ]

    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json({
                    **message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json({
                    **message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_analysis_update(
        self,
        analysis_id: str,
        status: str,
        progress: int,
        message: str = ""
    ):
        """Send analysis progress update to all connected clients"""
        await self.broadcast({
            "type": "analysis_update",
            "analysis_id": analysis_id,
            "status": status,
            "progress": progress,
            "message": message
        })

    async def send_agent_status(
        self,
        analysis_id: str,
        agent_name: str,
        status: str,
        message: str = ""
    ):
        """Send agent status update"""
        await self.broadcast({
            "type": "agent_status",
            "analysis_id": analysis_id,
            "agent_name": agent_name,
            "status": status,
            "message": message
        })

    async def send_log_message(self, analysis_id: str, log_data: Dict[str, Any]):
        """Send a log message to clients subscribed to this analysis"""
        # Store log in memory (keep last 100 per analysis)
        if analysis_id not in self.analysis_logs:
            self.analysis_logs[analysis_id] = []

        self.analysis_logs[analysis_id].append(log_data)
        # Keep only last 100 logs
        if len(self.analysis_logs[analysis_id]) > 100:
            self.analysis_logs[analysis_id] = self.analysis_logs[analysis_id][-100:]

        # Send to all clients subscribed to this analysis
        interested_clients = self.get_interested_clients(analysis_id)

        for client_id in interested_clients:
            await self.send_personal_message(client_id, log_data)

    def get_analysis_logs(self, analysis_id: str) -> list:
        """Get all stored logs for an analysis"""
        return self.analysis_logs.get(analysis_id, [])

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
