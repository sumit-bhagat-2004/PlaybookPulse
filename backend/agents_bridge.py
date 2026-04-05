"""
Agents Bridge: CIS-Only Compliance System

Connects backend to the CIS compliance agents:
- StaticCISAgent: Pre-PR compliance checks
- DynamicCISAgent: Post-merge runtime validation
- ComplianceLogger: Structured logging
- AlertSystem: Dev team notifications

Only CIS Controls v8 is supported (no NIST, SOC2, ISO).
"""

import asyncio
import sys
import os
import httpx
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Add agents directory to path for direct imports
AGENTS_DIR = Path(__file__).parent.parent / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

# Try to import agents directly (for same-process mode)
AGENTS_AVAILABLE = False
CIS_AGENTS_AVAILABLE = False

try:
    # Set working directory for agents config to find .env
    original_cwd = os.getcwd()
    os.chdir(AGENTS_DIR)
    
    from app.services.analysis_service import AnalysisService, run_analysis_task, _analyses_store
    from app.models.schemas import AnalysisRequest as AgentAnalysisRequest, ComplianceFramework, AnalysisStatus
    from app.agents.playbook_parser import PlaybookParserAgent
    from app.agents.adherence_checker import AdherenceCheckerAgent
    from app.agents.compliance_mapper import ComplianceMapperAgent
    from app.agents.incident_trail import IncidentTrailAgent
    
    os.chdir(original_cwd)
    AGENTS_AVAILABLE = True
    print("[AgentsBridge] Core agents imported successfully")
except ImportError as e:
    print(f"WARNING: Could not import core agents: {e}")
    AGENTS_AVAILABLE = False
except Exception as e:
    print(f"WARNING: Error importing core agents: {e}")
    AGENTS_AVAILABLE = False

# Try to import CIS compliance agents
try:
    from app.compliance import (
        StaticCISAgent,
        DynamicCISAgent,
        ComplianceLogger,
        AlertSystem,
        create_alert_system
    )
    CIS_AGENTS_AVAILABLE = True
    print("[AgentsBridge] CIS compliance agents imported successfully")
except ImportError as e:
    print(f"WARNING: Could not import CIS agents: {e}")
    CIS_AGENTS_AVAILABLE = False


