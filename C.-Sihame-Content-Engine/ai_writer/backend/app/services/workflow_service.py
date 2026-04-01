from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.schemas import (
    AdaptPlatformRequest,
    AdaptPlatformResponse,
    ApproveTextRequest,
    ApproveTextResponse,
    DraftRecordResponse,
    GenerateDraftRequest,
    PostDraftResponse,
    PostStatus,
    ReviseDraftRequest,
    ReviseDraftResponse,
    RevisionEntry,
    StoredDraft,
)
from app.services.context_builder import DynamicContextBuilder
from app.services.draft_repository import DraftRepository
from app.services.llm_router import TextModelRouter


class ContentWorkflowService:
    def __init__(
        self,
        context_builder: DynamicContextBuilder,
        text_router: TextModelRouter,
        draft_repository: DraftRepository,
    ) -> None:
        self.context_builder = context_builder
        self.text_router = text_router
        self.draft_repository = draft_repository

    async def generate_draft(self, request: GenerateDraftRequest) -> PostDraftResponse:
        assembled = self.context_builder.build_payload(
            user_raw_input=request.raw_input,
            post_type=request.post_type,
            platform=request.platform,
        )
        result = await self.text_router.generate_primary_draft(assembled.prompt)
        now = datetime.now(timezone.utc)
        draft = StoredDraft(
            draft_id=str(uuid4()),
            raw_input=request.raw_input,
            post_type=request.post_type,
            platform=request.platform,
            status=PostStatus.DRAFT_GENERATED,
            model_used=result.model_used,
            angle=result.angle,
            hook=result.hook,
            body=result.body,
            cta=result.cta,
            safety_flags=result.safety_flags,
            routing_metadata=assembled.routing_metadata.model_dump(mode="json"),
            created_at=now,
            updated_at=now,
        )
        await self.draft_repository.create(draft)
        return PostDraftResponse(**draft.model_dump())

    async def revise_draft(self, request: ReviseDraftRequest) -> ReviseDraftResponse:
        draft = await self.draft_repository.get(request.draft_id)
        if draft.status == PostStatus.APPROVED_TEXT:
            raise ValueError(f"Draft {draft.draft_id} is already approved and cannot be revised.")
        revised = await self.text_router.revise_draft(
            current_draft={
                "angle": draft.angle,
                "hook": draft.hook,
                "body": draft.body,
                "cta": draft.cta,
                "safety_flags": draft.safety_flags,
            },
            instruction=request.edit_instruction,
        )
        revision = RevisionEntry(
            instruction=request.edit_instruction,
            before_body=draft.body,
            after_body=revised.body,
            model_used=revised.model_used,
            created_at=datetime.now(timezone.utc),
        )
        draft.angle = revised.angle
        draft.hook = revised.hook
        draft.body = revised.body
        draft.cta = revised.cta
        draft.safety_flags = revised.safety_flags
        draft.model_used = revised.model_used
        draft.status = PostStatus.UNDER_REVIEW
        draft.updated_at = datetime.now(timezone.utc)
        draft.revision_history.append(revision)
        await self.draft_repository.update(draft)
        return ReviseDraftResponse(
            draft_id=draft.draft_id,
            status=draft.status,
            model_used=draft.model_used,
            angle=draft.angle,
            hook=draft.hook,
            body=draft.body,
            cta=draft.cta,
            safety_flags=draft.safety_flags,
            revisions_count=len(draft.revision_history),
        )

    async def approve_text(self, request: ApproveTextRequest) -> ApproveTextResponse:
        draft = await self.draft_repository.get(request.draft_id)
        if draft.status not in {PostStatus.DRAFT_GENERATED, PostStatus.UNDER_REVIEW}:
            raise ValueError(f"Draft {draft.draft_id} cannot transition from {draft.status}.")
        draft.approved_text = request.approved_text
        draft.status = PostStatus.APPROVED_TEXT
        draft.updated_at = datetime.now(timezone.utc)
        await self.draft_repository.update(draft)
        return ApproveTextResponse(
            draft_id=draft.draft_id,
            status=draft.status,
            approved_text=draft.approved_text,
            model_used=draft.model_used,
        )

    async def get_draft(self, draft_id: str) -> DraftRecordResponse:
        draft = await self.draft_repository.get(draft_id)
        return DraftRecordResponse(**draft.model_dump())

    async def adapt_draft(self, request: AdaptPlatformRequest) -> AdaptPlatformResponse:
        draft = await self.draft_repository.get(request.draft_id)
        if draft.status != PostStatus.APPROVED_TEXT:
            raise ValueError(f"Draft {draft.draft_id} must be approved before adapting for a platform.")
        if not draft.approved_text:
            raise ValueError(f"Draft {draft.draft_id} is missing approved text.")
        
        result = await self.text_router.adapt_platform_draft(draft.approved_text, request.target_platform)
        
        return AdaptPlatformResponse(
            draft_id=draft.draft_id,
            target_platform=request.target_platform,
            adapted_text=result.body,
            model_used=result.model_used
        )
