"""GitHub integration client"""
from typing import List, Dict, Any, Optional
from github import Github, GithubException

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import IntegrationException


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self):
        if not settings.github_token:
            logger.warning("GitHub token not configured - GitHub integration disabled")
            self.client = None
        else:
            self.client = Github(settings.github_token)
    
    def is_configured(self) -> bool:
        """Check if GitHub is properly configured"""
        return self.client is not None
    
    async def get_repository(self, repo_full_name: str):
        """Get repository object"""
        if not self.is_configured():
            return None
        
        try:
            return self.client.get_repo(repo_full_name)
        except GithubException as e:
            logger.error(f"Failed to get repository: {e}")
            raise IntegrationException(f"Failed to get GitHub repository: {e}")
    
    async def get_recent_events(
        self,
        repo_full_name: str,
        event_types: List[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent repository events
        
        Args:
            repo_full_name: Repository full name (org/repo)
            event_types: Filter by event types (e.g., ['PushEvent', 'IssuesEvent'])
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        if not self.is_configured():
            logger.warning("GitHub not configured, returning empty events")
            return []
        
        try:
            repo = await self.get_repository(repo_full_name)
            if not repo:
                return []
            
            events = []
            for event in repo.get_events()[:limit]:
                event_data = {
                    "type": event.type,
                    "created_at": str(event.created_at),
                    "actor": event.actor.login if event.actor else "Unknown",
                    "payload": {}
                }
                
                # Add type-specific payload data
                if event.type == "PushEvent":
                    event_data["payload"] = {
                        "commits": len(event.payload.get("commits", [])),
                        "ref": event.payload.get("ref", "")
                    }
                elif event.type == "IssuesEvent":
                    event_data["payload"] = {
                        "action": event.payload.get("action", ""),
                        "issue_number": event.payload.get("issue", {}).get("number")
                    }
                elif event.type == "PullRequestEvent":
                    event_data["payload"] = {
                        "action": event.payload.get("action", ""),
                        "pr_number": event.payload.get("pull_request", {}).get("number")
                    }
                
                # Filter by event types if specified
                if not event_types or event.type in event_types:
                    events.append(event_data)
            
            logger.info(f"Retrieved {len(events)} events from GitHub repo {repo_full_name}")
            return events
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise IntegrationException(f"Failed to get GitHub events: {e}")
    
    async def get_pull_requests(
        self,
        repo_full_name: str,
        state: str = "all",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get repository pull requests"""
        if not self.is_configured():
            return []
        
        try:
            repo = await self.get_repository(repo_full_name)
            if not repo:
                return []
            
            prs = []
            for pr in repo.get_pulls(state=state)[:limit]:
                prs.append({
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "created_at": str(pr.created_at),
                    "updated_at": str(pr.updated_at),
                    "merged_at": str(pr.merged_at) if pr.merged_at else None,
                    "author": pr.user.login if pr.user else "Unknown"
                })
            
            return prs
            
        except GithubException as e:
            logger.error(f"Failed to get pull requests: {e}")
            return []
    
    async def parse_repo_for_incident(
        self,
        repo_full_name: str,
        since: str = None
    ) -> Dict[str, Any]:
        """
        Parse GitHub repository activity for incident-related information
        
        Returns:
            Dictionary with structured incident data
        """
        events = await self.get_recent_events(repo_full_name)
        prs = await self.get_pull_requests(repo_full_name, state="closed", limit=20)
        
        # Filter for incident-related PRs
        incident_keywords = ["hotfix", "incident", "emergency", "critical", "urgent"]
        incident_prs = [
            pr for pr in prs
            if any(keyword in pr["title"].lower() for keyword in incident_keywords)
        ]
        
        return {
            "events": events,
            "pull_requests": prs,
            "incident_prs": incident_prs,
            "total_events": len(events),
            "total_prs": len(prs)
        }


# Global client instance
_client: Optional[GitHubClient] = None


def get_github_client() -> GitHubClient:
    """Get or create global GitHub client"""
    global _client
    if _client is None:
        _client = GitHubClient()
    return _client
