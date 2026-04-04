import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Don't auto-parse JSON for complex types
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        json_schema_extra=None,
    )
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_title: str = Field(default="PlaybookPulse Multi-Agent Backend", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")
    api_secret_key: str = Field(default="dev-secret-key-change-in-production", alias="API_SECRET_KEY")
    
    # CORS - accept as string, property will parse it
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS"
    )
    
    # Anthropic/Claude API
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", alias="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=4096, alias="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(default=0.7, alias="ANTHROPIC_TEMPERATURE")
    
    # Google Gemini API
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")
    gemini_max_tokens: int = Field(default=8192, alias="GEMINI_MAX_TOKENS")
    
    # LLM Provider Selection (anthropic or gemini)
    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    
    # Slack Integration
    slack_bot_token: str = Field(default="", alias="SLACK_BOT_TOKEN")
    slack_app_token: str = Field(default="", alias="SLACK_APP_TOKEN")
    slack_signing_secret: str = Field(default="", alias="SLACK_SIGNING_SECRET")
    
    # Jira Integration
    jira_url: str = Field(default="", alias="JIRA_URL")
    jira_email: str = Field(default="", alias="JIRA_EMAIL")
    jira_api_token: str = Field(default="", alias="JIRA_API_TOKEN")
    
    # GitHub Integration
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_org: str = Field(default="", alias="GITHUB_ORG")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # Agent Configuration
    max_concurrent_agents: int = Field(default=5, alias="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(default=300, alias="AGENT_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    analysis_timeout: int = Field(default=300, alias="ANALYSIS_TIMEOUT")  # 5 minutes
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./playbook_pulse.db",
        alias="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(default="", alias="REDIS_URL")
    
    # WebSocket
    ws_heartbeat_interval: int = Field(default=30, alias="WS_HEARTBEAT_INTERVAL")
    ws_max_connections: int = Field(default=100, alias="WS_MAX_CONNECTIONS")
    
    @field_validator('anthropic_api_key')
    @classmethod
    def validate_anthropic_key(cls, v: str, info) -> str:
        """Validate Anthropic API key if using anthropic provider"""
        # Skip validation if empty - will check at runtime based on provider
        if not v or v.strip() == "":
            return v
        if not v.startswith('sk-ant-'):
            raise ValueError(
                f"Invalid ANTHROPIC_API_KEY format. "
                f"Expected key starting with 'sk-ant-', got '{v[:10]}...'"
            )
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.cors_origins, str):
            import json
            try:
                parsed = json.loads(self.cors_origins)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
        return self.cors_origins if isinstance(self.cors_origins, list) else []


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for getting settings"""
    return settings
