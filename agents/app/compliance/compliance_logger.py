"""
Compliance Logger

Structured logging for all compliance checks with:
- JSON formatted output
- Failure detection
- Violation tracking
- Alert triggering

All compliance events flow through this logger.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceEventType(str, Enum):
    # Check events
    CHECK_STARTED = "check_started"
    CHECK_COMPLETED = "check_completed"
    CHECK_FAILED = "check_failed"
    
    # Compliance events
    CONTROL_COMPLIANT = "control_compliant"
    CONTROL_PARTIAL = "control_partial"
    CONTROL_NON_COMPLIANT = "control_non_compliant"
    
    # SLA events
    SLA_MET = "sla_met"
    SLA_VIOLATED = "sla_violated"
    
    # System events
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    
    # Alert events
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_SENT = "alert_sent"
    ALERT_FAILED = "alert_failed"


class ComplianceLogger:
    """
    Centralized compliance event logger
    
    Logs all compliance events in structured JSON format,
    detects failures, and triggers alerts via AlertSystem.
    """
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        alert_system: Optional['AlertSystem'] = None,
        log_to_console: bool = True,
        log_to_file: bool = True
    ):
        self.log_dir = Path(log_dir) if log_dir else Path("logs/compliance")
        self.alert_system = alert_system
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        
        # Create log directory
        if self.log_to_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.events: List[Dict[str, Any]] = []
        
        # Tracking
        self.violation_count = 0
        self.error_count = 0
        self.checks_completed = 0
        
        self.log_event(
            ComplianceEventType.AGENT_STARTED,
            LogLevel.INFO,
            {"session_id": self.session_id, "message": "ComplianceLogger initialized"}
        )
    
    def log_event(
        self,
        event_type: ComplianceEventType,
        level: LogLevel,
        data: Dict[str, Any],
        trigger_alert: bool = False
    ) -> Dict[str, Any]:
        """
        Log a compliance event
        
        Args:
            event_type: Type of compliance event
            level: Log level
            data: Event data
            trigger_alert: Whether to trigger an alert
            
        Returns:
            The logged event
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type.value,
            "level": level.value,
            "data": data
        }
        
        self.events.append(event)
        
        # Update tracking
        if event_type == ComplianceEventType.CHECK_COMPLETED:
            self.checks_completed += 1
        elif event_type in [ComplianceEventType.CONTROL_NON_COMPLIANT, ComplianceEventType.SLA_VIOLATED]:
            self.violation_count += 1
            trigger_alert = True  # Always alert on violations
        elif event_type in [ComplianceEventType.CHECK_FAILED, ComplianceEventType.AGENT_ERROR]:
            self.error_count += 1
            trigger_alert = True  # Always alert on errors
        
        # Output
        if self.log_to_console:
            self._print_event(event)
        
        if self.log_to_file:
            self._write_event(event)
        
        # Trigger alert if needed
        if trigger_alert and self.alert_system:
            self._trigger_alert(event)
        
        return event
    
    def _print_event(self, event: Dict[str, Any]) -> None:
        """Print event to console"""
        level = event["level"]
        event_type = event["event_type"]
        timestamp = event["timestamp"]
        
        # Color codes for terminal
        colors = {
            "debug": "\033[90m",     # Gray
            "info": "\033[94m",      # Blue
            "warning": "\033[93m",   # Yellow
            "error": "\033[91m",     # Red
            "critical": "\033[95m"   # Magenta
        }
        reset = "\033[0m"
        
        color = colors.get(level, "")
        prefix = f"{color}[{timestamp}] [{level.upper()}] [{event_type}]{reset}"
        
        message = event["data"].get("message", json.dumps(event["data"]))
        print(f"{prefix} {message}")
    
    def _write_event(self, event: Dict[str, Any]) -> None:
        """Write event to log file"""
        log_file = self.log_dir / f"compliance_{self.session_id}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def _trigger_alert(self, event: Dict[str, Any]) -> None:
        """Trigger alert for the event"""
        if not self.alert_system:
            return
        
        try:
            self.alert_system.send_alert(
                title=f"Compliance {event['event_type']}",
                message=event["data"].get("message", "Compliance event triggered"),
                severity=event["level"],
                event=event
            )
            
            self.log_event(
                ComplianceEventType.ALERT_SENT,
                LogLevel.INFO,
                {"message": f"Alert sent for {event['event_type']}"},
                trigger_alert=False
            )
        except Exception as e:
            self.log_event(
                ComplianceEventType.ALERT_FAILED,
                LogLevel.ERROR,
                {"message": f"Failed to send alert: {str(e)}"},
                trigger_alert=False
            )
    
    # Convenience methods for common events
    
    def log_check_started(self, check_name: str, check_type: str, **kwargs) -> None:
        """Log that a compliance check has started"""
        self.log_event(
            ComplianceEventType.CHECK_STARTED,
            LogLevel.INFO,
            {
                "message": f"Started {check_type} check: {check_name}",
                "check_name": check_name,
                "check_type": check_type,
                **kwargs
            }
        )
    
    def log_check_completed(
        self, 
        check_name: str, 
        status: str, 
        score: Optional[float] = None,
        **kwargs
    ) -> None:
        """Log that a compliance check has completed"""
        self.log_event(
            ComplianceEventType.CHECK_COMPLETED,
            LogLevel.INFO if status == "pass" else LogLevel.WARNING,
            {
                "message": f"Completed check '{check_name}': {status}",
                "check_name": check_name,
                "status": status,
                "score": score,
                **kwargs
            }
        )
    
    def log_check_failed(self, check_name: str, error: str, **kwargs) -> None:
        """Log that a compliance check has failed"""
        self.log_event(
            ComplianceEventType.CHECK_FAILED,
            LogLevel.ERROR,
            {
                "message": f"Check '{check_name}' failed: {error}",
                "check_name": check_name,
                "error": error,
                **kwargs
            },
            trigger_alert=True
        )
    
    def log_control_result(
        self,
        control_id: str,
        control_title: str,
        status: str,
        evidence: List[str],
        gaps: List[str]
    ) -> None:
        """Log a CIS control check result"""
        if status == "compliant":
            event_type = ComplianceEventType.CONTROL_COMPLIANT
            level = LogLevel.INFO
        elif status == "partial":
            event_type = ComplianceEventType.CONTROL_PARTIAL
            level = LogLevel.WARNING
        else:
            event_type = ComplianceEventType.CONTROL_NON_COMPLIANT
            level = LogLevel.ERROR
        
        self.log_event(
            event_type,
            level,
            {
                "message": f"Control {control_id}: {status}",
                "control_id": control_id,
                "control_title": control_title,
                "status": status,
                "evidence_count": len(evidence),
                "gaps_count": len(gaps),
                "gaps": gaps
            },
            trigger_alert=(status == "non_compliant")
        )
    
    def log_sla_result(
        self,
        sla_name: str,
        status: str,
        required_minutes: float,
        actual_minutes: float
    ) -> None:
        """Log an SLA check result"""
        if status == "met":
            event_type = ComplianceEventType.SLA_MET
            level = LogLevel.INFO
        else:
            event_type = ComplianceEventType.SLA_VIOLATED
            level = LogLevel.ERROR
        
        self.log_event(
            event_type,
            level,
            {
                "message": f"SLA '{sla_name}': {status} (required: {required_minutes}m, actual: {actual_minutes}m)",
                "sla_name": sla_name,
                "status": status,
                "required_minutes": required_minutes,
                "actual_minutes": actual_minutes,
                "delta_minutes": actual_minutes - required_minutes
            },
            trigger_alert=(status == "violated")
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of logged events"""
        return {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "checks_completed": self.checks_completed,
            "violation_count": self.violation_count,
            "error_count": self.error_count,
            "event_types": self._count_event_types()
        }
    
    def _count_event_types(self) -> Dict[str, int]:
        """Count events by type"""
        counts = {}
        for event in self.events:
            event_type = event["event_type"]
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def export_logs(self, format: str = "json") -> str:
        """Export all logs"""
        if format == "json":
            return json.dumps(self.events, indent=2)
        else:
            # JSONL format
            return "\n".join(json.dumps(e) for e in self.events)
