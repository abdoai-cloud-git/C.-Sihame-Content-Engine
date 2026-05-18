from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.log_collector import collector
from app.models.schemas import DraftGenerationResult, TextModel


class ModelAdapterError(RuntimeError):
    pass


class GeminiChatAdapter:
    def __init__(self, api_key: str, base_url: str, model_name: str) -> None:
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete_text(self, prompt: str, role: str = "editor") -> str:
        collector.llm_call_start(self.model_name, role, len(prompt))
        t0 = time.monotonic()
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            if not getattr(response, "choices", None):
                raise ModelAdapterError(f"{self.model_name} returned unexpected format: {response}")
            content = response.choices[0].message.content
            if not content:
                raise ModelAdapterError(f"{self.model_name} returned empty content.")
            elapsed = int((time.monotonic() - t0) * 1000)
            collector.llm_call_done(self.model_name, role, elapsed, len(content))
            return content
        except Exception as exc:
            collector.llm_call_failed(self.model_name, role, str(exc))
            raise


class GPT55Adapter:
    """Adapter for GPT-5.x models via kie.ai /codex/v1/responses.
    Supports gpt-5-5 (~4s) and gpt-5-4 (~46s).
    """

    ENDPOINT = "https://api.kie.ai/codex/v1/responses"

    def __init__(self, api_key: str, model_name: str = "gpt-5-5") -> None:
        self.api_key = api_key
        self.model_name = model_name

    @staticmethod
    def extract_text_from_response(payload: Dict[str, Any]) -> str:
        for item in payload.get("output", []):
            if item.get("type") == "message":
                for block in item.get("content", []):
                    if block.get("type") == "output_text":
                        return block.get("text", "").strip()
        return ""

    async def complete_text(self, prompt: str, role: str = "primary") -> str:
        collector.llm_call_start(self.model_name, role, len(prompt))
        t0 = time.monotonic()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model_name,
            "stream": False,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            "reasoning": {"effort": "low"},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.ENDPOINT, headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
            text = self.extract_text_from_response(payload)
            if not text:
                raise ModelAdapterError(f"{self.model_name} returned no output_text blocks.")
            elapsed = int((time.monotonic() - t0) * 1000)
            collector.llm_call_done(self.model_name, role, elapsed, len(text))
            return text
        except Exception as exc:
            collector.llm_call_failed(self.model_name, role, str(exc))
            raise


