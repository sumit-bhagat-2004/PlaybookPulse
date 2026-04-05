"""
CIS Framework Knowledge Base
Maps incident response activities to CIS Controls v8 and CIS Incident Response Guide
"""
from typing import Dict, List, Any
from enum import Enum

class CISControlV8(Enum):
    """CIS Controls v8 relevant to incident response"""
    CONTROL_6 = "6"    # Access Control Management
    CONTROL_8 = "8"    # Audit Log Management
    CONTROL_11 = "11"  # Data Recovery
    CONTROL_13 = "13"  # Network Monitoring and Defense
    CONTROL_17 = "17"  # Incident Response Management
    CONTROL_18 = "18"  # Penetration Testing

class CISIRPhase(Enum):
    """CIS IR Guide phases"""
    PREPARATION = "preparation"
    DETECTION = "detection"
    ANALYSIS = "analysis"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    POST_INCIDENT = "post_incident"

# Strict SLA requirements (in minutes) per phase
CIS_SLA_REQUIREMENTS = {
    CISIRPhase.DETECTION: {
        "initial_response": 15,      # Must acknowledge within 15 minutes
        "description": "Immediate acknowledgment and initial assessment"
    },
    CISIRPhase.ANALYSIS: {
        "initial_analysis": 30,      # Begin analysis within 30 minutes
        "complete_analysis": 120,    # Complete initial analysis within 2 hours
        "description": "Assess scope, severity, and impact"
    },
    CISIRPhase.CONTAINMENT: {
        "short_term": 60,           # Short-term containment within 1 hour
        "long_term": 240,           # Long-term containment within 4 hours
        "description": "Isolate affected systems and prevent spread"
    },
    CISIRPhase.ERADICATION: {
        "complete": 480,            # Remove threat within 8 hours (critical incidents)
        "description": "Remove malicious artifacts and restore integrity"
    },
    CISIRPhase.RECOVERY: {
        "initiate": 120,            # Begin recovery within 2 hours of eradication
        "complete": 1440,           # Full recovery within 24 hours (depends on severity)
        "description": "Restore systems to normal operation"
    },
    CISIRPhase.POST_INCIDENT: {
        "lessons_learned": 10080,   # Post-mortem within 7 days
        "documentation": 4320,      # Document within 3 days
        "description": "Review incident and update procedures"
    }
}

# CIS Control 17 (Incident Response Management) safeguards
CIS_CONTROL_17_SAFEGUARDS = {
    "17.1": {
        "title": "Designate Personnel to Manage Incident Handling",
        "description": "Assign incident commanders and team members",
        "required_actions": [
            "Incident commander assigned",
            "Team roles defined",
            "Communication channels established"
        ]
    },
    "17.2": {
        "title": "Establish and Maintain Contact Information",
        "description": "Maintain contact information for reporting security incidents",
        "required_actions": [
            "Contact list created",
            "Stakeholders notified",
            "Escalation paths followed"
        ]
    },
    "17.3": {
        "title": "Establish and Maintain an Enterprise Process for Reporting Incidents",
        "description": "Create standardized reporting process",
        "required_actions": [
            "Incident ticket created",
            "Standard fields populated",
            "Severity classification assigned"
        ]
    },
    "17.4": {
        "title": "Establish and Maintain an Incident Response Process",
        "description": "Follow documented IR process",
        "required_actions": [
            "Playbook steps followed",
            "Documentation maintained",
            "Timeline recorded"
        ]
    },
    "17.5": {
        "title": "Assign Key Roles and Responsibilities",
        "description": "Define roles for incident response",
        "required_actions": [
            "Roles assigned per step",
            "Responsibilities clear",
            "Accountability tracked"
        ]
    },
    "17.6": {
        "title": "Define Mechanisms for Communicating During Incident Response",
        "description": "Establish incident communication channels",
        "required_actions": [
            "Dedicated Slack channel created",
            "Status updates posted",
            "Stakeholder communication logged"
        ]
    },
    "17.7": {
        "title": "Conduct Routine Incident Response Exercises",
        "description": "Practice incident response procedures",
        "required_actions": [
            "Exercise documented",
            "Lessons captured",
            "Improvements identified"
        ]
    },
    "17.8": {
        "title": "Conduct Post-Incident Reviews",
        "description": "Review and learn from incidents",
        "required_actions": [
            "Post-mortem scheduled",
            "Root cause identified",
            "Action items created",
            "Playbook updated"
        ]
    },
    "17.9": {
        "title": "Establish and Maintain Security Incident Thresholds",
        "description": "Define incident severity levels",
        "required_actions": [
            "Severity determined",
            "Thresholds documented",
            "Appropriate response level activated"
        ]
    }
}

