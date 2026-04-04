"""Compliance Mapper Agent - Maps findings to compliance frameworks"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.schemas import ComplianceMapping, ComplianceFramework, AdherenceLevel
import json
import os


class ComplianceMapperAgent(BaseAgent):
    """Agent responsible for mapping adherence to compliance frameworks"""
    
    def __init__(self):
        super().__init__("compliance_mapper")
        self.frameworks_data = self._load_frameworks()
    
    def _load_frameworks(self) -> Dict[str, Any]:
        """Load compliance framework data"""
        frameworks = {}
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "compliance")
        
        framework_files = {
            "nist_sp_800_61": "nist_sp_800_61.json",
            "soc2_cc7": "soc2_cc7.json",
            "iso_27001_a16": "iso_27001_a16.json"
        }
        
        for framework_key, filename in framework_files.items():
            filepath = os.path.join(data_dir, filename)
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        frameworks[framework_key] = json.load(f)
                    self.log(f"Loaded framework: {framework_key}")
                else:
                    self.log(f"Framework file not found: {filepath}", level="warning")
                    # Use minimal default
                    frameworks[framework_key] = self._get_default_framework(framework_key)
            except Exception as e:
                self.log(f"Failed to load {framework_key}: {e}", level="error")
                frameworks[framework_key] = self._get_default_framework(framework_key)
        
        return frameworks
    
    def _get_default_framework(self, framework_key: str) -> Dict[str, Any]:
        """Get default framework structure"""
        defaults = {
            "nist_sp_800_61": {
                "name": "NIST SP 800-61",
                "description": "Computer Security Incident Handling Guide",
                "controls": [
                    {"id": "IR-1", "title": "Incident Response Policy and Procedures"},
                    {"id": "IR-4", "title": "Incident Handling"},
                    {"id": "IR-5", "title": "Incident Monitoring"},
                    {"id": "IR-6", "title": "Incident Reporting"},
                    {"id": "IR-8", "title": "Incident Response Plan"}
                ]
            },
            "soc2_cc7": {
                "name": "SOC 2 CC7",
                "description": "System Operations - Detection and Incident Management",
                "controls": [
                    {"id": "CC7.1", "title": "Incident Detection"},
                    {"id": "CC7.2", "title": "Incident Response"},
                    {"id": "CC7.3", "title": "Incident Monitoring"},
                    {"id": "CC7.4", "title": "Incident Documentation"},
                    {"id": "CC7.5", "title": "Incident Analysis"}
                ]
            },
            "iso_27001_a16": {
                "name": "ISO 27001 A.16",
                "description": "Information Security Incident Management",
                "controls": [
                    {"id": "A.16.1.1", "title": "Responsibilities and procedures"},
                    {"id": "A.16.1.2", "title": "Reporting information security events"},
                    {"id": "A.16.1.3", "title": "Reporting information security weaknesses"},
                    {"id": "A.16.1.4", "title": "Assessment of and decision on information security events"},
                    {"id": "A.16.1.5", "title": "Response to information security incidents"},
                    {"id": "A.16.1.6", "title": "Learning from information security incidents"},
                    {"id": "A.16.1.7", "title": "Collection of evidence"}
                ]
            }
        }
        return defaults.get(framework_key, {"name": framework_key, "controls": []})
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map adherence checks to compliance frameworks
        
        Args:
            input_data: Dict with 'adherence_checks', 'frameworks'
            
        Returns:
            Dict with compliance mappings
        """
        adherence_checks = input_data.get("adherence_checks", [])
        requested_frameworks = input_data.get("frameworks", ["nist_sp_800_61"])
        
        if not adherence_checks:
            return self.create_result(
                success=False,
                error="No adherence checks provided"
            )
        
        self.log(f"Mapping to {len(requested_frameworks)} compliance frameworks")
        
        all_mappings = []
        
        for framework_name in requested_frameworks:
            framework_key = framework_name.lower()
            if framework_key not in self.frameworks_data:
                self.log(f"Unknown framework: {framework_name}", level="warning")
                continue
            
            framework = self.frameworks_data[framework_key]
            self.log(f"Processing framework: {framework.get('name')}")
            
            mappings = await self._map_to_framework(
                framework_key,
                framework,
                adherence_checks
            )
            
            all_mappings.extend(mappings)
        
        self.log(f"Generated {len(all_mappings)} compliance mappings")
        
        return self.create_result(
            success=True,
            data={
                "compliance_mappings": all_mappings,
                "frameworks_analyzed": requested_frameworks,
                "total_mappings": len(all_mappings)
            }
        )
    
    async def _map_to_framework(
        self,
        framework_key: str,
        framework: Dict[str, Any],
        adherence_checks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Map adherence checks to specific framework controls"""
        
        # Prepare adherence summary
        adherence_summary = "\n".join([
            f"- Step {check['step_id']}: {check['adherence_level']} "
            f"(Evidence: {len(check.get('evidence', []))}, Gaps: {len(check.get('gaps', []))})"
            for check in adherence_checks
        ])
        
        controls = framework.get("controls", [])
        
        system_prompt = f"""You are a compliance expert specializing in {framework.get('name')}.
Your task is to map incident response adherence to specific compliance controls."""
        
        prompt = f"""Analyze how the incident response adherence maps to {framework.get('name')} controls.

Framework: {framework.get('name')}
Description: {framework.get('description')}

Available Controls:
{json.dumps(controls, indent=2)}

Adherence Summary:
{adherence_summary}

For each relevant control, provide a JSON array with:
{{
    "mappings": [
        {{
            "control_id": "Control ID from framework",
            "control_title": "Control title",
            "adherence_level": "full|partial|none",
            "supporting_evidence": ["Specific evidence from adherence checks"],
            "gaps": ["Identified gaps relevant to this control"]
        }}
    ]
}}

Map to ALL relevant controls."""
        
        try:
            result = await self.call_llm_structured(prompt, system_prompt)
            mappings_data = result.get("mappings", [])
            
            # Convert to ComplianceMapping objects
            mappings = []
            for mapping in mappings_data:
                try:
                    compliance_mapping = ComplianceMapping(
                        framework=ComplianceFramework(framework_key),
                        control_id=mapping.get("control_id", ""),
                        control_title=mapping.get("control_title", ""),
                        adherence_level=AdherenceLevel(mapping.get("adherence_level", "none")),
                        supporting_evidence=mapping.get("supporting_evidence", [])
                    )
                    mappings.append(compliance_mapping.dict())
                except Exception as e:
                    self.log(f"Failed to create mapping: {e}", level="warning")
            
            return mappings
            
        except Exception as e:
            self.log(f"Failed to map to {framework_key}: {e}", level="error")
            return []
