"""Health check endpoints"""
from fastapi import APIRouter
from app.config import settings
from app.services.analysis_service import get_metrics

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "playbook-pulse-agents",
        "version": settings.api_version,
        "environment": settings.environment,
        "anthropic_configured": bool(settings.anthropic_api_key),
        "gemini_configured": bool(settings.gemini_api_key),
        "slack_configured": bool(settings.slack_bot_token),
        "jira_configured": bool(settings.jira_url and settings.jira_api_token),
        "github_configured": bool(settings.github_token)
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/metrics")
async def get_analysis_metrics():
    """Get analysis metrics and statistics"""
    return {
        "status": "ok",
        "metrics": get_metrics()
    }
