import os
from typing import Dict, List

from app.core.config import settings
from app.models.schemas import ContextAssembly, RoutingMetadata, VoiceRoute


class DynamicContextBuilder:
    CORE_CONSTITUTION_FILES = [
        ("core", "SYSTEM_PROMPT.md"),
        ("core", "CLINICAL_BOUNDARIES.md"),
        ("core", "OUTPUT_RULES.md"),
        ("core", "DECISION_POLICY.md"),
        ("core", "DO_NOT_IMITATE.md"),
        ("core", "forbidden_topics.md"),
        ("core", "icp.md"),
        ("core", "PLATFORM_RULES.md"),
    ]

    ROUTE_TO_FILES: Dict[VoiceRoute, List[tuple[str, str]]] = {
        VoiceRoute.SOUL_2023: [
            ("voice", "VOICE_ROUTING_RULES.md"),
            ("voice", "STYLE_BIBLE_MASTER.md"),
            ("voice", "PATTERNS_MASTER.md"),
            ("voice", "PHRASEBANK_MASTER.md"),
            ("core", "METHODOLOGY_MAP.md"),
            ("core", "POST_TYPES.md"),
        ],
        VoiceRoute.METHODOLOGY: [
            ("voice", "VOICE_ROUTING_RULES.md"),
            ("core", "METHODOLOGY_MAP.md"),
            ("core", "POST_TYPES.md"),
        ],
        VoiceRoute.HYBRID: [
            ("voice", "VOICE_ROUTING_RULES.md"),
            ("voice", "STYLE_BIBLE_MASTER.md"),
            ("voice", "PATTERNS_MASTER.md"),
            ("voice", "PHRASEBANK_MASTER.md"),
            ("core", "METHODOLOGY_MAP.md"),
            ("core", "POST_TYPES.md"),
        ],
        VoiceRoute.RITUAL: [
            ("voice", "VOICE_ROUTING_RULES.md"),
            ("voice", "STYLE_BIBLE_MASTER.md"),
            ("voice", "PATTERNS_MASTER.md"),
            ("voice", "PHRASEBANK_MASTER.md"),
            ("rituals", "RITUAL_TEMPLATES_2023.md"),
            ("core", "METHODOLOGY_MAP.md"),
            ("core", "POST_TYPES.md"),
        ],
    }

    ROUTE_TO_EXAMPLES: Dict[VoiceRoute, List[tuple[str, str]]] = {
        VoiceRoute.SOUL_2023: [
            ("examples", "PRIMARY_GOLD_EXAMPLES.md"),
            ("examples", "RAW_TO_FINAL_EXAMPLES.md"),
        ],
        VoiceRoute.METHODOLOGY: [
            ("examples", "RAW_TO_FINAL_EXAMPLES.md"),
            ("examples", "SECONDARY_EXAMPLE_FRAGMENTS.md"),
        ],
        VoiceRoute.HYBRID: [
            ("examples", "RAW_TO_FINAL_EXAMPLES.md"),
            ("examples", "PRIMARY_GOLD_EXAMPLES.md"),
        ],
        VoiceRoute.RITUAL: [
            ("rituals", "RITUAL_TEMPLATES_2023.md"),
            ("examples", "PRIMARY_GOLD_EXAMPLES.md"),
        ],
    }

    SOUL_TYPES = {"reflection", "clinic story", "open questions"}
    RITUAL_TYPES = {"prayer / reflection", "monthly intention"}
    HYBRID_TYPES = {"promo"}

    def __init__(self):
        self.kb_dir = settings.KNOWLEDGE_PACK_DIR

    def _read_file(self, folder: str, filename: str) -> str:
        filepath = os.path.join(self.kb_dir, folder, filename)
        if not os.path.exists(filepath):
            return f"\n[Warning: {filename} not found in {folder}.]\n"
        with open(filepath, "r", encoding="utf-8") as handle:
            return handle.read()

    def _read_recent_feedback(self) -> str:
        # Assuming the feedback log is sitting in the ai_writer root directory
        filepath = os.path.join(os.path.dirname(self.kb_dir), "feedback_log.md")
        if not os.path.exists(filepath):
            return "No recent feedback available."
        
        with open(filepath, "r", encoding="utf-8") as handle:
            content = handle.read()
            # If the log gets too long, we only want the most recent feedback (top of the file below the header)
            # A simple approach: grab the first 3000 characters to keep context size manageable
            return content[:3000] + "\n...[truncated]" if len(content) > 3000 else content

    def _normalize_post_type(self, post_type: str) -> str:
        return post_type.strip().lower()

    def _resolve_route(self, post_type: str) -> VoiceRoute:
        normalized = self._normalize_post_type(post_type)
        if normalized in self.HYBRID_TYPES:
            return VoiceRoute.HYBRID
        if normalized in self.RITUAL_TYPES:
            return VoiceRoute.RITUAL
        if normalized in self.SOUL_TYPES:
            return VoiceRoute.SOUL_2023
        return VoiceRoute.METHODOLOGY

    def _render_sections(self, header: str, file_refs: List[tuple[str, str]]) -> str:
        rendered = [f"### {header} ###", ""]
        for folder, filename in file_refs:
            content = self._read_file(folder, filename)
            rendered.append(f"--- BEGIN {filename} ---")
            rendered.append(content)
            rendered.append(f"--- END {filename} ---")
            rendered.append("")
        return "\n".join(rendered)

    def build_payload(self, user_raw_input: str, post_type: str, platform: str) -> ContextAssembly:
        route = self._resolve_route(post_type)
        core_files = self.CORE_CONSTITUTION_FILES.copy()

        # Phase 4 conditional logic: inject specific files depending on post_type
        normalized_post_type = self._normalize_post_type(post_type)
        if normalized_post_type == "promo" or "offer" in normalized_post_type:
            core_files.append(("core", "offer_map.md"))
            core_files.append(("core", "objections.md"))
        elif normalized_post_type == "clinic story" or "story" in normalized_post_type:
            core_files.append(("core", "transformation_stories.md"))

        core_section = self._render_sections("CORE CONSTITUTION & RULES", core_files)
        route_section = self._render_sections("VOICE & METHODOLOGY LAYER", self.ROUTE_TO_FILES[route])
        example_section = self._render_sections("SELECTIVE CURATED EXAMPLES", self.ROUTE_TO_EXAMPLES[route])
        
        feedback_content = self._read_recent_feedback()
        feedback_section = f"### RECENT FEEDBACK & LESSONS LEARNED ###\n{feedback_content}\n"

        route_notes = {
            VoiceRoute.SOUL_2023: "Use the 2023 soul register. Prioritize body sensations, intimate pacing, and contemplative cadence.",
            VoiceRoute.METHODOLOGY: "Use the methodology-first register. Be clear, clinically safe, and avoid heavy 2023 metaphors.",
            VoiceRoute.HYBRID: "Start by touching the pain in the 2023 soul register, then transition into a grounded methodology-first explanation.",
            VoiceRoute.RITUAL: "Use the ritual register. Respect the recurring 2023 ritual templates and keep the tone devotional, contained, and steady.",
        }

        prompt = f"""
{core_section}

{route_section}

{example_section}

{feedback_section}

=========================================
EXECUTION POLICY
=========================================
- Active voice route: {route.value}
- Route instruction: {route_notes[route]}
- Platform target: {platform}
- Post type: {post_type}
- Clinical and output boundaries always override style.
- Return the response STRICTLY as a JSON object with exactly these keys:
  "angle", "hook", "body", "cta", "safety_flags"
- Do not include markdown fences.
- Do not include any image prompt or extra keys in this phase.

=========================================
USER REQUEST
=========================================
The Coach has provided the following raw input. Generate one PRD-aligned structured text draft.

RAW INPUT:
"{user_raw_input}"
=========================================
""".strip()

        injected_files = [filename for _, filename in self.CORE_CONSTITUTION_FILES + self.ROUTE_TO_FILES[route]]
        example_files = [filename for _, filename in self.ROUTE_TO_EXAMPLES[route]]

        metadata = RoutingMetadata(
            voice_route=route,
            injected_files=injected_files,
            example_files=example_files,
            notes=[route_notes[route]],
        )
        return ContextAssembly(prompt=prompt, routing_metadata=metadata)
