"""Enums and constants"""
from enum import Enum


class AgentType(str, Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    PLAYBOOK_PARSER = "playbook_parser"
    INCIDENT_TRAIL = "incident_trail"
    ADHERENCE_CHECKER = "adherence_checker"
    COMPLIANCE_MAPPER = "compliance_mapper"


class IntegrationType(str, Enum):
    """Supported integration types"""
    SLACK = "slack"
    JIRA = "jira"
    GITHUB = "github"
    ANTHROPIC = "anthropic"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Constants
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300
WEBSOCKET_HEARTBEAT = 30
