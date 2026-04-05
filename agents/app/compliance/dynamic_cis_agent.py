"""
Dynamic CIS Compliance Agent (Post-Merge Check)

This agent performs dynamic compliance checks AFTER PR merges using live incident data:
- Runtime validation against actual incidents
- Timestamp/SLA analysis on real events  
- Evidence collection from Slack, Jira, GitHub
- Live compliance scoring

Used in: Post-deployment hooks, scheduled audits, incident analysis
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from dateutil import parser as date_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    print("WARNING: python-dateutil not installed. Install with: pip install python-dateutil")


class DynamicCISAgent:
    """
    Post-Merge Dynamic Compliance Agent
    
    Validates incident response activities against CIS Controls v8 using:
    - Live incident data (Slack threads, Jira tickets, GitHub events)
    - Real timestamps for SLA validation
    - Evidence-based compliance assessment
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
                print("[DynamicCISAgent] Initialized with LangChain")
            except Exception as e:
                print(f"[DynamicCISAgent] LangChain init failed: {e}")
                self.use_langchain = False
        else:
            print("[DynamicCISAgent] Running in fallback mode")
        
        # CIS Control 17 SLA requirements (in minutes)
        self.sla_requirements = {
            "initial_response": 15,      # 15 min to acknowledge
            "initial_assessment": 30,    # 30 min to assess
            "containment_start": 60,     # 1 hour to start containment
            "containment_complete": 240, # 4 hours to complete containment
            "eradication": 480,          # 8 hours for eradication
            "recovery_start": 600,       # 10 hours to start recovery
            "post_incident": 10080       # 7 days for post-mortem
        }
    
    async def check_post_merge(
        self,
        playbook_steps: List[Dict[str, Any]],
        incident_data: Dict[str, Any],
        adherence_checks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run dynamic CIS compliance checks after merge with live data
        
        Args:
            playbook_steps: Parsed playbook steps
            incident_data: Live incident data from integrations
            adherence_checks: Previous adherence check results (optional)
            
        Returns:
            Dynamic compliance check results
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Extract timeline from incident data
        timeline = self._extract_timeline(incident_data)
        
        # Calculate SLA compliance
        sla_results = self._check_sla_compliance(timeline)
        
        # Check each CIS control dynamically
        control_results = await self._check_controls_dynamic(
            playbook_steps,
            incident_data,
            timeline,
            adherence_checks
        )
        
        # Calculate overall score
        passed = sum(1 for c in control_results if c["status"] == "compliant")
        partial = sum(1 for c in control_results if c["status"] == "partial")
        total = len(control_results)
        
        compliance_score = round(
            ((passed + partial * 0.5) / total) * 100, 2
        ) if total > 0 else 0
        
        # Identify violations
        violations = [
            c for c in control_results 
            if c["status"] in ["non_compliant", "violation"]
        ]
        
        results = {
            "check_type": "dynamic",
            "phase": "post_merge",
            "timestamp": timestamp,
            "framework": "CIS Controls v8",
            "incident_timeline": {
                "start_time": timeline[0]["timestamp"] if timeline else None,
                "end_time": timeline[-1]["timestamp"] if timeline else None,
                "total_events": len(timeline),
                "sources": list(set(e.get("source", "unknown") for e in timeline))
            },
            "sla_compliance": sla_results,
            "controls_checked": control_results,
            "compliance_score": compliance_score,
            "violations": violations,
            "violation_count": len(violations),
            "overall_status": "compliant" if len(violations) == 0 else "non_compliant",
            "recommendations": self._generate_dynamic_recommendations(
                control_results, sla_results, violations
            )
        }
        
        return results
    
    def _extract_timeline(self, incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and sort timeline events from incident data"""
        timeline = []
        
        # Extract from Slack
        slack_data = incident_data.get("slack", {})
        if isinstance(slack_data, dict):
            messages = slack_data.get("messages", [])
            for msg in messages:
                ts = msg.get("ts") or msg.get("timestamp")
                if ts:
                    timeline.append({
                        "timestamp": self._parse_timestamp(ts),
                        "source": "slack",
                        "type": "message",
                        "content": msg.get("text", "")[:200],
                        "user": msg.get("user", "unknown")
                    })
        
        # Extract from Jira
        jira_data = incident_data.get("jira", {})
        if isinstance(jira_data, dict):
            # Ticket creation
            created = jira_data.get("created")
            if created:
                timeline.append({
                    "timestamp": self._parse_timestamp(created),
                    "source": "jira",
                    "type": "ticket_created",
                    "content": f"Ticket {jira_data.get('key', 'unknown')} created"
                })
            
            # Comments
            comments = jira_data.get("comments", [])
            for comment in comments:
                ts = comment.get("created") or comment.get("timestamp")
                if ts:
                    timeline.append({
                        "timestamp": self._parse_timestamp(ts),
                        "source": "jira",
                        "type": "comment",
                        "content": comment.get("body", "")[:200]
                    })
            
            # Status changes (from changelog)
            changelog = jira_data.get("changelog", [])
            for change in changelog:
                ts = change.get("created") or change.get("timestamp")
                if ts:
                    timeline.append({
                        "timestamp": self._parse_timestamp(ts),
                        "source": "jira",
                        "type": "status_change",
                        "content": f"Changed: {change.get('field', '')} to {change.get('to', '')}"
                    })
        
        # Extract from GitHub
        github_events = incident_data.get("github", [])
        if isinstance(github_events, list):
            for event in github_events:
                ts = event.get("created_at") or event.get("timestamp")
                if ts:
                    timeline.append({
                        "timestamp": self._parse_timestamp(ts),
                        "source": "github",
                        "type": event.get("type", "event"),
                        "content": event.get("message", event.get("title", ""))[:200]
                    })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min)
        
        return timeline
    
    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """Parse various timestamp formats"""
        if ts is None:
            return None
        
        if isinstance(ts, datetime):
            return ts
        
        if isinstance(ts, (int, float)):
            # Unix timestamp (could be seconds or milliseconds)
            if ts > 1e12:  # Milliseconds
                ts = ts / 1000
            try:
                return datetime.fromtimestamp(ts)
            except (ValueError, OSError):
                return None
        
        if isinstance(ts, str):
            if DATEUTIL_AVAILABLE:
                try:
                    return date_parser.parse(ts)
                except:
                    pass
            
            # Fallback parsing
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(ts, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _check_sla_compliance(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check SLA compliance based on timeline"""
        if not timeline or len(timeline) < 2:
            return {
                "status": "insufficient_data",
                "message": "Not enough timeline events to check SLAs",
                "checks": []
            }
        
        checks = []
        first_event = timeline[0]
        incident_start = first_event["timestamp"]
        
        # Find key events
        first_response = None
        containment_start = None
        
        for event in timeline[1:]:
            if event["timestamp"] is None:
                continue
            
            content_lower = event.get("content", "").lower()
            
            # Look for first human response
            if first_response is None and event.get("type") in ["message", "comment"]:
                first_response = event["timestamp"]
            
            # Look for containment activities
            if containment_start is None:
                if any(kw in content_lower for kw in ["contain", "isolate", "block", "disable"]):
                    containment_start = event["timestamp"]
        
        # Check initial response SLA
        if first_response and incident_start:
            delta_minutes = (first_response - incident_start).total_seconds() / 60
            sla_met = delta_minutes <= self.sla_requirements["initial_response"]
            
            checks.append({
                "sla": "initial_response",
                "required_minutes": self.sla_requirements["initial_response"],
                "actual_minutes": round(delta_minutes, 2),
                "status": "met" if sla_met else "violated",
                "severity": "critical" if not sla_met else None
            })
        
        # Check containment SLA
        if containment_start and incident_start:
            delta_minutes = (containment_start - incident_start).total_seconds() / 60
            sla_met = delta_minutes <= self.sla_requirements["containment_start"]
            
            checks.append({
                "sla": "containment_start",
                "required_minutes": self.sla_requirements["containment_start"],
                "actual_minutes": round(delta_minutes, 2),
                "status": "met" if sla_met else "violated",
                "severity": "high" if not sla_met else None
            })
        
        # Calculate overall SLA status
        violations = [c for c in checks if c["status"] == "violated"]
        
        return {
            "status": "violated" if violations else "compliant",
            "total_checks": len(checks),
            "violations": len(violations),
            "checks": checks
        }
    
    async def _check_controls_dynamic(
        self,
        playbook_steps: List[Dict[str, Any]],
        incident_data: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Check CIS controls dynamically with live data"""
        
        controls = [
            ("17.1", "Designate Personnel", self._check_17_1),
            ("17.3", "Incident Reporting Process", self._check_17_3),
            ("17.4", "IR Process Execution", self._check_17_4),
            ("17.5", "Key Roles Assigned", self._check_17_5),
            ("17.6", "Communication Mechanisms", self._check_17_6),
            ("17.8", "Post-Incident Review", self._check_17_8),
        ]
        
        results = []
        for control_id, control_title, check_func in controls:
            result = check_func(incident_data, timeline, adherence_checks)
            result["control_id"] = control_id
            result["control_title"] = control_title
            results.append(result)
        
        return results
    
    def _check_17_1(
        self, 
        incident_data: Dict[str, Any], 
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Check 17.1: Designated personnel managing incident"""
        evidence = []
        
        # Look for IC assignment in messages
        for event in timeline:
            content = event.get("content", "").lower()
            if any(kw in content for kw in ["incident commander", "ic:", "leading", "i'll take lead"]):
                evidence.append(f"IC assignment found: {event.get('content', '')[:100]}")
        
        if evidence:
            return {
                "status": "compliant",
                "evidence": evidence,
                "gaps": []
            }
        else:
            return {
                "status": "non_compliant",
                "evidence": [],
                "gaps": ["No evidence of incident commander assignment found in timeline"]
            }
    
    def _check_17_3(
        self,
        incident_data: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Check 17.3: Incident reporting process followed"""
        evidence = []
        gaps = []
        
        # Check if Jira ticket was created
        jira_data = incident_data.get("jira", {})
        if jira_data and jira_data.get("key"):
            evidence.append(f"Jira ticket created: {jira_data.get('key')}")
        else:
            gaps.append("No Jira ticket created for incident")
        
        # Check if Slack channel was used
        slack_data = incident_data.get("slack", {})
        if slack_data and len(slack_data.get("messages", [])) > 0:
            evidence.append(f"Slack communication: {len(slack_data.get('messages', []))} messages")
        else:
            gaps.append("No Slack communication found")
        
        status = "compliant" if len(evidence) >= 2 else ("partial" if evidence else "non_compliant")
        
        return {
            "status": status,
            "evidence": evidence,
            "gaps": gaps
        }
    
    def _check_17_4(
        self,
        incident_data: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Check 17.4: IR process executed properly"""
        evidence = []
        gaps = []
        
        phases_found = set()
        phase_keywords = {
            "detection": ["detect", "alert", "found", "discovered"],
            "containment": ["contain", "isolate", "block", "disable"],
            "eradication": ["remove", "clean", "patch", "fix"],
            "recovery": ["restore", "recover", "resume", "back online"]
        }
        
        for event in timeline:
            content = event.get("content", "").lower()
            for phase, keywords in phase_keywords.items():
                if any(kw in content for kw in keywords):
                    phases_found.add(phase)
        
        for phase in phases_found:
            evidence.append(f"Phase '{phase}' activities found in timeline")
        
        missing_phases = set(phase_keywords.keys()) - phases_found
        for phase in missing_phases:
            gaps.append(f"No evidence of '{phase}' phase activities")
        
        if len(phases_found) >= 3:
            status = "compliant"
        elif len(phases_found) >= 2:
            status = "partial"
        else:
            status = "non_compliant"
        
        return {
            "status": status,
            "evidence": evidence,
            "gaps": gaps,
            "phases_detected": list(phases_found)
        }
    
    def _check_17_5(
        self,
        incident_data: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Check 17.5: Key roles assigned during incident"""
        evidence = []
        gaps = []
        
        # Look for different roles mentioned
        roles_found = set()
        role_keywords = {
            "security": ["security", "soc", "analyst"],
            "engineering": ["engineer", "dev", "developer", "sre"],
            "management": ["manager", "lead", "director"],
            "communications": ["comms", "pr", "status page"]
        }
        
        for event in timeline:
            content = event.get("content", "").lower()
            user = event.get("user", "").lower()
            
            for role, keywords in role_keywords.items():
                if any(kw in content or kw in user for kw in keywords):
                    roles_found.add(role)
        
        for role in roles_found:
            evidence.append(f"Role '{role}' participated in response")
        
        if len(roles_found) >= 2:
            status = "compliant"
        elif len(roles_found) >= 1:
            status = "partial"
        else:
            status = "non_compliant"
            gaps.append("Could not identify distinct roles in incident response")
        
        return {
            "status": status,
            "evidence": evidence,
            "gaps": gaps,
            "roles_detected": list(roles_found)
        }
    
    def _check_17_6(
        self,
        incident_data: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Check 17.6: Communication mechanisms used"""
        evidence = []
        gaps = []
        
        sources = set(e.get("source") for e in timeline if e.get("source"))
        
        if "slack" in sources:
            evidence.append("Slack used for communication")
        if "jira" in sources:
            evidence.append("Jira used for tracking")
        if "github" in sources:
            evidence.append("GitHub used for code changes")
        
        if len(sources) >= 2:
            status = "compliant"
            evidence.append(f"Multiple communication channels used: {', '.join(sources)}")
        elif len(sources) == 1:
            status = "partial"
            gaps.append("Only one communication channel used")
        else:
            status = "non_compliant"
            gaps.append("No communication channels detected")
        
        return {
            "status": status,
            "evidence": evidence,
            "gaps": gaps
        }
    
    def _check_17_8(
        self,
        incident_data: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        adherence_checks: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Check 17.8: Post-incident review conducted"""
        evidence = []
        gaps = []
        
        # Look for post-incident activities
        postmortem_found = False
        for event in timeline:
            content = event.get("content", "").lower()
            if any(kw in content for kw in ["postmortem", "post-mortem", "retrospective", "lessons learned", "review"]):
                postmortem_found = True
                evidence.append(f"Post-incident activity found: {event.get('content', '')[:100]}")
        
        if postmortem_found:
            status = "compliant"
        else:
            status = "non_compliant"
            gaps.append("No post-incident review evidence found")
        
        return {
            "status": status,
            "evidence": evidence,
            "gaps": gaps
        }
    
    def _generate_dynamic_recommendations(
        self,
        control_results: List[Dict[str, Any]],
        sla_results: Dict[str, Any],
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on dynamic analysis"""
        recommendations = []
        
        # SLA recommendations
        for check in sla_results.get("checks", []):
            if check.get("status") == "violated":
                recommendations.append(
                    f"[SLA VIOLATION] {check['sla']}: Took {check['actual_minutes']} min "
                    f"(required: {check['required_minutes']} min)"
                )
        
        # Control recommendations
        for result in control_results:
            if result.get("status") == "non_compliant":
                for gap in result.get("gaps", []):
                    recommendations.append(
                        f"[{result['control_id']}] {gap}"
                    )
        
        return recommendations
