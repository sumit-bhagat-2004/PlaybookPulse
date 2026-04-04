"""Analysis endpoints - Core API for multi-agent analysis"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, List
import asyncio
import os
from datetime import datetime

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    ReportRequest
)
from app.services.analysis_service import AnalysisService, run_analysis_task
from app.services.pdf_generator import PDFGenerator
from app.utils.logger import logger

router = APIRouter()

# Import WebSocket manager
from app.api.v1.websocket import ws_manager


@router.post("/analysis/start", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new incident response analysis
    
    This endpoint initiates the multi-agent workflow:
    1. Parse playbook
    2. Collect incident data
    3. Check adherence
    4. Map to compliance frameworks
    """
    try:
        logger.info("Received analysis request")
        
        # Create analysis service
        service = AnalysisService()
        
        # Start analysis in background
        analysis_id = await service.start_analysis(request)
        
        # Schedule background task with WebSocket updates
        background_tasks.add_task(
            run_analysis_task,
            analysis_id,
            request,
            ws_manager
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status=AnalysisStatus.PENDING,
            message="Analysis started successfully",
            result=None
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """Get analysis status and results"""
    try:
        service = AnalysisService()
        result = await service.get_analysis(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status=result.get("status", AnalysisStatus.PENDING),
            message="Analysis retrieved successfully",
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis", response_model=List[AnalysisResponse])
async def list_analyses(
    limit: int = 10,
    offset: int = 0
):
    """List all analyses"""
    try:
        service = AnalysisService()
        analyses = await service.list_analyses(limit=limit, offset=offset)
        
        return [
            AnalysisResponse(
                analysis_id=analysis.get("analysis_id"),
                status=analysis.get("status", AnalysisStatus.PENDING),
                message="",
                result=analysis
            )
            for analysis in analyses
        ]
        
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/{analysis_id}/report")
async def generate_report(
    analysis_id: str,
    report_request: ReportRequest
):
    """Generate a report for completed analysis"""
    try:
        service = AnalysisService()
        result = await service.get_analysis(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if result.get("status") != AnalysisStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Analysis not completed yet"
            )
        
        # Handle different report formats
        if report_request.format == "pdf":
            generator = PDFGenerator()
            
            # Generate PDF
            pdf_bytes = generator.generate_analysis_report(
                analysis_data=result,
                include_recommendations=report_request.include_recommendations,
                include_evidence=report_request.include_evidence
            )
            
            # Save PDF to reports directory
            os.makedirs("reports", exist_ok=True)
            filepath = f"reports/{analysis_id}.pdf"
            
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
            
            logger.info(f"Generated PDF report for {analysis_id} ({len(pdf_bytes)} bytes)")
            
            return {
                "analysis_id": analysis_id,
                "format": "pdf",
                "generated_at": datetime.utcnow().isoformat(),
                "download_url": f"/api/v1/reports/{analysis_id}.pdf",
                "size_bytes": len(pdf_bytes)
            }
        
        elif report_request.format == "json":
            # Return raw JSON data
            return {
                "analysis_id": analysis_id,
                "format": "json",
                "generated_at": datetime.utcnow().isoformat(),
                "data": result
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {report_request.format}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{filename}")
async def download_report(filename: str):
    """Download a generated report"""
    filepath = f"reports/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Security: Only allow PDF files and prevent directory traversal
    if not filename.endswith(".pdf") or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filename
    )


@router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis"""
    try:
        service = AnalysisService()
        deleted = await service.delete_analysis(analysis_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {"message": "Analysis deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
