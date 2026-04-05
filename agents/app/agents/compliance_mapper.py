"""
CIS Controls v8 Compliance Mapper Agent
Maps incident response findings to CIS Controls v8 (Control 17 - Incident Response)
ONLY supports CIS framework - no NIST, SOC2, or ISO
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.schemas import ComplianceMapping, ComplianceFramework, AdherenceLevel
import json
import os


# CIS Controls v8 - Control 17: Incident Response and Management
CIS_CONTROLS_V8 = {
    "name": "CIS Controls v8",
    "description": "Center for Internet Security Controls Version 8 - Control 17: Incident Response",
    "controls": [
        {
            "id": "17.1",
            "title": "Designate Personnel to Manage Incident Handling",
            "description": "Designate one key person, and at least one backup, who will manage incident handling process.",
            "sla_minutes": None,
            "phase": "preparation"
        },
        {
            "id": "17.2", 
            "title": "Establish and Maintain Contact Information for Reporting Security Incidents",
            "description": "Establish and maintain contact information for parties that need to be informed of security incidents.",
            "sla_minutes": None,
            "phase": "preparation"
        },
        {
            "id": "17.3",
            "title": "Establish and Maintain an Enterprise Process for Reporting Incidents",
            "description": "Establish and maintain an enterprise process for workforce members to report security incidents.",
            "sla_minutes": 15,  # Initial response SLA
            "phase": "detection"
        },
        {
            "id": "17.4",
            "title": "Establish and Maintain an Incident Response Process",
            "description": "Establish and maintain an incident response process that addresses roles, responsibilities, communication requirements, and the phases of incident response.",
            "sla_minutes": None,
            "phase": "preparation"
        },
        {
            "id": "17.5",
            "title": "Assign Key Roles and Responsibilities",
            "description": "Assign key roles and responsibilities for incident response, including staff from legal, IT, information security, facilities, public relations, human resources, incident responders, and analysts.",
            "sla_minutes": 15,  # Must assign IC within 15 min
            "phase": "detection"
        },
        {
            "id": "17.6",
            "title": "Define Mechanisms for Communicating During Incident Response",
            "description": "Define mechanisms for communicating during an incident response.",
            "sla_minutes": 30,  # Establish comms within 30 min
            "phase": "containment"
        },
        {
            "id": "17.7",
            "title": "Conduct Routine Incident Response Exercises",
            "description": "Plan and conduct routine incident response exercises and scenarios.",
            "sla_minutes": None,
            "phase": "post_incident"
        },
        {
            "id": "17.8",
            "title": "Conduct Post-Incident Reviews",
            "description": "Conduct post-incident reviews.",
            "sla_minutes": 2880,  # Within 48 hours
            "phase": "post_incident"
        },
        {
            "id": "17.9",
            "title": "Establish and Maintain Security Incident Thresholds",
            "description": "Establish and maintain security incident thresholds, including at a minimum, differentiating between an incident and an event.",
            "sla_minutes": None,
            "phase": "preparation"
        }
    ]
}


class ComplianceMapperAgent(BaseAgent):
    """
    CIS Controls v8 Compliance Mapper Agent
    Maps adherence checks ONLY to CIS Controls v8 Control 17
    """
    
    def __init__(self):
        super().__init__("compliance_mapper")
        self.cis_framework = CIS_CONTROLS_V8
        self.log("Initialized CIS Controls v8 Compliance Mapper (CIS-only mode)")
    
    def _get_cis_framework(self) -> Dict[str, Any]:
        """Get CIS Controls v8 framework data"""
        return self.cis_framework
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map adherence checks to CIS Controls v8 ONLY
        
        Args:
            input_data: Dict with 'adherence_checks'
            
        Returns:
            Dict with CIS compliance mappings
        """
        adherence_checks = input_data.get("adherence_checks", [])
        # Ignore frameworks param - we ONLY use CIS
        
        if not adherence_checks:
            return self.create_result(
                success=False,
                error="No adherence checks provided"
            )
        
        self.log("Mapping to CIS Controls v8 (Control 17 - Incident Response)")
        
        mappings = await self._map_to_cis(adherence_checks)
        
        self.log(f"Generated {len(mappings)} CIS compliance mappings")
        
        return self.create_result(
            success=True,
            data={
                "compliance_mappings": mappings,
                "frameworks_analyzed": ["cis_controls_v8"],
                "total_mappings": len(mappings),
                "framework_details": {
                    "name": self.cis_framework["name"],
                    "description": self.cis_framework["description"],
                    "total_controls": len(self.cis_framework["controls"])
                }
            }
        )
    
    async def _map_to_cis(self, adherence_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map adherence checks to CIS Controls v8 Control 17"""
        
        # Prepare adherence summary
        adherence_summary = "\n".join([
            f"- Step {check['step_id']}: {check['adherence_level']} "
            f"(Evidence: {len(check.get('evidence', []))}, Gaps: {len(check.get('gaps', []))})"
            for check in adherence_checks
        ])
        
        controls = self.cis_framework.get("controls", [])
        
        system_prompt = """You are a CIS Controls v8 compliance expert specializing in Control 17 (Incident Response).
Your task is to STRICTLY map incident response adherence to CIS Controls v8 Control 17 safeguards.
Be precise and evidence-based in your mappings."""
        
        prompt = f"""Analyze how the incident response adherence maps to CIS Controls v8 Control 17.

Framework: CIS Controls v8
Focus Area: Control 17 - Incident Response and Management

Available CIS Controls:
{json.dumps(controls, indent=2)}

Adherence Summary from Playbook Analysis:
{adherence_summary}

For each CIS control, evaluate compliance and provide a JSON array:
{{
    "mappings": [
        {{
            "control_id": "17.X",
            "control_title": "Exact control title from above",
            "adherence_level": "full|partial|none",
            "supporting_evidence": ["Specific evidence supporting this assessment"],
            "gaps": ["Specific gaps found for this control"],
            "sla_status": "met|violated|not_applicable"
        }}
    ]
}}

Map to ALL 9 CIS Control 17 safeguards. Be strict - if there's no evidence, mark as "none"."""
        
        try:
            result = await self.call_llm_structured(prompt, system_prompt)
            mappings_data = result.get("mappings", [])
            
            mappings = []
            for mapping in mappings_data:
                try:
                    # Ensure supporting_evidence is list of strings
                    evidence = mapping.get("supporting_evidence", [])
                    if not isinstance(evidence, list):
                        evidence = []
                    evidence = [str(e) if not isinstance(e, str) else e for e in evidence]
                    
                    # Ensure gaps is list of strings
                    gaps = mapping.get("gaps", [])
                    if not isinstance(gaps, list):
                        gaps = []
                    gaps = [str(g) if not isinstance(g, str) else g for g in gaps]
                    
                    compliance_mapping = ComplianceMapping(
                        framework=ComplianceFramework.CIS_CONTROLS_V8,
                        control_id=mapping.get("control_id", ""),
                        control_title=mapping.get("control_title", ""),
                        adherence_level=AdherenceLevel(mapping.get("adherence_level", "none")),
                        supporting_evidence=evidence,
                        gaps=gaps
                    )
                    
                    mapping_dict = compliance_mapping.dict()
                    mapping_dict["sla_status"] = mapping.get("sla_status", "not_applicable")
                    mappings.append(mapping_dict)
                    
                except Exception as e:
                    self.log(f"Failed to create mapping: {e}", level="warning")
            
            return mappings
            
        except Exception as e:
            self.log(f"Failed to map to CIS: {e}", level="error")
            return self._fallback_cis_mapping(adherence_checks)
    
    def _fallback_cis_mapping(self, adherence_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback mapping when LLM fails"""
        mappings = []
        
        for control in self.cis_framework["controls"]:
            # Simple heuristic mapping based on phase
            relevant_checks = [
                c for c in adherence_checks 
                if self._phase_matches(c.get("step_id", ""), control.get("phase", ""))
            ]
            
            if relevant_checks:
                full = sum(1 for c in relevant_checks if c.get("adherence_level") == "full")
                partial = sum(1 for c in relevant_checks if c.get("adherence_level") == "partial")
                total = len(relevant_checks)
                
                if full == total:
                    level = "full"
                elif full + partial > 0:
                    level = "partial"
                else:
                    level = "none"
            else:
                level = "none"
            
            mappings.append({
                "framework": "cis_controls_v8",
                "control_id": control["id"],
                "control_title": control["title"],
                "adherence_level": level,
                "supporting_evidence": [f"Based on {len(relevant_checks)} relevant step checks"],
                "gaps": [] if level == "full" else [f"Control {control['id']} requires attention"],
                "sla_status": "not_applicable"
            })
        
        return mappings
    
    def _phase_matches(self, step_id: str, control_phase: str) -> bool:
        """Check if step matches control phase"""
        phase_keywords = {
            "preparation": ["prep", "plan", "establish"],
            "detection": ["detect", "alert", "initial", "step_1", "step_2"],
            "containment": ["contain", "isolate", "block", "step_3", "step_4"],
            "post_incident": ["review", "lesson", "post", "step_9", "step_10"]
        }
        
        keywords = phase_keywords.get(control_phase, [])
        step_lower = step_id.lower()
        return any(kw in step_lower for kw in keywords)
