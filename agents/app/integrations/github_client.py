"""GitHub integration client"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
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
    
    async def get_commits(
        self,
        repo_full_name: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        branch: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get detailed commit information from repository
        
        Args:
            repo_full_name: Repository full name (org/repo)
            since: Only commits after this date
            until: Only commits before this date
            branch: Specific branch to get commits from
            limit: Maximum number of commits to return
            
        Returns:
            List of detailed commit dictionaries
        """
        if not self.is_configured():
            logger.warning("GitHub not configured, returning empty commits")
            return []
        
        try:
            repo = await self.get_repository(repo_full_name)
            if not repo:
                return []
            
            # Set default time range if not provided (last 7 days)
            if not since:
                since = datetime.utcnow() - timedelta(days=7)
            
            commits = []
            commit_count = 0
            
            # Get commits from specific branch or default branch
            if branch:
                try:
                    branch_obj = repo.get_branch(branch)
                    commits_iter = repo.get_commits(sha=branch_obj.commit.sha, since=since, until=until)
                except GithubException:
                    logger.warning(f"Branch {branch} not found, using default branch")
                    commits_iter = repo.get_commits(since=since, until=until)
            else:
                commits_iter = repo.get_commits(since=since, until=until)
            
            for commit in commits_iter:
                if commit_count >= limit:
                    break
                
                try:
                    # Extract commit details
                    commit_data = {
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "author": {
                            "name": commit.commit.author.name if commit.commit.author else "Unknown",
                            "email": commit.commit.author.email if commit.commit.author else "Unknown",
                            "username": commit.author.login if commit.author else "Unknown"
                        },
                        "committer": {
                            "name": commit.commit.committer.name if commit.commit.committer else "Unknown",
                            "date": str(commit.commit.committer.date) if commit.commit.committer else None
                        },
                        "date": str(commit.commit.author.date) if commit.commit.author else None,
                        "url": commit.html_url,
                        "stats": {
                            "additions": commit.stats.additions if commit.stats else 0,
                            "deletions": commit.stats.deletions if commit.stats else 0,
                            "total": commit.stats.total if commit.stats else 0
                        },
                        "files_changed": []
                    }
                    
                    # Get files changed (limited to avoid rate limits)
                    try:
                        files = commit.files
                        if files:
                            for file in files[:20]:  # Limit to 20 files per commit
                                commit_data["files_changed"].append({
                                    "filename": file.filename,
                                    "status": file.status,
                                    "additions": file.additions,
                                    "deletions": file.deletions,
                                    "changes": file.changes
                                })
                    except Exception as file_error:
                        logger.debug(f"Could not fetch files for commit {commit.sha}: {file_error}")
                    
                    commits.append(commit_data)
                    commit_count += 1
                    
                except Exception as commit_error:
                    logger.warning(f"Error processing commit {commit.sha}: {commit_error}")
                    continue
            
            logger.info(f"Retrieved {len(commits)} commits from GitHub repo {repo_full_name}")
            return commits
            
        except GithubException as e:
            logger.error(f"GitHub API error fetching commits: {e}")
            raise IntegrationException(f"Failed to get GitHub commits: {e}")
    
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
        since: str = None,
        until: str = None,
        branch: str = None
    ) -> Dict[str, Any]:
        """
        Parse GitHub repository activity for incident-related information
        
        Args:
            repo_full_name: Repository full name (org/repo)
            since: ISO timestamp or datetime string for start of incident window
            until: ISO timestamp or datetime string for end of incident window
            branch: Specific branch to analyze
            
        Returns:
            Dictionary with structured incident data including detailed commits
        """
        # Parse time range
        since_dt = None
        until_dt = None
        
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                logger.warning(f"Could not parse 'since' timestamp: {since}, using default")
        
        if until:
            try:
                until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                logger.warning(f"Could not parse 'until' timestamp: {until}")
        
        # Fetch all data in parallel conceptually (but PyGithub is sync)
        events = await self.get_recent_events(repo_full_name)
        prs = await self.get_pull_requests(repo_full_name, state="closed", limit=20)
        commits = await self.get_commits(
            repo_full_name,
            since=since_dt,
            until=until_dt,
            branch=branch,
            limit=100
        )
        
        # Filter for incident-related PRs
        incident_keywords = ["hotfix", "incident", "emergency", "critical", "urgent", "fix", "patch"]
        incident_prs = [
            pr for pr in prs
            if any(keyword in pr["title"].lower() for keyword in incident_keywords)
        ]
        
        # Filter for incident-related commits
        incident_commits = [
            commit for commit in commits
            if any(keyword in commit["message"].lower() for keyword in incident_keywords)
        ]
        
        # Build timeline of all activities
        timeline = []
        
        # Add commits to timeline
        for commit in commits:
            timeline.append({
                "type": "commit",
                "timestamp": commit["date"],
                "actor": commit["author"]["username"],
                "description": commit["message"].split('\n')[0][:100],  # First line, truncated
                "sha": commit["sha"],
                "files_changed": len(commit["files_changed"]),
                "additions": commit["stats"]["additions"],
                "deletions": commit["stats"]["deletions"]
            })
        
        # Add PRs to timeline
        for pr in prs:
            timeline.append({
                "type": "pull_request",
                "timestamp": pr["created_at"],
                "actor": pr["author"],
                "description": f"PR #{pr['number']}: {pr['title']}",
                "pr_number": pr["number"],
                "state": pr["state"]
            })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "events": events,
            "pull_requests": prs,
            "incident_prs": incident_prs,
            "commits": commits,
            "incident_commits": incident_commits,
            "timeline": timeline,
            "total_events": len(events),
            "total_prs": len(prs),
            "total_commits": len(commits),
            "total_incident_commits": len(incident_commits)
        }


# Global client instance
_client: Optional[GitHubClient] = None


def get_github_client() -> GitHubClient:
    """Get or create global GitHub client"""
    global _client
    if _client is None:
        _client = GitHubClient()
    return _client
