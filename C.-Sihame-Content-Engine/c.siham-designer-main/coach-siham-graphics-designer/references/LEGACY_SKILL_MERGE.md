# LEGACY SKILL MERGE

This file consolidates the most useful reusable patterns pulled from older design / Nano Banana / prompting resources in the workspace and backups.

## Sources merged
- `skills/graphics-designer/references/social-design-system.md`
- `skills/graphics-designer/references/design-prompt-library.md`
- `skills/nanobanana-skill/references/prompt-framework.md`
- `skills/nanobanana-skill/references/nanobanana-api-sop.md`
- `recovered/kie-nano-banana-playbook.md`
- `skills/graphics-designer/scripts/design_brief_template.py`
- `skills/nanobanana-skill/scripts/prompt_scorecard.py`

---

## 1. Social design baseline (imported and adapted)
### Core templates
- Feed post (1:1)
- Portrait post / cover (4:5)
- Story / Reel cover (9:16)
- Carousel card set

### Useful structure from the old graphics-designer skill
- Hook zone
- Proof/details zone
- CTA zone

### Adaptation for Coach Sihame
Use the structure only when the post is educational or promotional.
Do **not** force this structure on reflective/spiritual posts.

---

## 2. Old prompt-library lessons worth keeping
### Keep
- clear subject
- clear palette
- clear hierarchy intention
- continuity / consistency add-on

### Reject from the old generic library
- generic marketing style phrasing
- default CTA-heavy visual language
- overly broad "social media design" wording

### Better adaptation
Use:
- "premium calm visual language"
- "Arabic-text-friendly negative space"
- "emotionally safe composition"
- "soft, bespoke, non-template layout"

---

## 3. Nano Banana prompt-engineering lessons worth keeping
### Strong inherited structure
- intent
- subject
- scene
- camera/composition
- palette/lookdev
- constraints
- output spec

### Best operational lessons kept
- V1 = broad generation
- V2 = fix top 2 defects only
- V3 = polish contrast / readability / composition

### Correction pattern to keep
- Keep everything from previous output except specific fixes
- Lock what must stay unchanged

This is highly useful for Coach Sihame image iteration.

---

## 4. Kie / Nano Banana operating knowledge worth keeping
### Important operational facts
- Model options: `google/nano-banana`, `google/nano-banana-edit`, `nano-banana-pro`
- Polling states: `waiting`, `queuing`, `generating`, `success`, `fail`
- Retry transient issues: 429 / 455 / 500
- Avoid blind retry on 401 / 402 / 422

### Best default for premium stills
- `model`: `nano-banana-pro`
- `aspect_ratio`: `4:5` or `1:1` for posts
- `resolution`: `2K` for iteration, `4K` for finals if needed
- `output_format`: `png`

---

## 5. What we are reusing directly for the new graphics designer
### Reused concepts
- design brief template
- prompt QA scorecard
- prompt iteration discipline
- Kie operational model knowledge
- simple social composition logic

### Reused with modification
- generic social prompt framework → rewritten into Coach Sihame taste framework
- old design prompt library → filtered through premium / calm / Arabic-safe rules

### Explicitly not reused
- generic marketing CTA styling
- generic logo-generation logic
- loud promotional design language
- broad "professional marketing" wording that weakens Sihame brand specificity

---

## 6. Merge rule for future additions
When importing from old design / prompting / Nano Banana skills:
1. Keep only reusable operating patterns
2. Rewrite them into Coach Sihame taste
3. Reject any generic marketing or template-heavy aesthetics
4. Prefer calm, premium, meaning-led design logic over generic social tactics
