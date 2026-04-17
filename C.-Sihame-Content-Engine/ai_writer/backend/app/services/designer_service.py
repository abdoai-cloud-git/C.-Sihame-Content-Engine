from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.services.llm_router import GeminiChatAdapter, ModelAdapterError

logger = logging.getLogger(__name__)


class DesignerServiceError(RuntimeError):
    pass


class DesignerService:
    """Handles text extraction from approved posts and image generation via Kie.ai."""

    EXTRACTION_PROMPT = """You are the visual mind of Coach Sihame, a somatic trauma therapy coach.

Your role is not to decorate her posts. Your role is to find the hidden image inside each post — the one that makes the reader feel the meaning before they finish reading.

━━━ STEP 0 — CLASSIFY THE POST ━━━
Read the post and choose exactly ONE type:

• REFLECTION — deeply personal, inward-facing, the words carry the emotion. The image breathes quietly behind the text.
• CONTRAST — two inner states compared (regulation vs calming, boundary vs wall, reaction vs response, mindful vs mind-full). Needs a visual split between them.
• SOMATIC_PRACTICE — guides the reader through a body sensation, regulation practice, or self-contact. Body presence matters more than concepts.
• EDUCATIONAL — explains a mechanism (inner parts, the maestro, the nervous system). The image must make the concept visible.
• PROMOTIONAL — announces an offer, program, retreat, or masterclass. The image must feel invitational, elegant, confident — never pushy.
• STORY — an intimate personal anecdote, behind-the-scenes moment, or conversational message to the audience. Warm, human, close.

━━━ STEP 1 — FIND THE EMOTIONAL CENTER ━━━
From the post, extract:
• The core feeling or body sensation (e.g., "chest held tight", "breath that cannot settle", "weight that does not lift")
• For CONTRAST and SOMATIC_PRACTICE posts only: the two states (FROM state → TO state)
• The one question the reader is left holding after reading

━━━ STEP 2 — CHOOSE THE SYMBOL FROM SIHAME'S WORLD ━━━
Choose ONE object or natural form that physically embodies what you found in Step 1.
Draw from Coach Sihame's 2025–2026 symbolic world — objects that feel warm, contained, ancient, handcrafted, or quietly alive.

⚠️ PRIORITY ORDER: Always try the 2025–2026 symbols first. Only fall back to earlier ones if nothing fits.

── 2025–2026 SYMBOLS (Use First) ──

The maestro / inner conductor / orchestration:
→ an open conductor's hand held still at the center of gathering sound | the precise moment a baton lowers into waiting silence | a single anchor point from which motion radiates outward | a score laid open on a still table, no hand yet touching it | the hollow center of a circular form from which all arcs begin

The symphony / inner harmony / multiple inner parts:
→ several small vessels of different sizes arranged quietly around a shared center | a grouping of smooth stones settling into their own formation | scattered seed pods drawn together toward a warm hollow | concentric light rings converging inward to one still point | a collection of small ceramic forms each distinct yet arranged as one

Qitaf / harvest / the quiet fruit of a long journey:
→ a ripened branch bowing gently under the weight of its own fruit | a single grain suspended over an open palm just before landing | a threshold crossed with something held gently | a basket resting on a warm stone with what has been gathered | a single dried botanical form hanging in still air, everything already done

Sukoon / deep stillness / not silence-as-absence but presence-as-fullness:
→ a flat water surface with no movement but enormous depth implied beneath | a stone that has sat in one place long enough to become part of the earth | the held breath of a room just before something begins | a single horizontal line where water meets sky in early morning | a smooth palm-sized river stone resting on cream fabric

Return / homecoming / not change but arrival:
→ a door standing slightly open with warm interior light | a threshold worn smooth by returning feet | a path of stone leading toward a lit archway | a familiar curve in a landscape that signals arrival | a key resting still beside an open lock

Sarian / subtle flowing / movement invisible until felt:
→ a very slow river visible only by the lean of grass at its edge | a thin thread of pale smoke rising in completely still air | the edge of sand where shallow water retreats without drama | ripples on deep still water — not from above but from within | a barely perceptible gradient from one earth tone to the next

── CLASSIC SIHAME SYMBOLS (Fallback — still valid) ──

Body constriction / held breath / shutdown:
→ a tightly sealed clay vessel before firing | a compressed seed pod that has not yet opened | a knotted raw thread | geological strata under pressure | a dry root clenched in parched soil | compressed mineral layers in cross-section | a tightly folded new leaf that has not yet unfurled | a sealed beeswax form

Release / breath returning / expansion:
→ a seed pod's first opening | still water receiving a single drop and rippling outward gently | a knotted thread resolving into one clean line | a narrow river mouth opening into wide calm water | a tightly wound botanical spiral beginning to open | a flat stone allowing a single breath of water across its surface | a petal separating from a bud at its own pace | morning fog lifting from a warm valley floor

Safety / being held / containment:
→ a deep ceramic bowl with warm inner depth | an architectural arch with open breathable interior | a clay alcove lit softly from within | nested curves of worn basket weave | a cupped form as abstract geometric holding shape | a hollow in warm stone holding pooled light | a nest-form woven from dried grass with one warm egg | a thick-walled clay cup with steam | a stone doorway open to interior warmth | a low curved alcove in aged plaster

Stillness / witnessing / presence:
→ a perfectly still water surface with reflected champagne light | a single smooth horizontal horizon | the edge of dawn on a flat cream surface | one unhurried shaft of warm gold through an architectural threshold | a smooth river stone in open palm | the moment winter light enters an empty room | a single feather settled on still water

Inner multiplicity / the maestro / inner parts:
→ small scattered forms quietly gathering around a warm center point | concentric rings converging inward to a still point | a single conductor's anchor point from which motion radiates | a soft container holding multiple small inner forms | different-sized droplets meeting at a shared center | a cluster of seed forms around one larger core | a gathering of smooth pebbles around a single warm stone

Spiritual groundedness / divine light / fitrah:
→ champagne light refracted through aged crystal | the moment dawn first touches a still water surface | one precise shaft of warm gold light through an opening in stone | morning light arriving on closed eyelids | a warm ember in an open hand | the precise angle at which light folds over a curved earthen wall

Overwhelm / fragmentation / scatter (CONTRAST posts only — one side):
→ a dense knotted thread mass | compressed scattered clay fragments before they are gathered | tangled unresolved lines | visual weight without resolution | multiple seed pods scattered before gathering | torn layers of dried earth | a knot of raw fibers before combing

Transformation / threshold / crossing:
→ a half-unfolded botanical form mid-opening | the exact moment a knotted thread releases into a single clean line | a door left ajar with warm light beyond | a narrow passage where contained water opens into stillness | a seed mid-germination splitting at the seam | a folded form beginning to unfurl | a heel mark in soft earth at a threshold

Promotional anchor / invitation without pressure:
→ a smooth rounded stone resting on soft linen | a single sealed letter on warm paper | an open book on a still table with one candle beyond | a small vessel with its lid set beside it — ready but unhurried | a path of flat stepping stones leading toward open light

Story / intimacy / behind the scenes:
→ a warm cup on an imperfect wooden surface | a notebook open to a half-written page | a window with morning light and a simple interior | a worn chair in soft directional light | a threshold between inside warmth and outside quiet

━━━ STEP 3 — COMPOSE BASED ON POST TYPE ━━━

If REFLECTION:
• One soft symbol, centered or gently off-center in deep negative space
• Atmospheric, quiet — no split composition, no dramatic tension
• The object exists in stillness. It is not mid-action. It simply is.
• Large upper-third negative space for Arabic calligraphy

If CONTRAST:
• Split composition — FROM state (tension) on the left, TO state (opening) on the right
• The chosen object appears in both states: closed/compressed on the left, open/resolved on the right
• The single champagne gold glow marks the turning point at the center

If SOMATIC_PRACTICE:
• The object embodies the body sensation directly — it IS the sensation made visible, not a metaphor observed from outside
• Soft, warm, contained slow visual rhythm — this image must feel safe enough to breathe into
• Warm containment over dramatic contrast — even if there is a FROM→TO, it is gentle, not sharp

If EDUCATIONAL:
• The object must explain the concept simply and clearly — symbolic clarity over atmospheric beauty
• One clean central metaphor that makes the mechanism visible at a glance
• Composition is readable, not just felt

If PROMOTIONAL:
• One clean, beautiful anchor object centered with generous breathing space above and below
• No split composition — this is an invitation, not a contrast
• Warm cream background, high legibility space reserved for CTA text
• Confident, still, premium — never urgent or cluttered

If STORY:
• Close, warm, intimate — the object feels like it belongs in a real moment
• Slightly more cropped than a Reflection; more spontaneous but still curated
• Avoid high-concept symbolism — keep it human and physical
• Warm directional light, texture, grounded in a real surface

━━━ STEP 4 — APPLY BRAND PALETTE TO YOUR OBJECT ━━━
Map palette to the object's natural zones. Do not introduce new objects just to show color:
• Tension / constriction zones → muted terracotta (#C4784A) / burnt sienna
• Healing / expansion zones → warm sage green (#8A9E82), always warm-leaning, never cool or teal
• The single turning point glow → muted champagne gold (#C8A96B) — one point per design
• Background / negative space → warm cream (#F5EDE0)
• Secondary surface depth → warm greige (#B5A898)
• Lighting: soft warm cinematic — directional golden-hour light, deep elegant shadows, large upper-third negative space reserved for text overlay
• NEVER cold teal, blue, pure white, or cool grey

━━━ OUTPUT ━━━
Return ONLY valid JSON — no markdown fences, no ### headers, no extra text.

• "title": The single most powerful phrase from the post. Max 8 Arabic words.
• "support": One grounded supporting sentence. Max 15 Arabic words.
• "symbol": Full English image-generation prompt written as ONE or TWO flowing prose paragraphs. No headers. No labels. Describe: the object, its placement, what it looks like in each zone, exact colors on each part, lighting direction, texture, and mood. This goes directly into an AI image generator.
• "concept_ar": 1–2 short warm Arabic sentences describing what the image shows and why it connects to the post. For a non-technical Arabic reader. No English words.
• Use \\n for line breaks to keep valid JSON.
• JSON format exactly: {{"title": "...", "support": "...", "symbol": "...", "concept_ar": "..."}}

APPROVED POST:
{approved_text}"""

    CONCEPT_EXPANSION_PROMPT = """You are the visual mind of Coach Sihame, a somatic trauma therapy coach.

The coach has described what she wants the image to show, in Arabic:
"{concept_ar}"

Your job: honor her description exactly, then expand it into a precise, cinematic English image-generation prompt.

STEP 1 — HONOR THE COACH'S INTENT FIRST
Read her Arabic description carefully. If she named a specific object or scene, keep it faithfully — do not replace or override her choice. If she described only a feeling or inner state without naming an object, you may choose one — but it must come from Coach Sihame's symbolic world (see below).

STEP 2 — IF AN OBJECT IS NEEDED, CHOOSE FROM SIHAME'S 2025–2026 WORLD
Try these first — they reflect her current voice:
• The maestro / conductor → an open hand held still at the center of gathering sound | a conductor's anchor point from which motion radiates | a score lying open on a still table
• The symphony → several small vessels arranged around a shared center | sound rings converging to one still point | a cluster of distinct forms arranged as one
• Qitaf / harvest → a branch bowing gently under its own fruit | an open palm receiving a single grain | a basket resting on a warm stone
• Sukoon / stillness → flat water with depth implied beneath | a stone that has become part of the earth | the held breath of a room
• Return / arrival → a door ajar with warm interior light | a threshold worn smooth | a path of stone toward a lit archway
• Sarian / flowing → a very slow river visible by the lean of grass | thin smoke rising in still air | water retreating from smooth sand

If none of these fit, fall back to classic Sihame symbols:
• Body constriction → sealed clay vessel | compressed seed pod | knotted raw thread | dry clenched root
• Release / expansion → seed pod opening | still water receiving a drop | knotted thread resolving into one clean line
• Safety / being held → deep ceramic bowl | architectural arch with open interior | clay alcove lit from within | nested worn basket curves
• Stillness / presence → perfectly still water surface | single horizontal horizon | champagne light through a threshold
• Inner multiplicity → scattered small forms gathering toward a warm center | concentric rings converging to stillness
• Transformation → half-open botanical form | thread releasing into a clean line | narrow passage opening into calm water

STEP 3 — ONLY ADD A CONTRAST IF THE COACH'S DESCRIPTION IMPLIES IT
If her description clearly has two states (before/after, closed/open, tension/release) — show them:
• Tension / FROM zones → muted terracotta (#C4784A) / burnt sienna, warm-leaning
• Release / TO zones → warm sage green (#8A9E82), always warm, never cool or teal
• The single turning point → muted champagne gold (#C8A96B)

If her description has only one state or is purely reflective — do NOT invent a contrast. Describe that single state fully and beautifully.

STEP 4 — APPLY BRAND PALETTE AND LIGHT
• Background → warm cream (#F5EDE0)
• Secondary depth surfaces → warm greige (#B5A898)
• Lighting: soft warm cinematic, directional golden-hour light, deep elegant shadows, large upper-third negative space reserved for Arabic text overlay
• NEVER cold teal, blue, pure white, or cool grey

Write ONE or TWO flowing prose paragraphs. No markdown headers. No labels. Be specific: name the object, describe its zones, the exact colors on each part, the lighting direction, texture, and mood. This prompt goes directly into an AI image generator.

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

    # ── Archetype taxonomy — used for exclusion tracking across generations ──
    # Maps known objects/keywords to their symbolic archetype category name.
    # When building exclusion blocks, we exclude at the ARCHETYPE level, not
    # just the object level, to prevent near-synonym repetition.
    ARCHETYPE_KEYWORDS: Dict[str, str] = {
        # Maestro / conductor
        "conductor": "MAESTRO", "maestro": "MAESTRO", "baton": "MAESTRO", "score": "MAESTRO",
        "anchor point": "MAESTRO", "orchestr": "MAESTRO",
        # Symphony / harmony
        "symphony": "SYMPHONY", "vessels arranged": "SYMPHONY", "concentric ring": "SYMPHONY",
        "cluster": "SYMPHONY", "gathering": "SYMPHONY",
        # Qitaf / harvest
        "qitaf": "QITAF", "harvest": "QITAF", "fruit": "QITAF", "branch bowing": "QITAF",
        "basket": "QITAF", "grain": "QITAF", "ripened": "QITAF",
        # Sukoon / stillness
        "sukoon": "STILLNESS", "flat water": "STILLNESS", "still water": "STILLNESS",
        "horizon": "STILLNESS", "river stone": "STILLNESS", "smooth stone": "STILLNESS",
        # Return / arrival / threshold
        "door": "THRESHOLD", "doorway": "THRESHOLD", "arch": "THRESHOLD",
        "threshold": "THRESHOLD", "passage": "THRESHOLD", "path of stone": "THRESHOLD",
        "corridor": "THRESHOLD",
        # Sarian / flowing
        "sarian": "FLOWING", "smoke rising": "FLOWING", "slow river": "FLOWING",
        "water retreating": "FLOWING", "sand": "FLOWING", "gradient": "FLOWING",
        # Containment / bowl / vessel
        "bowl": "CONTAINMENT", "vessel": "CONTAINMENT", "clay": "CONTAINMENT",
        "ceramic": "CONTAINMENT", "alcove": "CONTAINMENT", "basket weave": "CONTAINMENT",
        "cupped": "CONTAINMENT", "cup": "CONTAINMENT",
        # Botanical / seed / pod
        "seed pod": "BOTANICAL", "botanical": "BOTANICAL", "leaf": "BOTANICAL",
        "petal": "BOTANICAL", "bud": "BOTANICAL", "seed": "BOTANICAL",
        "flower": "BOTANICAL", "root": "BOTANICAL", "branch": "BOTANICAL",
        "germination": "BOTANICAL",
        # Thread / line / knot
        "thread": "THREAD", "knot": "THREAD", "fiber": "THREAD", "line": "THREAD",
        # Water / drop / ripple
        "water": "WATER", "drop": "WATER", "ripple": "WATER", "river mouth": "WATER",
        "pool": "WATER", "reflecting": "WATER",
        # Light / glow / lantern
        "light": "LIGHT", "lantern": "LIGHT", "flame": "LIGHT", "glow": "LIGHT",
        "shaft of": "LIGHT", "dawn": "LIGHT", "ember": "LIGHT", "crystal": "LIGHT",
        # Geological / stone / rock
        "geological": "GEOLOGICAL", "strata": "GEOLOGICAL", "mineral": "GEOLOGICAL",
        "stone": "GEOLOGICAL", "rock": "GEOLOGICAL", "pebble": "GEOLOGICAL",
        # Story / intimate objects
        "cup": "STORY_OBJECT", "notebook": "STORY_OBJECT", "window": "STORY_OBJECT",
        "chair": "STORY_OBJECT", "table": "STORY_OBJECT",
    }

    # Archetype opposition map — when an archetype is excluded, suggest its opposite
    ARCHETYPE_OPPOSITES: Dict[str, str] = {
        "CONTAINMENT": "THRESHOLD or FLOWING",
        "WATER": "GEOLOGICAL or THREAD",
        "BOTANICAL": "ARCHITECTURAL or GEOLOGICAL",
        "THREAD": "BOTANICAL or WATER",
        "LIGHT": "GEOLOGICAL or CONTAINMENT",
        "GEOLOGICAL": "WATER or BOTANICAL",
        "THRESHOLD": "CONTAINMENT or STILLNESS",
        "STILLNESS": "FLOWING or BOTANICAL",
        "FLOWING": "STILLNESS or CONTAINMENT",
        "MAESTRO": "QITAF or BOTANICAL",
        "SYMPHONY": "STILLNESS or THRESHOLD",
        "QITAF": "MAESTRO or CONTAINMENT",
        "STORY_OBJECT": "MAESTRO or BOTANICAL",
    }

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

    def detect_archetype(self, symbol_text: str) -> str:
        """Detect the dominant symbolic archetype from an English image prompt.

        Scans for known archetype keywords and returns the archetype name.
        Falls back to 'UNKNOWN' if nothing matches.
        """
        lower = symbol_text.lower()
        archetype_counts: Dict[str, int] = {}
        for keyword, archetype in self.ARCHETYPE_KEYWORDS.items():
            if keyword.lower() in lower:
                archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

        if not archetype_counts:
            return "UNKNOWN"
        return max(archetype_counts, key=lambda k: archetype_counts[k])

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

    REGENERATE_CONCEPT_PROMPT = """You are the visual mind of Coach Sihame, a somatic trauma therapy coach.

