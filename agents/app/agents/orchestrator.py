"""Orchestrator Agent - Coordinates the entire multi-agent workflow"""
from typing import Dict, Any, Optional
from datetime import datetime

from app.agents.base import BaseAgent
from app.agents.playbook_parser import PlaybookParserAgent
from app.agents.incident_trail import IncidentTrailAgent
from app.agents.adherence_checker import AdherenceCheckerAgent
from app.agents.compliance_mapper import ComplianceMapperAgent
from app.models.schemas import AnalysisStatus, AnalysisResult
from app.utils.helpers import generate_id


class OrchestratorAgent(BaseAgent):
    """Main orchestrator that coordinates all other agents"""
    
    def __init__(self):
        super().__init__("orchestrator")
        
        # Initialize sub-agents
        self.playbook_parser = PlaybookParserAgent()
        self.incident_trail = IncidentTrailAgent()
        self.adherence_checker = AdherenceCheckerAgent()
        self.compliance_mapper = ComplianceMapperAgent()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete analysis workflow
        
        Args:
            input_data: Complete analysis request data
            
        Returns:
            Complete analysis results
        """
        analysis_id = generate_id(prefix="analysis")
        self.log(f"Starting analysis: {analysis_id}")
        
        # Initialize result
        result = {
            "analysis_id": analysis_id,
            "status": AnalysisStatus.IN_PROGRESS,
            "playbook_steps": [],
            "incident_data": {},
            "adherence_checks": [],
            "compliance_mappings": [],
            "overall_score": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None,
            "errors": []
        }
        
        try:
            # Step 1: Parse Playbook
            self.log("Step 1/4: Parsing playbook")
            playbook_result = await self.playbook_parser.process({
                "playbook_content": input_data.get("playbook_content", "")
            })
            
            if not playbook_result["success"]:
                raise Exception(f"Playbook parsing failed: {playbook_result.get('error')}")
            
            result["playbook_steps"] = playbook_result["data"]["steps"]
            self.log(f"Parsed {len(result['playbook_steps'])} playbook steps")
            
            # Step 2: Collect Incident Data
            self.log("Step 2/4: Collecting incident data")
            incident_result = await self.incident_trail.process({
                "slack_thread_id": input_data.get("slack_thread_id"),
                "jira_ticket_id": input_data.get("jira_ticket_id"),
                "github_repo": input_data.get("github_repo")
            })
            
            if incident_result["success"]:
                result["incident_data"] = incident_result["data"]
                self.log("Incident data collected successfully")
            else:
                self.log("Incident data collection had issues, continuing", level="warning")
                result["errors"].append(f"Incident trail: {incident_result.get('error')}")
            
            # Step 3: Check Adherence
            self.log("Step 3/4: Checking adherence to playbook")
            adherence_result = await self.adherence_checker.process({
                "playbook_steps": result["playbook_steps"],
                "incident_data": result["incident_data"]
            })
            
            if not adherence_result["success"]:
                raise Exception(f"Adherence checking failed: {adherence_result.get('error')}")
            
            result["adherence_checks"] = adherence_result["data"]["adherence_checks"]
            result["overall_score"] = adherence_result["data"]["overall_score"]
            self.log(f"Adherence score: {result['overall_score']}%")
            
            # Step 4: Map to Compliance Frameworks
            self.log("Step 4/4: Mapping to compliance frameworks")
            compliance_result = await self.compliance_mapper.process({
                "adherence_checks": result["adherence_checks"],
                "frameworks": input_data.get("compliance_frameworks", ["nist_sp_800_61"])
            })
            
            if compliance_result["success"]:
                result["compliance_mappings"] = compliance_result["data"]["compliance_mappings"]
                self.log(f"Generated {len(result['compliance_mappings'])} compliance mappings")
            else:
                self.log("Compliance mapping had issues, continuing", level="warning")
                result["errors"].append(f"Compliance mapper: {compliance_result.get('error')}")
            
            # Mark as completed
            result["status"] = AnalysisStatus.COMPLETED
            result["completed_at"] = datetime.utcnow()
            result["updated_at"] = datetime.utcnow()
            
            self.log(f"Analysis {analysis_id} completed successfully")
            
            return self.create_result(success=True, data=result)
            
        except Exception as e:
            self.log(f"Analysis failed: {e}", level="error")
            result["status"] = AnalysisStatus.FAILED
            result["updated_at"] = datetime.utcnow()
            result["errors"].append(str(e))
            
            return self.create_result(
                success=False,
                data=result,
                error=str(e)
            )
    
    async def get_progress(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get progress of an ongoing analysis
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Progress information
        """
        # This would integrate with a state store in production
        return {
            "analysis_id": analysis_id,
            "status": "in_progress",
            "current_step": "Checking adherence",
            "progress_percentage": 65
        }
