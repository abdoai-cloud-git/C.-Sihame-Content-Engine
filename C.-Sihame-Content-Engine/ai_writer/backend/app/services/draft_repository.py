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

    @abstractmethod
    async def list_history(self, limit: int = 20) -> list[StoredDraft]:
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

    async def list_history(self, limit: int = 20) -> list[StoredDraft]:
        drafts = list(self._drafts.values())
        drafts.sort(key=lambda d: d.updated_at, reverse=True)
        return drafts[:limit]


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

    async def list_history(self, limit: int = 20) -> list[StoredDraft]:
        # Minimal fetch to optimize fetching. Actually we can simply fetch raw_input, post_type, status, etc.
        # But for StoredDraft we might need all fields, or we can just fetch all and let mapping happen in route.
        # Given it's a general repository method, let's just fetch all or specific fields if we create a lighter model,
        # but StoredDraft requires all fields. Let's just fetch everything for now and limit the fields in the API response.
        response = self._table().select("*").order("updated_at", desc=True).limit(limit).execute()
        return [StoredDraft.model_validate(d) for d in response.data]


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
