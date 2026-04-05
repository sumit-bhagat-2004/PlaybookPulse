from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from slack_app import slack_handler
from config import settings
from agents_bridge import AgentsBridge
from data_loader import load_playbook
from pathlib import Path
import asyncio
import os

app = FastAPI(
    title="PlaybookPulse CIS Compliance API",
    description="AI-powered CIS Controls v8 compliance auditing for incident response",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents bridge with Google API key
agents_bridge = AgentsBridge(
    google_api_key=os.environ.get("GOOGLE_API_KEY") or getattr(settings, 'GOOGLE_API_KEY', None)
)


# ============ Request/Response Models ============

class PrePRRequest(BaseModel):
    """Request for pre-PR static CIS compliance check"""
    playbook_content: str
    config_files: Optional[Dict[str, str]] = None


class PostMergeRequest(BaseModel):
    """Request for post-merge dynamic CIS compliance check"""
    playbook_content: str
    slack_thread_id: Optional[str] = None
    slack_channel_id: Optional[str] = None
    jira_ticket_id: Optional[str] = None
    github_repo: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request for full incident analysis"""
    playbook_content: Optional[str] = None
    use_sample_playbook: bool = False
    slack_thread_data: Optional[dict] = None
    jira_ticket_data: Optional[dict] = None
    github_events: Optional[list] = None


class ComplianceResponse(BaseModel):
    """Response for compliance checks"""
    status: str
    phase: str
    framework: str = "CIS Controls v8"
    timestamp: Optional[str] = None
    compliance_score: Optional[float] = None
    overall_status: Optional[str] = None
    controls_checked: Optional[List[dict]] = None
    violations: Optional[List[dict]] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response for full analysis"""
    status: str
    framework: str = "CIS Controls v8"
    timestamp: Optional[str] = None
    playbook: Optional[dict] = None
    adherence: Optional[dict] = None
    cis_compliance: Optional[dict] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "PlaybookPulse",
        "version": "2.0.0",
        "framework": "CIS Controls v8 (ONLY)",
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "integrations": {
            "slack": settings.has_slack_credentials,
            "github": settings.has_github_credentials,
            "gemini": settings.has_gemini_credentials
        },
        "endpoints": {
            "health": "/health",
            "pre_pr": "/compliance/pre-pr",
            "post_merge": "/compliance/post-merge",
            "analyze": "/analyze",
            "report_pdf": "/report/{incident_id}/pdf",
            "slack_events": "/slack/events",
            "docs": "/docs"
        }
    }


# ============ CIS Compliance Endpoints ============

@app.post("/compliance/pre-pr", response_model=ComplianceResponse)
async def pre_pr_compliance_check(request: PrePRRequest):
    """
    PRE-PR Static CIS Compliance Check (Before merge)
    
    Validates playbook against CIS Controls v8 Control 17 requirements.
    Use in CI/CD pipelines to catch compliance issues before merge.
    """
    result = await agents_bridge.check_pre_pr(
        playbook_content=request.playbook_content,
        config_files=request.config_files
    )
    
    return ComplianceResponse(
        status=result.get("overall_status", "unknown"),
        phase="pre_pr",
        framework="CIS Controls v8",
        timestamp=result.get("timestamp"),
        compliance_score=result.get("compliance_score"),
        overall_status=result.get("overall_status"),
        controls_checked=result.get("controls_checked"),
        violations=result.get("blocking_issues"),
        recommendations=result.get("recommendations"),
        error=result.get("error")
    )


@app.post("/compliance/post-merge", response_model=ComplianceResponse)
async def post_merge_compliance_check(request: PostMergeRequest):
    """
    POST-MERGE Dynamic CIS Compliance Check (After merge / Live incident)
    
    Validates incident response against CIS Controls v8 using REAL data:
    - Fetches Slack thread messages from Slack API
    - Timeline and SLA validation
    - Evidence-based compliance assessment
    """
    # Fetch real Slack data if credentials available and thread provided
    slack_data = None
    if request.slack_thread_id and request.slack_channel_id and settings.has_slack_credentials:
        try:
            from slack_sdk import WebClient
            client = WebClient(token=settings.SLACK_BOT_TOKEN)
            
            result = client.conversations_replies(
                channel=request.slack_channel_id,
                ts=request.slack_thread_id
            )
            
            slack_data = {
                "messages": result.get("messages", []),
                "channel_id": request.slack_channel_id,
                "thread_ts": request.slack_thread_id
            }
            print(f"[PostMerge] Fetched {len(slack_data['messages'])} Slack messages")
            
        except Exception as e:
            print(f"[PostMerge] Failed to fetch Slack data: {e}")
    
    result = await agents_bridge.check_post_merge(
        playbook_content=request.playbook_content,
        slack_thread_data=slack_data
    )
    
    return ComplianceResponse(
        status=result.get("overall_status", "unknown"),
        phase="post_merge",
        framework="CIS Controls v8",
        timestamp=result.get("timestamp"),
        compliance_score=result.get("compliance_score"),
        overall_status=result.get("overall_status"),
        controls_checked=result.get("controls_checked"),
        violations=result.get("violations"),
        recommendations=result.get("recommendations"),
        error=result.get("error")
    )


