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
3. **symbol**: The COMPLETE visual concept paragraph that encompasses the DESIGN DIRECTION, VISUAL COMPOSITION, and COLOR PALETTE.

SYMBOL RULES & EXAMPLES:
- The symbol MUST include 3 sections exactly: "### DESIGN DIRECTION", "VISUAL COMPOSITION:", and "### COLOR PALETTE".
- The composition MUST be described physically as a cinematic still-life on a "warm cream linen surface".
- It must vividly map psychological states to our strict brand colors: muted terracotta/sienna for tension/chaos, warm sage green for healing/expansion, and champagne gold for the central anchor/glow.
- Include explicit lighting and shadow descriptions.
- Below are 3 golden examples of how to write the "symbol" parameter:

Golden Example 1:
### DESIGN DIRECTION
A premium breath-like editorial visual for Coach Sihame. Theme: expansion, letting go, awakening the inner maestro.

VISUAL COMPOSITION: A warm intimate still-life shot from above on a warm cream linen surface. In the center: a small handmade lantern of soft ivory frosted glass, glowing warmly from inside with muted champagne gold light. Around it: soft silk fabric trails. On the left side the silk is slightly gathered and loosely knotted — in warm greige and muted terracotta tones (the old self, tension). On the right the silk opens, unfurls, and flows freely downward — in warm cream and hints of warm sage green (expansion, breath, the inner maestro). Background: warm cream linen at center transitioning to muted terracotta at top edges, with soft warm sage green in bottom corners. Warm overhead lighting, soft internal lantern glow. Large editorial negative space in the upper third.

### COLOR PALETTE
Warm comforting earth tones. Background: warm cream linen. Left tension accent: muted terracotta/burnt orange. Right expansion accent: muted warm sage green, earthy olive-tinted, not teal. Center glow: muted champagne gold lantern light, warm antique gold, not bright metallic. Neutral: warm greige/taupe. Do NOT use cold teal, blue, pure white, or cool gray.

Golden Example 2:
### DESIGN DIRECTION
A premium precision-warm program visual for Coach Sihame. Theme: integration of opposites, the healing compass.

VISUAL COMPOSITION: A warm intimate still-life shot from above on a warm cream linen surface. In the absolute center: a thin elegant compass needle, crafted from polished warm greige metal with a muted champagne gold tip. The surface beneath the needle transitions from left to right — on the left a soft muted terracotta zone (tension, chaos, the knotted self) and on the right a muted warm sage green zone (healing, calm, integration). The color boundary beneath the needle is seamless and gradient-soft, not sharp. Warm overhead studio lighting, soft deep shadows. Wide margins, large editorial negative space in the upper half for text.

### COLOR PALETTE
Warm comforting earth tones. Background: warm cream linen. Left zone: muted terracotta/burnt orange earthy sienna. Right zone: muted warm sage green, earthy olive-tinted, not teal. Compass accent: muted champagne gold, warm antique gold, not bright metallic. Neutral: warm greige/taupe. Do NOT use cold teal, blue, pure white, or cool gray.

Golden Example 3:
### DESIGN DIRECTION
A premium editorial visual for Coach Sihame. Theme: the nervous system caught between betrayal and healing.

VISUAL COMPOSITION: A warm still-life shot from above on a warm cream linen surface. In the center: a delicate network of translucent ivory silk threads (representing the nervous system). On the left side, threads are slightly knotted and tangled — rendered in warm terracotta and deep greige tones. Moving right, the threads untangle, lighten, and glow gently from within. A small perfect ivory-colored sphere rests at the center of the untangled zone. Warm, soft overhead lighting. Photorealistic silk and linen texture. Large negative space in the upper third for text.

### COLOR PALETTE
Warm comforting earth tones. Background: warm cream linen. Left tension zone: muted terracotta/burnt orange earthy sienna. Right healing zone: muted warm sage green, earthy olive-tinted, not teal. Center glow: muted champagne gold, warm antique gold, not bright metallic. Do NOT use cold teal, blue, pure white, or cool gray.

