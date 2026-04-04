import os
from typing import Literal
from dotenv import load_dotenv

# Only load .env if not in test mode
if not os.getenv("PYTEST_CURRENT_TEST"):
    load_dotenv()

class Settings:
    """Centralized configuration management for PlaybookPulse"""
    
    def __init__(self):
        # Reload values from environment on initialization
        # This allows tests to override with monkeypatch
        self.ENVIRONMENT: Literal["development", "production"] = os.getenv("ENVIRONMENT", "development")
        self.SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
        self.SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
        self.GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
        self.SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
        self.SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    @property
    def has_slack_credentials(self) -> bool:
        """Check if Slack credentials are configured"""
        return bool(self.SLACK_BOT_TOKEN and self.SLACK_SIGNING_SECRET)
    
    @property
    def has_github_credentials(self) -> bool:
        """Check if GitHub credentials are configured"""
        return bool(self.GITHUB_TOKEN)
    
    @property
    def has_gemini_credentials(self) -> bool:
        """Check if Gemini API key is configured"""
        return bool(self.GOOGLE_API_KEY)
    
    def validate_production(self) -> None:
        """Validate that all required production credentials are present"""
        if self.is_production:
            missing = []
            if not self.SLACK_BOT_TOKEN:
                missing.append("SLACK_BOT_TOKEN")
            if not self.SLACK_SIGNING_SECRET:
                missing.append("SLACK_SIGNING_SECRET")
            
            if missing:
                raise ValueError(
                    f"Production environment requires these variables: {', '.join(missing)}\n"
                    f"Please set them in your .env file or environment."
                )

# Global settings instance
settings = Settings()
