"""Slack integration client"""
from typing import List, Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import IntegrationException


class SlackClient:
    """Client for interacting with Slack API"""
    
    def __init__(self):
        if not settings.slack_bot_token:
            logger.warning("Slack bot token not configured - Slack integration disabled")
            self.client = None
        else:
            self.client = WebClient(token=settings.slack_bot_token)
    
    def is_configured(self) -> bool:
        """Check if Slack is properly configured"""
        return self.client is not None
    
    async def get_thread_messages(self, channel_id: str, thread_ts: str) -> List[Dict[str, Any]]:
        """
        Get all messages from a Slack thread
        
        Args:
            channel_id: Slack channel ID
            thread_ts: Thread timestamp
            
        Returns:
            List of message dictionaries
        """
        if not self.is_configured():
            logger.warning("Slack not configured, returning empty messages")
            return []
        
        try:
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            
            messages = response.get("messages", [])
            logger.info(f"Retrieved {len(messages)} messages from Slack thread")
            
            return messages
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e}")
            raise IntegrationException(f"Failed to get Slack thread: {e}")
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information"""
        if not self.is_configured():
            return {"id": user_id, "name": "Unknown User"}
        
        try:
            response = self.client.users_info(user=user_id)
            return response.get("user", {})
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {e}")
            return {"id": user_id, "name": "Unknown User"}
    
    async def parse_thread_for_incident(
        self,
        channel_id: str,
        thread_ts: str
    ) -> Dict[str, Any]:
        """
        Parse a Slack thread to extract incident information
        
        Returns:
            Dictionary with structured incident data
        """
        messages = await self.get_thread_messages(channel_id, thread_ts)
        
        if not messages:
            return {
                "messages": [],
                "participants": [],
                "timeline": [],
                "actions_taken": []
            }
        
        # Extract participants
        participants = list(set(msg.get("user", "") for msg in messages if msg.get("user")))
        
        # Build timeline
        timeline = [
            {
                "timestamp": msg.get("ts"),
                "user": msg.get("user"),
                "text": msg.get("text", ""),
                "reactions": msg.get("reactions", [])
            }
            for msg in messages
        ]
        
        # Try to identify actions (messages with certain keywords)
        action_keywords = ["resolved", "fixed", "deployed", "escalated", "notified", "investigated"]
        actions_taken = [
            {
                "timestamp": msg.get("ts"),
                "user": msg.get("user"),
                "action": msg.get("text", "")
            }
            for msg in messages
            if any(keyword in msg.get("text", "").lower() for keyword in action_keywords)
        ]
        
        return {
            "messages": messages,
            "participants": participants,
            "timeline": timeline,
            "actions_taken": actions_taken
        }


# Global client instance
_client: Optional[SlackClient] = None


def get_slack_client() -> SlackClient:
    """Get or create global Slack client"""
    global _client
    if _client is None:
        _client = SlackClient()
    return _client
