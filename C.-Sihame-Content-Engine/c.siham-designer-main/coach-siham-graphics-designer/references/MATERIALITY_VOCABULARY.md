# MATERIALITY VOCABULARY

## Purpose
Define the canonical materiality terms used to describe typography to the AI image generation model (Nano Banana).
This prevents vocabulary drift across prompts and ensures visual consistency.

**Rule:** Always use these exact phrases. Do not paraphrase, abbreviate, or substitute synonyms.

---

## Calligraphic Headline — Farsi Script & Gold (خط الفارسي)

| Descriptor | Use when |
|---|---|
| "Flowing Farsi-style Arabic calligraphy with a gentle diagonal lean" | Always for calligraphic titles |
| "Fluid connected letterforms with elegant thin-to-thick stroke variation" | Always for calligraphic titles |
| "Drawn with a fine pointed nib" | Always for calligraphic titles |
| "Warm champagne gold ink color — not black" | Always — the ink color itself is gold, not just the diacritics |
| "Gold leaf accents on diacritics and tashkeel marks" | Always for calligraphic titles with diacritics |
| "Champagne/muted gold, not bright metallic" | Clarifier when "gold" alone may be misinterpreted |

### Do NOT use
- ❌ ~~"broad-nib calligraphy pen"~~ → Farsi uses a **pointed nib**, not broad
- ❌ ~~"gold foil"~~ → use "gold leaf"
- ❌ ~~"metallic gold"~~ → use "muted/champagne gold"
- ❌ ~~"black ink calligraphy"~~ → the headline ink color is **warm gold, not black**
- ❌ ~~"Diwani"~~ or ~~"Rakkas"~~ → those are different styles; our style is **خط الفارسي**
- ❌ ~~"calligraphy font"~~ → use the materiality descriptors above

---

## Body / Support Text — Geometric Clarity

| Descriptor | Use when |
|---|---|
| "Clean, thick, corporate-style geometric letterforms" | Default for body text |
| "Sharp, precise sans-serif strokes with even weight distribution" | Default for body text |
| "Modern Kufic-inspired geometric clarity" | When emphasizing the Arabic geometric heritage |

### Do NOT use
- ~~"Rubik"~~ → use geometric materiality descriptors
- ~~"sans-serif font"~~ → use "geometric sans-serif letterforms"
- ~~"modern font"~~ → too vague, use full descriptor

---

## Signature — Fine Ink

| Descriptor | Use when |
|---|---|
| "Delicate pen-written cursive, as if signed by hand with a fine-point ink pen" | Always for the Siham Atamnia signature |
| "Light ink impression, elegant and restrained" | Always for the signature |

### Do NOT use
- ~~"handwriting font"~~ → use pen-written descriptors
- ~~"script font"~~ → use ink pen materiality
- ~~"cursive"~~ alone → always pair with "pen-written" and "fine-point ink"

---

## Paper / Surface

| Descriptor | Use when |
|---|---|
| "Typography rendered as real calligraphy ink on soft, textured cotton paper with subtle grain" | Always as the paper anchor |
| "Textured paper" | Short form acceptable only when the full descriptor is already present |

### Do NOT use
- ~~"parchment"~~ → too medieval, use "textured cotton paper"
- ~~"canvas"~~ → wrong material, use "cotton paper"
- ~~"cardstock"~~ → too commercial, use "cotton paper"

---

## Emotional Atmosphere

| Descriptor | Use when |
|---|---|
| "Poetic, spoken, artistic" | Calligraphic / reflective layouts |
| "Quiet editorial elegance" | Clean, body-led layouts |
| "Handcrafted, not machine-generated" | All layouts — reinforces the premium artisanal feel |

---

## Quick Copy-Paste Reference

### Full calligraphic title block:
```
Flowing ink strokes with slight ink bleed on textured paper. Traditional sweeping curves, hand-drawn with a broad-nib calligraphy pen. Gold leaf accents on diacritics and tashkeel marks (champagne/muted gold). Poetic, spoken, artistic.
```

### Full body text block:
```
Clean, thick, geometric sans-serif Arabic letterforms. Sharp, precise strokes with even weight distribution. Modern Kufic-inspired geometric clarity.
```

### Full signature block:
```
"Siham Atamnia" in delicate pen-written cursive, as if signed by hand with a fine-point ink pen. Light ink impression, elegant and restrained.
```

### Full paper anchor:
```
All typography rendered as real calligraphy ink on soft, textured cotton paper with subtle grain.
```

---

## Color Materiality — Coach Confirmed Warm Earth Palette

> Use these exact color descriptions in prompts. Nano Banana responds to material color descriptions, not hex codes.

### Primary Background
```
Warm cream linen background, soft and inviting like aged cotton paper
```

### Warm Accent (Terracotta)
```
Warm terracotta clay tones, muted burnt orange, earthy sienna
```

### Calm Accent (Sage)
```
Muted warm sage green, earthy olive-tinted green, not teal, not blue-green
```

### Sacred Glow (Gold)
```
Muted champagne gold, warm antique gold, not bright metallic, not shiny
```

### Neutral Ground
```
Warm greige, warm taupe, soft parchment gray
```

### Full Palette Block (copy-paste for prompts):
```
COLOR PALETTE: Warm, comforting earth tones. Background: warm cream linen. Accents: muted terracotta/burnt orange and warm sage green. Glow: muted champagne gold as a single point of light. Neutral: warm greige/taupe. Do NOT use cold teal, blue, pure white, or cool gray.
```

### Forbidden Color Language (never use in prompts)
- ❌ ~~"sage"~~ alone → say "warm sage green, not teal"
- ❌ ~~"teal"~~ → forbidden completely
- ❌ ~~"navy"~~ or ~~"blue"~~ → forbidden
- ❌ ~~"white background"~~ → use "warm cream linen background"
- ❌ ~~"gray"~~ alone → say "warm greige" or "warm taupe"
- ❌ ~~"gold metallic"~~ → say "muted champagne gold"
