from typing import AsyncGenerator
from app.config import get_settings, Settings


async def get_config() -> Settings:
    """FastAPI dependency for configuration"""
    return get_settings()


# Add more dependencies as needed
async def get_current_user():
    """Placeholder for authentication dependency"""
    # TODO: Implement authentication
    return {"user_id": "demo_user"}
