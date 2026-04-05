"""
Static CIS Compliance Agent (Pre-PR Check)

This agent performs static compliance checks BEFORE PR merges:
- Policy validation
- Configuration analysis  
- SLA definition verification
- Playbook structure validation

Used in: GitHub Actions, CI/CD pipelines, pre-merge hooks
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class StaticCISAgent:
    """
    Pre-PR Static Compliance Agent
    
    Checks playbooks and configurations against CIS Controls v8 BEFORE merge.
    This is a "shift-left" approach to compliance.
    """
    
    def __init__(self, google_api_key: Optional[str] = None):
        self.use_langchain = LANGCHAIN_AVAILABLE and google_api_key is not None
        
        if self.use_langchain:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=google_api_key,
                    temperature=0.1
                )
                print("[StaticCISAgent] Initialized with LangChain")
            except Exception as e:
                print(f"[StaticCISAgent] LangChain init failed: {e}")
                self.use_langchain = False
        else:
            print("[StaticCISAgent] Running in fallback mode")
        
        # CIS Control 17 requirements for static analysis
        self.cis_requirements = self._load_static_requirements()
    
    def _load_static_requirements(self) -> Dict[str, Any]:
        """Load CIS requirements for static analysis"""
        return {
            "17.1": {
                "id": "17.1",
                "title": "Designate Personnel to Manage Incident Handling",
                "static_checks": [
                    "playbook_has_roles_defined",
                    "incident_commander_role_exists",
                    "escalation_path_defined"
                ]
            },
            "17.2": {
                "id": "17.2", 
                "title": "Establish Contact Information for Reporting",
                "static_checks": [
                    "contact_list_exists",
                    "notification_channels_defined",
                    "external_contacts_documented"
                ]
            },
            "17.3": {
                "id": "17.3",
                "title": "Establish Enterprise Process for Reporting",
                "static_checks": [
                    "reporting_process_documented",
                    "initial_response_sla_defined",
                    "alert_thresholds_set"
                ]
            },
            "17.4": {
                "id": "17.4",
                "title": "Establish Incident Response Process",
                "static_checks": [
                    "all_phases_documented",
                    "roles_responsibilities_clear",
                    "communication_plan_exists"
                ]
            },
            "17.5": {
                "id": "17.5",
                "title": "Assign Key Roles and Responsibilities",
                "static_checks": [
                    "legal_team_identified",
                    "it_security_team_identified",
                    "pr_team_identified",
                    "analyst_roles_defined"
                ]
            },
            "17.6": {
                "id": "17.6",
                "title": "Define Communication Mechanisms",
                "static_checks": [
                    "internal_comms_defined",
                    "external_comms_defined",
                    "secure_channels_specified"
                ]
            },
            "17.7": {
                "id": "17.7",
                "title": "Conduct Routine IR Exercises",
                "static_checks": [
                    "exercise_schedule_defined",
                    "exercise_scenarios_documented",
                    "exercise_metrics_specified"
                ]
            },
            "17.8": {
                "id": "17.8",
                "title": "Conduct Post-Incident Reviews",
                "static_checks": [
                    "postmortem_template_exists",
                    "review_timeline_defined",
                    "lessons_learned_process"
                ]
            },
            "17.9": {
                "id": "17.9",
                "title": "Establish Security Incident Thresholds",
                "static_checks": [
                    "severity_levels_defined",
                    "incident_vs_event_criteria",
                    "escalation_thresholds_set"
                ]
            }
        }
    
    async def check_pre_pr(
        self,
        playbook_content: str,
        config_files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Run static CIS compliance checks before PR merge
        
        Args:
            playbook_content: Markdown content of the playbook
            config_files: Optional dict of config files {filename: content}
            
        Returns:
            Static compliance check results
        """
        timestamp = datetime.utcnow().isoformat()
        
        results = {
            "check_type": "static",
            "phase": "pre_pr",
            "timestamp": timestamp,
            "framework": "CIS Controls v8",
            "controls_checked": [],
            "overall_status": "pass",
            "blocking_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Run checks for each CIS control
        for control_id, control in self.cis_requirements.items():
            check_result = await self._check_control_static(
                control_id, 
                control,
                playbook_content,
                config_files
            )
            results["controls_checked"].append(check_result)
            
            # Track blocking issues
            if check_result["status"] == "fail":
                results["blocking_issues"].extend(check_result.get("failures", []))
                results["overall_status"] = "fail"
            elif check_result["status"] == "warn" and results["overall_status"] != "fail":
                results["warnings"].extend(check_result.get("warnings", []))
                if results["overall_status"] == "pass":
                    results["overall_status"] = "warn"
        
        # Calculate score
        passed = sum(1 for c in results["controls_checked"] if c["status"] == "pass")
        total = len(results["controls_checked"])
        results["compliance_score"] = round((passed / total) * 100, 2) if total > 0 else 0
        
        # Generate recommendations
        results["recommendations"] = self._generate_static_recommendations(results)
        
        return results
    
    async def _check_control_static(
        self,
        control_id: str,
        control: Dict[str, Any],
        playbook_content: str,
        config_files: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Check a single CIS control statically"""
        
        result = {
            "control_id": control_id,
            "control_title": control["title"],
            "status": "pass",
            "checks_performed": [],
            "failures": [],
            "warnings": []
        }
        
        playbook_lower = playbook_content.lower()
        
        for check in control["static_checks"]:
            check_passed, message = self._perform_static_check(
                check, playbook_lower, config_files
            )
            
            result["checks_performed"].append({
                "check": check,
                "passed": check_passed,
                "message": message
            })
            
            if not check_passed:
                if self._is_critical_check(check):
                    result["status"] = "fail"
                    result["failures"].append(f"{control_id}: {message}")
                else:
                    if result["status"] == "pass":
                        result["status"] = "warn"
                    result["warnings"].append(f"{control_id}: {message}")
        
        return result
    
    def _perform_static_check(
        self, 
        check_name: str, 
        playbook_lower: str,
        config_files: Optional[Dict[str, str]]
    ) -> tuple[bool, str]:
        """Perform a specific static check"""
        
        check_rules = {
            # 17.1 - Personnel
            "playbook_has_roles_defined": (
                any(kw in playbook_lower for kw in ["responsible", "role", "team", "owner"]),
                "Playbook must define responsible roles/teams"
            ),
            "incident_commander_role_exists": (
                any(kw in playbook_lower for kw in ["incident commander", "ic", "incident lead", "lead responder"]),
                "Incident Commander role must be defined"
            ),
            "escalation_path_defined": (
                any(kw in playbook_lower for kw in ["escalat", "notify", "alert manager"]),
                "Escalation path should be defined"
            ),
            
            # 17.2 - Contacts
            "contact_list_exists": (
                any(kw in playbook_lower for kw in ["contact", "notify", "call", "email", "slack"]),
                "Contact/notification list should exist"
            ),
            "notification_channels_defined": (
                any(kw in playbook_lower for kw in ["slack", "email", "pagerduty", "opsgenie", "channel"]),
                "Notification channels must be specified"
            ),
            "external_contacts_documented": (
                any(kw in playbook_lower for kw in ["vendor", "legal", "external", "third party", "customer"]),
                "External contacts should be documented"
            ),
            
            # 17.3 - Reporting Process
            "reporting_process_documented": (
                any(kw in playbook_lower for kw in ["report", "document", "log", "record"]),
                "Reporting process must be documented"
            ),
            "initial_response_sla_defined": (
                any(kw in playbook_lower for kw in ["minute", "hour", "sla", "response time", "within"]),
                "Initial response SLA should be defined"
            ),
            "alert_thresholds_set": (
                any(kw in playbook_lower for kw in ["alert", "threshold", "trigger", "monitor"]),
                "Alert thresholds should be set"
            ),
            
            # 17.4 - IR Process
            "all_phases_documented": (
                all(phase in playbook_lower for phase in ["detection", "containment", "recovery"]),
                "All IR phases (detection, containment, recovery) must be documented"
            ),
            "roles_responsibilities_clear": (
                any(kw in playbook_lower for kw in ["responsible", "role", "duty", "task"]),
                "Roles and responsibilities must be clear"
            ),
            "communication_plan_exists": (
                any(kw in playbook_lower for kw in ["communicate", "notify", "status", "update"]),
                "Communication plan should exist"
            ),
            
            # 17.5 - Key Roles
            "legal_team_identified": (
                any(kw in playbook_lower for kw in ["legal", "counsel", "attorney", "compliance"]),
                "Legal team should be identified"
            ),
            "it_security_team_identified": (
                any(kw in playbook_lower for kw in ["security", "soc", "siem", "analyst"]),
                "IT Security team must be identified"
            ),
            "pr_team_identified": (
                any(kw in playbook_lower for kw in ["pr", "public relation", "communication", "media"]),
                "PR/Communications team should be identified"
            ),
            "analyst_roles_defined": (
                any(kw in playbook_lower for kw in ["analyst", "engineer", "responder", "investigator"]),
                "Analyst roles must be defined"
            ),
            
            # 17.6 - Communication Mechanisms
            "internal_comms_defined": (
                any(kw in playbook_lower for kw in ["internal", "team", "slack", "channel"]),
                "Internal communication mechanisms must be defined"
            ),
            "external_comms_defined": (
                any(kw in playbook_lower for kw in ["external", "customer", "stakeholder", "public"]),
                "External communication mechanisms should be defined"
            ),
            "secure_channels_specified": (
                any(kw in playbook_lower for kw in ["secure", "encrypted", "private"]),
                "Secure communication channels should be specified"
            ),
            
            # 17.7 - Exercises
            "exercise_schedule_defined": (
                any(kw in playbook_lower for kw in ["exercise", "drill", "tabletop", "test"]),
                "Exercise schedule should be defined"
            ),
            "exercise_scenarios_documented": (
                any(kw in playbook_lower for kw in ["scenario", "simulation", "practice"]),
                "Exercise scenarios should be documented"
            ),
            "exercise_metrics_specified": (
                any(kw in playbook_lower for kw in ["metric", "measure", "kpi", "objective"]),
                "Exercise metrics should be specified"
            ),
            
            # 17.8 - Post-Incident
            "postmortem_template_exists": (
                any(kw in playbook_lower for kw in ["postmortem", "post-mortem", "post mortem", "review", "retrospective"]),
                "Postmortem template should exist"
            ),
            "review_timeline_defined": (
                any(kw in playbook_lower for kw in ["within", "day", "hour", "timeline"]),
                "Review timeline should be defined"
            ),
            "lessons_learned_process": (
                any(kw in playbook_lower for kw in ["lesson", "improve", "update", "change"]),
                "Lessons learned process should be defined"
            ),
            
            # 17.9 - Thresholds
            "severity_levels_defined": (
                any(kw in playbook_lower for kw in ["severity", "critical", "high", "medium", "low", "p1", "p2"]),
                "Severity levels must be defined"
            ),
            "incident_vs_event_criteria": (
                any(kw in playbook_lower for kw in ["incident", "event", "classify", "criteria"]),
                "Incident vs event classification criteria should exist"
            ),
            "escalation_thresholds_set": (
                any(kw in playbook_lower for kw in ["escalat", "threshold", "trigger"]),
                "Escalation thresholds should be set"
            )
        }
        
        if check_name in check_rules:
            passed, message = check_rules[check_name]
            return passed, message
        
        return True, f"Check {check_name} not implemented"
    
    def _is_critical_check(self, check_name: str) -> bool:
        """Determine if a check failure should block the PR"""
        critical_checks = {
            "playbook_has_roles_defined",
            "incident_commander_role_exists",
            "all_phases_documented",
            "severity_levels_defined",
            "it_security_team_identified",
            "initial_response_sla_defined"
        }
        return check_name in critical_checks
    
    def _generate_static_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on static analysis"""
        recommendations = []
        
        for issue in results.get("blocking_issues", []):
            recommendations.append(f"[CRITICAL] Fix before merge: {issue}")
        
        for warning in results.get("warnings", []):
            recommendations.append(f"[WARNING] Consider addressing: {warning}")
        
        if results["compliance_score"] < 70:
            recommendations.append(
                "[ACTION] Compliance score below 70%. Review CIS Control 17 requirements."
            )
        
        return recommendations
