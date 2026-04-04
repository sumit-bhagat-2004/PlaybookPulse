from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Input Schemas (What the APIs/Fixtures return) ---

class SlackMessage(BaseModel):
    user: str
    timestamp: datetime
    text: str

class JiraEvent(BaseModel):
    status_change: str
    timestamp: datetime
    actor: str

class JiraTicket(BaseModel):
    ticket_id: str
    title: str
    events: List[JiraEvent]

class GitCommit(BaseModel):
    commit_hash: str
    author: str
    message: str
    timestamp: datetime

# --- Output Schemas (What the AI Orchestrator produces) ---

class PlaybookStep(BaseModel):
    step_number: int
    description: str
    expected_timeline_minutes: Optional[int] = None
    compliance_frameworks: List[str] = []

class StepAdherence(BaseModel):
    step_number: int
    status: str  # "FOLLOWED", "DELAYED", "MISSED"
    explanation: str
    actual_timeline_minutes: Optional[int] = None

class IncidentReport(BaseModel):
    incident_id: str
    playbook_steps: List[PlaybookStep]
    adherence_results: List[StepAdherence]
