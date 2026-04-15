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

Your mission: design a cinematic still-image that is a precise visual translation of THIS specific post — not a generic therapy image.

━━━ PHASE 1: MINE THE POST FOR RAW MATERIAL ━━━
Read the post. Extract:
① ONE precise body sensation or physical feeling mentioned (e.g., "chest tightening", "held breath", "shaky legs", "clenched jaw")
② THE core psychological movement: what is the reader releasing, reclaiming, or understanding?
③ ONE unexpected, surprising real-world object or natural phenomenon that physically embodies that movement — chosen from the world of: astronomy, geology, botany, architecture, physics, culinary arts, cartography, watchmaking, glassblowing, weaving light, geology, marine life, metallurgy, geometry, ruins, or any other domain. Think laterally. Surprise yourself.

━━━ PHASE 2: BUILD THE VISUAL FROM YOUR CHOSEN OBJECT ━━━
Start from your chosen object in ③. Ask: how does this object, in its natural state, show the FROM → TO transformation?
• Choose ONE visual modality:
  - Still-Life: place the object on a warm cream surface, shot from above or at a low cinematic angle
  - Atmospheric: let the object dissolve into light, water, air, or space

Now paint the scene specifically:
• What part of the object represents the FROM state (tension, fear, shutdown)?
• What part represents the TO state (release, safety, aliveness)?
• Where is the golden turning-point moment between the two?

