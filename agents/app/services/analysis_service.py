"""Analysis Service - Orchestrates the multi-agent analysis workflow"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import time

from app.agents.orchestrator import OrchestratorAgent
from app.models.schemas import AnalysisRequest, AnalysisStatus
from app.utils.logger import logger
from app.utils.helpers import generate_id
from app.utils.log_handler import set_analysis_context, clear_analysis_context
from app.config import settings


# Module-level shared state (replace with database in production)
_analyses_store: Dict[str, Dict] = {}

# Module-level metrics tracking
_metrics = {
    "analyses_started": 0,
    "analyses_completed": 0,
    "analyses_failed": 0,
    "analyses_timed_out": 0,
    "total_analysis_time": 0.0,
    "last_analysis_time": 0.0
}


class AnalysisService:
    """Service for managing analysis workflows"""

    def __init__(self):
        self.orchestrator = OrchestratorAgent()

    async def start_analysis(self, request: AnalysisRequest) -> str:
        """
        Initiate a new analysis

        Args:
            request: Analysis request

        Returns:
            Analysis ID
        """
        analysis_id = generate_id(prefix="analysis")

        # Store initial analysis state
        _analyses_store[analysis_id] = {
            "analysis_id": analysis_id,
            "status": AnalysisStatus.PENDING,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "request": request.dict()
        }

        logger.info(f"Analysis {analysis_id} created")
        return analysis_id

    async def run_analysis(
        self,
        analysis_id: str,
        request: AnalysisRequest
    ):
        """
        Run the analysis workflow

        This is typically called as a background task
        """
        try:
            logger.info(f"Starting analysis workflow for {analysis_id}")

            # Update status
            _analyses_store[analysis_id]["status"] = AnalysisStatus.IN_PROGRESS
            _analyses_store[analysis_id]["updated_at"] = datetime.utcnow().isoformat()

            # Prepare input for orchestrator
            orchestrator_input = {
                "playbook_content": request.playbook_content,
                "slack_thread_id": request.slack_thread_id,
                "jira_ticket_id": request.jira_ticket_id,
                "github_repo": request.github_repo,
                "compliance_frameworks": [f.value for f in request.compliance_frameworks]
            }

            # Run orchestrator
            result = await self.orchestrator.process(orchestrator_input)

            if result["success"]:
                # Store complete results
                _analyses_store[analysis_id].update({
                    "status": AnalysisStatus.COMPLETED,
                    "result": result["data"],
                    "completed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                })
                logger.info(f"Analysis {analysis_id} completed successfully")
            else:
                # Store failure
                _analyses_store[analysis_id].update({
                    "status": AnalysisStatus.FAILED,
                    "error": result.get("error"),
                    "updated_at": datetime.utcnow().isoformat()
                })
                logger.error(f"Analysis {analysis_id} failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed with exception: {e}")
            _analyses_store[analysis_id].update({
                "status": AnalysisStatus.FAILED,
                "error": str(e),
                "updated_at": datetime.utcnow().isoformat()
            })

    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by ID"""
        return _analyses_store.get(analysis_id)

    async def list_analyses(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all analyses with pagination"""
        all_analyses = list(_analyses_store.values())

        # Sort by created_at descending
        all_analyses.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        return all_analyses[offset:offset + limit]

    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis"""
        if analysis_id in _analyses_store:
            del _analyses_store[analysis_id]
            logger.info(f"Analysis {analysis_id} deleted")
            return True
        return False


async def run_analysis_task(
    analysis_id: str,
    request: AnalysisRequest,
    ws_manager=None
):
    """
    Module-level function to run analysis workflow in background tasks.
    This operates on the shared _analyses_store state.

    Args:
        analysis_id: ID of the analysis to run
        request: Analysis request parameters
        ws_manager: Optional WebSocketManager for real-time updates
    """
    # Set logging context for this analysis
    set_analysis_context(analysis_id)

    orchestrator = OrchestratorAgent()
    start_time = time.time()

    # Track metrics
    _metrics["analyses_started"] += 1

    try:
        logger.info(f"Starting analysis workflow for {analysis_id}")

        # Update status
        _analyses_store[analysis_id]["status"] = AnalysisStatus.IN_PROGRESS
        _analyses_store[analysis_id]["updated_at"] = datetime.utcnow().isoformat()
        _analyses_store[analysis_id]["start_time"] = start_time

        # Send initial progress update
        if ws_manager:
            await ws_manager.send_analysis_update(
                analysis_id, "in_progress", 10, "Analysis started"
            )

        # Wrap analysis in timeout
        try:
            async with asyncio.timeout(settings.analysis_timeout):
                # Prepare input for orchestrator
                orchestrator_input = {
                    "playbook_content": request.playbook_content,
                    "slack_thread_id": request.slack_thread_id,
                    "jira_ticket_id": request.jira_ticket_id,
                    "github_repo": request.github_repo,
                    "compliance_frameworks": [f.value for f in request.compliance_frameworks]
                }

                # Send progress: playbook parsing
                if ws_manager:
                    await ws_manager.send_analysis_update(
                        analysis_id, "in_progress", 25, "Parsing playbook"
                    )

                # Run orchestrator
                result = await orchestrator.process(orchestrator_input)

                # Send progress: analysis complete
                if ws_manager:
                    await ws_manager.send_analysis_update(
                        analysis_id, "in_progress", 90, "Finalizing results"
                    )

                if result["success"]:
                    # Store complete results
                    duration = time.time() - start_time

                    # Extract slack_messages and slack_thread_id from result
                    slack_data = result["data"].get("incident_data", {})
                    slack_messages = []
                    slack_thread_id = request.slack_thread_id or ""

                    # Parse slack messages from incident data
                    if "slack_timeline" in slack_data:
                        slack_messages = slack_data.get("slack_timeline", [])

                    _analyses_store[analysis_id].update({
                        "status": AnalysisStatus.COMPLETED,
                        "result": result["data"],
                        "slack_thread_id": slack_thread_id,
                        "slack_messages": slack_messages,
                        "completed_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "duration_seconds": round(duration, 2)
                    })

                    # Update metrics
                    _metrics["analyses_completed"] += 1
                    _metrics["total_analysis_time"] += duration
                    _metrics["last_analysis_time"] = duration

                    logger.info(f"✅ Analysis {analysis_id} completed in {duration:.2f}s")

                    # Send completion notification
                    if ws_manager:
                        await ws_manager.send_analysis_update(
                            analysis_id, "completed", 100, "Analysis completed successfully"
                        )
                else:
                    # Store failure
                    duration = time.time() - start_time
                    _analyses_store[analysis_id].update({
                        "status": AnalysisStatus.FAILED,
                        "error": result.get("error"),
                        "updated_at": datetime.utcnow().isoformat(),
                        "duration_seconds": round(duration, 2)
                    })

                    # Update metrics
                    _metrics["analyses_failed"] += 1
                    _metrics["last_analysis_time"] = duration

                    logger.error(f"❌ Analysis {analysis_id} failed after {duration:.2f}s: {result.get('error')}")

                    # Send failure notification
                    if ws_manager:
                        await ws_manager.send_analysis_update(
                            analysis_id, "failed", 0, f"Analysis failed: {result.get('error')}"
                        )

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.error(f"⏱️  Analysis {analysis_id} timed out after {settings.analysis_timeout}s")
            _analyses_store[analysis_id].update({
                "status": AnalysisStatus.FAILED,
                "error": f"Analysis timed out after {settings.analysis_timeout} seconds",
                "updated_at": datetime.utcnow().isoformat(),
                "duration_seconds": round(duration, 2)
            })

            # Update metrics
            _metrics["analyses_timed_out"] += 1
            _metrics["analyses_failed"] += 1
            _metrics["last_analysis_time"] = duration

            # Send timeout notification
            if ws_manager:
                await ws_manager.send_analysis_update(
                    analysis_id, "failed", 0, f"Analysis timed out after {settings.analysis_timeout}s"
                )

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ Analysis {analysis_id} failed with exception after {duration:.2f}s: {e}")
        _analyses_store[analysis_id].update({
            "status": AnalysisStatus.FAILED,
            "error": str(e),
            "updated_at": datetime.utcnow().isoformat(),
            "duration_seconds": round(duration, 2)
        })

        # Update metrics
        _metrics["analyses_failed"] += 1
        _metrics["last_analysis_time"] = duration

        # Send error notification
        if ws_manager:
            await ws_manager.send_analysis_update(
                analysis_id, "failed", 0, f"Error: {str(e)}"
            )

    finally:
        # Clear logging context
        clear_analysis_context()


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis by ID (module-level function for use in WebSocket endpoint)"""
    return _analyses_store.get(analysis_id)


def get_metrics() -> Dict[str, Any]:
    """Get current analysis metrics"""
    total_completed = _metrics["analyses_completed"]
    avg_time = (_metrics["total_analysis_time"] / total_completed) if total_completed > 0 else 0

    return {
        "analyses_started": _metrics["analyses_started"],
        "analyses_completed": _metrics["analyses_completed"],
        "analyses_failed": _metrics["analyses_failed"],
        "analyses_timed_out": _metrics["analyses_timed_out"],
        "success_rate": round(
            (_metrics["analyses_completed"] / _metrics["analyses_started"] * 100)
            if _metrics["analyses_started"] > 0 else 0,
            2
        ),
        "average_duration_seconds": round(avg_time, 2),
        "last_analysis_duration_seconds": round(_metrics["last_analysis_time"], 2),
        "active_analyses": len([
            a for a in _analyses_store.values()
            if a.get("status") == AnalysisStatus.IN_PROGRESS
        ])
    }

