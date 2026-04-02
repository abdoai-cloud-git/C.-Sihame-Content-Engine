from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PostStatus(str, Enum):
    DRAFT_GENERATED = "draft_generated"
    UNDER_REVIEW = "under_review"
    APPROVED_TEXT = "approved_text"


class TextModel(str, Enum):
    GEMINI_3_1_PRO = "gemini-3.1-pro"
    CLAUDE_SONNET_4_6 = "claude-sonnet-4-6"
    GEMINI_3_FLASH = "gemini-3-flash"


class VoiceRoute(str, Enum):
    SOUL_2023 = "soul_2023"
    METHODOLOGY = "methodology"
    HYBRID = "hybrid"
    RITUAL = "ritual"


class GenerateDraftRequest(BaseModel):
    raw_input: str = Field(..., min_length=1, description="The raw voice note or text from Coach Sihame")
    post_type: str = Field(default="Reflection", description="The intended post type")
    platform: str = Field(default="general", description="Target platform (telegram vs instagram vs general)")


class DraftContent(BaseModel):
    angle: str = Field(..., description="The deep psychological or somatic angle behind this post")
    hook: str = Field(..., description="The opening 1-2 lines that ground the reader safely")
    body: str = Field(..., description="The main content")
    cta: str = Field(..., description="The call to action")
    safety_flags: str = Field(default="", description="Warnings if the raw input required safety adjustments")


class DraftGenerationResult(DraftContent):
    model_used: TextModel = Field(..., description="Which text model produced this structured output")


class RoutingMetadata(BaseModel):
    voice_route: VoiceRoute
    injected_files: List[str] = Field(default_factory=list)
    example_files: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class ContextAssembly(BaseModel):
    prompt: str
    routing_metadata: RoutingMetadata


class RevisionEntry(BaseModel):
    instruction: str
    before_body: str
    after_body: str
    model_used: TextModel
    created_at: datetime


class StoredDraft(BaseModel):
    draft_id: str
    raw_input: str
    post_type: str
    platform: str
    status: PostStatus
    model_used: TextModel
    angle: str
    hook: str
    body: str
    cta: str
    safety_flags: str = ""
    approved_text: Optional[str] = None
    revision_history: List[RevisionEntry] = Field(default_factory=list)
    routing_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class PostDraftResponse(DraftContent):
    draft_id: str
    status: PostStatus
    model_used: TextModel


class ReviseDraftRequest(BaseModel):
    draft_id: str = Field(..., description="The previously generated draft id")
    edit_instruction: str = Field(..., min_length=1, description="For example: Make it shorter")


class ReviseDraftResponse(PostDraftResponse):
    revisions_count: int


class ApproveTextRequest(BaseModel):
    draft_id: str = Field(..., description="The draft id being approved")
    approved_text: str = Field(..., min_length=1, description="The final approved text after human review")


class ApproveTextResponse(BaseModel):
    draft_id: str
    status: PostStatus
    approved_text: str
    model_used: TextModel


class AdaptPlatformRequest(BaseModel):
    draft_id: str = Field(..., description="The approved draft id being adapted")
    target_platforms: List[str] = Field(..., description="The platforms to adapt the content for (e.g., instagram, telegram, facebook, tiktok)")


class AdaptPlatformResponse(BaseModel):
    draft_id: str
    results: Dict[str, str] = Field(..., description="Dictionary mapping platform name to adapted text")
    model_used: TextModel


class HistoryItemResponse(BaseModel):
    draft_id: str
    title: str
    post_type: str
    status: str
    updated_at: datetime


class HistoryListResponse(BaseModel):
    items: List[HistoryItemResponse]


class DraftRecordResponse(PostDraftResponse):
    raw_input: str
    post_type: str
    platform: str
    approved_text: Optional[str] = None
    revision_history: List[RevisionEntry] = Field(default_factory=list)
    routing_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
