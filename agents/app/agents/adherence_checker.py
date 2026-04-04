"""Adherence Checker Agent - Compares actual vs expected actions"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.schemas import AdherenceCheck, AdherenceLevel, PlaybookStep


class AdherenceCheckerAgent(BaseAgent):
    """Agent responsible for checking adherence to playbook steps"""
    
    def __init__(self):
        super().__init__("adherence_checker")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check adherence between playbook steps and actual incident response
        
        Args:
            input_data: Dict with 'playbook_steps' and 'incident_data'
            
        Returns:
            Dict with adherence checks for each step
        """
        playbook_steps = input_data.get("playbook_steps", [])
        incident_data = input_data.get("incident_data", {})
        
        if not playbook_steps:
            return self.create_result(
                success=False,
                error="No playbook steps provided"
            )
        
        self.log(f"Checking adherence for {len(playbook_steps)} playbook steps")
        
        system_prompt = """You are an expert incident response auditor.
Your task is to compare what SHOULD have been done (playbook steps) with what WAS actually done (incident data).
Be thorough and objective in your analysis.
Identify:
- Actions that were completed as expected
- Actions that were partially completed
- Actions that were missed or not completed
- Any additional actions taken that weren't in the playbook"""
        
        # Prepare incident summary
        incident_summary = self._prepare_incident_summary(incident_data)
        
        adherence_checks = []
        
        for step in playbook_steps:
            self.log(f"Checking adherence for step: {step.get('step_id')}")
            
            prompt = f"""Analyze whether the following playbook step was followed during the incident response.

Playbook Step:
- Phase: {step.get('phase')}
- Description: {step.get('description')}
- Required Actions: {', '.join(step.get('required_actions', []))}
- Responsible Roles: {', '.join(step.get('responsible_roles', []))}

Incident Data Summary:
{incident_summary}

Provide a JSON response with:
{{
    "adherence_level": "full|partial|none",
    "evidence": ["Specific evidence from incident data supporting your assessment"],
    "gaps": ["Specific gaps or missing actions"],
    "recommendations": ["Specific recommendations for improvement"]
}}

Be specific and reference actual data from the incident."""
            
            try:
                result = await self.call_llm_structured(prompt, system_prompt)
                
                # Validate LLM response
                if not isinstance(result, dict):
                    self.log(f"LLM returned invalid response for step {step.get('step_id')}", level="warning")
                    result = {}
                
                if "error" in result:
                    raise ValueError(result.get("error"))
                
                # Validate adherence_level
                adherence_level = result.get("adherence_level", "none")
                if adherence_level not in ["full", "partial", "none"]:
                    self.log(f"Invalid adherence_level '{adherence_level}', defaulting to 'none'", level="warning")
                    adherence_level = "none"
                
                adherence_check = AdherenceCheck(
                    step_id=step.get("step_id"),
                    adherence_level=AdherenceLevel(adherence_level),
                    evidence=result.get("evidence", []) if isinstance(result.get("evidence"), list) else [],
                    gaps=result.get("gaps", []) if isinstance(result.get("gaps"), list) else [],
                    recommendations=result.get("recommendations", []) if isinstance(result.get("recommendations"), list) else []
                )
                
                adherence_checks.append(adherence_check.dict())
                
            except Exception as e:
                self.log(f"Failed to check step {step.get('step_id')}: {e}", level="error")
                # Add a failed check
                adherence_checks.append({
                    "step_id": step.get("step_id"),
                    "adherence_level": "none",
                    "evidence": [],
                    "gaps": [f"Analysis failed: {str(e)}"],
                    "recommendations": ["Manual review required"]
                })
        
        # Calculate overall adherence score
        total_steps = len(adherence_checks)
        full_adherence = sum(1 for check in adherence_checks if check["adherence_level"] == "full")
        partial_adherence = sum(1 for check in adherence_checks if check["adherence_level"] == "partial")
        
        overall_score = (full_adherence + (partial_adherence * 0.5)) / total_steps if total_steps > 0 else 0
        
        self.log(f"Adherence check complete. Overall score: {overall_score:.2%}")
        
        return self.create_result(
            success=True,
            data={
                "adherence_checks": adherence_checks,
                "overall_score": round(overall_score * 100, 2),
                "total_steps": total_steps,
                "full_adherence": full_adherence,
                "partial_adherence": partial_adherence,
                "no_adherence": total_steps - full_adherence - partial_adherence
            }
        )
    
    def _prepare_incident_summary(self, incident_data: Dict[str, Any]) -> str:
        """Prepare a summary of incident data for analysis"""
        summary_parts = []
        
        # Slack data
        slack_messages = incident_data.get("slack_messages", [])
        if slack_messages:
            summary_parts.append(f"Slack: {len(slack_messages)} messages exchanged")
            if incident_data.get("slack_timeline"):
                summary_parts.append(f"Timeline: {len(incident_data['slack_timeline'])} events")
        
        # Jira data
        jira_issue = incident_data.get("jira_issue", {})
        if jira_issue:
            summary_parts.append(f"Jira: Ticket {jira_issue.get('key')} - {jira_issue.get('status')}")
            jira_comments = incident_data.get("jira_comments", [])
            if jira_comments:
                summary_parts.append(f"Jira Comments: {len(jira_comments)} updates")
        
        # GitHub data
        github_events = incident_data.get("github_events", [])
        if github_events:
            summary_parts.append(f"GitHub: {len(github_events)} events")
            incident_prs = incident_data.get("github_incident_prs", [])
            if incident_prs:
                summary_parts.append(f"Incident PRs: {len(incident_prs)}")
        
        return "\n".join(summary_parts) if summary_parts else "No incident data available"