━━━ PHASE 3: APPLY BRAND COLORS TO YOUR OBJECT ━━━
Map the brand palette onto YOUR chosen object's natural forms — do not introduce new objects just to show color:
• FROM state zones → muted terracotta / burnt sienna tones
• TO state zones → warm sage green tones
• The turning-point → muted champagne gold glow
• Background / negative space → warm cream (#F5EDE0)
• Lighting: soft warm cinematic — directional golden-hour light, deep elegant shadows, large upper-third negative space reserved for text overlay
• NEVER use cold teal, blue, pure white, or cool grey

━━━ OUTPUT ━━━
Return ONLY valid JSON — no markdown fences, no ### headers, no extra text.

• "title": The single most powerful phrase from the post. Max 8 Arabic words.
• "support": One grounded supporting sentence. Max 15 Arabic words.
• "symbol": Full English image-generation prompt written as ONE or TWO flowing prose paragraphs. No headers, no labels. Describe: what object, where it is placed, what it looks like in the FROM zone vs the TO zone, specific colors, lighting direction, texture, and mood. This goes directly into an AI image generator.
• "concept_ar": 1–2 short warm Arabic sentences describing what the image shows and why it relates to the post. For a non-technical Arabic reader. No English words.
• Use \\n for line breaks to keep valid JSON.
• JSON format exactly: {{"title": "...", "support": "...", "symbol": "...", "concept_ar": "..."}}

APPROVED POST:
{approved_text}"""

    CONCEPT_EXPANSION_PROMPT = """You are a visual content director for Coach Sihame, a somatic trauma therapy coach.

The coach has described her vision in Arabic:
"{concept_ar}"

Your job: translate and expand this into a precise, cinematic English image-generation prompt.

STEP 1 — IDENTIFY THE CORE OBJECT OR PHENOMENON
If the coach described a specific object or scene, honor it. If she described only a feeling or concept, choose ONE surprising real-world object to embody it — drawn from domains like: astronomy, glassblowing, geology, botany, architecture, cartography, metallurgy, culinary arts, weaving light, marine biology, ancient ruins, or physics. Do not default to the obvious.

STEP 2 — DESCRIBE THE TRANSFORMATION THROUGH THAT OBJECT
Show the FROM state (tension, fear, shutdown) on one side and the TO state (release, safety, aliveness) on the other, using the form and texture of your chosen object.

STEP 3 — MAP BRAND COLORS ONTO THE OBJECT'S NATURAL FORMS
• FROM zones → muted terracotta / burnt sienna
• TO zones → warm sage green
• Turning point → muted champagne gold glow
• Background → warm cream (#F5EDE0)
• Lighting: soft warm cinematic, directional golden-hour light, deep elegant shadows, large upper-third negative space for text
• NEVER cold teal, blue, pure white, or cool grey

Write ONE or TWO flowing prose paragraphs. No markdown headers. No labels. Be specific: name the object, describe its FROM and TO zones, describe the exact colors on each part, the lighting direction, and the mood. This prompt goes directly into an AI image generator.

Return ONLY the expanded English image prompt. Nothing else."""

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
Warm, comforting editorial elegance. Quiet integration. Poetic and artistic. Handcrafted physical reality, not machine-generated. 8K resolution. Highly detailed photorealistic textures matching the specific objects, materials, or atmosphere described."""

    # Polling configuration
    # Kie.ai image generation takes 250-300s in practice; budget 6 minutes to be safe.
    POLL_INITIAL_DELAY: float = 10.0   # wait a bit longer before first check
    POLL_INTERVAL: float = 6.0         # check every 6 seconds
    POLL_MAX_ATTEMPTS: int = 60        # 60 × 6s = 360s (~6 minutes)

    def __init__(self, llm_adapter: GeminiChatAdapter | None = None) -> None:
        self.llm_adapter = llm_adapter or GeminiChatAdapter(
            api_key=settings.KIE_API_KEY,
            base_url=settings.KIE_GEMINI_PRO_BASE_URL,
            model_name=settings.MODEL_PRIMARY,
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
        """Use LLM to extract headline, body, visual concept, and Arabic summary from approved text.

        Returns:
            dict with keys 'title', 'support', 'symbol', and 'concept_ar'
        """
        prompt = self.EXTRACTION_PROMPT.format(approved_text=approved_text)
        try:
            raw_text = await self.llm_adapter.complete_text(prompt)
            logger.debug("[extract_text_blocks] raw LLM response: %s", raw_text[:500])
            result = self._extract_json(raw_text)
            title = result.get("title", "").strip()
            support = result.get("support", "").strip()
            symbol = result.get("symbol", "").strip()
            concept_ar = result.get("concept_ar", "").strip()
            if not title or not support:
                raise DesignerServiceError("LLM returned empty title or support text.")
            if not symbol:
                logger.warning(
                    "[extract_text_blocks] symbol field is empty. "
                    "LLM keys returned: %s. Raw (first 800 chars): %s",
                    list(result.keys()),
                    raw_text[:800],
                )
            if not concept_ar:
                logger.warning("[extract_text_blocks] concept_ar field is empty. LLM keys: %s", list(result.keys()))
            logger.debug(
                "[extract_text_blocks] extracted — title=%r, support=%r, symbol_len=%d, concept_ar=%r",
                title, support, len(symbol), concept_ar[:80] if concept_ar else "",
            )
            return {"title": title, "support": support, "symbol": symbol, "concept_ar": concept_ar}
        except ModelAdapterError as e:
            raise DesignerServiceError(f"Text extraction failed: {e}") from e

    def build_image_prompt(self, title: str, support: str, symbol: str) -> str:
        """Construct the full image generation prompt from brand rules."""
        return self.IMAGE_PROMPT_TEMPLATE.format(title=title, support=support, symbol=symbol)

    async def expand_arabic_concept(self, concept_ar: str) -> str:
        """Expand the coach's natural Arabic visual description into a full technical English image prompt.

        The coach writes what she *feels* the image should show (in Arabic).
        This method translates + expands that into the detailed English prompt
        that the image generator needs, while enforcing all brand visual rules.

        Args:
            concept_ar: Natural Arabic description from the coach, e.g.
                        "أريد صورة تُظهر يدين: واحدة مشدودة وأخرى مرتاحة"
        Returns:
            Full English image generation prompt following brand guidelines.
        """
        prompt = self.CONCEPT_EXPANSION_PROMPT.format(concept_ar=concept_ar)
        try:
            expanded = await self.llm_adapter.complete_text(prompt)
            expanded = expanded.strip()
            # Strip any accidental code fences
            expanded = self._strip_code_fences(expanded)
            logger.debug("[expand_arabic_concept] expanded symbol length=%d", len(expanded))
            return expanded
        except ModelAdapterError as e:
            raise DesignerServiceError(f"Concept expansion failed: {e}") from e

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
