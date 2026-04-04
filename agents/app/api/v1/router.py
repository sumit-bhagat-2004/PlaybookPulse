"""Main API router - combines all v1 endpoints"""
from fastapi import APIRouter

from app.api.v1 import health, analysis, websocket

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(
    health.router,
    tags=["health"]
)

api_router.include_router(
    analysis.router,
    tags=["analysis"]
)

api_router.include_router(
    websocket.router,
    tags=["websocket"]
)
