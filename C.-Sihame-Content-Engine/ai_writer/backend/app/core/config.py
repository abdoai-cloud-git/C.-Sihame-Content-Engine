import json
import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Coach Sihame AI Content Engine"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8080

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://c-sihame-content-engine.vercel.app",
        ]
    )

    # Kie.ai
    KIE_API_KEY: str = os.getenv("KIE_API_KEY", "")
    KIE_BASE_URL: str = "https://api.kie.ai"
    KIE_IMAGE_API_URL: str = "https://api.kie.ai/api/v1/jobs/createTask"
    KIE_TASK_STATUS_URL: str = "https://api.kie.ai/api/v1/jobs/recordInfo"

    # PRD-aligned text model roles
    MODEL_PRIMARY: str = "gemini-3.1-pro"
    MODEL_SECONDARY: str = "claude-sonnet-4-6"
    MODEL_EDITOR: str = "gemini-3-flash"

    # Persistence
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "memory")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_DRAFTS_TABLE: str = os.getenv("SUPABASE_DRAFTS_TABLE", "content_drafts")

    # Runtime content paths
    PROJECT_ROOT: str = str(Path(__file__).resolve().parents[3])
    KNOWLEDGE_PACK_DIR: str = str(
        Path(
            os.getenv(
                "KNOWLEDGE_PACK_DIR",
                str(Path(__file__).resolve().parents[3] / "knowledge_pack"),
            )
        )
    )
    FEEDBACK_LOG_PATH: str = str(
        Path(
            os.getenv(
                "FEEDBACK_LOG_PATH",
                str(Path(__file__).resolve().parents[3] / "feedback_log.md"),
            )
        )
    )
    DESIGNER_PACK_DIR: str = str(
        Path(
            os.getenv(
                "DESIGNER_PACK_DIR",
                str(Path(__file__).resolve().parents[3] / "c.siham-designer-main" / "coach-siham-graphics-designer"),
            )
        )
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                return [str(origin).strip() for origin in json.loads(raw) if str(origin).strip()]
            return [origin.strip() for origin in raw.split(",") if origin.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        raise ValueError("CORS_ORIGINS must be a list or a comma-separated string.")

    @property
    def KIE_GEMINI_PRO_BASE_URL(self) -> str:
        return f"{self.KIE_BASE_URL}/gemini-3.1-pro/v1"

    @property
    def KIE_GEMINI_FLASH_BASE_URL(self) -> str:
        return f"{self.KIE_BASE_URL}/gemini-3-flash/v1"

    @property
    def KIE_CLAUDE_MESSAGES_URL(self) -> str:
        return f"{self.KIE_BASE_URL}/claude/v1/messages"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"


settings = Settings()
