"""Incident Trail Agent - Collects data from various sources"""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.models.schemas import IncidentData
from app.config import settings


class IncidentTrailAgent(BaseAgent):
    """Agent responsible for collecting incident data from various sources"""
    
    def __init__(self):
        super().__init__("incident_trail")
        self.slack_client = None
        self.jira_client = None
        self.github_client = None
        
        # Lazy load optional integrations only if configured
        self._init_optional_integrations()
    
    def _init_optional_integrations(self):
        """Initialize optional integrations if configured"""
        # Slack
        if settings.slack_bot_token:
            try:
                from app.integrations.slack_client import get_slack_client
                self.slack_client = get_slack_client()
            except ImportError:
                self.log("Slack SDK not installed - Slack integration disabled", level="warning")
        
        # Jira
        if settings.jira_url and settings.jira_api_token:
            try:
                from app.integrations.jira_client import get_jira_client
                self.jira_client = get_jira_client()
            except ImportError:
                self.log("Jira client not available - Jira integration disabled", level="warning")
        
        # GitHub
        if settings.github_token:
            try:
                from app.integrations.github_client import get_github_client
                self.github_client = get_github_client()
            except ImportError:
                self.log("GitHub client not available - GitHub integration disabled", level="warning")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect incident data from configured integrations
        
        Args:
            input_data: Dict with 'slack_thread_id', 'jira_ticket_id', 'github_repo'
            
        Returns:
            Dict with collected incident data
        """
        slack_thread_id = input_data.get("slack_thread_id")
        jira_ticket_id = input_data.get("jira_ticket_id")
        github_repo = input_data.get("github_repo")
        
        self.log("Starting incident trail collection")
        
        incident_data = {
            "slack_messages": [],
            "jira_comments": [],
            "github_events": [],
            "integrations_status": {
                "slack": self.slack_client is not None,
                "jira": self.jira_client is not None,
                "github": self.github_client is not None
            }
        }
        
        # Collect from Slack
        if slack_thread_id and self.slack_client and self.slack_client.is_configured():
            try:
                self.log(f"Collecting Slack data from thread: {slack_thread_id}")
                # Parse slack_thread_id (format: channel_id:thread_ts)
                if ":" in slack_thread_id:
                    channel_id, thread_ts = slack_thread_id.split(":", 1)
                    slack_data = await self.slack_client.parse_thread_for_incident(
                        channel_id, thread_ts
                    )
                    incident_data["slack_messages"] = slack_data.get("messages", [])
                    incident_data["slack_participants"] = slack_data.get("participants", [])
                    incident_data["slack_timeline"] = slack_data.get("timeline", [])
                    self.log(f"Collected {len(incident_data['slack_messages'])} Slack messages")
                else:
                    self.log("Invalid Slack thread ID format", level="warning")
            except Exception as e:
                self.log(f"Failed to collect Slack data: {e}", level="error")
        elif slack_thread_id:
            self.log("Slack integration not configured - skipping Slack data collection", level="warning")
        
        # Collect from Jira
        if jira_ticket_id and self.jira_client and self.jira_client.is_configured():
            try:
                self.log(f"Collecting Jira data from ticket: {jira_ticket_id}")
                jira_data = await self.jira_client.parse_issue_for_incident(jira_ticket_id)
                incident_data["jira_issue"] = jira_data.get("issue", {})
                incident_data["jira_comments"] = jira_data.get("comments", [])
                incident_data["jira_timeline"] = jira_data.get("timeline", [])
                self.log(f"Collected {len(incident_data['jira_comments'])} Jira comments")
            except Exception as e:
                self.log(f"Failed to collect Jira data: {e}", level="error")
        elif jira_ticket_id:
            self.log("Jira integration not configured - skipping Jira data collection", level="warning")
        
        # Collect from GitHub
        if github_repo and self.github_client and self.github_client.is_configured():
            try:
                self.log(f"Collecting GitHub data from repo: {github_repo}")
                github_data = await self.github_client.parse_repo_for_incident(github_repo)
                incident_data["github_events"] = github_data.get("events", [])
                incident_data["github_prs"] = github_data.get("pull_requests", [])
                incident_data["github_incident_prs"] = github_data.get("incident_prs", [])
                self.log(f"Collected {len(incident_data['github_events'])} GitHub events")
            except Exception as e:
                self.log(f"Failed to collect GitHub data: {e}", level="error")
        elif github_repo:
            self.log("GitHub integration not configured - skipping GitHub data collection", level="warning")
        
        self.log("Incident trail collection completed")
        
        return self.create_result(
            success=True,
            data=incident_data
        )
