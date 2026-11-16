import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Veloxa CXO Cockpit"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./veloxa.db"
    
    # Strict privacy rules: No individual salary disclosure to CEO
    STRICT_SALARY_PRIVACY: bool = True
    
    # Default release cutoff: Day 1 (2026-11-16 10:00:00 IST)
    DEFAULT_AS_OF_RELEASE_DAY: str = "Day1"
    DEFAULT_AS_OF_TIMESTAMP: str = "2026-11-16T10:00:00+05:30"
    
    # Optional LLM API Key (Mock deterministic fallback is default)
    GEMINI_API_KEY: str = ""
    USE_MOCK_LLM_FALLBACK: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