class TextModelRouter:
    """3-tier fallback chain.

    GENERATION (via /codex/v1/responses):
      1. GPT-5.5 (gpt-5-5)  -- primary   (~4s)
      2. GPT-5.4 (gpt-5-4)  -- secondary (~46s)
      3. Gemini Flash        -- tertiary last resort

    EDITING (voice-check, revise, platform adapt):
      Gemini Flash -- fast and reliable
    """

    def __init__(
        self,
        primary_adapter=None,
        secondary_adapter=None,
        tertiary_adapter=None,
        editor_adapter=None,
    ) -> None:
        api_key = settings.KIE_API_KEY
        if not api_key:
            raise RuntimeError("KIE_API_KEY is not set.")
        self.primary_adapter = primary_adapter or GPT55Adapter(api_key=api_key, model_name=settings.MODEL_PRIMARY)
        self.secondary_adapter = secondary_adapter or GPT55Adapter(api_key=api_key, model_name=settings.MODEL_SECONDARY)
        self.tertiary_adapter = tertiary_adapter or GeminiChatAdapter(api_key=api_key, base_url=settings.KIE_GEMINI_FLASH_BASE_URL, model_name=settings.MODEL_TERTIARY)
        self.editor_adapter = editor_adapter or GeminiChatAdapter(api_key=api_key, base_url=settings.KIE_GEMINI_FLASH_BASE_URL, model_name=settings.MODEL_EDITOR)

    _VOICE_CHECK_PROMPT = """\
You are a precision voice editor for Coach Sihame Atamnia.
A draft has just been revised. Your ONLY job is to catch and silently fix two categories of errors:

1. FORBIDDEN WORDS -- replace any word from this list with a Sihame-appropriate alternative:
   * harb / taghalab / iqtala / kasar / tajawaz / takhallas / iqta
   * fight / conquer / eliminate / break / overcome / get rid of
   Preferred alternatives: hudur, ihtawa, dhab, tawassa, istaqbal, i-tarafa, isma7, arkhi qabdatak

2. CRUSHED BREATHING -- if the body field contains a paragraph with 3+ consecutive sentences
   without a line break, insert line breaks between sentences to restore the somatic breathing rhythm.

If NEITHER error is present, return the draft UNCHANGED.
Do not restructure the content. Do not change any meaning. Do not add new ideas.

Return STRICT JSON with exactly these keys: "angle", "hook", "body", "cta", "safety_flags".
Do not include markdown fences.

DRAFT TO CHECK:
{draft_json}
"""

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
    def _extract_json_object(cls, raw_text: str) -> Dict[str, Any]:
        cleaned = cls._strip_code_fences(raw_text)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ModelAdapterError("Model response did not contain a valid JSON object.")
            data = json.loads(cleaned[start : end + 1])
        if isinstance(data.get("safety_flags"), list):
            data["safety_flags"] = " | ".join(str(s) for s in data["safety_flags"])
        return data

    async def _voice_check_draft(self, draft: DraftGenerationResult) -> DraftGenerationResult:
        draft_dict = draft.model_dump(exclude={"model_used"})
        prompt = self._VOICE_CHECK_PROMPT.format(draft_json=json.dumps(draft_dict, ensure_ascii=False))
        try:
            raw_text = await self.editor_adapter.complete_text(prompt)
            payload = self._extract_json_object(raw_text)
            return DraftGenerationResult(model_used=draft.model_used, **payload)
        except Exception as e:
            print(f"[VOICE CHECK PASSED OVER] {e}")
            return draft

    async def _complete_json(self, adapter, prompt: str, model_used: TextModel) -> DraftGenerationResult:
        raw_text = await adapter.complete_text(prompt)
        payload = self._extract_json_object(raw_text)
        return DraftGenerationResult(model_used=model_used, **payload)

    async def generate_primary_draft(self, prompt: str) -> DraftGenerationResult:
        """3-tier fallback: GPT-5.5 -> GPT-5.4 -> Gemini Flash."""
        try:
            return await self._complete_json(self.primary_adapter, prompt, TextModel.GPT_5_5)
        except Exception as e:
            collector.llm_fallback(failed_model=settings.MODEL_PRIMARY, fallback_model=settings.MODEL_SECONDARY, reason=str(e))

        try:
            return await self._complete_json(self.secondary_adapter, prompt, TextModel.GPT_5_4)
        except Exception as e:
            collector.llm_fallback(failed_model=settings.MODEL_SECONDARY, fallback_model=settings.MODEL_TERTIARY, reason=str(e))

        try:
            return await self._complete_json(self.tertiary_adapter, prompt, TextModel.GEMINI_3_FLASH)
        except Exception as e:
            raise ModelAdapterError(
                f"All writers failed. GPT-5.5={settings.MODEL_PRIMARY}, GPT-5.4={settings.MODEL_SECONDARY}, Flash={settings.MODEL_TERTIARY}. Last: {e}"
            ) from e

    async def revise_draft(self, current_draft: Dict[str, str], instruction: str, *, post_type: str, platform: str, voice_route: str, route_note: str) -> DraftGenerationResult:
        prompt = f"""You are the PRD-aligned editor for Coach Sihame.
Revise the draft below per the instruction. Preserve schema and brand discipline.

CONTEXT: post_type={post_type}, platform={platform}, voice_route={voice_route}
{route_note}

Return STRICT JSON: "angle", "hook", "body", "cta", "safety_flags". No markdown fences.

INSTRUCTION: {instruction}

CURRENT DRAFT:
{json.dumps(current_draft, ensure_ascii=False)}""".strip()
        draft = await self._complete_json(self.editor_adapter, prompt, TextModel.GEMINI_3_FLASH)
        draft = await self._voice_check_draft(draft)
        return draft

    _PLATFORM_RULES: dict[str, str] = {
        "telegram": "Reflective, spacious, text-led. No hashtags unless original had them. Somatic breathing rhythm.",
        "instagram": "Strong hook. Tight pacing. 3-5 Arabic hashtags. Concise CTA.",
        "facebook": "Slightly explanatory. Longer paragraphs OK. 1-2 thematic tags max.",
        "tiktok": "Max 150 words. Punchy opening. No academic framing. Direct and clear.",
    }

    async def adapt_platform_draft(self, approved_text: str, platform: str, *, post_type: str, voice_route: str, route_note: str) -> DraftGenerationResult:
        platform_rules = self._PLATFORM_RULES.get(platform.lower(), "Adjust for target platform.")
        prompt = f"""You are the PRD-aligned editor for Coach Sihame.
Adapt this approved post for {platform} without changing its meaning.

CONTEXT: post_type={post_type}, voice_route={voice_route}
PLATFORM RULES ({platform.upper()}): {platform_rules}

Return STRICT JSON: "angle"="", "hook"="", "body"=adapted text, "cta"="", "safety_flags"="". No markdown fences.

APPROVED POST:
{approved_text}"""
        return await self._complete_json(self.editor_adapter, prompt, TextModel.GEMINI_3_FLASH)