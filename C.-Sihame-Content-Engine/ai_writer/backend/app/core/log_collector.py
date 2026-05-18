"""
log_collector.py — In-memory structured event log for developer visibility.

This is a builder-only tool. It captures key events (LLM calls, draft lifecycle,
image jobs, errors) in a fixed-size ring buffer.

Access via: GET /api/v1/admin/logs?token=<ADMIN_LOG_TOKEN>
Never expose this endpoint or token to end users.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Optional


# ── Event types ──────────────────────────────────────────────────────────────

class Level:
    INFO  = "INFO"
    WARN  = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


@dataclass
class LogEvent:
    ts: float                          # Unix timestamp
    level: str                         # INFO | WARN | ERROR | DEBUG
    event: str                         # short machine-readable key
    msg: str                           # human-readable summary
    data: Dict[str, Any] = field(default_factory=dict)  # arbitrary context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts":    self.ts,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.ts)),
            "level": self.level,
            "event": self.event,
            "msg":   self.msg,
            "data":  self.data,
        }


# ── Ring-buffer collector (singleton) ────────────────────────────────────────

class LogCollector:
    """Thread-safe-enough ring buffer for structured log events.

    Not meant for high-throughput production tracing — purely for developer
    visibility into what the backend is doing during a session.
    Max 500 entries; oldest are dropped automatically.
    """

    MAX_ENTRIES = 500

    def __init__(self) -> None:
        self._buf: Deque[LogEvent] = deque(maxlen=self.MAX_ENTRIES)

    def _push(
        self,
        level: str,
        event: str,
        msg: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._buf.append(LogEvent(
            ts=time.time(),
            level=level,
            event=event,
            msg=msg,
            data=data or {},
        ))

    # ── Convenience helpers ───────────────────────────────────────────────────

    def info(self, event: str, msg: str, **data: Any) -> None:
        self._push(Level.INFO, event, msg, data)

    def warn(self, event: str, msg: str, **data: Any) -> None:
        self._push(Level.WARN, event, msg, data)

    def error(self, event: str, msg: str, **data: Any) -> None:
        self._push(Level.ERROR, event, msg, data)

    def debug(self, event: str, msg: str, **data: Any) -> None:
        self._push(Level.DEBUG, event, msg, data)

    # ── Domain-specific helpers ───────────────────────────────────────────────

    def draft_requested(self, raw_input: str, post_type: str, platform: str) -> None:
        self.info("draft.requested",
                  f"Generate draft — type={post_type} platform={platform}",
                  raw_input_preview=raw_input[:120],
                  post_type=post_type,
                  platform=platform)

    def llm_call_start(self, model: str, role: str, prompt_chars: int) -> None:
        self.info("llm.call.start",
                  f"LLM call → {model} [{role}]",
                  model=model, role=role, prompt_chars=prompt_chars)

    def llm_call_done(self, model: str, role: str, elapsed_ms: int, output_chars: int) -> None:
        self.info("llm.call.done",
                  f"LLM done ← {model} [{role}] in {elapsed_ms}ms",
                  model=model, role=role, elapsed_ms=elapsed_ms, output_chars=output_chars)

    def llm_call_failed(self, model: str, role: str, error: str) -> None:
        self.error("llm.call.failed",
                   f"LLM FAILED {model} [{role}]: {error[:200]}",
                   model=model, role=role, error=error[:500])

    def llm_fallback(self, failed_model: str, fallback_model: str, reason: str) -> None:
        self.warn("llm.fallback",
                  f"Primary {failed_model} failed → falling back to {fallback_model}",
                  failed_model=failed_model, fallback_model=fallback_model,
                  reason=reason[:300])

    def draft_saved(self, draft_id: str, model_used: str, voice_route: str) -> None:
        self.info("draft.saved",
                  f"Draft {draft_id} saved — model={model_used} route={voice_route}",
                  draft_id=draft_id, model_used=model_used, voice_route=voice_route)

    def draft_revised(self, draft_id: str, instruction_preview: str) -> None:
        self.info("draft.revised",
                  f"Draft {draft_id} revised",
                  draft_id=draft_id, instruction_preview=instruction_preview[:120])

    def draft_approved(self, draft_id: str) -> None:
        self.info("draft.approved", f"Draft {draft_id} approved", draft_id=draft_id)

    def draft_rejected(self, draft_id: str, reason: str) -> None:
        self.warn("draft.rejected",
                  f"Draft {draft_id} rejected",
                  draft_id=draft_id, reason=reason[:200])

    def image_job_queued(self, job_id: str, draft_id: str) -> None:
        self.info("image.job.queued",
                  f"Image job {job_id} queued for draft {draft_id}",
                  job_id=job_id, draft_id=draft_id)

    def image_job_done(self, job_id: str, image_url: str, elapsed_ms: int) -> None:
        self.info("image.job.done",
                  f"Image job {job_id} done in {elapsed_ms}ms",
                  job_id=job_id, image_url=image_url, elapsed_ms=elapsed_ms)

    def image_job_failed(self, job_id: str, error: str) -> None:
        self.error("image.job.failed",
                   f"Image job {job_id} FAILED: {error[:200]}",
                   job_id=job_id, error=error[:500])

    def supabase_error(self, operation: str, error: str) -> None:
        self.error("supabase.error",
                   f"Supabase {operation} failed: {error[:200]}",
                   operation=operation, error=error[:500])

    # ── Read access ───────────────────────────────────────────────────────────

    def recent(self, limit: int = 200, level: Optional[str] = None) -> list[Dict[str, Any]]:
        """Return the most recent `limit` events, newest first. Optionally filter by level."""
        events = list(self._buf)
        events.reverse()
        if level:
            events = [e for e in events if e.level == level.upper()]
        return [e.to_dict() for e in events[:limit]]

    def clear(self) -> None:
        self._buf.clear()


# ── Module-level singleton ────────────────────────────────────────────────────
collector = LogCollector()
