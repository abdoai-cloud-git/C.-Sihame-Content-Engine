import unittest

from app.models.schemas import TextModel
from app.services.llm_router import ClaudeMessagesAdapter, ModelAdapterError, TextModelRouter


class StaticAdapter:
    def __init__(self, payload=None, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error

    async def complete_text(self, prompt: str) -> str:
        if self.error:
            raise self.error
        return self.payload


class TextModelRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_falls_back_to_secondary_writer(self) -> None:
        router = TextModelRouter(
            primary_adapter=StaticAdapter(error=RuntimeError("primary failed")),
            secondary_adapter=StaticAdapter(
                payload='{"angle":"fallback","hook":"h","body":"b","cta":"c","safety_flags":""}'
            ),
            editor_adapter=StaticAdapter(
                payload='{"angle":"edit","hook":"h","body":"b","cta":"c","safety_flags":""}'
            ),
        )

        result = await router.generate_primary_draft("prompt")

        self.assertEqual(result.model_used, TextModel.CLAUDE_SONNET_4_6)
        self.assertEqual(result.angle, "fallback")

    async def test_raises_when_no_json_found(self) -> None:
        router = TextModelRouter(
            primary_adapter=StaticAdapter(payload="not json"),
            secondary_adapter=StaticAdapter(payload="still not json"),
            editor_adapter=StaticAdapter(
                payload='{"angle":"edit","hook":"h","body":"b","cta":"c","safety_flags":""}'
            ),
        )

        with self.assertRaises(ModelAdapterError):
            await router.generate_primary_draft("prompt")

    def test_claude_text_extraction_reads_text_blocks(self) -> None:
        payload = {
            "content": [
                {"type": "text", "text": "first"},
                {"type": "tool_use", "name": "ignored"},
                {"type": "text", "text": "second"},
            ]
        }
        self.assertEqual(ClaudeMessagesAdapter.extract_text_from_response(payload), "first\nsecond")
