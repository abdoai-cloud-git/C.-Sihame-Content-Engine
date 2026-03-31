import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Coach Sihame AI Content Engine"
    API_V1_STR: str = "/api/v1"

    # Kie.ai
    KIE_API_KEY: str = os.getenv("KIE_API_KEY", "")
    KIE_BASE_URL: str = "https://api.kie.ai"

    # PRD-aligned text model roles
    MODEL_PRIMARY: str = "gemini-3.1-pro"
    MODEL_SECONDARY: str = "claude-sonnet-4-6"
    MODEL_EDITOR: str = "gemini-3-flash"

    # Persistence
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "memory")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_DRAFTS_TABLE: str = os.getenv("SUPABASE_DRAFTS_TABLE", "content_drafts")

    # Knowledge Pack Location
    KNOWLEDGE_PACK_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "knowledge_pack",
    )

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
