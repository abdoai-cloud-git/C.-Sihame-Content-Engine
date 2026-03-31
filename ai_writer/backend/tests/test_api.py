import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import DraftGenerationResult, TextModel
from app.services.context_builder import DynamicContextBuilder
from app.services.draft_repository import InMemoryDraftRepository
from app.services.workflow_service import ContentWorkflowService
from app.api.routes.generate import get_workflow_service


class FakeTextRouter:
    async def generate_primary_draft(self, prompt: str) -> DraftGenerationResult:
        return DraftGenerationResult(
            angle="somatic angle",
            hook="soft hook",
            body="original body",
            cta="gentle cta",
            safety_flags="",
            model_used=TextModel.GEMINI_3_1_PRO,
        )

    async def revise_draft(self, current_draft, instruction: str) -> DraftGenerationResult:
        return DraftGenerationResult(
            angle=current_draft["angle"],
            hook=current_draft["hook"],
            body=f"{current_draft['body']} | revised: {instruction}",
            cta=current_draft["cta"],
            safety_flags=current_draft["safety_flags"],
            model_used=TextModel.GEMINI_3_FLASH,
        )


class ApiWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryDraftRepository()
        self.workflow = ContentWorkflowService(
            context_builder=DynamicContextBuilder(),
            text_router=FakeTextRouter(),
            draft_repository=self.repo,
        )
        app.dependency_overrides[get_workflow_service] = lambda: self.workflow
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.client.close()

    def test_full_text_workflow(self) -> None:
        create_response = self.client.post(
            "/api/v1/content/draft",
            json={
                "raw_input": "Write about inner fear with a reflective tone.",
                "post_type": "Reflection",
                "platform": "telegram",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        created = create_response.json()
        self.assertEqual(created["status"], "draft_generated")
        self.assertEqual(created["model_used"], "gemini-3.1-pro")
        draft_id = created["draft_id"]

        revise_response = self.client.post(
            "/api/v1/content/revise",
            json={"draft_id": draft_id, "edit_instruction": "Make it shorter"},
        )
        self.assertEqual(revise_response.status_code, 200)
        revised = revise_response.json()
        self.assertEqual(revised["status"], "under_review")
        self.assertEqual(revised["model_used"], "gemini-3-flash")
        self.assertEqual(revised["revisions_count"], 1)

        approve_response = self.client.post(
            "/api/v1/content/approve-text",
            json={"draft_id": draft_id, "approved_text": "final approved text"},
        )
        self.assertEqual(approve_response.status_code, 200)
        approved = approve_response.json()
        self.assertEqual(approved["status"], "approved_text")
        self.assertEqual(approved["approved_text"], "final approved text")

        fetch_response = self.client.get(f"/api/v1/content/{draft_id}")
        self.assertEqual(fetch_response.status_code, 200)
        fetched = fetch_response.json()
        self.assertEqual(fetched["approved_text"], "final approved text")
        self.assertEqual(len(fetched["revision_history"]), 1)
        self.assertEqual(fetched["routing_metadata"]["voice_route"], "soul_2023")

    def test_cannot_revise_after_approval(self) -> None:
        draft_id = self.client.post(
            "/api/v1/content/draft",
            json={
                "raw_input": "Invite to a PEAT promo gently.",
                "post_type": "Promo",
                "platform": "instagram",
            },
        ).json()["draft_id"]
        self.client.post(
            "/api/v1/content/approve-text",
            json={"draft_id": draft_id, "approved_text": "locked"},
        )

        revise_response = self.client.post(
            "/api/v1/content/revise",
            json={"draft_id": draft_id, "edit_instruction": "Change everything"},
        )
        self.assertEqual(revise_response.status_code, 409)
