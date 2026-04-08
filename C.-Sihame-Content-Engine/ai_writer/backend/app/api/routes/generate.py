from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import (
    AdaptPlatformRequest,
    AdaptPlatformResponse,
    ApproveTextRequest,
    ApproveTextResponse,
    DesignExtractRequest,
    DesignExtractResponse,
    DesignGenerateRequest,
    DesignGenerateResponse,
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
    )


@router.post("/design/generate", response_model=DesignGenerateResponse)
async def generate_design_image(
    request: DesignGenerateRequest,
    draft_repo: DraftRepository = Depends(get_draft_repository),
    designer: DesignerService = Depends(get_designer_service),
):
    """
    Generate a branded image from coach-approved text blocks via Kie.ai Nano Banana 2.
    The image URL is stored in Supabase (Kie hosts media for 14 days).
    """
    try:
        draft = await draft_repo.get(request.draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Draft {request.draft_id} not found.") from exc

    if draft.status != PostStatus.APPROVED_TEXT:
        raise HTTPException(status_code=409, detail="Draft must be approved before generating design image.")

    # Build the full image prompt from brand rules
    prompt = designer.build_image_prompt(
        title=request.design_title,
        support=request.design_support,
        symbol=request.design_symbol,
    )

    try:
        image_url = await designer.generate_image(prompt)
    except DesignerServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Persist design data
    from datetime import datetime, timezone
    draft.design_title = request.design_title
    draft.design_support = request.design_support
    draft.design_symbol = request.design_symbol
    draft.design_prompt = prompt
    draft.design_image_url = image_url
    draft.updated_at = datetime.now(timezone.utc)
    await draft_repo.update(draft)

    return DesignGenerateResponse(
        draft_id=draft.draft_id,
        design_image_url=image_url,
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

