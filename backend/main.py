from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from slack_app import slack_handler
from config import settings
from agents_bridge import AgentsBridge, run_quick_analysis
from data_loader import load_playbook
from pathlib import Path
import asyncio

app = FastAPI(
    title="PlaybookPulse Integration API",
    description="AI-powered incident response compliance auditing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents bridge
agents_bridge = AgentsBridge()


# Request/Response models
class AnalysisRequest(BaseModel):
    playbook_content: Optional[str] = None
    use_sample_playbook: bool = False
    compliance_frameworks: List[str] = ["nist_sp_800_61"]
    slack_thread_data: Optional[dict] = None
    jira_ticket_data: Optional[dict] = None
    github_events: Optional[list] = None


class AnalysisResponse(BaseModel):
    status: str
    timestamp: Optional[str] = None
    playbook: Optional[dict] = None
    adherence: Optional[dict] = None
    compliance: Optional[dict] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None


@app.get("/")
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
            "analyze": "/analyze",
            "playbooks": "/playbooks",
            "docs": "/docs"
        }
    }


@app.post("/slack/events")
async def slack_events(request: Request):
    # Route all incoming POST traffic on this endpoint to the Slack Bolt app
    return await slack_handler.handle(request)


@app.get("/health")
async def health_check():
    return {
        "status": "Integration layer is live.",
        "environment": settings.ENVIRONMENT,
        "agents_available": agents_bridge.use_direct,
        "integrations": {
            "slack": settings.has_slack_credentials,
            "github": settings.has_github_credentials,
            "gemini": settings.has_gemini_credentials
        }
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_incident(request: AnalysisRequest):
    """
    Run incident response compliance analysis using multi-agent system.

    This endpoint triggers the full analysis pipeline:
    1. Playbook Parser - Extracts structured steps from playbook
    2. Incident Trail - Collects incident data from integrations
    3. Adherence Checker - Compares actual vs expected actions
    4. Compliance Mapper - Maps findings to compliance frameworks
    """
    try:
        # Determine playbook content
        if request.use_sample_playbook or not request.playbook_content:
            playbook_path = Path(__file__).parent / "fixtures" / "playbook_comprehensive.md"
            if playbook_path.exists():
                with open(playbook_path) as f:
                    playbook_content = f.read()
            else:
                playbook_content = load_playbook()
        else:
            playbook_content = request.playbook_content

        # Run analysis
        result = await agents_bridge.analyze_incident(
            playbook_content=playbook_content,
            slack_thread_data=request.slack_thread_data,
            jira_ticket_data=request.jira_ticket_data,
            github_events=request.github_events,
            compliance_frameworks=request.compliance_frameworks
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))

        return AnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/playbooks")
async def list_playbooks():
    """List available sample playbooks"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    playbooks = []

    for f in fixtures_dir.glob("*.md"):
        with open(f) as file:
            content = file.read()
            # Extract title from first heading
            title = f.stem
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

        playbooks.append({
            "id": f.stem,
            "title": title,
            "filename": f.name,
            "size_bytes": f.stat().st_size
        })

    return {"playbooks": playbooks}


@app.get("/playbooks/{playbook_id}")
async def get_playbook(playbook_id: str):
    """Get a specific playbook by ID"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    playbook_path = fixtures_dir / f"{playbook_id}.md"

    if not playbook_path.exists():
        raise HTTPException(status_code=404, detail="Playbook not found")

    with open(playbook_path) as f:
        content = f.read()

    return {
        "id": playbook_id,
        "filename": playbook_path.name,
        "content": content
    }
