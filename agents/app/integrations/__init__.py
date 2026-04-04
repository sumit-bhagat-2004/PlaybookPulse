"""Integrations package"""
# Core LLM clients (always available)
from app.integrations.llm_client import LLMClient, get_llm_client

__all__ = [
    "LLMClient",
    "get_llm_client",
]

# Optional integrations - import only when needed
# from app.integrations.slack_client import SlackClient, get_slack_client
# from app.integrations.jira_client import JiraClient, get_jira_client
# from app.integrations.github_client import GitHubClient, get_github_client
