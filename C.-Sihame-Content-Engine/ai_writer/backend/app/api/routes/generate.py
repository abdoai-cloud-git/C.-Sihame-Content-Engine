from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import (
    ApproveTextRequest,
    ApproveTextResponse,
    DraftRecordResponse,
    GenerateDraftRequest,
    PostDraftResponse,
    ReviseDraftRequest,
    ReviseDraftResponse,
)
from app.services.context_builder import DynamicContextBuilder
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
