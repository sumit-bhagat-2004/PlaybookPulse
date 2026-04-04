"""GitHub PR Generator Service"""
from typing import Dict, Any, Optional

from app.config import settings
from app.utils.logger import logger


class PRGenerator:
    """Service for creating GitHub pull requests"""
    
    def __init__(self):
        self.client = None
        if settings.github_token:
            try:
                from github import Github
                self.client = Github(settings.github_token)
            except ImportError:
                logger.warning("PyGithub not installed - PR generation disabled")
        else:
            logger.warning("GitHub token not configured - PR generation disabled")
    
    async def create_playbook_update_pr(
        self,
        repo_full_name: str,
        analysis_data: Dict[str, Any],
        branch_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a PR with playbook updates based on analysis findings
        
        Args:
            repo_full_name: Repository (org/repo)
            analysis_data: Analysis results
            branch_name: Branch name (auto-generated if not provided)
            
        Returns:
            PR information or None if failed
        """
        if not self.client:
            logger.error("GitHub client not initialized")
            return None
        
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Generate branch name
            if not branch_name:
                analysis_id = analysis_data.get("analysis_id", "unknown")
                branch_name = f"playbook-updates-{analysis_id}"
            
            # Create PR title and body
            title = f"Playbook Updates Based on Analysis {analysis_data.get('analysis_id')}"
            
            body = self._generate_pr_body(analysis_data)
            
            # Note: Actual file changes would require more complex logic
            # This is a placeholder for the PR creation flow
            
            logger.info(f"Would create PR in {repo_full_name}: {title}")
            
            return {
                "repository": repo_full_name,
                "branch": branch_name,
                "title": title,
                "body": body,
                "status": "draft"
            }
            
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def _generate_pr_body(self, analysis_data: Dict[str, Any]) -> str:
        """Generate PR description from analysis"""
        result = analysis_data.get("result", {})
        
        body_parts = [
            "## Analysis Summary",
            f"**Analysis ID:** {analysis_data.get('analysis_id')}",
            f"**Overall Score:** {result.get('overall_score', 0)}%",
            "",
            "## Recommended Updates",
            ""
        ]
        
        adherence_checks = result.get("adherence_checks", [])
        for check in adherence_checks:
            if check.get("recommendations"):
                body_parts.append(f"### {check.get('step_id')}")
                for rec in check.get("recommendations", []):
                    body_parts.append(f"- {rec}")
                body_parts.append("")
        
        return "\n".join(body_parts)
