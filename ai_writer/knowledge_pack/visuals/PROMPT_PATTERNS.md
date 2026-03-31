# PROMPT PATTERNS

This document provides the rules for constructing the `image_prompt` that the graphics designer brain will output. This prompt is intended to be fed directly to an image generation model (like Midjourney, DALL-E, or a designer building the asset in Figma).

## General Rules for `image_prompt` Construction

When the system outputs an `image_prompt`, it must follow these structural guidelines:

1.  **Format**: Be extremely descriptive. Do not include UI instructions in the image prompt (e.g., "put the text here"), but rather frame the composition to *allow* for text placement.
2.  **Subject**: Define the central visual element (abstract shape, landscape, elegant object, portrait).
3.  **Atmosphere & Lighting**: Define the mood (e.g., cinematic lighting, soft morning glow, muted studio light, chiaroscuro).
4.  **Color Palette**: explicitly pass the requested color direction (e.g., "muted beige and warm earth tones", "desaturated sage green with soft white").
5.  **Style & Medium**: Define how it should look (e.g., "minimalist 3D render", "high-end editorial photography", "fine art abstract painting", "clean geometric layout").
6.  **Composition/Negative Space**: crucial for Coach Sihame's style. Explicitly ask for "massive negative space", "clean simple background", or "asymmetrical layout leaving the right side empty for text".

## Examples by Post Type

### For a Refection Visual / Quote Card
**Pattern**: `[Subject/Metaphor], [Lighting], [Color Palette], massive negative space, minimalist editorial photography, deeply emotional and calming atmosphere.`
*   *Example*: "A single beam of soft morning sunlight hitting a smooth, minimal beige wall, massive negative space on the left side, muted earthy tones, high-end editorial photography, deeply calm and grounding atmosphere, clean composition."

### For a Promotional Visual
**Pattern**: `[Elegant Object/Scene], [Clean Lighting], [Brand Colors], crisp and highly legible composition, minimalist design, premium aesthetic.`
*   *Example*: "A closed, premium hardcover book sitting on a minimal linen table, shot from above, muted neutral colors, soft shadow, massive clean beige negative space at the top half of the image for text placement, high-end luxury aesthetic, sharp and elegant."

### For an Educational Post (Background Concept)
**Pattern**: `[Subtle Texture/Gradient], [Soft Lighting], [Brand Colors], extremely minimal, no distraction, clean canvas.`
*   *Example*: "A very soft, blurred gradient going from warm sand to soft charcoal, extremely smooth transition, no harsh lines, clean minimalist background, elegant and premium, large negative space."

### Symbolic Emotional Visual
**Pattern**: `[Metaphorical Subject], [Ethereal Lighting], [Muted Palette], soft focus, evocative, spiritual depth.`
*   *Example*: "A gentle ripple on a dark, perfectly still body of water, muted charcoal and deep navy tones, soft ethereal lighting, massive dark negative space at the top, deeply spiritual and settling, minimalist composition."

## What to NEVER include in the `image_prompt`:
*   Never ask the image generator to write text (e.g., "Write the words 'Inner Peace'").
*   Never use cheap style keywords (e.g., "cartoon", "vector art", "clipart", "funny").
*   Never use overly detailed, chaotic scenes. Maintain simplicity.
