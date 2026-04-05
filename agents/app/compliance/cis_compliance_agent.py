"""
LangChain-based CIS Compliance Agent
Performs strict compliance checking against CIS Controls v8 and CIS IR Guide
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("WARNING: LangChain not available. CIS Compliance Agent will use fallback mode.")

from app.compliance.cis_framework import get_cis_requirements_for_step, get_all_cis_controls
from app.compliance.timestamp_analyzer import TimestampAnalyzer


class CISComplianceAgent:
    """
    LangChain-based agent for strict CIS compliance checking
    
    This agent uses an LLM to reason about compliance, providing:
    - Detailed analysis of each step against CIS requirements
    - Strict enforcement of SLAs
    - Evidence-based compliance decisions
    - Specific remediation recommendations
    """
    
    def __init__(self, google_api_key: Optional[str] = None, use_langchain: bool = True):
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.timestamp_analyzer = TimestampAnalyzer()
        
        if self.use_langchain and google_api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=google_api_key,
                    temperature=0.1,  # Low temperature for strict, consistent compliance decisions
                    convert_system_message_to_human=True
                )
                print("[CISComplianceAgent] Initialized with LangChain and Gemini")
            except Exception as e:
                print(f"[CISComplianceAgent] Failed to initialize LangChain: {e}")
                self.use_langchain = False
        else:
            self.use_langchain = False
            print("[CISComplianceAgent] Running in fallback mode (no LangChain)")
    
    async def analyze_compliance(
        self,
        playbook_steps: List[Dict[str, Any]],
        incident_data: Dict[str, Any],
        adherence_checks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive CIS compliance analysis
        
        Args:
            playbook_steps: Parsed playbook steps
            incident_data: Incident data (Slack, Jira, GitHub)
            adherence_checks: Existing adherence check results
            
        Returns:
            CIS compliance report with strict violation analysis
        """
        print("[CISComplianceAgent] Starting CIS compliance analysis...")
        
        # Extract timeline
        timeline = self.timestamp_analyzer.extract_timeline_from_incident_data(incident_data)
        print(f"[CISComplianceAgent] Extracted {len(timeline)} timeline events")
        
        # Analyze timing for each step
        timing_results = []
        for step in playbook_steps:
            timing = self.timestamp_analyzer.calculate_step_timing(
                step_id=step.get("id", "unknown"),
                step_title=step.get("title", ""),
                step_phase=step.get("phase", ""),
                playbook_step_data=step
            )
            timing_results.append(timing)
        
        # Generate SLA violation report
        sla_report = self.timestamp_analyzer.generate_sla_violation_report(timing_results)
        print(f"[CISComplianceAgent] Found {sla_report['total_violations']} SLA violations")
        
        # Perform detailed CIS compliance analysis
        if self.use_langchain:
            cis_analysis = await self._langchain_compliance_analysis(
                playbook_steps,
                adherence_checks,
                timing_results,
                timeline
            )
        else:
            cis_analysis = self._fallback_compliance_analysis(
                playbook_steps,
                adherence_checks,
                timing_results
            )
        
        return {
            "framework": "CIS Controls v8 + CIS IR Guide",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "incident_timeline": {
                "incident_start": self.timestamp_analyzer.incident_start_time.isoformat() if self.timestamp_analyzer.incident_start_time else None,
                "total_events": len(timeline),
                "event_sources": list(set(e["source"] for e in timeline))
            },
            "sla_compliance": sla_report,
            "timing_analysis": timing_results,
            "cis_control_compliance": cis_analysis,
            "overall_cis_score": self._calculate_overall_cis_score(cis_analysis, sla_report),
            "strict_violations": self._identify_strict_violations(cis_analysis, sla_report),
            "recommendations": self._generate_cis_recommendations(cis_analysis, sla_report)
        }
    
    async def _langchain_compliance_analysis(
        self,
        playbook_steps: List[Dict[str, Any]],
        adherence_checks: List[Dict[str, Any]],
        timing_results: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LangChain to perform detailed compliance reasoning"""
        
        # Get CIS Control 17 safeguards
        cis_safeguards = get_all_cis_controls()
        
        # Create prompt template
        system_template = """You are a strict CIS Controls v8 compliance auditor specializing in Incident Response (Control 17).

Your role is to analyze incident response activities against CIS Control 17 safeguards and provide:
1. Detailed compliance assessment for each safeguard
2. Identification of violations and gaps
3. Severity rating for each violation
4. Specific remediation actions

CIS Control 17 Safeguards:
{cis_safeguards}

Evaluation Criteria:
- STRICT enforcement: Any deviation from requirements is a violation
- Evidence-based: Decisions must be backed by timeline evidence
- SLA violations are CRITICAL compliance failures
- Missing documentation is a MAJOR violation

Output your analysis as JSON with this structure:
{{
  "safeguard_compliance": [
    {{
      "safeguard_id": "17.1",
      "compliant": true/false,
      "evidence": ["list of supporting evidence"],
      "violations": ["list of specific violations"],
      "severity": "critical"/"high"/"medium"/"low"/"none",
      "remediation": "specific actions needed"
    }}
  ],
  "critical_findings": ["list of critical issues"],
  "compliance_score_pct": 0-100
}}"""
        
        human_template = """Analyze this incident response for CIS Control 17 compliance:

PLAYBOOK STEPS ({num_steps} total):
{playbook_summary}

ADHERENCE RESULTS:
{adherence_summary}

TIMING ANALYSIS (SLA Compliance):
{timing_summary}

INCIDENT TIMELINE ({num_events} events):
{timeline_summary}

Perform a STRICT compliance analysis. Identify ALL violations, even minor ones."""
        
        # Prepare data summaries
        playbook_summary = "\n".join([
            f"- {s.get('id')}: {s.get('title')} [Phase: {s.get('phase')}]"
            for s in playbook_steps[:10]  # Limit to first 10
        ])
        
        adherence_summary = "\n".join([
            f"- {a.get('step_id')}: {a.get('adherence_level')} - {len(a.get('gaps', []))} gaps"
            for a in adherence_checks[:10]
        ])
        
        timing_summary = "\n".join([
            f"- {t.get('step_title')}: {'VIOLATED' if t.get('sla_status') == 'violated' else 'OK'} "
            f"(Expected: {t.get('expected_sla_minutes')}min, Actual: {t.get('time_from_incident_start_minutes')}min)"
            for t in timing_results if t.get('evidence_found')
        ][:10])
        
        timeline_summary = "\n".join([
            f"[{e['timestamp'].strftime('%H:%M')}] {e['source']}: {e.get('action', '')[:60]}"
            for e in timeline[:15]  # First 15 events
        ])
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        
        # Create chain
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser
        
        try:
            # Invoke chain
            result = await chain.ainvoke({
                "cis_safeguards": json.dumps(cis_safeguards, indent=2),
                "num_steps": len(playbook_steps),
                "playbook_summary": playbook_summary,
                "adherence_summary": adherence_summary,
                "timing_summary": timing_summary if timing_summary else "No timing data available",
                "num_events": len(timeline),
                "timeline_summary": timeline_summary
            })
            
            return result
            
        except Exception as e:
            print(f"[CISComplianceAgent] LangChain analysis failed: {e}")
            return self._fallback_compliance_analysis(playbook_steps, adherence_checks, timing_results)
    
    def _fallback_compliance_analysis(
        self,
        playbook_steps: List[Dict[str, Any]],
        adherence_checks: List[Dict[str, Any]],
        timing_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback compliance analysis without LangChain"""
        
        safeguard_compliance = []
        critical_findings = []
        
        # Check 17.1: Incident commander assigned
        ic_evidence = any("commander" in str(s.get("title", "")).lower() or "assign" in str(s.get("title", "")).lower() for s in playbook_steps)
        safeguard_compliance.append({
            "safeguard_id": "17.1",
            "compliant": ic_evidence,
            "evidence": ["Playbook includes commander assignment step"] if ic_evidence else [],
            "violations": ["No evidence of incident commander assignment"] if not ic_evidence else [],
            "severity": "high" if not ic_evidence else "none",
            "remediation": "Assign incident commander at start of response" if not ic_evidence else ""
        })
        if not ic_evidence:
            critical_findings.append("No incident commander assigned (CIS 17.1)")
        
        # Check 17.6: Communication channels
        comm_evidence = any("slack" in str(s.get("title", "")).lower() or "channel" in str(s.get("title", "")).lower() for s in playbook_steps)
        safeguard_compliance.append({
            "safeguard_id": "17.6",
            "compliant": comm_evidence,
            "evidence": ["Communication channel step in playbook"] if comm_evidence else [],
            "violations": ["No dedicated communication channel established"] if not comm_evidence else [],
            "severity": "medium" if not comm_evidence else "none",
            "remediation": "Create dedicated incident Slack channel" if not comm_evidence else ""
        })
        
        # Check 17.8: Post-incident review
        post_mortem_evidence = any("post" in str(s.get("title", "")).lower() or "lessons" in str(s.get("title", "")).lower() for s in playbook_steps)
        safeguard_compliance.append({
            "safeguard_id": "17.8",
            "compliant": post_mortem_evidence,
            "evidence": ["Post-mortem step included"] if post_mortem_evidence else [],
            "violations": ["No post-incident review planned"] if not post_mortem_evidence else [],
            "severity": "high" if not post_mortem_evidence else "none",
            "remediation": "Schedule post-incident review within 7 days" if not post_mortem_evidence else ""
        })
        if not post_mortem_evidence:
            critical_findings.append("No post-incident review (CIS 17.8)")
        
        compliant_count = sum(1 for s in safeguard_compliance if s["compliant"])
        compliance_score = (compliant_count / len(safeguard_compliance)) * 100 if safeguard_compliance else 0
        
        return {
            "safeguard_compliance": safeguard_compliance,
            "critical_findings": critical_findings,
            "compliance_score_pct": compliance_score
        }
    
    def _calculate_overall_cis_score(self, cis_analysis: Dict[str, Any], sla_report: Dict[str, Any]) -> float:
        """Calculate overall CIS compliance score"""
        # Weight components
        safeguard_score = cis_analysis.get("compliance_score_pct", 0) * 0.6
        sla_score = sla_report.get("compliance_score", 0) * 0.4
        
        return round(safeguard_score + sla_score, 2)
    
    def _identify_strict_violations(self, cis_analysis: Dict[str, Any], sla_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify all strict violations"""
        violations = []
        
        # Add safeguard violations
        for safeguard in cis_analysis.get("safeguard_compliance", []):
            if not safeguard.get("compliant"):
                violations.append({
                    "type": "cis_safeguard",
                    "safeguard_id": safeguard.get("safeguard_id"),
                    "severity": safeguard.get("severity"),
                    "description": f"CIS {safeguard.get('safeguard_id')} violation: {', '.join(safeguard.get('violations', []))}"
                })
        
        # Add SLA violations
        for violation in sla_report.get("violations_by_step", []):
            violations.append({
                "type": "sla_violation",
                "step": violation.get("step_title"),
                "severity": violation.get("severity"),
                "description": f"SLA violated: {violation.get('step_title')} took {violation.get('actual_minutes')}min (expected {violation.get('expected_minutes')}min)"
            })
        
        return violations
    
    def _generate_cis_recommendations(self, cis_analysis: Dict[str, Any], sla_report: Dict[str, Any]) -> List[str]:
        """Generate specific CIS-based recommendations"""
        recommendations = []
        
        # Add remediation from safeguards
        for safeguard in cis_analysis.get("safeguard_compliance", []):
            if safeguard.get("remediation"):
                recommendations.append(f"[CIS {safeguard.get('safeguard_id')}] {safeguard.get('remediation')}")
        
        # Add SLA recommendations
        if sla_report.get("critical_violations", 0) > 0:
            recommendations.append(f"CRITICAL: {sla_report['critical_violations']} steps exceeded SLA by >100%. Implement automation to reduce response time.")
        
        if sla_report.get("total_violations", 0) > 0:
            recommendations.append(f"Review and optimize workflow for {sla_report['total_violations']} steps that violated SLAs")
        
        # Add critical findings
        for finding in cis_analysis.get("critical_findings", []):
            recommendations.append(f"CRITICAL: {finding}")
        
        return recommendations if recommendations else ["No critical violations found - maintain current controls"]
