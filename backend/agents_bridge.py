"""
Agents Bridge: Connects backend to the multi-agent analysis service

This module provides a clean interface for the backend to call the agents API.
It can work either:
1. Direct import (same process) - faster, for development
2. HTTP client (separate processes) - production mode

The bridge abstracts these implementation details from the Slack handler.
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
    print("✅ Agents imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import agents directly: {e}")
    AGENTS_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Error importing agents: {e}")
    AGENTS_AVAILABLE = False


class AgentsBridge:
    """Bridge to connect backend with multi-agent analysis service."""
    
    def __init__(self, agents_api_url: Optional[str] = None):
        """
        Initialize the agents bridge.
        
        Args:
            agents_api_url: URL of agents API (e.g., "http://localhost:8001")
                           If None, uses direct import mode.
        """
        self.agents_api_url = agents_api_url
        self.use_direct = agents_api_url is None and AGENTS_AVAILABLE
        
        if self.use_direct:
            print("🔗 AgentsBridge: Using DIRECT mode (same process)")
        elif agents_api_url:
            print(f"🔗 AgentsBridge: Using HTTP mode ({agents_api_url})")
        else:
            print("⚠️ AgentsBridge: Agents not available!")
    
    async def analyze_incident(
        self,
        playbook_content: str,
        slack_thread_data: Optional[Dict[str, Any]] = None,
        jira_ticket_data: Optional[Dict[str, Any]] = None,
        github_events: Optional[List[Dict[str, Any]]] = None,
        compliance_frameworks: List[str] = None
    ) -> Dict[str, Any]:
        """
        Run full incident analysis using multi-agent system.
        
        Args:
            playbook_content: Markdown content of the playbook
            slack_thread_data: Parsed Slack thread data (optional)
            jira_ticket_data: Parsed Jira ticket data (optional)
            github_events: List of GitHub events (optional)
            compliance_frameworks: List of framework names (default: NIST)
            
        Returns:
            Analysis result dictionary
        """
        if compliance_frameworks is None:
            compliance_frameworks = ["nist_sp_800_61"]
        
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
            return {
                "status": "error",
                "error": "Agents service not available"
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
            # Convert framework strings to enums
            frameworks = []
            for f in compliance_frameworks:
                try:
                    frameworks.append(ComplianceFramework(f.lower()))
                except ValueError:
                    frameworks.append(ComplianceFramework.NIST_SP_800_61)
            
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
                "frameworks": [f.value for f in frameworks]
            })
            
            compliance_mappings = []
            if compliance_result and compliance_result.get("success"):
                compliance_mappings = compliance_result.get("data", {}).get("compliance_mappings", [])
            print(f"[AgentsBridge] Generated {len(compliance_mappings)} compliance mappings")
            
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
                "compliance": {
                    "frameworks_analyzed": compliance_frameworks,
                    "mappings": compliance_mappings
                },
                "incident_data": {
                    "slack_available": slack_thread_data is not None,
                    "jira_available": jira_ticket_data is not None,
                    "github_available": github_events is not None
                },
                "recommendations": self._generate_recommendations(adherence_checks, compliance_mappings)
            }
            
        except Exception as e:
            import traceback
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
        compliance_mappings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Based on adherence gaps
        none_adherence = [c for c in adherence_checks if c.get("adherence_level") == "none"]
        partial_adherence = [c for c in adherence_checks if c.get("adherence_level") == "partial"]
        
        if none_adherence:
            recommendations.append(
                f"⚠️ {len(none_adherence)} playbook step(s) were not followed. "
                "Review and implement automation for these steps."
            )
            
        if partial_adherence:
            recommendations.append(
                f"📋 {len(partial_adherence)} playbook step(s) were partially followed. "
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
                    recommendations.append(f"🔧 Gap identified: {gap}")
        
        # Based on compliance issues
        compliance_issues = [
            m for m in compliance_mappings 
            if m.get("adherence_level") in ["none", "partial"]
        ]
        
        if compliance_issues:
            frameworks_affected = list(set(m.get("framework") for m in compliance_issues))
            recommendations.append(
                f"📜 Compliance frameworks requiring attention: {', '.join(str(f) for f in frameworks_affected)}"
            )
        
        if not recommendations:
            recommendations.append("✅ Good compliance posture! Consider documenting this incident for future reference.")
        
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