Rules:
- Give ONLY the 3 values in STRICT JSON exactly: {{"title": "...", "support": "...", "symbol": "..."}}
- Do not include markdown fences.
- Use \\n for line breaks inside the symbol string so it remains valid JSON.

APPROVED POST:
{approved_text}"""

    IMAGE_PROMPT_TEMPLATE = """Portrait-format social media card, 4:5 aspect ratio.

{symbol}

### TYPOGRAPHY RULE
HEADLINE: Flowing Farsi-style Arabic calligraphy (خط الفارسي) with a gentle diagonal lean. Fluid connected letterforms with elegant thin-to-thick stroke variation, drawn with a fine pointed nib. Warm champagne gold ink color — not black. Gold leaf accents on diacritics (tashkeel) in the same warm gold tone. Poetic, spoken, artistic.
BODY: Clean, thick, geometric sans-serif Arabic letterforms. Sharp, precise strokes with even weight. Modern Kufic-inspired clarity.
SIGNATURE: "Siham Atamnia" in delicate pen-written cursive, fine-point ink, light and restrained.
PAPER: All typography rendered as real calligraphy ink on soft, textured cotton paper with subtle grain.

### TEXT BLOCKS
- Title: "{title}"
  Placement: Top Center, upper area
  Materiality: HEADLINE (warm champagne gold ink, Farsi-style)
  Importance: Primary

- Support: "{support}"
  Placement: Center, below title
  Materiality: BODY (warm dark greige ink)
  Importance: Secondary

- Signature: "Siham Atamnia"
  Placement: Bottom Right Corner
  Materiality: SIGNATURE (fine cursive, restrained)
  Importance: Tertiary

### ATMOSPHERE
Warm, comforting editorial elegance. Quiet integration. Poetic and artistic. Handcrafted physical reality, not machine-generated. 8K resolution, photorealistic linen and silk texture."""

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

    @staticmethod
    def _fix_json_newlines(raw: str) -> str:
        """Escape literal newlines/carriage-returns inside JSON string values.

        The LLM often puts real line-breaks inside the multi-line `symbol`
        value instead of the escaped \\n sequence, producing invalid JSON.
        This parser walks the string character-by-character so it only
        replaces newlines that sit inside a quoted string value.
        """
        result: list[str] = []
        in_string = False
        escape_next = False
        for ch in raw:
            if escape_next:
                result.append(ch)
                escape_next = False
            elif ch == "\\" and in_string:
                result.append(ch)
                escape_next = True
            elif ch == '"':
                result.append(ch)
                in_string = not in_string
            elif ch in ("\n", "\r") and in_string:
                result.append("\\n")
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def _extract_json(cls, raw_text: str) -> Dict[str, Any]:
        cleaned = cls._strip_code_fences(raw_text)
        # Fix literal newlines inside string values (common with multi-line symbol)
        cleaned = cls._fix_json_newlines(cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise DesignerServiceError("LLM response did not contain valid JSON for text extraction.")
            return json.loads(cleaned[start : end + 1])

    async def extract_text_blocks(self, approved_text: str) -> Dict[str, str]:
        """Use LLM to extract headline, body, and visual concept from approved text.

        Returns:
            dict with keys 'title', 'support', and 'symbol'
        """
        prompt = self.EXTRACTION_PROMPT.format(approved_text=approved_text)
        try:
            raw_text = await self.llm_adapter.complete_text(prompt)
            logger.debug("[extract_text_blocks] raw LLM response: %s", raw_text[:500])
            result = self._extract_json(raw_text)
            title = result.get("title", "").strip()
            support = result.get("support", "").strip()
            symbol = result.get("symbol", "").strip()
            if not title or not support:
                raise DesignerServiceError("LLM returned empty title or support text.")
            if not symbol:
                logger.warning(
                    "[extract_text_blocks] symbol field is empty. "
                    "LLM keys returned: %s. Raw (first 800 chars): %s",
                    list(result.keys()),
                    raw_text[:800],
                )
            logger.debug(
                "[extract_text_blocks] extracted — title=%r, support=%r, symbol_len=%d",
                title, support, len(symbol),
            )
            return {"title": title, "support": support, "symbol": symbol}
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