The coach's post has already been distilled into two short, precise texts:

TITLE (headline — the single most powerful phrase):
"{title}"

SUPPORT (the grounding sentence — the emotional core):
"{support}"

These two sentences are the concentrated juice of the post. Your job is to invent a FRESH visual concept rooted completely in these words.

{exclusion_block}

━━━ WHAT TO DO ━━━

1. Feel the emotional weight inside TITLE and SUPPORT. What body sensation, inner state, or life moment do they point to?

2. Choose ONE object or natural form from Coach Sihame's 2025–2026 symbolic world.

   ── 2025–2026 SYMBOLS (Try these first) ──
   • The maestro / conductor → open hand held still at center of gathering sound | anchor point from which motion radiates | a score lying open on a still table | a baton held at rest
   • The symphony / harmony → several small vessels arranged around a shared center | sound rings converging to one still point | different-sized forms arranged as one whole | a cluster of distinct seed forms near one larger core
   • Qitaf / harvest → a branch bowing gently under its own fruit | open palm receiving a single grain | a basket resting on warm stone | a dried botanical form with everything already complete
   • Sukoon / stillness → flat water with enormous depth implied beneath | a stone that has become part of the earth | the held breath of a room before something begins | a smooth river stone on cream linen
   • Return / arrival → a door slightly ajar with warm interior light | a threshold worn smooth by returning feet | a path of stepping stones toward an open lit archway
   • Sarian / flowing → a slow river visible only by the lean of grass at its edge | thin smoke rising in still air | water retreating from smooth sand | a barely visible gradient from one warm earth tone to the next

   ── CLASSIC SYMBOLS (Fallback if 2025–2026 don't fit) ──
   • Constriction / held breath → sealed clay vessel | compressed seed pod | knotted raw thread | dry clenched root | compressed mineral layers | sealed beeswax form
   • Release / expansion → seed pod first opening | still water receiving a drop | knotted thread resolving to one clean line | a petal separating from a bud at its own pace
   • Safety / being held → deep ceramic bowl | open architectural arch | clay alcove lit from within | nested worn basket weave | a hollow in warm stone holding pooled light
   • Stillness / presence → perfectly still water | single smooth horizon | champagne light through a threshold | a smooth river stone in open palm
   • Inner multiplicity → small forms gathering around a warm center | concentric rings converging to stillness | different-sized droplets meeting at a shared center
   • Spiritual groundedness → champagne light refracted through aged crystal | dawn touching still water | warm ember in open hand | the angle at which light folds over a curved earthen wall
   • Transformation → half-open botanical form | thread releasing into a clean line | narrow passage opening into calm water | a seed mid-germination

3. Apply the brand palette to the object's natural zones:
   • Tension / constriction → muted terracotta (#C4784A) / burnt sienna
   • Healing / expansion → warm sage green (#8A9E82) — warm, never cool or teal
   • Single turning-point glow → muted champagne gold (#C8A96B)
   • Background → warm cream (#F5EDE0)
   • Lighting: soft warm cinematic, directional golden-hour, large upper-third negative space for Arabic text
   • NEVER: cold teal, blue, pure white, cool grey

━━━ OUTPUT ━━━
Return ONLY valid JSON — no markdown, no headers, no extra text.
• "symbol": Full English image-generation prompt. ONE or TWO flowing prose paragraphs. Describe the object, its zones, exact colors, lighting, texture, mood. No labels.
• "concept_ar": 1–2 short warm Arabic sentences describing what the image shows and why it connects to the post — for a non-technical Arabic reader. No English words.
• JSON format exactly: {{"symbol": "...", "concept_ar": ""}}"""

    EXCLUSION_BLOCK_TEMPLATE = """━━━ ⚠️ WHAT YOU ALREADY TRIED — DO NOT REPEAT ━━━

You already generated these concepts. You MUST choose something visually and symbolically distinct from ALL of them:

{history_items}

ARCHETYPE-LEVEL RULES (most important):
{archetype_rules}

ADDITIONAL CONSTRAINTS:
• Pick a DIFFERENT physical object — not a near-synonym or variant of anything above
• Pick a DIFFERENT archetype category entirely
• The new image must feel visually completely distinct — different shape, material, texture, and mood
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    async def expand_arabic_concept(self, concept_ar: str) -> str:
        """Expand the coach's natural Arabic visual description into a full technical English image prompt.

        The coach writes what she *feels* the image should show (in Arabic).
        This method translates + expands that into the detailed English prompt
        that the image generator needs, while enforcing all brand visual rules.

        This is also the COACH OVERRIDE PATH: if the coach writes or edits
        concept_ar directly (rather than accepting the auto-generated one),
        call this method to build the image prompt from her intent — bypassing
        the full extract_text_blocks() cycle entirely.

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

    async def regenerate_concept(
        self,
        title: str,
        support: str,
        history: Optional[List[Dict[str, str]]] = None,
        # Legacy parameters kept for backward compatibility — prefer `history`
        previous_symbol: str = "",
        previous_concept_ar: str = "",
    ) -> Dict[str, str]:
        """Generate a fresh visual concept using ONLY the short distilled title + support.

        Injects an archetype-level anti-repetition block when previous concepts are
        provided, forcing the LLM to choose a wholly different symbolic category
        each time. Tracks up to the last 3 generations to avoid near-synonym drift.

        Args:
            title:              The short headline string (max ~8 Arabic words).
            support:            The single grounding sentence (max ~15 Arabic words).
            history:            List of previous generation dicts, each with keys:
                                  'symbol' (English prompt), 'concept_ar' (Arabic summary),
                                  and optionally 'archetype' (auto-detected if missing).
                                  Most recent last. Max 3 entries used.
            previous_symbol:    Legacy — single previous English image prompt (to avoid).
            previous_concept_ar: Legacy — single previous Arabic description (to avoid).

        Returns:
            dict with keys 'symbol' (English image prompt), 'concept_ar' (Arabic summary),
            and 'archetype' (detected archetype of the new symbol for future exclusion).
        """
        # ── Normalise to history list ────────────────────────────────────────
        if history is None:
            history = []

        # Back-compat: promote legacy single-item params into history
        if not history and previous_symbol and previous_concept_ar:
            history = [{"symbol": previous_symbol, "concept_ar": previous_concept_ar}]

        # Cap at last 3 entries
        history = history[-3:]

        exclusion_block = ""
        if history:
            history_items_text = ""
            excluded_archetypes: list[str] = []

            for i, entry in enumerate(history, 1):
                sym = entry.get("symbol", "")
                car = entry.get("concept_ar", "")
                arch = entry.get("archetype") or self.detect_archetype(sym)
                if arch and arch != "UNKNOWN" and arch not in excluded_archetypes:
                    excluded_archetypes.append(arch)
                history_items_text += (
                    f"[Attempt {i}]\n"
                    f"  Symbol: {sym[:300]}{'...' if len(sym) > 300 else ''}\n"
                    f"  Arabic description: {car}\n"
                    f"  Detected archetype: {arch}\n\n"
                )

            archetype_rules_lines = []
            for arch in excluded_archetypes:
                opposite = self.ARCHETYPE_OPPOSITES.get(arch, "a completely different category")
                archetype_rules_lines.append(
                    f"• EXCLUDED archetype: {arch} — switch to {opposite} instead"
                )
            archetype_rules = "\n".join(archetype_rules_lines) if archetype_rules_lines else "• Choose any archetype not represented above."

            exclusion_block = self.EXCLUSION_BLOCK_TEMPLATE.format(
                history_items=history_items_text.strip(),
                archetype_rules=archetype_rules,
            )

        prompt = self.REGENERATE_CONCEPT_PROMPT.format(
            title=title,
            support=support,
            exclusion_block=exclusion_block,
        )
        try:
            raw_text = await self.llm_adapter.complete_text(prompt)
            logger.debug("[regenerate_concept] raw LLM response: %s", raw_text[:500])
            result = self._extract_json(raw_text)
            symbol = result.get("symbol", "").strip()
            concept_ar = result.get("concept_ar", "").strip()
            if not symbol:
                logger.warning("[regenerate_concept] symbol field empty. Keys: %s", list(result.keys()))
            if not concept_ar:
                logger.warning("[regenerate_concept] concept_ar field empty. Keys: %s", list(result.keys()))

            detected_archetype = self.detect_archetype(symbol)
            logger.debug(
                "[regenerate_concept] done — symbol_len=%d, archetype=%s, concept_ar=%r",
                len(symbol), detected_archetype, concept_ar[:80] if concept_ar else "",
            )
            return {"symbol": symbol, "concept_ar": concept_ar, "archetype": detected_archetype}
        except ModelAdapterError as e:
            raise DesignerServiceError(f"Concept regeneration failed: {e}") from e


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
