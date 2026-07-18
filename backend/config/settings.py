from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="AI Recruiter Assistant MVP")
    API_V1_STR: str = Field(default="/api/v1")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./recruiter.db")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # JWT Auth
    SECRET_KEY: str = Field(default="super_secret_key_for_development_only_12345")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 8)
    
    # OpenAI (for LangGraph)
    OPENAI_API_KEY: str = Field(default="")
    
    # NVIDIA Nemotron Fallback
    NVIDIA_API_KEY: str = Field(default="")
    
    # Third-Party Integrations (Mocked)
    ZOHO_CLIENT_ID: str = Field(default="")
    KEKA_API_KEY: str = Field(default="")
    HACKEREARTH_CLIENT_SECRET: str = Field(default="")
    AUTHBRIDGE_TOKEN: str = Field(default="")
    NAUKRI_API_KEY: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
