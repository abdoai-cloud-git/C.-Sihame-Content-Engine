from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PostStatus(str, Enum):
    DRAFT_GENERATED = "draft_generated"
    UNDER_REVIEW = "under_review"
    APPROVED_TEXT = "approved_text"
    REJECTED = "rejected"

class TextModel(str, Enum):
    CLAUDE_SONNET_4_6 = "claude-sonnet-4-6"   # primary writer + editor
    GPT_5_2 = "gpt-5.2"                        # secondary writer (fallback)
    GEMINI_3_1_PRO = "gemini-3.1-pro"          # tertiary writer (last resort)
    GEMINI_3_FLASH = "gemini-3-flash"           # kept for legacy compat only


class VoiceRoute(str, Enum):
    SOUL_2023 = "soul_2023"
    METHODOLOGY = "methodology"
    HYBRID = "hybrid"
    RITUAL = "ritual"


class GenerateDraftRequest(BaseModel):
    raw_input: str = Field(..., min_length=1, description="The raw voice note or text from Coach Sihame")
    post_type: str = Field(default="Reflection", description="The intended post type")
    platform: str = Field(default="general", description="Target platform (telegram vs instagram vs general)")
    rejection_feedback: Optional[str] = Field(
        default=None,
        description="Optional rejection feedback to guide regeneration away from the previous failure.",
    )
    mood_context: Optional[str] = Field(
        default=None,
        description=(
            "Optional internal state of the coach at this moment — what she feels, "
            "what moved her, or what drove this post today. "
            "This is used to modulate the AI's tone without explicitly naming the mood in the output. "
            "Example: 'أحسست بثقل هذا الصباح، لكن شيئاً في الجلسة أعاد إليّ الاتساع'"
        ),
    )


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
    rejection_reason: Optional[str] = None
    revision_history: List[RevisionEntry] = Field(default_factory=list)
    routing_metadata: Dict[str, Any] = Field(default_factory=dict)
    design_title: Optional[str] = None
    design_support: Optional[str] = None
    design_symbol: Optional[str] = None
    design_prompt: Optional[str] = None
    design_image_url: Optional[str] = None
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
    approved_text: Optional[str] = Field(
        default=None,
        description="Optional final text override. If omitted, the backend assembles the approved post from the current structured draft.",
    )


class ApproveTextResponse(BaseModel):
    draft_id: str
    status: PostStatus
    approved_text: str
    model_used: TextModel


class RejectDraftRequest(BaseModel):
    draft_id: str = Field(..., description="The draft id being rejected")
    reason: Optional[str] = Field(None, description="Optional reason for rejection")


class RejectDraftResponse(BaseModel):
    draft_id: str
    status: PostStatus
    rejection_reason: Optional[str]


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
    design_title: Optional[str] = None
    design_support: Optional[str] = None
    design_symbol: Optional[str] = None
    design_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DesignExtractRequest(BaseModel):
    draft_id: str = Field(..., description="The approved draft to extract text from")


class DesignExtractResponse(BaseModel):
    draft_id: str
    design_title: str = Field(..., description="Extracted headline for the image")
    design_support: str = Field(..., description="Extracted body/support text for the image")
    design_symbol: str = Field(..., description="Extracted symbolic element for the image")
    design_concept_ar: str = Field(default="", description="Brief Arabic description of the visual concept for the coach")


class DesignGenerateRequest(BaseModel):
    draft_id: str = Field(..., description="The approved draft id")
    design_title: str = Field(..., description="Coach-approved headline text")
    design_support: str = Field(..., description="Coach-approved body text")
    design_symbol: str = Field(default="", description="Technical English image prompt (auto-generated)")
    design_concept_ar: str = Field(default="", description="Coach's Arabic visual concept — if provided, overrides design_symbol via LLM expansion")


class ConceptHistoryEntry(BaseModel):
    """One previous concept generation, used for archetype-level exclusion tracking."""
    symbol: str = Field(..., description="English image prompt from a previous generation")
    concept_ar: str = Field(default="", description="Arabic concept summary from the same generation")
    archetype: Optional[str] = Field(default=None, description="Auto-detected archetype — will be computed server-side if omitted")


class DesignRegenerateConceptRequest(BaseModel):
    """Request a fresh visual concept derived from the short distilled texts only (not the full post)."""
    draft_id: str = Field(..., description="The approved draft id")
    design_title: str = Field(..., description="Current (possibly coach-edited) headline")
    design_support: str = Field(..., description="Current (possibly coach-edited) support sentence — the juice")
    # ── Preferred: full history list for archetype-level exclusion ──────────
    history: Optional[List[ConceptHistoryEntry]] = Field(
        default=None,
        description="Ordered list of previous concept generations (oldest first, max 3). "
                    "When provided, exclusion operates at the archetype level across all entries."
    )
    # ── Legacy single-entry fields — still accepted for backward compatibility ──
    previous_symbol: str = Field(default="", description="[Legacy] Previous English image prompt to avoid")
    previous_concept_ar: str = Field(default="", description="[Legacy] Previous Arabic concept to avoid")



class DesignGenerateResponse(BaseModel):
    draft_id: str
    design_image_url: str = Field(..., description="URL of the generated image (Kie.ai hosted, 14-day TTL)")


class DesignJobResponse(BaseModel):
    job_id: str = Field(..., description="Unique ID for the background generation job")
    status: str = Field(default="pending", description="Job status: pending | done | failed")
    draft_id: str = Field(..., description="Draft ID — pass as query param when polling status for Supabase fallback")


class DesignJobStatusResponse(BaseModel):
    job_id: str
    status: str = Field(description="Job status: pending | done | failed")
    image_url: Optional[str] = Field(default=None, description="Image URL — set when status is 'done'")
    error: Optional[str] = Field(default=None, description="Error message — set when status is 'failed'")
