# NANOBANANA OPERATIONAL RULES

## Recommended generation defaults
- Model: `nano-banana-pro`
- Aspect ratio: `4:5` for feed, `9:16` for stories, `1:1` when needed
- Resolution: `2K` for iteration, `4K` for final hero outputs
- Output format: `png`

## Iteration discipline
### V1
Broad direction test.

### V2
Fix only the top 2 defects.
Do not rewrite the whole direction.

### V3
Polish:
- contrast
- spacing / negative space
- readability support
- bespoke feel

## Correction prompt pattern
Use language like:
- Keep the same emotional tone and overall composition.
- Fix only: [issue 1], [issue 2].
- Do not change: [locked element 1], [locked element 2].

## Retry / failure policy
- Retry transient failures: 429, 455, 500
- Do not blindly retry 401, 402, 422
- Use backoff (3s -> 8s -> 20s)

## Coach Sihame-specific rule
Never evaluate success only by beauty.
Evaluate by:
- brand taste
- emotional safety
- Arabic text-friendliness
- negative space quality
- whether it feels bespoke instead of generic
- whether the quiet brand sign-off `Siham Atamnia` is present in a bottom placement when appropriate

## Brand sign-off prompt rule
When generating final feed visuals for Coach Siham, request a subtle signature line:
- text: `Siham Atamnia`
- placement: center bottom, right bottom corner, or left bottom corner
- style: small, elegant, restrained, secondary
- never overpower the Arabic headline/body

## Typography-first prompting rule
When font consistency matters, do not rely on one buried sentence about typography.

Instead:
- define text blocks explicitly
- define each block's role explicitly
- define each block's **materiality** explicitly (ink, paper, accent treatment)
- define placement explicitly
- define hierarchy explicitly
- forbid extra decorative font substitution

Example pattern:
- title text = ... / title materiality = flowing ink calligraphy with gold leaf diacritics / title placement = top center / title importance = primary
- support text = ... / support materiality = clean geometric sans-serif letterforms / support placement = middle / support importance = secondary
- signature text = Siham Atamnia / signature materiality = fine-point ink pen cursive / signature placement = bottom right / signature importance = tertiary

## Emotional atmosphere anchors
For calligraphic and reflective layouts, anchor the prompt with emotional register cues:
- "Poetic, spoken, artistic"
- "Quiet editorial elegance"
- "Handcrafted, not machine-generated"

These atmospheric cues help the AI produce cohesive, emotionally resonant typography rather than sterile text.

## Critical typography rule
For Arabic font consistency and brand elegance, add this as its own top-level block in every prompt:
```
TYPOGRAPHY RULE:
HEADLINE: Flowing Farsi-style Arabic calligraphy (خط الفارسي) with a gentle diagonal lean. Fluid connected letterforms with elegant thin-to-thick stroke variation, drawn with a fine pointed nib. Warm champagne gold ink color — not black. Gold leaf accents on diacritics (tashkeel) in the same warm gold tone. Poetic, spoken, artistic.
BODY: Clean, thick, geometric sans-serif Arabic letterforms. Sharp, precise strokes with even weight. Modern Kufic-inspired clarity.
SIGNATURE: "Siham Atamnia" in delicate pen-written cursive, fine-point ink, light and restrained.
PAPER: All typography rendered as real calligraphy ink on soft, textured cotton paper with subtle grain.
```
This rule must be explicit, structured, and non-negotiable. Do not bury it inside design paragraphs.
Do not use font names (Rubik, Diwani, Rakkas) in image generation prompts — use materiality descriptors instead.