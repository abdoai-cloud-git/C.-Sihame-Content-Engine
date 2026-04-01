from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.schemas import DraftGenerationResult, TextModel


class ModelAdapterError(RuntimeError):
    pass


class GeminiChatAdapter:
    def __init__(self, api_key: str, base_url: str, model_name: str) -> None:
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete_text(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        if not getattr(response, "choices", None):
            print(f"[DEBUG] Raw response: {response}")
            raise ModelAdapterError(f"{self.model_name} returned unexpected format: {response}")
            
        content = response.choices[0].message.content
        if not content:
            raise ModelAdapterError(f"{self.model_name} returned empty content.")
        return content


class ClaudeMessagesAdapter:
    def __init__(self, api_key: str, endpoint: str, model_name: str) -> None:
        self.api_key = api_key
        self.endpoint = endpoint
        self.model_name = model_name

    @staticmethod
    def extract_text_from_response(payload: Dict[str, Any]) -> str:
        parts = []
        for block in payload.get("content", []):
            text = block.get("text")
            if text:
                parts.append(text)
        return "\n".join(parts).strip()

    async def complete_text(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.endpoint, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
        text = self.extract_text_from_response(payload)
        if not text:
            raise ModelAdapterError(f"{self.model_name} returned no text blocks.")
        return text


class TextModelRouter:
    def __init__(
        self,
        primary_adapter: Optional[GeminiChatAdapter] = None,
        secondary_adapter: Optional[ClaudeMessagesAdapter] = None,
        editor_adapter: Optional[GeminiChatAdapter] = None,
    ) -> None:
        api_key = settings.KIE_API_KEY
        self.primary_adapter = primary_adapter or GeminiChatAdapter(
            api_key=api_key,
            base_url=settings.KIE_GEMINI_PRO_BASE_URL,
            model_name=settings.MODEL_PRIMARY,
        )
        self.secondary_adapter = secondary_adapter or ClaudeMessagesAdapter(
            api_key=api_key,
            endpoint=settings.KIE_CLAUDE_MESSAGES_URL,
            model_name=settings.MODEL_SECONDARY,
        )
        self.editor_adapter = editor_adapter or GeminiChatAdapter(
            api_key=api_key,
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
    def _extract_json_object(cls, raw_text: str) -> Dict[str, Any]:
        cleaned = cls._strip_code_fences(raw_text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ModelAdapterError("Model response did not contain a valid JSON object.")
            return json.loads(cleaned[start : end + 1])

    async def _complete_json(self, adapter: Any, prompt: str, model_used: TextModel) -> DraftGenerationResult:
        raw_text = await adapter.complete_text(prompt)
        payload = self._extract_json_object(raw_text)
        return DraftGenerationResult(model_used=model_used, **payload)

    async def generate_primary_draft(self, prompt: str) -> DraftGenerationResult:
        try:
            return await self._complete_json(self.primary_adapter, prompt, TextModel.GEMINI_3_1_PRO)
        except Exception as primary_error:
            try:
                return await self._complete_json(self.secondary_adapter, prompt, TextModel.CLAUDE_SONNET_4_6)
            except Exception as secondary_error:
                raise ModelAdapterError(
                    f"Primary writer failed: {primary_error}. Secondary writer failed: {secondary_error}."
                ) from secondary_error

    async def revise_draft(self, current_draft: Dict[str, str], instruction: str) -> DraftGenerationResult:
        prompt = f"""
You are the PRD-aligned worker/editor for Coach Sihame.
Revise the structured draft below exactly according to the instruction while preserving the same schema.
Return STRICT JSON with exactly these keys: "angle", "hook", "body", "cta", "safety_flags".
Do not include markdown fences.

EDIT INSTRUCTION:
{instruction}

CURRENT DRAFT:
{json.dumps(current_draft, ensure_ascii=False)}
""".strip()
        return await self._complete_json(self.editor_adapter, prompt, TextModel.GEMINI_3_FLASH)

    async def adapt_platform_draft(self, approved_text: str, platform: str) -> DraftGenerationResult:
        prompt = f"""
You are the PRD-aligned worker/editor for Coach Sihame.
Your task is to take this approved post and specifically adapt its formatting, structure, and spacing for the {platform} platform.
Do NOT change the core meaning or the voice. Adjust only paragraph lengths, text formatting constraints, use of emojis, or hashtags appropriate for {platform}.
Return EXACTLY the adapted text inside the "body" field of the JSON. For "angle", "hook", "cta", and "safety_flags", provide empty strings.

Return STRICT JSON with exactly these keys: "angle", "hook", "body", "cta", "safety_flags".
Do not include markdown fences.

APPROVED POST:
{approved_text}
""".strip()
        return await self._complete_json(self.editor_adapter, prompt, TextModel.GEMINI_3_FLASH)
