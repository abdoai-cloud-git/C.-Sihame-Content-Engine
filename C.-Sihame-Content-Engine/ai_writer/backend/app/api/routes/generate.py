import asyncio
import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import (
    AdaptPlatformRequest,
    AdaptPlatformResponse,
    ApproveTextRequest,
    ApproveTextResponse,
    DesignExtractRequest,
    DesignExtractResponse,
    DesignGenerateRequest,
    DesignJobResponse,
    DesignJobStatusResponse,
    DesignRegenerateConceptRequest,
    DraftRecordResponse,
    GenerateDraftRequest,
    HistoryItemResponse,
    HistoryListResponse,
    PostDraftResponse,
    PostStatus,
    ReviseDraftRequest,
    ReviseDraftResponse,
    RejectDraftRequest,
    RejectDraftResponse,
)
from app.services.context_builder import DynamicContextBuilder
from app.services.designer_service import DesignerService, DesignerServiceError
from app.services.draft_repository import DraftRepository, build_draft_repository
from app.services.llm_router import ModelAdapterError, TextModelRouter
from app.services.workflow_service import ContentWorkflowService

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory job store for async image generation
# job_id -> {"status": "pending"|"done"|"failed", "image_url": str|None, "error": str|None}
# This is process-local; sufficient for single-instance Cloud Run deployments.
# ---------------------------------------------------------------------------
_image_jobs: Dict[str, Dict[str, Any]] = {}


async def _run_image_generation_job(
    job_id: str,
    designer: "DesignerService",
    draft_repo: "DraftRepository",
    draft_id: str,
    design_title: str,
    design_support: str,
    design_symbol: str,
    concept_ar: str,
) -> None:
    """Background coroutine: runs Kie.ai polling and writes the result to _image_jobs."""
    try:
        # Expand Arabic concept → English symbol if coach provided one
        symbol = (
            await designer.expand_arabic_concept(concept_ar)
            if concept_ar
            else design_symbol
        )

        prompt = designer.build_image_prompt(
            title=design_title,
            support=design_support,
            symbol=symbol,
        )

        image_url = await designer.generate_image(prompt)

        # Persist to Supabase
        draft = await draft_repo.get(draft_id)
        draft.design_title = design_title
        draft.design_support = design_support
        draft.design_symbol = symbol
        draft.design_prompt = prompt
        draft.design_image_url = image_url
        draft.updated_at = datetime.now(timezone.utc)
        await draft_repo.update(draft)

        _image_jobs[job_id] = {"status": "done", "image_url": image_url, "error": None}
        logger.info("Image job %s done — url=%s", job_id, image_url)

    except Exception as exc:  # noqa: BLE001
        _image_jobs[job_id] = {"status": "failed", "image_url": None, "error": str(exc)}
        logger.error("Image job %s failed: %s", job_id, exc)



def get_context_builder():
    return DynamicContextBuilder()


def get_text_router():
    return TextModelRouter()


@lru_cache(maxsize=1)
def get_draft_repository() -> DraftRepository:
    return build_draft_repository()


def get_workflow_service(
    context_builder: DynamicContextBuilder = Depends(get_context_builder),
    text_router: TextModelRouter = Depends(get_text_router),
    draft_repository: DraftRepository = Depends(get_draft_repository),
):
    return ContentWorkflowService(
        context_builder=context_builder,
        text_router=text_router,
        draft_repository=draft_repository,
    )


