from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from app.core.config import settings
from app.models.schemas import StoredDraft

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - exercised only when Supabase is not installed
    Client = object  # type: ignore[assignment]
    create_client = None


class DraftRepository(ABC):
    @abstractmethod
    async def create(self, draft: StoredDraft) -> StoredDraft:
        raise NotImplementedError

    @abstractmethod
    async def update(self, draft: StoredDraft) -> StoredDraft:
        raise NotImplementedError

    @abstractmethod
    async def get(self, draft_id: str) -> StoredDraft:
        raise NotImplementedError


class InMemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self._drafts: Dict[str, StoredDraft] = {}

    async def create(self, draft: StoredDraft) -> StoredDraft:
        self._drafts[draft.draft_id] = draft
        return draft

    async def update(self, draft: StoredDraft) -> StoredDraft:
        self._drafts[draft.draft_id] = draft
        return draft

    async def get(self, draft_id: str) -> StoredDraft:
        if draft_id not in self._drafts:
            raise KeyError(draft_id)
        return self._drafts[draft_id]


class SupabaseDraftRepository(DraftRepository):
    def __init__(self, client: Client, table_name: str) -> None:
        self.client = client
        self.table_name = table_name

    def _table(self):
        return self.client.table(self.table_name)

    async def create(self, draft: StoredDraft) -> StoredDraft:
        self._table().upsert(draft.model_dump(mode="json")).execute()
        return draft

    async def update(self, draft: StoredDraft) -> StoredDraft:
        self._table().upsert(draft.model_dump(mode="json")).execute()
        return draft

    async def get(self, draft_id: str) -> StoredDraft:
        response = self._table().select("*").eq("draft_id", draft_id).limit(1).execute()
        if not response.data:
            raise KeyError(draft_id)
        return StoredDraft.model_validate(response.data[0])


def build_draft_repository() -> DraftRepository:
    if (
        settings.STORAGE_BACKEND.lower() == "supabase"
        and settings.SUPABASE_URL
        and settings.SUPABASE_ANON_KEY
        and create_client is not None
    ):
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        return SupabaseDraftRepository(client=client, table_name=settings.SUPABASE_DRAFTS_TABLE)
    return InMemoryDraftRepository()
