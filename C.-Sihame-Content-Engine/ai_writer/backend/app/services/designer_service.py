from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.services.llm_router import GeminiChatAdapter, ModelAdapterError

logger = logging.getLogger(__name__)


class DesignerServiceError(RuntimeError):
    pass


class DesignerService:
    """Handles text extraction from approved posts and image generation via Kie.ai."""

    EXTRACTION_PROMPT = """You are a visual content strategist for Coach Sihame, a somatic trauma therapy coach.
Given the following approved post text, extract exactly TWO text blocks for an image design:

1. **title**: The single most powerful sentence or phrase (headline). Maximum 8 words in Arabic.
2. **support**: A supporting sentence or key takeaway (body text). Maximum 15 words in Arabic.

Rules:
- Choose text that is visually impactful and meaningful
- The title should be the emotional anchor of the post
- The support should complement, not repeat, the title
- Keep both in Arabic
- Return STRICT JSON with exactly these keys: {{"title": "...", "support": "..."}}
- Do not include markdown fences or any other formatting

APPROVED POST:
{approved_text}"""

    IMAGE_PROMPT_TEMPLATE = """Portrait-format social media card, 4:5 aspect ratio.

BACKGROUND: Warm earth-toned gradient. Soft textured cotton paper with subtle grain.
Palette: Terracotta (#C67B5C), Warm Cream Linen (#F5E6D3), Warm Sage (#A8B89C), Champagne Gold (#D4AF37).
Generous negative space. Quiet editorial elegance. Handcrafted, not machine-generated.

TYPOGRAPHY RULE:
HEADLINE: "{title}"
Style: Flowing Farsi-style Arabic calligraphy (خط الفارسي) with gentle diagonal lean. Fluid connected letterforms with elegant thin-to-thick stroke variation, drawn with a fine pointed nib. Warm champagne gold ink color — not black. Gold leaf accents on diacritics (tashkeel). Poetic, spoken, artistic.
Placement: Upper-center area. Primary hierarchy.

BODY: "{support}"
Style: Clean, thick, geometric sans-serif Arabic letterforms. Sharp, precise strokes with even weight. Modern Kufic-inspired clarity.
Placement: Center, below headline. Secondary hierarchy.

SIGNATURE: "Siham Atamnia"
Style: Delicate pen-written cursive, fine-point ink, light and restrained.
Placement: Bottom-right corner. Tertiary hierarchy.

PAPER: All typography rendered as real calligraphy ink on soft, textured cotton paper with subtle grain.
Do NOT render as a template or mockup. This is a finished artwork."""

    # Polling configuration
    POLL_INITIAL_DELAY: float = 5.0
    POLL_INTERVAL: float = 3.0
    POLL_MAX_ATTEMPTS: int = 40  # ~2 minutes total

    def __init__(self, llm_adapter: GeminiChatAdapter | None = None) -> None:
        self.llm_adapter = llm_adapter or GeminiChatAdapter(
            api_key=settings.KIE_API_KEY,
            base_url=settings.KIE_GEMINI_FLASH_BASE_URL,
            model_name=settings.MODEL_EDITOR,
        )

    @staticmethod
    def _strip_code_fences(raw_text: str) -> str:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    @classmethod
    def _extract_json(cls, raw_text: str) -> Dict[str, Any]:
        cleaned = cls._strip_code_fences(raw_text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise DesignerServiceError("LLM response did not contain valid JSON for text extraction.")
            return json.loads(cleaned[start : end + 1])

    async def extract_text_blocks(self, approved_text: str) -> Dict[str, str]:
        """Use LLM to extract headline + body from approved text.

        Returns:
            dict with keys 'title' and 'support'
        """
        prompt = self.EXTRACTION_PROMPT.format(approved_text=approved_text)
        try:
            raw_text = await self.llm_adapter.complete_text(prompt)
            result = self._extract_json(raw_text)
            title = result.get("title", "").strip()
            support = result.get("support", "").strip()
            if not title or not support:
                raise DesignerServiceError("LLM returned empty title or support text.")
            return {"title": title, "support": support}
        except ModelAdapterError as e:
            raise DesignerServiceError(f"Text extraction failed: {e}") from e

    def build_image_prompt(self, title: str, support: str) -> str:
        """Construct the full image generation prompt from brand rules."""
        return self.IMAGE_PROMPT_TEMPLATE.format(title=title, support=support)

    async def generate_image(self, prompt: str) -> str:
        """Call Kie.ai Nano Banana 2 API and poll for result.

        Returns:
            The image URL from the successful task result.
        """
        # Step 1: Create task
        task_id = await self._create_kie_task(prompt)
        logger.info(f"Kie.ai task created: {task_id}")

        # Step 2: Poll for completion
        await asyncio.sleep(self.POLL_INITIAL_DELAY)

        for attempt in range(self.POLL_MAX_ATTEMPTS):
            result = await self._poll_kie_task(task_id)
            state = result.get("state", "")

            if state == "success":
                return self._extract_image_url(result)
            elif state in ("failed", "error"):
                fail_msg = result.get("failMsg", "Unknown error")
                raise DesignerServiceError(f"Kie.ai image generation failed: {fail_msg}")

            logger.info(f"Kie.ai task {task_id} state: {state} (attempt {attempt + 1}/{self.POLL_MAX_ATTEMPTS})")
            await asyncio.sleep(self.POLL_INTERVAL)

        raise DesignerServiceError(f"Kie.ai task {task_id} timed out after {self.POLL_MAX_ATTEMPTS} polling attempts.")

    async def _create_kie_task(self, prompt: str) -> str:
        """POST to Kie.ai createTask endpoint."""
        headers = {
            "Authorization": f"Bearer {settings.KIE_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "nano-banana-2",
            "input": {
                "prompt": prompt,
                "image_input": [],
                "aspect_ratio": "4:5",
                "resolution": "1K",
                "output_format": "png",
            },
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(settings.KIE_IMAGE_API_URL, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data", {})
        task_id = data.get("taskId")
        if not task_id:
            raise DesignerServiceError(f"Kie.ai createTask did not return a taskId. Response: {payload}")
        return task_id

    async def _poll_kie_task(self, task_id: str) -> Dict[str, Any]:
        """GET task status from Kie.ai."""
        headers = {
            "Authorization": f"Bearer {settings.KIE_API_KEY}",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                settings.KIE_TASK_STATUS_URL,
                params={"taskId": task_id},
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()

        return payload.get("data", {})

    @staticmethod
    def _extract_image_url(task_data: Dict[str, Any]) -> str:
        """Extract the first image URL from a successful task result."""
        result_json_str = task_data.get("resultJson", "{}")
        try:
            result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
        except json.JSONDecodeError:
            raise DesignerServiceError(f"Could not parse resultJson: {result_json_str}")

        urls = result_json.get("resultUrls", [])
        if not urls:
            raise DesignerServiceError("Kie.ai task succeeded but returned no image URLs.")
        return urls[0]
