"""Pydantic models and schemas"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Enums
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ComplianceFramework(str, Enum):
    CIS_CONTROLS_V8 = "cis_controls_v8"  # PRIMARY - CIS Controls v8 Control 17


class AdherenceLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


# Request/Response Models
class AnalysisRequest(BaseModel):
    """Request to start a new analysis"""
    playbook_content: str = Field(..., description="Markdown content of the playbook")
    slack_thread_id: Optional[str] = Field(None, description="Slack thread ID for incident")
    jira_ticket_id: Optional[str] = Field(None, description="Jira ticket ID")
    github_repo: Optional[str] = Field(None, description="GitHub repository (org/repo)")
    compliance_frameworks: List[ComplianceFramework] = Field(
        default=[ComplianceFramework.CIS_CONTROLS_V8],
        description="Compliance frameworks to check against (CIS Controls v8 only)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "playbook_content": "# Incident Response Playbook\n## Detection\n...",
                "slack_thread_id": "1234567890.123456",
                "jira_ticket_id": "INC-123",
                "github_repo": "myorg/myrepo"
            }
        }


class PlaybookStep(BaseModel):
    """A single step in the playbook"""
    step_id: str
    phase: str
    description: str
    required_actions: List[str]
    responsible_roles: List[str]


class IncidentData(BaseModel):
    """Collected incident data"""
    slack_messages: List[Dict[str, Any]] = []
    jira_comments: List[Dict[str, Any]] = []
    github_events: List[Dict[str, Any]] = []


class AdherenceCheck(BaseModel):
    """Result of adherence checking for a step"""
    step_id: str
    adherence_level: AdherenceLevel
    evidence: List[str]
    gaps: List[str]
    recommendations: List[str]


class ComplianceMapping(BaseModel):
    """Mapping to compliance framework"""
    framework: ComplianceFramework
    control_id: str
    control_title: str
    adherence_level: AdherenceLevel
    supporting_evidence: List[str]


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    analysis_id: str
    status: AnalysisStatus
    playbook_steps: List[PlaybookStep] = []
    incident_data: Optional[IncidentData] = None
    adherence_checks: List[AdherenceCheck] = []
    compliance_mappings: List[ComplianceMapping] = []
    overall_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    """API response for analysis"""
    analysis_id: str
    status: AnalysisStatus
    message: str
    result: Optional[AnalysisResult] = None


class ReportRequest(BaseModel):
    """Request to generate a report"""
    format: str = Field(default="pdf", pattern="^(pdf|json|html)$")
    include_recommendations: bool = Field(default=True)
    include_evidence: bool = Field(default=True)


class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str
    analysis_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
