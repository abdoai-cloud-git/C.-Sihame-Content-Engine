# SOURCE OF TRUTH

## Purpose
Clarify which files define the system, which files support it, and which files are only examples or generated artifacts.

---

## Primary source-of-truth files
These are the core logic files that should drive the designer system.

### Core identity / meaning system
- `coach-siham-graphics-designer/core/identity/BRAND_CORE_SHEET.md`
- `coach-siham-graphics-designer/core/identity/BRAND_SIGNAL_EXTRACTION.md`
- `coach-siham-graphics-designer/core/identity/BRAND_TO_VISUAL_TRANSLATION.md`
- `coach-siham-graphics-designer/core/identity/SUBCONSCIOUS_ARCHITECTURE.md`

### Visual decision logic
- `coach-siham-graphics-designer/core/decision/VISUAL_MODES_FRAMEWORK.md`
- `coach-siham-graphics-designer/core/decision/POST_TO_DESIGN_TEXT_MAP.md`
- `coach-siham-graphics-designer/core/decision/CONCEPT_CONTRAST_VISUALS.md`
- `coach-siham-graphics-designer/core/decision/GUIDED_PRACTICE_VISUALS.md`

### Typography / text logic
- `coach-siham-graphics-designer/core/typography/TITLING_LAYER.md`
- `coach-siham-graphics-designer/core/typography/TYPOGRAPHIC_LAYOUT_ENGINE.md`

### Symbol logic
- `coach-siham-graphics-designer/core/symbols/MEANING_TO_SYMBOL_MAP.md`
- `coach-siham-graphics-designer/core/symbols/SYMBOLIC_VISUAL_LANGUAGE.md`

### Evaluation logic
- `coach-siham-graphics-designer/core/evaluation/MEANING_ALIGNMENT_SCORECARD.md`
- `coach-siham-graphics-designer/core/evaluation/VISUAL_EVALUATION_WORKFLOW.md`
- `coach-siham-graphics-designer/core/evaluation/BENCHMARK_TEST_PLAN.md`

### Operating entrypoint
- `coach-siham-graphics-designer/INDEX.md`

---

## Supporting files
These help implementation but are not the highest-level source of truth.

- `coach-siham-graphics-designer/support/GRAPHICS_DESIGNER_AGENT_BRIEF.md`
- `coach-siham-graphics-designer/support/SOCIAL_MEDIA_ADVISOR_SYSTEM.md`
- `coach-siham-graphics-designer/references/TYPOGRAPHY_RULES.md`
- `coach-siham-graphics-designer/references/NANOBANANA_OPERATIONAL_RULES.md`
- `coach-siham-graphics-designer/references/LEGACY_SKILL_MERGE.md`
- `coach-siham-graphics-designer/NANOBANANA_AUTO_IMPROVE_REFLECTION.md`
- `coach-siham-graphics-designer/scripts/`

---

## Examples, not source-of-truth
These should be treated as reference outputs, not governing logic.

- `examples/visual-decisions/*.json`
- `outputs/*.png`

These files are useful for:
- showing the shape of outputs
- regression comparisons
- benchmark references

But they should not silently redefine the system.

---

## Rule
If there is a conflict:
1. primary source-of-truth files win
2. supporting files adapt to them
3. examples never override them