# ============ Slack Integration ============

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
    Full CIS Controls v8 Compliance Analysis
    
    Pipeline:
    1. Playbook Parser - Extracts structured steps
    2. Incident Trail - Collects incident data
    3. Adherence Checker - Compares actual vs expected
    4. CIS Mapper - Maps to CIS Controls v8 Control 17
    5. Dynamic CIS Agent - SLA validation
    
    Framework: CIS Controls v8 ONLY
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
        
        # Load fixtures if no data provided
        import json
        slack_data = request.slack_thread_data
        jira_data = request.jira_ticket_data
        github_events = request.github_events
        
        if not slack_data and not jira_data and not github_events:
            print("[Analyze] Loading fixture data...")
            slack_path = Path(__file__).parent / "fixtures" / "slack_thread.json"
            jira_path = Path(__file__).parent / "fixtures" / "jira_ticket.json"
            
            if slack_path.exists():
                with open(slack_path) as f:
                    messages = json.load(f)
                    slack_data = {"messages": messages}
            
            if jira_path.exists():
                with open(jira_path) as f:
                    jira_data = json.load(f)

        # Run CIS-only analysis
        result = await agents_bridge.analyze_incident(
            playbook_content=playbook_content,
            slack_thread_data=slack_data,
            jira_ticket_data=jira_data,
            github_events=github_events,
            compliance_frameworks=["cis_controls_v8"]  # CIS ONLY
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))

        return AnalysisResponse(
            status=result.get("status", "unknown"),
            framework="CIS Controls v8",
            timestamp=result.get("timestamp"),
            playbook=result.get("playbook"),
            adherence=result.get("adherence"),
            cis_compliance=result.get("cis_compliance"),
            recommendations=result.get("recommendations"),
            error=result.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PDF Report Endpoints ============

# Store for analysis results (in production use Redis/DB)
ANALYSIS_STORE: Dict[str, Any] = {}


@app.post("/report/generate")
async def generate_report(request: AnalysisRequest):
    """
    Run analysis and generate PDF report
    
    Returns incident_id that can be used to download the PDF
    """
    from datetime import datetime
    from pdf_generator import generate_cis_compliance_pdf
    
    # Run analysis first
    analysis_result = await analyze_incident(request)
    
    # Generate incident ID
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Store result
    ANALYSIS_STORE[incident_id] = {
        "analysis": analysis_result.dict(),
        "timestamp": datetime.now().isoformat()
    }
    
    # Generate PDF
    try:
        pdf_path = generate_cis_compliance_pdf(
            analysis_result=analysis_result.dict(),
            incident_id=incident_id
        )
        
        return {
            "incident_id": incident_id,
            "status": "success",
            "pdf_url": f"/report/{incident_id}/pdf",
            "analysis": analysis_result
        }
    except Exception as e:
        return {
            "incident_id": incident_id,
            "status": "error",
            "error": str(e),
            "analysis": analysis_result
        }


@app.get("/report/{incident_id}/pdf")
async def download_report(incident_id: str):
    """Download generated PDF report"""
    reports_dir = Path(__file__).parent / "reports"
    
    # Look for PDF file
    for pdf_file in reports_dir.glob(f"*{incident_id}*.pdf"):
        return FileResponse(
            path=str(pdf_file),
            filename=f"PlaybookPulse_CIS_Report_{incident_id}.pdf",
            media_type="application/pdf"
        )
    
    raise HTTPException(status_code=404, detail=f"Report not found for incident {incident_id}")


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
