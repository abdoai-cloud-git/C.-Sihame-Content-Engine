from __future__ import annotations

from datetime import datetime, timezone
import asyncio
from uuid import uuid4

from app.core.log_collector import collector
from app.models.schemas import (
    AdaptPlatformRequest,
    AdaptPlatformResponse,
    ApproveTextRequest,
    ApproveTextResponse,
    DraftRecordResponse,
    GenerateDraftRequest,
    HistoryItemResponse,
    HistoryListResponse,
    PostDraftResponse,
    PostStatus,
    ReviseDraftRequest,
    ReviseDraftResponse,
    RevisionEntry,
    StoredDraft,
    RejectDraftRequest,
    RejectDraftResponse,
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

    @staticmethod
    def _assemble_post_text(*parts: str | None) -> str:
        return "\n\n".join(part.strip() for part in parts if part and part.strip())

    @staticmethod
    def _get_route_context(draft: StoredDraft) -> tuple[str, str]:
        metadata = draft.routing_metadata or {}
        voice_route = str(metadata.get("voice_route", "methodology"))
        notes = metadata.get("notes") or []
        route_note = notes[0] if notes else "Respect the stored route and methodology constraints."
        return voice_route, route_note

    async def generate_draft(self, request: GenerateDraftRequest) -> PostDraftResponse:
        collector.draft_requested(request.raw_input, request.post_type, request.platform)
        assembled = self.context_builder.build_payload(
            user_raw_input=request.raw_input,
            post_type=request.post_type,
            platform=request.platform,
            rejection_feedback=request.rejection_feedback,
            mood_context=request.mood_context,
        )
        collector.debug("draft.context_built",
                        f"Context assembled — route={assembled.routing_metadata.voice_route.value} "
                        f"files={len(assembled.routing_metadata.injected_files)}",
                        voice_route=assembled.routing_metadata.voice_route.value,
                        injected_files=assembled.routing_metadata.injected_files,
                        prompt_chars=len(assembled.prompt))
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
        collector.draft_saved(draft.draft_id, result.model_used.value, assembled.routing_metadata.voice_route.value)
        return PostDraftResponse(**draft.model_dump())

    async def revise_draft(self, request: ReviseDraftRequest) -> ReviseDraftResponse:
        draft = await self.draft_repository.get(request.draft_id)
        if draft.status == PostStatus.APPROVED_TEXT:
            raise ValueError(f"Draft {draft.draft_id} is already approved and cannot be revised.")
        voice_route, route_note = self._get_route_context(draft)
        revised = await self.text_router.revise_draft(
            current_draft={
                "angle": draft.angle,
                "hook": draft.hook,
                "body": draft.body,
                "cta": draft.cta,
                "safety_flags": draft.safety_flags,
            },
            instruction=request.edit_instruction,
            post_type=draft.post_type,
            platform=draft.platform,
            voice_route=voice_route,
            route_note=route_note,
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
        collector.draft_revised(draft.draft_id, request.edit_instruction)
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
        approved_text = (request.approved_text or "").strip()
        if not approved_text:
            approved_text = self._assemble_post_text(draft.hook, draft.body, draft.cta)
        if not approved_text:
            raise ValueError(f"Draft {draft.draft_id} has no content to approve.")
        draft.approved_text = approved_text
        draft.status = PostStatus.APPROVED_TEXT
        draft.updated_at = datetime.now(timezone.utc)
        await self.draft_repository.update(draft)
        collector.draft_approved(draft.draft_id)
        return ApproveTextResponse(
            draft_id=draft.draft_id,
            status=draft.status,
            approved_text=draft.approved_text,
            model_used=draft.model_used,
        )

    async def reject_draft(self, request: RejectDraftRequest) -> RejectDraftResponse:
        """
        Transitions a draft to the REJECTED status and stores the provided reason.
        
        Workflow State Machine:
        1. Current Status: DRAFT (Pending review)
        2. Action: User clicks 'Reject' and provides feedback.
        3. New Status: REJECTED
        4. Data recorded: `rejection_reason` (string)
        
        This transition is a critical feedback signal. By explicitly rejecting 
        a draft, we preserve the 'negative sample' which is invaluable for 
        quality tracking and potential model refinement. 
        
        In the frontend, this status change is typically the trigger for a 
        subsequent 'Regenerate' call, where the initial user prompt is 
        processed again, potentially reaching a better outcome by avoiding 
        previous mistakes documented in the reason.
        
        Args:
            request (RejectDraftRequest): contains the draft_id and the feedback reason.
            
        Returns:
            RejectDraftResponse: The updated draft status and recorded reason.
        """
        draft = await self.draft_repository.get(request.draft_id)
        if draft.status not in {PostStatus.DRAFT_GENERATED, PostStatus.UNDER_REVIEW}:
            raise ValueError(f"Draft {draft.draft_id} cannot transition from {draft.status} to rejected.")
        draft.status = PostStatus.REJECTED
        draft.rejection_reason = request.reason
        draft.updated_at = datetime.now(timezone.utc)
        await self.draft_repository.update(draft)
        collector.draft_rejected(draft.draft_id, request.reason or "")
        return RejectDraftResponse(
            draft_id=draft.draft_id,
            status=draft.status,
            rejection_reason=draft.rejection_reason,
        )

    async def get_draft(self, draft_id: str) -> DraftRecordResponse:
        draft = await self.draft_repository.get(draft_id)
        return DraftRecordResponse(**draft.model_dump())

    async def adapt_draft(self, request: AdaptPlatformRequest) -> AdaptPlatformResponse:
        draft = await self.draft_repository.get(request.draft_id)
        if draft.status != PostStatus.APPROVED_TEXT:
            raise ValueError(f"Draft {draft.draft_id} must be approved before adapting for a platform.")
        approved_source_text = (draft.approved_text or "").strip() or self._assemble_post_text(draft.hook, draft.body, draft.cta)
        if not approved_source_text:
            raise ValueError(f"Draft {draft.draft_id} is missing approved text.")
        voice_route, route_note = self._get_route_context(draft)

        async def _adapt(platform: str):
            result = await self.text_router.adapt_platform_draft(
                approved_source_text,
                platform,
                post_type=draft.post_type,
                voice_route=voice_route,
                route_note=route_note,
            )
            return platform, result
        
        results = await asyncio.gather(*[_adapt(p) for p in request.target_platforms])
        
        adapted_dict = {p: r.body for p, r in results}
        # Just use the model_used of the first result as an indicator
        model_used = results[0][1].model_used if results else draft.model_used
        
        return AdaptPlatformResponse(
            draft_id=draft.draft_id,
            results=adapted_dict,
            model_used=model_used
        )

    async def list_history(self, limit: int = 20) -> HistoryListResponse:
        drafts = await self.draft_repository.list_history(limit=limit)
        items = []
        for d in drafts:
            # Create a short title from raw_input
            title = (d.raw_input[:50] + "...") if len(d.raw_input) > 50 else (d.raw_input or "مسودة بدون عنوان")
            items.append(HistoryItemResponse(
                draft_id=d.draft_id,
                title=title,
                post_type=d.post_type,
                status=d.status,
                updated_at=d.updated_at
            ))
        return HistoryListResponse(items=items)
