"""Playbook Parser Agent - Extracts and structures playbook requirements"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.schemas import PlaybookStep


class PlaybookParserAgent(BaseAgent):
    """Agent responsible for parsing incident response playbooks"""
    
    def __init__(self):
        super().__init__("playbook_parser")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a playbook and extract structured steps
        
        Args:
            input_data: Dict with 'playbook_content' key
            
        Returns:
            Dict with parsed playbook steps
        """
        playbook_content = input_data.get("playbook_content", "")
        
        if not playbook_content:
            return self.create_result(
                success=False,
                error="No playbook content provided"
            )
        
        self.log(f"Parsing playbook ({len(playbook_content)} characters)")
        
        system_prompt = """You are an expert at analyzing incident response playbooks.
Your task is to extract structured information from playbook documents.
Focus on identifying:
- Clear phases/stages of incident response
- Specific steps and actions required
- Responsible roles for each step
- Dependencies between steps
- Required tools or systems"""
        
        prompt = f"""Analyze the following incident response playbook and extract structured information.

Playbook Content:
{playbook_content}

Please provide a JSON response with the following structure:
{{
    "playbook_title": "Title of the playbook",
    "phases": ["Phase 1", "Phase 2", ...],
    "steps": [
        {{
            "step_id": "step_1",
            "phase": "Detection",
            "description": "Clear description of the step",
            "required_actions": ["Action 1", "Action 2"],
            "responsible_roles": ["Role 1", "Role 2"],
            "dependencies": ["step_id that must complete first"]
        }}
    ]
}}

Extract ALL steps and be thorough."""
        
        try:
            result = await self.call_llm_structured(prompt, system_prompt)
            
            # Validate LLM response structure
            if not isinstance(result, dict):
                self.log("LLM returned non-dict response, using defaults", level="warning")
                result = {}
            
            if "error" in result:
                self.log(f"LLM parsing failed: {result.get('error')}", level="warning")
                return self.create_result(
                    success=False,
                    error=f"Failed to parse playbook: {result.get('error')}"
                )
            
            steps = result.get("steps", [])
            
            # Validate steps is a list
            if not isinstance(steps, list):
                self.log("LLM returned invalid steps format, using empty list", level="warning")
                steps = []
            
            self.log(f"Extracted {len(steps)} steps from playbook")
            
            # Convert to PlaybookStep objects
            playbook_steps = [
                PlaybookStep(
                    step_id=step.get("step_id", f"step_{i+1}"),
                    phase=step.get("phase", "Unknown"),
                    description=step.get("description", ""),
                    required_actions=step.get("required_actions", []),
                    responsible_roles=step.get("responsible_roles", [])
                )
                for i, step in enumerate(steps)
            ]
            
            return self.create_result(
                success=True,
                data={
                    "playbook_title": result.get("playbook_title", "Untitled Playbook"),
                    "phases": result.get("phases", []),
                    "steps": [step.dict() for step in playbook_steps],
                    "total_steps": len(playbook_steps)
                }
            )
            
        except Exception as e:
            self.log(f"Failed to parse playbook: {e}", level="error")
            return self.create_result(
                success=False,
                error=str(e)
            )