class AgentsBridge:
    """
    Bridge to connect backend with CIS-only compliance agents.
    
    Supports:
    - Pre-PR static compliance checks (StaticCISAgent)
    - Post-merge dynamic compliance checks (DynamicCISAgent)
    - Full incident analysis pipeline
    """
    
    def __init__(self, agents_api_url: Optional[str] = None, google_api_key: Optional[str] = None):
        """
        Initialize the agents bridge.
        
        Args:
            agents_api_url: URL of agents API (e.g., "http://localhost:8001")
                           If None, uses direct import mode.
            google_api_key: Google API key for LangChain agents
        """
        self.agents_api_url = agents_api_url
        self.use_direct = agents_api_url is None and AGENTS_AVAILABLE
        self.google_api_key = google_api_key or os.environ.get("GOOGLE_API_KEY")
        
        # Initialize CIS agents if available
        self.static_cis_agent = None
        self.dynamic_cis_agent = None
        self.compliance_logger = None
        self.alert_system = None
        
        if CIS_AGENTS_AVAILABLE:
            # Create alert system (stub - user implements integrations)
            self.alert_system = create_alert_system(
                slack_webhook=os.environ.get("SLACK_ALERT_WEBHOOK"),
                pagerduty_key=os.environ.get("PAGERDUTY_API_KEY"),
                webhook_url=os.environ.get("ALERT_WEBHOOK_URL")
            )
            
            # Create compliance logger
            self.compliance_logger = ComplianceLogger(
                log_dir="logs/compliance",
                alert_system=self.alert_system
            )
            
            # Create CIS agents
            self.static_cis_agent = StaticCISAgent(google_api_key=self.google_api_key)
            self.dynamic_cis_agent = DynamicCISAgent(google_api_key=self.google_api_key)
            
            print("[AgentsBridge] CIS compliance system initialized")
        
        if self.use_direct:
            print("[AgentsBridge] Using DIRECT mode (same process)")
        elif agents_api_url:
            print(f"[AgentsBridge] Using HTTP mode ({agents_api_url})")
        else:
            print("WARNING: AgentsBridge: Agents not available!")
    
    async def check_pre_pr(
        self,
        playbook_content: str,
        config_files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Run PRE-PR static CIS compliance checks.
        
        Use this BEFORE merging PRs to catch compliance issues early.
        
        Args:
            playbook_content: Markdown content of the playbook
            config_files: Optional dict of config files to check
            
        Returns:
            Static compliance check results
        """
        if not self.static_cis_agent:
            return {
                "status": "error",
                "error": "StaticCISAgent not available",
                "phase": "pre_pr"
            }
        
        if self.compliance_logger:
            self.compliance_logger.log_check_started("pre_pr", "static")
        
        try:
            result = await self.static_cis_agent.check_pre_pr(
                playbook_content=playbook_content,
                config_files=config_files
            )
            
            if self.compliance_logger:
                self.compliance_logger.log_check_completed(
                    "pre_pr",
                    result.get("overall_status", "unknown"),
                    score=result.get("compliance_score")
                )
            
            return result
            
        except Exception as e:
            if self.compliance_logger:
                self.compliance_logger.log_check_failed("pre_pr", str(e))
            return {
                "status": "error",
                "error": str(e),
                "phase": "pre_pr"
            }
    
    async def check_post_merge(
        self,
        playbook_content: str,
        slack_thread_data: Optional[Dict[str, Any]] = None,
        jira_ticket_data: Optional[Dict[str, Any]] = None,
        github_events: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run POST-MERGE dynamic CIS compliance checks.
        
        Use this AFTER merging or during incident analysis with live data.
        
        Args:
            playbook_content: Markdown content of the playbook
            slack_thread_data: Live Slack thread data
            jira_ticket_data: Live Jira ticket data
            github_events: Live GitHub events
            
        Returns:
            Dynamic compliance check results
        """
        if not self.dynamic_cis_agent:
            return {
                "status": "error",
                "error": "DynamicCISAgent not available",
                "phase": "post_merge"
            }
        
        if self.compliance_logger:
            self.compliance_logger.log_check_started("post_merge", "dynamic")
        
        try:
            # First, parse playbook to get steps
            parser = PlaybookParserAgent() if AGENTS_AVAILABLE else None
            playbook_steps = []
            
            if parser:
                parse_result = await parser.process({"playbook_content": playbook_content})
                if parse_result.get("success"):
                    playbook_steps = parse_result.get("data", {}).get("steps", [])
            
            # Prepare incident data
            incident_data = {
                "slack": slack_thread_data or {},
                "jira": jira_ticket_data or {},
                "github": github_events or []
            }
            
            result = await self.dynamic_cis_agent.check_post_merge(
                playbook_steps=playbook_steps,
                incident_data=incident_data,
                adherence_checks=None
            )
            
            if self.compliance_logger:
                self.compliance_logger.log_check_completed(
                    "post_merge",
                    result.get("overall_status", "unknown"),
                    score=result.get("compliance_score")
                )
                
                # Log individual control results
                for control in result.get("controls_checked", []):
                    self.compliance_logger.log_control_result(
                        control_id=control.get("control_id", ""),
                        control_title=control.get("control_title", ""),
                        status=control.get("status", "unknown"),
                        evidence=control.get("evidence", []),
                        gaps=control.get("gaps", [])
                    )
                
                # Log SLA results
                for sla_check in result.get("sla_compliance", {}).get("checks", []):
                    self.compliance_logger.log_sla_result(
                        sla_name=sla_check.get("sla", ""),
                        status=sla_check.get("status", "unknown"),
                        required_minutes=sla_check.get("required_minutes", 0),
                        actual_minutes=sla_check.get("actual_minutes", 0)
                    )
            
            return result
            
        except Exception as e:
            if self.compliance_logger:
                self.compliance_logger.log_check_failed("post_merge", str(e))
            return {
                "status": "error",
                "error": str(e),
                "phase": "post_merge"
            }
    
    async def analyze_incident(
        self,
        playbook_content: str,
        slack_thread_data: Optional[Dict[str, Any]] = None,
        jira_ticket_data: Optional[Dict[str, Any]] = None,
        github_events: Optional[List[Dict[str, Any]]] = None,
        compliance_frameworks: List[str] = None
    ) -> Dict[str, Any]:
        """
        Run full incident analysis with CIS-only compliance.
        
        Args:
            playbook_content: Markdown content of the playbook
            slack_thread_data: Parsed Slack thread data (optional)
            jira_ticket_data: Parsed Jira ticket data (optional)
            github_events: List of GitHub events (optional)
            compliance_frameworks: IGNORED - always uses CIS Controls v8
            
        Returns:
            Analysis result dictionary
        """
        # Always use CIS Controls v8
        compliance_frameworks = ["cis_controls_v8"]
        
        if self.use_direct:
            return await self._analyze_direct(
                playbook_content,
                slack_thread_data,
                jira_ticket_data,
                github_events,
                compliance_frameworks
            )
        elif self.agents_api_url:
            return await self._analyze_via_http(
                playbook_content,
                slack_thread_data,
                jira_ticket_data,
                github_events,
                compliance_frameworks
            )
        else:
            # Fallback: Use CIS-only analysis when core agents unavailable
            return await self._analyze_cis_only(
                playbook_content,
                slack_thread_data,
                jira_ticket_data,
                github_events
            )
    
    async def _analyze_cis_only(
        self,
        playbook_content: str,
        slack_thread_data: Optional[Dict[str, Any]],
        jira_ticket_data: Optional[Dict[str, Any]],
        github_events: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        CIS-only analysis when core agents aren't available.
        Uses StaticCISAgent and DynamicCISAgent directly.
        """
        from datetime import datetime
        
        try:
            # Run pre-PR static check
            pre_pr_result = await self.check_pre_pr(playbook_content)
            
            # Run post-merge dynamic check
            post_merge_result = await self.check_post_merge(
                playbook_content,
                slack_thread_data,
                jira_ticket_data
            )
            
            # Combine results
            static_score = pre_pr_result.get("compliance_score", 0)
            dynamic_score = post_merge_result.get("compliance_score", 0)
            overall_score = (static_score + dynamic_score) / 2
            
            # Collect recommendations
            recommendations = []
            recommendations.extend(pre_pr_result.get("recommendations", []))
            recommendations.extend(post_merge_result.get("recommendations", []))
            
            return {
                "status": "completed",
                "framework": "CIS Controls v8",
                "timestamp": datetime.now().isoformat(),
                "playbook": {
                    "title": "Incident Response Playbook",
                    "step_count": len(playbook_content.split('\n'))
                },
                "adherence": {
                    "overall_score": overall_score,
                    "full_adherence": 0,
                    "partial_adherence": 0,
                    "no_adherence": 0,
                    "step_results": []
                },
                "cis_compliance": {
                    "framework": "CIS Controls v8",
                    "static_analysis": pre_pr_result,
                    "dynamic_analysis": post_merge_result,
                    "mappings": pre_pr_result.get("controls_checked", [])
                },
                "recommendations": recommendations[:10]  # Top 10
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"CIS-only analysis failed: {str(e)}"
            }
    
    async def _analyze_direct(
        self,
        playbook_content: str,
        slack_thread_data: Optional[Dict[str, Any]],
        jira_ticket_data: Optional[Dict[str, Any]],
        github_events: Optional[List[Dict[str, Any]]],
        compliance_frameworks: List[str]
    ) -> Dict[str, Any]:
        """Run analysis using direct imports (same process)."""
        try:
            # Always use CIS Controls v8
            frameworks = [ComplianceFramework.CIS_CONTROLS_V8]
            
            # Step 1: Parse playbook
            print("[AgentsBridge] Step 1: Parsing playbook...")
            parser = PlaybookParserAgent()
            parse_result = await parser.process({
                "playbook_content": playbook_content
            })
            
            if not parse_result or not parse_result.get("success"):
                return {
                    "status": "error",
                    "error": f"Playbook parsing failed: {parse_result.get('error') if parse_result else 'Unknown'}"
                }
            
            playbook_steps = parse_result.get("data", {}).get("steps", [])
            print(f"[AgentsBridge] Parsed {len(playbook_steps)} steps")
            
            # Step 2: Collect incident data
            print("[AgentsBridge] Step 2: Collecting incident data...")
            incident_agent = IncidentTrailAgent()
            incident_result = await incident_agent.process({
                "slack_data": slack_thread_data,
                "jira_data": jira_ticket_data,
                "github_events": github_events
            })
            
            incident_data = incident_result.get("data", {}) if incident_result else {}
            
            # Step 3: Check adherence
            print("[AgentsBridge] Step 3: Checking adherence...")
            adherence_agent = AdherenceCheckerAgent()
            adherence_result = await adherence_agent.process({
                "playbook_steps": playbook_steps,
                "incident_data": incident_data
            })
            
            adherence_checks = []
            if adherence_result and adherence_result.get("success"):
                adherence_checks = adherence_result.get("data", {}).get("adherence_checks", [])
            print(f"[AgentsBridge] Performed {len(adherence_checks)} adherence checks")
            
            # Step 4: Map to compliance frameworks
            print("[AgentsBridge] Step 4: Mapping to compliance frameworks...")
            mapper = ComplianceMapperAgent()
            compliance_result = await mapper.process({
                "adherence_checks": adherence_checks,
                "frameworks": ["cis_controls_v8"]  # CIS only
            })
            
            compliance_mappings = []
            if compliance_result and compliance_result.get("success"):
                compliance_mappings = compliance_result.get("data", {}).get("compliance_mappings", [])
            print(f"[AgentsBridge] Generated {len(compliance_mappings)} CIS compliance mappings")
            
            # Step 5: Dynamic CIS Compliance Analysis (Post-merge style)
            dynamic_cis_result = None
            if self.dynamic_cis_agent:
                try:
                    print("[AgentsBridge] Step 5: Running dynamic CIS compliance analysis...")
                    
                    dynamic_cis_result = await self.dynamic_cis_agent.check_post_merge(
                        playbook_steps=playbook_steps,
                        incident_data={
                            "slack": slack_thread_data or {},
                            "jira": jira_ticket_data or {},
                            "github": github_events or []
                        },
                        adherence_checks=adherence_checks
                    )
                    print(f"[AgentsBridge] CIS compliance score: {dynamic_cis_result.get('compliance_score', 'N/A')}%")
                    
                    # Log results if logger available
                    if self.compliance_logger:
                        for control in dynamic_cis_result.get("controls_checked", []):
                            self.compliance_logger.log_control_result(
                                control_id=control.get("control_id", ""),
                                control_title=control.get("control_title", ""),
                                status=control.get("status", "unknown"),
                                evidence=control.get("evidence", []),
                                gaps=control.get("gaps", [])
                            )
                    
                except Exception as cis_error:
                    print(f"[AgentsBridge] CIS compliance analysis failed: {cis_error}")
                    dynamic_cis_result = {
                        "error": str(cis_error),
                        "framework": "CIS Controls v8 (failed)"
                    }
            
            # Calculate overall score
            overall_score = 0.0
            if adherence_checks:
                full = sum(1 for c in adherence_checks if c.get("adherence_level") == "full")
                partial = sum(1 for c in adherence_checks if c.get("adherence_level") == "partial")
                total = len(adherence_checks)
                overall_score = ((full + partial * 0.5) / total) * 100 if total > 0 else 0
            
            return {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "framework": "CIS Controls v8",
                "playbook": {
                    "title": parse_result.get("data", {}).get("playbook_title", "Unknown"),
                    "phases": parse_result.get("data", {}).get("phases", []),
                    "total_steps": len(playbook_steps)
                },
                "adherence": {
                    "checks": adherence_checks,
                    "overall_score": round(overall_score, 2),
                    "full_adherence": sum(1 for c in adherence_checks if c.get("adherence_level") == "full"),
                    "partial_adherence": sum(1 for c in adherence_checks if c.get("adherence_level") == "partial"),
                    "no_adherence": sum(1 for c in adherence_checks if c.get("adherence_level") == "none")
                },
                "cis_compliance": {
                    "framework": "CIS Controls v8",
                    "mappings": compliance_mappings,
                    "dynamic_analysis": dynamic_cis_result
                },
                "incident_data": {
                    "slack_available": slack_thread_data is not None,
                    "jira_available": jira_ticket_data is not None,
                    "github_available": github_events is not None
                },
                "recommendations": self._generate_recommendations(adherence_checks, compliance_mappings, dynamic_cis_result)
            }
            
        except Exception as e:
            import traceback
            if self.compliance_logger:
                self.compliance_logger.log_check_failed("analyze_incident", str(e))
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    async def _analyze_via_http(
        self,
        playbook_content: str,
        slack_thread_data: Optional[Dict[str, Any]],
        jira_ticket_data: Optional[Dict[str, Any]],
        github_events: Optional[List[Dict[str, Any]]],
        compliance_frameworks: List[str]
    ) -> Dict[str, Any]:
        """Run analysis via HTTP API call."""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Start analysis
                response = await client.post(
                    f"{self.agents_api_url}/api/v1/analysis/start",
                    json={
                        "playbook_content": playbook_content,
                        "compliance_frameworks": compliance_frameworks,
                        "slack_thread_id": None,  # Data passed differently
                        "jira_ticket_id": None,
                        "github_repo": None
                    }
                )
                response.raise_for_status()
                start_result = response.json()
                
                analysis_id = start_result.get("analysis_id")
                if not analysis_id:
                    return {"status": "error", "error": "No analysis ID returned"}
                
                # Poll for completion
                max_attempts = 60
                for attempt in range(max_attempts):
                    await asyncio.sleep(5)
                    
                    status_response = await client.get(
                        f"{self.agents_api_url}/api/v1/analysis/{analysis_id}"
                    )
                    status_response.raise_for_status()
                    result = status_response.json()
                    
                    status = result.get("status")
                    if status == "completed":
                        return result.get("result", result)
                    elif status == "failed":
                        return {"status": "error", "error": result.get("error", "Analysis failed")}
                
                return {"status": "error", "error": "Analysis timed out"}
                
        except httpx.HTTPError as e:
            return {"status": "error", "error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _generate_recommendations(
        self,
        adherence_checks: List[Dict[str, Any]],
        compliance_mappings: List[Dict[str, Any]],
        cis_compliance_result: Dict[str, Any] = None
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # CIS compliance recommendations (highest priority)
        if cis_compliance_result and not cis_compliance_result.get("error"):
            cis_recs = cis_compliance_result.get("recommendations", [])
            recommendations.extend(cis_recs[:5])  # Top 5 CIS recommendations
        
        # Based on adherence gaps
        none_adherence = [c for c in adherence_checks if c.get("adherence_level") == "none"]
        partial_adherence = [c for c in adherence_checks if c.get("adherence_level") == "partial"]
        
        if none_adherence:
            recommendations.append(
                f"WARNING: {len(none_adherence)} playbook step(s) were not followed. "
                "Review and implement automation for these steps."
            )
            
        if partial_adherence:
            recommendations.append(
                f"INFO: {len(partial_adherence)} playbook step(s) were partially followed. "
                "Consider adding clearer guidelines and checklists."
            )
        
        # Extract unique gaps and add them
        all_gaps = []
        for check in adherence_checks:
            all_gaps.extend(check.get("gaps", []))
        
        if all_gaps:
            unique_gaps = list(set(all_gaps))[:3]  # Top 3 unique gaps
            for gap in unique_gaps:
                if len(gap) < 200:  # Only add reasonable-length gaps
                    recommendations.append(f"GAP: {gap}")
        
        # Based on compliance issues
        compliance_issues = [
            m for m in compliance_mappings 
            if m.get("adherence_level") in ["none", "partial"]
        ]
        
        if compliance_issues:
            cis_controls = [m.get("control_id") for m in compliance_issues if m.get("control_id")]
            if cis_controls:
                recommendations.append(
                    f"CIS COMPLIANCE: Controls requiring attention: {', '.join(cis_controls[:5])}"
                )
        
        # Add SLA violation warnings if present
        if cis_compliance_result:
            sla_checks = cis_compliance_result.get("sla_compliance", {}).get("checks", [])
            violations = [c for c in sla_checks if c.get("status") == "violated"]
            for v in violations[:3]:  # Top 3 SLA violations
                recommendations.append(
                    f"SLA VIOLATION: {v.get('sla', 'Unknown')} - "
                    f"Required {v.get('required_minutes', 'N/A')} min, "
                    f"Actual {v.get('actual_minutes', 'N/A')} min"
                )
        
        if not recommendations:
            recommendations.append("PASS: Good CIS Controls v8 compliance! Consider documenting this incident for future reference.")
        
        return recommendations


# Convenience function for one-off analysis
async def run_quick_analysis(
    playbook_content: str,
    slack_data: Optional[Dict[str, Any]] = None,
    agents_api_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a quick analysis with minimal configuration.
    
    Args:
        playbook_content: Playbook markdown content
        slack_data: Optional Slack thread data
        agents_api_url: Optional agents API URL (uses direct mode if None)
        
    Returns:
        Analysis result dictionary
    """
    bridge = AgentsBridge(agents_api_url)
    return await bridge.analyze_incident(
        playbook_content=playbook_content,
        slack_thread_data=slack_data
    )


# For testing
if __name__ == "__main__":
    import asyncio
    
    # Load test playbook
    playbook_path = Path(__file__).parent / "fixtures" / "playbook_comprehensive.md"
    with open(playbook_path) as f:
        playbook = f.read()
    
    async def test():
        bridge = AgentsBridge()
        result = await bridge.analyze_incident(playbook)
        print(f"\nAnalysis Result:")
        print(f"  Status: {result.get('status')}")
        print(f"  Score: {result.get('adherence', {}).get('overall_score', 'N/A')}%")
        print(f"  Recommendations: {len(result.get('recommendations', []))}")
    
    asyncio.run(test())