# Mapping of playbook step types to CIS controls
PLAYBOOK_STEP_TO_CIS_MAPPING = {
    "detection": {
        "phase": CISIRPhase.DETECTION,
        "controls": [CISControlV8.CONTROL_17],
        "safeguards": ["17.1", "17.2", "17.3"],
        "sla_key": "initial_response"
    },
    "acknowledgment": {
        "phase": CISIRPhase.DETECTION,
        "controls": [CISControlV8.CONTROL_17],
        "safeguards": ["17.1", "17.6"],
        "sla_key": "initial_response"
    },
    "analysis": {
        "phase": CISIRPhase.ANALYSIS,
        "controls": [CISControlV8.CONTROL_8, CISControlV8.CONTROL_17],
        "safeguards": ["17.4", "17.9"],
        "sla_key": "complete_analysis"
    },
    "containment": {
        "phase": CISIRPhase.CONTAINMENT,
        "controls": [CISControlV8.CONTROL_6, CISControlV8.CONTROL_13, CISControlV8.CONTROL_17],
        "safeguards": ["17.4", "17.5"],
        "sla_key": "short_term"
    },
    "eradication": {
        "phase": CISIRPhase.ERADICATION,
        "controls": [CISControlV8.CONTROL_17],
        "safeguards": ["17.4", "17.5"],
        "sla_key": "complete"
    },
    "recovery": {
        "phase": CISIRPhase.RECOVERY,
        "controls": [CISControlV8.CONTROL_11, CISControlV8.CONTROL_17],
        "safeguards": ["17.4", "17.5"],
        "sla_key": "complete"
    },
    "post_incident": {
        "phase": CISIRPhase.POST_INCIDENT,
        "controls": [CISControlV8.CONTROL_17],
        "safeguards": ["17.8"],
        "sla_key": "lessons_learned"
    },
    "communication": {
        "phase": CISIRPhase.DETECTION,
        "controls": [CISControlV8.CONTROL_17],
        "safeguards": ["17.2", "17.6"],
        "sla_key": None
    }
}

def get_cis_requirements_for_step(step_type: str, step_phase: str = None) -> Dict[str, Any]:
    """Get CIS requirements for a specific playbook step"""
    step_type = step_type.lower()
    mapping = PLAYBOOK_STEP_TO_CIS_MAPPING.get(step_type)
    
    if not mapping and step_phase:
        phase_normalized = step_phase.lower().replace(" ", "_")
        for key, value in PLAYBOOK_STEP_TO_CIS_MAPPING.items():
            if phase_normalized in key or key in phase_normalized:
                mapping = value
                break
    
    if not mapping:
        mapping = {
            "phase": CISIRPhase.DETECTION,
            "controls": [CISControlV8.CONTROL_17],
            "safeguards": ["17.4"],
            "sla_key": None
        }
    
    result = {
        "cis_phase": mapping["phase"].value,
        "cis_controls": [c.value for c in mapping["controls"]],
        "cis_safeguards": [],
        "sla_minutes": None,
        "sla_description": ""
    }
    
    for safeguard_id in mapping["safeguards"]:
        safeguard = CIS_CONTROL_17_SAFEGUARDS.get(safeguard_id, {})
        result["cis_safeguards"].append({
            "id": safeguard_id,
            "title": safeguard.get("title", ""),
            "required_actions": safeguard.get("required_actions", [])
        })
    
    if mapping["sla_key"]:
        sla_info = CIS_SLA_REQUIREMENTS.get(mapping["phase"], {})
        result["sla_minutes"] = sla_info.get(mapping["sla_key"])
        result["sla_description"] = sla_info.get("description", "")
    
    return result

def get_all_cis_controls() -> List[Dict[str, Any]]:
    """Get all CIS Control 17 safeguards"""
    return [
        {
            "id": safeguard_id,
            "title": safeguard["title"],
            "description": safeguard["description"],
            "required_actions": safeguard["required_actions"]
        }
        for safeguard_id, safeguard in CIS_CONTROL_17_SAFEGUARDS.items()
    ]

class SLAViolationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

def calculate_sla_violation_severity(expected_minutes: int, actual_minutes: int) -> SLAViolationSeverity:
    """Calculate severity of SLA violation"""
    if actual_minutes <= expected_minutes:
        return SLAViolationSeverity.NONE
    
    overage_pct = ((actual_minutes - expected_minutes) / expected_minutes) * 100
    
    if overage_pct > 100:
        return SLAViolationSeverity.CRITICAL
    elif overage_pct > 50:
        return SLAViolationSeverity.HIGH
    elif overage_pct > 25:
        return SLAViolationSeverity.MEDIUM
    else:
        return SLAViolationSeverity.LOW
