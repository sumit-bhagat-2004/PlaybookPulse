"""
Timestamp Analysis Module
Extracts timestamps from incident data and calculates SLA compliance
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from app.compliance.cis_framework import (
    get_cis_requirements_for_step,
    calculate_sla_violation_severity,
    SLAViolationSeverity
)


class TimestampAnalyzer:
    """Analyzes timestamps from incident data to check SLA compliance"""
    
    def __init__(self):
        self.incident_start_time: Optional[datetime] = None
        self.timeline_events: List[Dict[str, Any]] = []
    
    def extract_timeline_from_incident_data(self, incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all timeline events from Slack, Jira, and GitHub data
        
        Returns:
            List of events with timestamps, sorted chronologically
        """
        events = []
        
        # Extract from Slack messages
        slack_messages = incident_data.get("slack_messages", [])
        for msg in slack_messages:
            timestamp_str = msg.get("timestamp")
            if timestamp_str:
                try:
                    ts = self._parse_timestamp(timestamp_str)
                    events.append({
                        "timestamp": ts,
                        "source": "slack",
                        "actor": msg.get("user", "unknown"),
                        "action": msg.get("text", "")[:100],  # First 100 chars
                        "raw_data": msg
                    })
                except Exception as e:
                    print(f"Failed to parse Slack timestamp {timestamp_str}: {e}")
        
        # Extract from Slack timeline (if structured differently)
        slack_timeline = incident_data.get("slack_timeline", [])
        for event in slack_timeline:
            timestamp_str = event.get("timestamp")
            if timestamp_str:
                try:
                    ts = self._parse_timestamp(timestamp_str)
                    if not any(e["timestamp"] == ts and e["source"] == "slack" for e in events):
                        events.append({
                            "timestamp": ts,
                            "source": "slack",
                            "action": event.get("text", "")[:100],
                            "raw_data": event
                        })
                except Exception:
                    pass
        
        # Extract from Jira events
        jira_timeline = incident_data.get("jira_timeline", [])
        for event in jira_timeline:
            timestamp_str = event.get("timestamp")
            if timestamp_str:
                try:
                    ts = self._parse_timestamp(timestamp_str)
                    events.append({
                        "timestamp": ts,
                        "source": "jira",
                        "actor": event.get("actor", "unknown"),
                        "action": event.get("status_change", "Status update"),
                        "raw_data": event
                    })
                except Exception as e:
                    print(f"Failed to parse Jira timestamp {timestamp_str}: {e}")
        
        # Extract from GitHub events
        github_events = incident_data.get("github_events", [])
        for event in github_events:
            timestamp_str = event.get("timestamp")
            if timestamp_str:
                try:
                    ts = self._parse_timestamp(timestamp_str)
                    events.append({
                        "timestamp": ts,
                        "source": "github",
                        "actor": event.get("author", "unknown"),
                        "action": event.get("message", "Commit")[:100],
                        "raw_data": event
                    })
                except Exception as e:
                    print(f"Failed to parse GitHub timestamp {timestamp_str}: {e}")
        
        # Sort by timestamp
        events.sort(key=lambda e: e["timestamp"])
        
        # Set incident start time as the first event
        if events and not self.incident_start_time:
            self.incident_start_time = events[0]["timestamp"]
        
        self.timeline_events = events
        return events
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse various timestamp formats"""
        try:
            # Try ISO format first
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            # Fall back to dateutil parser
            return date_parser.parse(timestamp_str)
    
    def calculate_step_timing(
        self,
        step_id: str,
        step_title: str,
        step_phase: str,
        playbook_step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate timing metrics for a specific playbook step
        
        Returns:
            Dict with timing analysis and SLA compliance
        """
        # Get CIS requirements for this step
        step_type = self._infer_step_type(step_title, step_phase)
        cis_req = get_cis_requirements_for_step(step_type, step_phase)
        
        # Find evidence of this step in timeline
        step_evidence = self._find_step_evidence(step_id, step_title, step_type)
        
        if not step_evidence:
            return {
                "step_id": step_id,
                "step_title": step_title,
                "step_type": step_type,
                "cis_phase": cis_req.get("cis_phase"),
                "expected_sla_minutes": cis_req.get("sla_minutes"),
                "actual_completion_time": None,
                "time_from_incident_start_minutes": None,
                "sla_status": "not_completed",
                "sla_violation_severity": None,
                "evidence_found": False
            }
        
        # Calculate timing
        completion_time = step_evidence["timestamp"]
        time_delta = completion_time - self.incident_start_time if self.incident_start_time else timedelta(0)
        actual_minutes = int(time_delta.total_seconds() / 60)
        
        # Check SLA compliance
        expected_sla = cis_req.get("sla_minutes")
        sla_status = "within_sla"
        violation_severity = SLAViolationSeverity.NONE
        
        if expected_sla:
            if actual_minutes > expected_sla:
                sla_status = "violated"
                violation_severity = calculate_sla_violation_severity(expected_sla, actual_minutes)
            else:
                sla_status = "within_sla"
        else:
            sla_status = "no_sla_defined"
        
        return {
            "step_id": step_id,
            "step_title": step_title,
            "step_type": step_type,
            "cis_phase": cis_req.get("cis_phase"),
            "expected_sla_minutes": expected_sla,
            "actual_completion_time": completion_time.isoformat(),
            "time_from_incident_start_minutes": actual_minutes,
            "sla_status": sla_status,
            "sla_violation_severity": violation_severity.value if violation_severity != SLAViolationSeverity.NONE else None,
            "sla_overage_minutes": actual_minutes - expected_sla if expected_sla and actual_minutes > expected_sla else 0,
            "evidence_found": True,
            "evidence_source": step_evidence["source"],
            "evidence_actor": step_evidence.get("actor"),
            "evidence_action": step_evidence.get("action")
        }
    
    def _infer_step_type(self, step_title: str, step_phase: str) -> str:
        """Infer step type from title and phase"""
        title_lower = step_title.lower()
        phase_lower = step_phase.lower() if step_phase else ""
        
        # Detection/Acknowledgment
        if any(word in title_lower for word in ["acknowledge", "alert", "detect", "notify pagerduty"]):
            return "acknowledgment"
        
        # Analysis
        if any(word in title_lower for word in ["analyze", "assess", "investigate", "determine", "calculate", "check logs"]):
            return "analysis"
        
        # Containment
        if any(word in title_lower for word in ["contain", "disable", "revoke", "block", "isolate"]):
            return "containment"
        
        # Eradication
        if any(word in title_lower for word in ["eradicate", "rotate", "remove", "replace", "fix"]):
            return "eradication"
        
        # Recovery
        if any(word in title_lower for word in ["recover", "restore", "verify", "test", "enable"]):
            return "recovery"
        
        # Post-incident
        if any(word in title_lower for word in ["post-mortem", "lessons", "review", "document", "close"]):
            return "post_incident"
        
        # Communication
        if any(word in title_lower for word in ["communicate", "notify", "update stakeholders", "escalate"]):
            return "communication"
        
        # Fall back to phase
        if "detection" in phase_lower:
            return "detection"
        elif "containment" in phase_lower:
            return "containment"
        elif "eradication" in phase_lower:
            return "eradication"
        elif "recovery" in phase_lower:
            return "recovery"
        elif "post" in phase_lower:
            return "post_incident"
        
        return "analysis"  # Default
    
    def _find_step_evidence(self, step_id: str, step_title: str, step_type: str) -> Optional[Dict[str, Any]]:
        """Find evidence of step completion in timeline"""
        title_keywords = step_title.lower().split()
        
        # Define evidence patterns for different step types
        evidence_patterns = {
            "acknowledgment": ["acknowledge", "looking into", "investigating", "pagerduty"],
            "analysis": ["analyzing", "checking", "found", "identified", "assess"],
            "containment": ["revoke", "disable", "block", "isolated", "contained"],
            "eradication": ["rotate", "fix", "deploy", "update", "patch"],
            "recovery": ["restore", "verify", "test", "operational", "recovered"],
            "post_incident": ["post-mortem", "lessons", "review", "documented"],
            "communication": ["notify", "notified", "escalate", "update"]
        }
        
        patterns = evidence_patterns.get(step_type, [])
        
        # Search timeline for matching evidence
        for event in self.timeline_events:
            action_lower = event.get("action", "").lower()
            
            # Check if action matches step keywords or patterns
            if any(keyword in action_lower for keyword in title_keywords if len(keyword) > 3):
                return event
            
            if any(pattern in action_lower for pattern in patterns):
                return event
        
        return None
    
    def generate_sla_violation_report(self, timing_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report of SLA violations"""
        violations = [r for r in timing_results if r.get("sla_status") == "violated"]
        
        critical_violations = [v for v in violations if v.get("sla_violation_severity") == "critical"]
        high_violations = [v for v in violations if v.get("sla_violation_severity") == "high"]
        medium_violations = [v for v in violations if v.get("sla_violation_severity") == "medium"]
        low_violations = [v for v in violations if v.get("sla_violation_severity") == "low"]
        
        return {
            "total_steps_analyzed": len(timing_results),
            "steps_with_sla": len([r for r in timing_results if r.get("expected_sla_minutes")]),
            "total_violations": len(violations),
            "critical_violations": len(critical_violations),
            "high_violations": len(high_violations),
            "medium_violations": len(medium_violations),
            "low_violations": len(low_violations),
            "violations_by_step": [
                {
                    "step_id": v.get("step_id"),
                    "step_title": v.get("step_title"),
                    "expected_minutes": v.get("expected_sla_minutes"),
                    "actual_minutes": v.get("time_from_incident_start_minutes"),
                    "overage_minutes": v.get("sla_overage_minutes"),
                    "severity": v.get("sla_violation_severity")
                }
                for v in violations
            ],
            "compliance_score": ((len(timing_results) - len(violations)) / len(timing_results) * 100) if timing_results else 0
        }
