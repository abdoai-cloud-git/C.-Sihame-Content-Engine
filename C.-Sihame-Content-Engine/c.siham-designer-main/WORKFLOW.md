# WORKFLOW

## Canonical workflow

### 1. Input
User sends:
- post text
- optional platform
- optional post type
- optional visual preference

Default assumptions:
- platform = Instagram
- language = Arabic
- goal = premium, meaning-first, brand-consistent visual

---

### 2. Read the post for meaning
Use the core identity and decision files to identify:
- emotional territory
- post function
- whether the post is reflective, educational, guided-practice, concept-contrast, or promo
- what the post is actually trying to do

This step must prioritize meaning over surface mood.

---

### 3. Choose the visual mode
Use the core decision files to determine:
- visual type
- design goal
- emotional tone
- layout direction
- text hierarchy
- symbol logic
- color behavior

The system should choose the design because it matches the post meaning.
Not because it is merely attractive.

---

### 4. Decide text-on-image
Choose only the most meaningful text.
Do not force the full caption into the frame.

Decide:
- title or no title
- title-led vs paragraph-led vs guided-practice hybrid
- supporting lines
- bottom signature line if appropriate: `Siham Atamnia`
- title font
- support/body font
- signature font

Font choice belongs here, at the concept/decision stage.
It should not be left as a loose late-stage preference.

---

### 5. Build the image prompt
Translate the design decision into a generation-ready prompt.
The prompt should preserve:
- meaning
- brand taste
- Arabic text-friendliness
- negative space quality
- emotional safety
- explicit font-role instructions from the decision step

For typography-sensitive outputs, use a **typography-first prompt structure**.
That means the prompt should state clearly, line by line, which text block is being rendered and which materiality treatment belongs to it.

CRITICAL TYPOGRAPHY RULE: Add this as its own top-level block in the prompt:
```
TYPOGRAPHY RULE:
HEADLINE: Flowing Farsi-style Arabic calligraphy (خط الفارسي) with a gentle diagonal lean. Fluid connected letterforms with elegant thin-to-thick stroke variation, drawn with a fine pointed nib. Warm champagne gold ink color — not black. Gold leaf accents on diacritics (tashkeel) in the same warm gold tone. Poetic, spoken, artistic.
BODY: Clean, thick, geometric sans-serif Arabic letterforms. Sharp, precise strokes with even weight. Modern Kufic-inspired clarity.
SIGNATURE: "Siham Atamnia" in delicate pen-written cursive, fine-point ink, light and restrained.
PAPER: All typography rendered as real calligraphy ink on soft, textured cotton paper with subtle grain.
```
This rule is non-negotiable and must appear as a separate block, not buried inside a design paragraph.
Do not use font names (Rubik, Diwani, Rakkas) in image generation prompts — use materiality descriptors instead.

The prompt should say clearly which materiality treatment is intended for:
- title
- support/body text
- signature

Prefer a structure like:
- text block 1 = title / materiality descriptors / placement / importance
- text block 2 = support / materiality descriptors / placement / importance
- text block 3 = signature / materiality descriptors / placement / importance

Do not bury typography rules inside a long aesthetic paragraph.
Typography instructions should be explicit and easy for the model to parse.

#### Style reference library (optional)
If Nano Banana supports image-to-image reference, attach a curated style reference image showing the desired calligraphy + gold diacritics + paper texture look. This anchors the AI's "visual DNA" for the prompt.

Style references live in:
- `coach-siham-graphics-designer/support/style-references/` (create as needed)

This step is optional but dramatically improves first-attempt quality when available.

---

### 6. Generate
Recommended generation defaults:
- model: `nano-banana-pro`
- aspect ratio: `4:5` for feed
- iterative correction instead of full random rewrites

Operational rules live in:
- `coach-siham-graphics-designer/references/NANOBANANA_OPERATIONAL_RULES.md`

---

### 7. Evaluate
Check the result using:
- meaning match
- Arabic readability
- brand fit
- negative space quality
- bespoke feel vs generic drift
- correct signature placement when needed

Reject if it is only beautiful but semantically weak.

Evaluation files:
- `coach-siham-graphics-designer/core/evaluation/MEANING_ALIGNMENT_SCORECARD.md`
- `coach-siham-graphics-designer/core/evaluation/VISUAL_EVALUATION_WORKFLOW.md`

---

### 8. Improve only the top defects
Do not rewrite the whole direction every round.
Fix only the top 1–2 problems first.

Examples:
- weak concept contrast
- generic symbolism
- weak Arabic hierarchy
- signature too prominent

---

## Short version
Post -> meaning -> visual mode -> text selection -> prompt -> generate -> evaluate -> targeted fix
