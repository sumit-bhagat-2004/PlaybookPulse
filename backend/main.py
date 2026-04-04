from fastapi import FastAPI, Request
from backend.slack_app import slack_handler
from backend.config import settings

api = FastAPI(
    title="PlaybookPulse Integration API",
    description="AI-powered incident response compliance auditing",
    version="1.0.0"
)

@api.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "PlaybookPulse",
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "integrations": {
            "slack": settings.has_slack_credentials,
            "github": settings.has_github_credentials,
            "gemini": settings.has_gemini_credentials
        },
        "endpoints": {
            "health": "/health",
            "slack_events": "/slack/events",
            "docs": "/docs"
        }
    }

@api.post("/slack/events")
async def slack_events(request: Request):
    # Route all incoming POST traffic on this endpoint to the Slack Bolt app
    return await slack_handler.handle(request)

@api.get("/health")
async def health_check():
    return {
        "status": "Integration layer is live.",
        "environment": settings.ENVIRONMENT,
        "integrations": {
            "slack": settings.has_slack_credentials,
            "github": settings.has_github_credentials,
            "gemini": settings.has_gemini_credentials
        }
    }
