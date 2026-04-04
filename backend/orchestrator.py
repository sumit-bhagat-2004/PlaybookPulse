"""
Orchestrator: Connects Slack → Gemini → GitHub → Slack

This module coordinates the full incident analysis pipeline:
1. Accept /playbookpulse command from Slack with repo name
2. Load incident data (from fixtures for now, live APIs later)
3. Send to Gemini AI for compliance analysis
4. Generate improved playbook based on gaps
5. Create GitHub PR with improvements
6. Notify user in Slack with PR link

STATUS: ⏳ TODO - Not yet integrated with Slack app
"""

import json
from typing import List, Dict, Any
from datetime import datetime

from google import genai
from data_loader import load_playbook, load_slack_thread
from github_integration import open_playbook_pr
from config import settings


class ComplianceOrchestrator:
    """Orchestrates incident analysis and remediation."""

    def __init__(self):
        self.gemini_client = None
        if settings.has_gemini_credentials:
            self.gemini_client = genai.Client(api_key=settings.google_api_key)

    def analyze_incident(self, repo_name: str) -> Dict[str, Any]:
        """
        Main orchestration method: Analyze incident and create PR.

        Args:
            repo_name: GitHub repository (e.g., "username/playbookpulse-demo")

        Returns:
            Dict with analysis results and PR URL
        """
        if not self.gemini_client:
            raise ValueError("Gemini API not configured. Add GOOGLE_API_KEY to .env")

        # Step 1: Load incident data
        print(f"[ORCHESTRATOR] Loading incident data...")
        playbook = load_playbook()
        slack_thread = load_slack_thread()

        # Step 2: Prepare incident summary for Gemini
        incident_summary = self._format_incident_for_analysis(playbook, slack_thread)

        # Step 3: Send to Gemini for analysis
        print(f"[ORCHESTRATOR] Sending to Gemini for compliance analysis...")
        analysis = self._gemini_analyze_compliance(incident_summary)

        # Step 4: Generate improved playbook
        print(f"[ORCHESTRATOR] Generating improved playbook...")
        improved_playbook = self._gemini_generate_improvements(playbook, analysis)

        # Step 5: Create GitHub PR
        print(f"[ORCHESTRATOR] Creating GitHub PR...")
        pr_url = self._create_remediation_pr(repo_name, improved_playbook, analysis)

        return {
            "status": "success",
            "analysis": analysis,
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat(),
        }

    def _format_incident_for_analysis(
        self, playbook: str, slack_thread: List[Any]
    ) -> str:
        """Format incident data into a prompt for Gemini."""
        # Convert slack thread to readable format
        slack_summary = "\n".join(
            [
                f"[{msg.timestamp.strftime('%H:%M')}] {msg.user}: {msg.text}"
                for msg in slack_thread
            ]
        )

        return f"""
# Incident Analysis Request

## Playbook
{playbook}

## Incident Timeline (from Slack)
{slack_summary}

## Analysis Task
1. Identify which playbook steps were followed vs missed
2. For steps that were followed, how close to the SLA?
3. List compliance frameworks that may have been violated
4. Suggest improvements to prevent similar gaps

Format your response as JSON:
{{
  "steps_followed": ["step 1", "step 2"],
  "steps_missed": ["step 6"],
  "timeline_gaps": [{{"step": "Rotate Credentials", "expected_min": 30, "actual_min": 120}}],
  "compliance_violations": ["SOC 2 CC7.3", "NIST SP 800-61 §3.3.1"],
  "improvement_suggestions": ["..."]
}}
"""

    def _gemini_analyze_compliance(self, incident_summary: str) -> Dict[str, Any]:
        """Send incident to Gemini for compliance analysis."""
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=incident_summary,
            )

            # Parse JSON response
            response_text = response.text.strip()

            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                # Simple heuristic: find first { and last }
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
            else:
                json_str = "{}"

            analysis = json.loads(json_str)
            return analysis

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "raw_analysis": response_text,
                "error": "Could not parse JSON from Gemini response",
            }
        except Exception as e:
            raise RuntimeError(f"Gemini analysis failed: {str(e)}")

    def _gemini_generate_improvements(
        self, playbook: str, analysis: Dict[str, Any]
    ) -> str:
        """Generate improved playbook based on gaps found."""
        improvements_prompt = f"""
Based on this compliance analysis:
{json.dumps(analysis, indent=2)}

Original Playbook:
{playbook}

Generate an IMPROVED playbook that:
1. Adds more specific SLA timelines
2. Includes explicit compliance framework references
3. Adds a step for Legal/Compliance notification if missing
4. Improves step clarity and detail
5. Adds checkpoints for validation

Output ONLY the improved markdown playbook, no other text.
"""

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=improvements_prompt,
        )

        return response.text.strip()

    def _create_remediation_pr(
        self, repo_name: str, improved_playbook: str, analysis: Dict[str, Any]
    ) -> str:
        """Create GitHub PR with improved playbook."""
        branch_name = f"fix-compliance-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Build PR description from analysis
        pr_body = self._build_pr_description(analysis)

        pr_url = open_playbook_pr(
            repo_name=repo_name,
            branch_name=branch_name,
            file_path="incident_response.md",
            new_content=improved_playbook,
            pr_title="🔒 Compliance Gap Fixes (Auto-Generated by PlaybookPulse)",
            pr_body=pr_body,
        )

        return pr_url

    def _build_pr_description(self, analysis: Dict[str, Any]) -> str:
        """Build GitHub PR description from analysis."""
        sections = ["# PlaybookPulse Compliance Analysis\n"]

        if "steps_missed" in analysis:
            sections.append(f"## Missed Steps\n{analysis['steps_missed']}\n")

        if "timeline_gaps" in analysis:
            sections.append("## Timeline Violations\n")
            for gap in analysis["timeline_gaps"]:
                sections.append(
                    f"- **{gap.get('step', 'Unknown')}**: "
                    f"Expected {gap.get('expected_min', '?')} min, "
                    f"took {gap.get('actual_min', '?')} min\n"
                )

        if "compliance_violations" in analysis:
            sections.append(
                f"## Compliance Frameworks Affected\n"
                f"{', '.join(analysis['compliance_violations'])}\n"
            )

        sections.append(
            "\n---\n_Generated by PlaybookPulse AI Orchestrator_ 🤖"
        )

        return "".join(sections)


# Entry point for Slack command
async def handle_playbookpulse_command(repo_name: str) -> Dict[str, Any]:
    """
    Slack command handler that triggers full analysis.

    This should be called from backend/slack_app.py when user runs:
        /playbookpulse username/repo

    Args:
        repo_name: GitHub repository name (e.g., "username/playbookpulse-demo")

    Returns:
        Result dict with PR URL and analysis
    """
    try:
        orchestrator = ComplianceOrchestrator()
        result = orchestrator.analyze_incident(repo_name)
        return {
            "status": "success",
            "message": f"✅ Analysis complete! PR created: {result['pr_url']}",
            "pr_url": result["pr_url"],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Analysis failed: {str(e)}",
            "error": str(e),
        }


# Example usage:
if __name__ == "__main__":
    # For testing locally
    import asyncio

    result = asyncio.run(
        handle_playbookpulse_command("username/playbookpulse-test")
    )
    print(json.dumps(result, indent=2))