@router.post("/draft", response_model=PostDraftResponse)
async def generate_draft(
    request: GenerateDraftRequest,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    try:
        return await workflow.generate_draft(request)
    except ModelAdapterError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/revise", response_model=ReviseDraftResponse)
async def revise_draft(
    request: ReviseDraftRequest,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    try:
        return await workflow.revise_draft(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ModelAdapterError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/approve-text", response_model=ApproveTextResponse)
async def approve_text(
    request: ApproveTextRequest,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    try:
        return await workflow.approve_text(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/reject", response_model=RejectDraftResponse)
async def reject_draft(
    request: RejectDraftRequest,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    """
    Rejects a content draft and records the reason for rejection.
    
    Architecture:
    This endpoint is the 'negative feedback' entry point of the Reject & Regenerate loop.
    1. It updates the draft status to 'REJECTED' in Supabase.
    2. It persists the 'rejection_reason' provided by the user.
    3. This feedback is critical for future model fine-tuning and immediately 
       informs the frontend to trigger a fresh generation attempt using the 
       original context combined with this specific feedback.
    
    Args:
        request: Contains draft_id and an optional rejection_reason string.
    """
    try:
        return await workflow.reject_draft(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    limit: int = 20,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    try:
        return await workflow.list_history(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/adapt", response_model=AdaptPlatformResponse)
async def adapt_platform(
    request: AdaptPlatformRequest,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    try:
        return await workflow.adapt_draft(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ModelAdapterError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# ---------------------------------------------------------------------------
# Graphics Designer endpoints
# ---------------------------------------------------------------------------

def get_designer_service():
    return DesignerService()


@router.post("/design/extract", response_model=DesignExtractResponse)
async def extract_design_text(
    request: DesignExtractRequest,
    draft_repo: DraftRepository = Depends(get_draft_repository),
    designer: DesignerService = Depends(get_designer_service),
):
    """
    Auto-extract headline + body text from an approved draft for image design.
    The coach can then review and edit these before generating the image.
    """
    try:
        draft = await draft_repo.get(request.draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc

    if draft.status != PostStatus.APPROVED_TEXT:
        raise HTTPException(status_code=409, detail="Draft must be approved before extracting design text.")

    source_text = draft.approved_text or draft.body
    if not source_text:
        raise HTTPException(status_code=400, detail="No approved text available for extraction.")

    try:
        text_blocks = await designer.extract_text_blocks(source_text)
    except DesignerServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Persist extracted text
    from datetime import datetime, timezone
    draft.design_title = text_blocks["title"]
    draft.design_support = text_blocks["support"]
    draft.design_symbol = text_blocks.get("symbol", "")
    draft.updated_at = datetime.now(timezone.utc)
    await draft_repo.update(draft)

    return DesignExtractResponse(
        draft_id=draft.draft_id,
        design_title=text_blocks["title"],
        design_support=text_blocks["support"],
        design_symbol=text_blocks.get("symbol", ""),
        design_concept_ar=text_blocks.get("concept_ar", ""),
    )



@router.post("/design/regenerate-concept", response_model=DesignExtractResponse)
async def regenerate_visual_concept(
    request: DesignRegenerateConceptRequest,
    draft_repo: DraftRepository = Depends(get_draft_repository),
    designer: DesignerService = Depends(get_designer_service),
):
    """
    Re-generate ONLY the visual concept (symbol + concept_ar) from the short
    distilled title + support texts — without re-reading the full approved post.

    This lets the coach keep her edited title/support while getting a completely
    fresh symbolic idea for the image.
    """
    try:
        draft = await draft_repo.get(request.draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc

    try:
        concept = await designer.regenerate_concept(
            title=request.design_title,
            support=request.design_support,
            previous_symbol=request.previous_symbol,
            previous_concept_ar=request.previous_concept_ar,
        )
    except DesignerServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Persist the fresh symbol to the draft (concept_ar is UI-only, not stored separately)
    from datetime import datetime, timezone
    draft.design_symbol = concept.get("symbol", "")
    draft.updated_at = datetime.now(timezone.utc)
    await draft_repo.update(draft)

    return DesignExtractResponse(
        draft_id=draft.draft_id,
        design_title=request.design_title,    # keep whatever the coach had
        design_support=request.design_support, # keep whatever the coach had
        design_symbol=concept.get("symbol", ""),
        design_concept_ar=concept.get("concept_ar", ""),
    )


@router.post("/design/generate", response_model=DesignJobResponse)
async def generate_design_image(
    request: DesignGenerateRequest,
    draft_repo: DraftRepository = Depends(get_draft_repository),
    designer: DesignerService = Depends(get_designer_service),
):
    """
    Kick off a background image generation job and return a job_id immediately.

    Kie.ai generation can take 400–750 seconds; holding an HTTP connection that
    long triggers browser "failed to fetch" errors.  This endpoint returns in
    < 1 second.  The frontend should poll GET /design/status/{job_id} every 15 s
    until status transitions to "done" or "failed".
    """
    try:
        draft = await draft_repo.get(request.draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc

    if draft.status != PostStatus.APPROVED_TEXT:
        raise HTTPException(status_code=409, detail="Draft must be approved before generating design image.")

    job_id = str(uuid.uuid4())
    _image_jobs[job_id] = {"status": "pending", "image_url": None, "error": None}

    asyncio.create_task(
        _run_image_generation_job(
            job_id=job_id,
            designer=designer,
            draft_repo=draft_repo,
            draft_id=request.draft_id,
            design_title=request.design_title,
            design_support=request.design_support,
            design_symbol=request.design_symbol,
            concept_ar=request.design_concept_ar.strip(),
        )
    )

    logger.info("Image job %s queued for draft %s", job_id, request.draft_id)
    return DesignJobResponse(job_id=job_id, status="pending")


@router.get("/design/status/{job_id}", response_model=DesignJobStatusResponse)
async def get_design_job_status(job_id: str):
    """
    Poll this endpoint every 15 seconds after calling POST /design/generate.
    Returns status=pending while Kie.ai is running, status=done with image_url
    on success, or status=failed with error on failure.
    """
    job = _image_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return DesignJobStatusResponse(
        job_id=job_id,
        status=job["status"],
        image_url=job.get("image_url"),
        error=job.get("error"),
    )



# ---------------------------------------------------------------------------
# Catch-all: Must be LAST (/{draft_id} matches any path segment)
# ---------------------------------------------------------------------------

@router.get("/{draft_id}", response_model=DraftRecordResponse)
async def get_draft(
    draft_id: str,
    workflow: ContentWorkflowService = Depends(get_workflow_service),
):
    try:
        return await workflow.get_draft(draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {draft_id} not found.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

