"""Jira integration client"""
from typing import List, Dict, Any, Optional
from jira import JIRA
from jira.exceptions import JIRAError

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import IntegrationException


class JiraClient:
    """Client for interacting with Jira API"""
    
    def __init__(self):
        if not all([settings.jira_url, settings.jira_email, settings.jira_api_token]):
            logger.warning("Jira credentials not configured - Jira integration disabled")
            self.client = None
        else:
            try:
                self.client = JIRA(
                    server=settings.jira_url,
                    basic_auth=(settings.jira_email, settings.jira_api_token)
                )
            except Exception as e:
                logger.error(f"Failed to initialize Jira client: {e}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Jira is properly configured"""
        return self.client is not None
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get Jira issue details
        
        Args:
            issue_key: Jira issue key (e.g., 'INC-123')
            
        Returns:
            Issue details dictionary
        """
        if not self.is_configured():
            logger.warning("Jira not configured, returning empty issue")
            return {}
        
        try:
            issue = self.client.issue(issue_key)
            
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description or "",
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "Unknown",
                "created": str(issue.fields.created),
                "updated": str(issue.fields.updated),
                "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown",
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
            }
            
        except JIRAError as e:
            logger.error(f"Jira API error: {e}")
            raise IntegrationException(f"Failed to get Jira issue: {e}")
    
    async def get_issue_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get comments from a Jira issue"""
        if not self.is_configured():
            return []
        
        try:
            issue = self.client.issue(issue_key)
            comments = []
            
            for comment in issue.fields.comment.comments:
                comments.append({
                    "id": comment.id,
                    "author": comment.author.displayName if comment.author else "Unknown",
                    "body": comment.body,
                    "created": str(comment.created),
                    "updated": str(comment.updated) if hasattr(comment, 'updated') else str(comment.created)
                })
            
            logger.info(f"Retrieved {len(comments)} comments from Jira issue {issue_key}")
            return comments
            
        except JIRAError as e:
            logger.error(f"Failed to get Jira comments: {e}")
            raise IntegrationException(f"Failed to get Jira comments: {e}")
    
    async def parse_issue_for_incident(self, issue_key: str) -> Dict[str, Any]:
        """
        Parse a Jira issue to extract incident information
        
        Returns:
            Dictionary with structured incident data
        """
        issue = await self.get_issue(issue_key)
        comments = await self.get_issue_comments(issue_key)
        
        if not issue:
            return {
                "issue": {},
                "comments": [],
                "timeline": [],
                "resolution_steps": []
            }
        
        # Build timeline from comments
        timeline = [
            {
                "timestamp": comment["created"],
                "author": comment["author"],
                "text": comment["body"]
            }
            for comment in comments
        ]
        
        # Try to identify resolution steps
        resolution_keywords = ["fixed", "resolved", "deployed", "patched", "updated"]
        resolution_steps = [
            {
                "timestamp": comment["created"],
                "author": comment["author"],
                "step": comment["body"]
            }
            for comment in comments
            if any(keyword in comment["body"].lower() for keyword in resolution_keywords)
        ]
        
        return {
            "issue": issue,
            "comments": comments,
            "timeline": timeline,
            "resolution_steps": resolution_steps
        }


# Global client instance
_client: Optional[JiraClient] = None


def get_jira_client() -> JiraClient:
    """Get or create global Jira client"""
    global _client
    if _client is None:
        _client = JiraClient()
    return _client
