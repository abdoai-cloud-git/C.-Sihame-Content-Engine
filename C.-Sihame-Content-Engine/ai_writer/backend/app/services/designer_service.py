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

    EXTRACTION_PROMPT = """You are a master visual content director for Coach Sihame, a somatic trauma therapy coach.
Given the following approved post text, extract exactly THREE elements for an image design:

1. **title**: The single most powerful sentence or phrase (headline). Maximum 8 words in Arabic.
2. **support**: A supporting sentence or key takeaway (body text). Maximum 15 words in Arabic.
3. **symbol**: A rich, cinematic, still-life VISUAL COMPOSITION paragraph that physically describes a scene containing a symbolic element representing the post's core meaning.
   
SYMBOL RULES & EXAMPLES:
- The symbol MUST be described physically as a cinematic still-life on a "warm cream linen surface".
- It must vividly map psychological states to our strict brand colors: muted terracotta/sienna for tension/chaos, warm sage green for healing/expansion, and champagne gold for the central anchor/glow.
- Include explicit lighting and shadow descriptions.
- Below are 3 golden examples of how to write the "symbol" parameter:

Golden Example 1 (Theme: expansion, letting go):
"A warm intimate still-life shot from above on a warm cream linen surface. In the center: a small handmade lantern of soft ivory frosted glass, glowing warmly from inside with muted champagne gold light. Around it: soft silk fabric trails. On the left side the silk is slightly gathered and loosely knotted — in warm greige and muted terracotta tones (the old self, tension). On the right the silk opens, unfurls, and flows freely downward — in warm cream and hints of warm sage green (expansion, breath, the inner maestro). Background: warm cream linen at center transitioning to muted terracotta at top edges, with soft warm sage green in bottom corners. Warm overhead lighting, soft internal lantern glow. Large editorial negative space in the upper third."

Golden Example 2 (Theme: integration, the healing compass):
"A warm intimate still-life shot from above on a warm cream linen surface. In the absolute center: a thin elegant compass needle, crafted from polished warm greige metal with a muted champagne gold tip. The surface beneath the needle transitions from left to right — on the left a soft muted terracotta zone (tension, chaos, the knotted self) and on the right a muted warm sage green zone (healing, calm, integration). The color boundary beneath the needle is seamless and gradient-soft, not sharp. Warm overhead studio lighting, soft deep shadows. Wide margins, large editorial negative space in the upper half for text."

Golden Example 3 (Theme: nervous system, processing trauma):
"A warm still-life shot from above on a warm cream linen surface. In the center: a delicate network of translucent ivory silk threads (representing the nervous system). On the left side, threads are slightly knotted and tangled — rendered in warm terracotta and deep greige tones. Moving right, the threads untangle, lighten, and glow gently from within. A small perfect ivory-colored sphere rests at the center of the untangled zone. Warm, soft overhead lighting. Photorealistic silk and linen texture. Large negative space in the upper third for text."

Rules:
- Give ONLY the 3 values in STRICT JSON exactly: {{"title": "...", "support": "...", "symbol": "..."}}
- Do not include markdown fences.

APPROVED POST:
{approved_text}"""

    IMAGE_PROMPT_TEMPLATE = """Portrait-format social media card, 4:5 aspect ratio.

### DESIGN DIRECTION
A premium, deeply grounded, editorial visual for Coach Sihame. Theme: somatic awakening and psychological safety.

VISUAL COMPOSITION: {symbol}

### COLOR PALETTE
Warm comforting earth tones. Background: natural linen and cotton tones transitioning to muted terracotta. Accents of warm sage green and champagne gold. 
CRITICAL RULE: Do NOT use cold teal, blue, pure white, or cool gray anywhere in the image.

### TYPOGRAPHY RULE
- Typeface Definition: Use an elegant, fine-pointed-nib Farsi-style Arabic calligraphy (خط الفارسي) for the main headline, blending fluid, connected, thin-to-thick strokes. Use a modern, thick, geometric Kufic-inspired sans-serif for secondary text. Use a delicate cursive for the signature. Apply warm champagne gold ink for calligraphy and muted terracotta for body text. Real ink and paper textures only.

### TEXT BLOCKS
- Title: "{title}"
  Placement: Upper-center area, beautifully balanced in negative space.
  Materiality: Flowing Farsi calligraphy, champagne gold ink, gold leaf accents on diacritics.
  Importance: Primary

- Support: "{support}"
  Placement: Lower-center area, perfectly aligned.
  Materiality: Clean geometric sans-serif Arabic, warm greige or terracotta ink.
  Importance: Secondary

- Signature: "Siham Atamnia"
  Placement: Bottom-right corner.
  Materiality: Delicate pen-written cursive, fine ink.
  Importance: Tertiary

### ATMOSPHERE
Luxurious, psychologically safe, deeply grounded, handcrafted, quiet, editorial, poetic. Hand-drawn on premium textured cotton paper. Warm overhead lighting. No digital gloss, no templates. This is a finished physical artwork."""

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

    def build_image_prompt(self, title: str, support: str, symbol: str) -> str:
        """Construct the full image generation prompt from brand rules."""
        return self.IMAGE_PROMPT_TEMPLATE.format(title=title, support=support, symbol=symbol)

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
