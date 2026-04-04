"""Database models (optional - for persistence)"""
from sqlalchemy import Column, String, DateTime, Text, Float, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

from app.models.schemas import AnalysisStatus

Base = declarative_base()


class Analysis(Base):
    """Database model for storing analysis results"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    playbook_content = Column(Text, nullable=False)
    slack_thread_id = Column(String, nullable=True)
    jira_ticket_id = Column(String, nullable=True)
    github_repo = Column(String, nullable=True)
    
    # JSON columns for complex data
    playbook_steps = Column(JSON, default=[])
    incident_data = Column(JSON, default={})
    adherence_checks = Column(JSON, default=[])
    compliance_mappings = Column(JSON, default=[])
    
    overall_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "status": self.status.value if self.status else None,
            "playbook_content": self.playbook_content,
            "slack_thread_id": self.slack_thread_id,
            "jira_ticket_id": self.jira_ticket_id,
            "github_repo": self.github_repo,
            "playbook_steps": self.playbook_steps,
            "incident_data": self.incident_data,
            "adherence_checks": self.adherence_checks,
            "compliance_mappings": self.compliance_mappings,
            "overall_score": self.overall_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
