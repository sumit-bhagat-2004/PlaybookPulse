import json
from pathlib import Path
from typing import List
from backend.schemas import SlackMessage, JiraTicket, GitCommit

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_playbook() -> str:
    playbook_path = FIXTURES_DIR / "playbook_v1.md"
    with open(playbook_path, "r") as f:
        return f.read()

def load_slack_thread() -> List[SlackMessage]:
    slack_path = FIXTURES_DIR / "slack_thread.json"
    with open(slack_path, "r") as f:
        data = json.load(f)
        return [SlackMessage(**msg) for msg in data]

def load_jira_ticket() -> JiraTicket:
    jira_path = FIXTURES_DIR / "jira_ticket.json"
    with open(jira_path, "r") as f:
        data = json.load(f)
        return JiraTicket(**data)

def load_github_commits() -> List[GitCommit]:
    github_path = FIXTURES_DIR / "github_commits.json"
    with open(github_path, "r") as f:
        data = json.load(f)
        return [GitCommit(**commit) for commit in data]
