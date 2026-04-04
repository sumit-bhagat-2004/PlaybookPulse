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
Extract structured information concisely. Keep descriptions brief (max 50 words each).
Respond ONLY with valid JSON - no markdown, no explanation."""
        
        prompt = f"""Analyze this playbook and extract structured information.

{playbook_content}

Respond with this EXACT JSON structure (keep descriptions SHORT):
{{"playbook_title": "title", "phases": ["Phase1", "Phase2"], "steps": [{{"step_id": "step_1", "phase": "Detection", "description": "brief description", "required_actions": ["action1"], "responsible_roles": ["role1"]}}]}}

IMPORTANT:
- Keep each description under 50 words
- Limit to the 10 MOST IMPORTANT steps
- Do NOT include markdown code blocks
- Output ONLY valid JSON"""
        
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
