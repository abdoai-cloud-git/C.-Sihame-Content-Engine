# TYPOGRAPHIC LAYOUT ENGINE

## Purpose
Translate the chosen title/body structure into a visual text hierarchy.

This layer decides:
- whether title or body leads
- how much text appears on the image
- how Arabic text should be spaced
- where the text should sit in relation to the image

---

## Core hierarchy modes

### Mode A — Title-led
Use when:
- educational post
- concept contrast
- promo post
- short reflection hook

Structure:
- title = hero
- body = secondary support
- CTA/details = tertiary

### Mode B — Paragraph-led
Use when:
- long reflection
- prayer/reflection
- quiet contemplative post

Structure:
- no dominant large title
- paragraph block is hero
- emphasis comes from spacing, not giant headline

### Mode C — Guided-practice hybrid
Use when:
- guided practice post
- body has practical instructions
- title helps frame the meaning

Structure:
- short title = hero cue
- selected body lines = core support
- full caption remains outside image

---

## Arabic typography rules
- generous line height
- strong margin discipline
- avoid squeezing text into decorative compositions
- if too much text is needed, split into carousel or keep body in caption only

---

## Layout decision outputs
```json
{
  "hierarchy_mode": "Guided-practice hybrid",
  "title_role": "hero cue",
  "body_role": "selected supporting lines",
  "text_amount_on_image": "medium",
  "recommended_lines_on_image": [
    "إذا شعرتِ اليوم أنكِ متسارعة من الداخل",
    "المطلوب أن يصل جسدك رسالة أمان"
  ],
  "placement": "upper-left title with lower-left supporting body",
  "negative_space_requirement": "large left and upper zones",
  "title_materiality": "clean geometric sans-serif letterforms, sharp precise strokes",
  "body_materiality": "clean geometric sans-serif letterforms, even weight distribution",
  "signature_materiality": "delicate pen-written cursive, fine-point ink",
  "reasoning": "The image should communicate safety quickly while preserving readability; the full post remains in caption, while the design carries only the most meaningful lines."
}
```

## Font-role decision rule
Font roles must be decided here as part of the layout decision itself.
Outputs must use **materiality descriptors** for prompt compatibility (see `references/TYPOGRAPHY_RULES.md`).

Always decide explicitly:
- `title_materiality`
- `body_materiality`
- `signature_materiality`

Default:
- Title: "clean geometric sans-serif letterforms, sharp precise strokes" (equivalent to Rubik)
- Body/support: "clean geometric sans-serif letterforms, even weight distribution" (equivalent to Rubik)
- Signature: "delicate pen-written cursive, fine-point ink" (equivalent to Rubik cursive)

Optional accent:
- Calligraphic ink materiality ("flowing ink strokes, broad-nib calligraphy pen, gold leaf diacritics") may be used only for the title
- only if the title is 3 words or less
- only if it improves the concept while staying premium and readable

## Typography-first output rule
When preparing the final prompt, layout decisions should be easy to translate into explicit text blocks.

Preferred structure:
- title text + title materiality + title placement + title importance
- support text + support materiality + support placement + support importance
- signature text + signature materiality + signature placement + signature importance

This should reduce font instructions getting lost inside broad visual prompting.
Do not use font names (Rubik, Diwani, Rakkas) in the final prompt — always translate to materiality descriptors.

---

## Signature / name line rule
For Coach Siham feed visuals, include the brand name in English as:
- `Siham Atamnia`

Placement options:
- center bottom
- right bottom corner
- left bottom corner

Default behavior:
- prefer a quiet bottom signature line
- keep it visually secondary to the main Arabic message
- use small, elegant, restrained typography
- never let the signature compete with the title or body
- do not place it in the upper half of the design unless explicitly requested

This is a consistency rule, not a decorative flourish.
The name should feel like a subtle brand sign-off.

## Rule
The design should never try to fit the full post just because space exists.
Only the most meaningful lines should go on-image.
The rest stays in the caption.
