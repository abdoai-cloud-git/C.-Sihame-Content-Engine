# Coach Sihame Graphics Designer Brain — Agent Brief

## Purpose
Build the **visual intelligence layer** for Coach Sihame’s content system.

This is **not** a generic AI image prompt generator.
It must function like a **brand-sensitive graphics designer brain** that understands:
- Coach Sihame’s tone
- her audience psychology
- her editorial boundaries
- her visual taste
- the difference between reflective, educational, promotional, and spiritually grounded content

The output should help the system make **design decisions first**, then generate visuals.

---

## Core Objective
Given a caption, post idea, or approved text draft, the system should determine:

1. the best **visual type**
2. the correct **design intention**
3. the right **layout direction**
4. the appropriate **emotional/visual tone**
5. the correct **color direction**
6. the right **text hierarchy**
7. the final **image/design prompt**
8. the list of **visual mistakes to avoid**
9. a **titling decision** for the design
10. a **typographic layout decision** for what text belongs on-image vs in caption

This layer must produce outputs that feel like they were guided by a thoughtful internal designer — not by a generic AI image tool.

---

## Design Role Definition
The system should behave like:

> **Coach Sihame’s internal visual designer**
>
> Someone who knows how to translate meaning into visuals while protecting:
> - elegance
> - emotional safety
> - Arabic readability
> - spiritual/psychological tone
> - non-generic premium presentation

It should not behave like:
- a random prompt writer
- a flashy social media template engine
- a generic Canva-style poster generator
- a fake luxury / overdesigned aesthetic bot

---

## Inputs
The visual designer brain should expect inputs such as:

- caption text
- raw content idea
- approved final post text
- platform (`Instagram`, `Facebook`, `Telegram`)
- optional post type
- optional user design request (e.g. calm / premium / symbolic / educational / quote / infographic)
- optional language (`Arabic`, `English`)

---

## Required Outputs
The system should return structured JSON in this shape:

```json
{
  "visual_type": "",
  "design_goal": "",
  "emotional_tone": "",
  "layout_direction": "",
  "text_hierarchy": "",
  "color_direction": "",
  "visual_elements": [],
  "image_prompt": "",
  "avoid": [],
  "reasoning_summary": ""
}
```

### Meaning of fields
- **visual_type** → quote card / educational visual / story visual / infographic / symbolic image / promo visual / cover
- **design_goal** → what the design is trying to achieve (clarify, soothe, invite, explain, convert, etc.)
- **emotional_tone** → calm / intimate / warm / structured / spiritual / scholarly / etc.
- **layout_direction** → how the composition should be arranged
- **text_hierarchy** → what should dominate visually and how reading flow should work
- **color_direction** → palette behavior, contrast level, warmth/coolness, restraint
- **visual_elements** → objects, motifs, icon families, textures, symbolism, composition anchors
- **image_prompt** → final visual generation prompt for downstream image model
- **avoid** → design mistakes / unwanted aesthetics / bad prompt directions
- **reasoning_summary** → short explanation of why this visual direction was chosen

---

## Context Sources
The visual designer brain must be aligned with the existing knowledge files.

### It should use and respect:
- style files
- voice/methodology files
- post-type logic
- editorial boundaries
- any visual identity rules that exist now or will be added

### Important note
The visual layer is **supporting the meaning of the content**.
It should not ignore the writing system.
It must stay aligned with:
- Coach Sihame’s methodology
- her audience’s emotional needs
- her brand’s soft but premium positioning

---

## Taste Profile
The visual taste should feel:

- premium
- calm
- elegant
- emotionally safe
- spiritually grounded
- psychologically intelligent
- minimal but not empty
- soft but not weak
- professional but never corporate
- intentional, not decorative

### The design should never feel:
- loud
- trendy for the sake of trendiness
- childish wellness
- cheap social media template-based
- fake luxury
- cluttered
- hyper-generic AI poster style
- visually noisy
- over-symbolic in a cliché way

---

## Core Visual Rules

### Must do
- protect Arabic readability first
- preserve brand consistency across outputs
- use restraint and spacing well
- support the meaning of the post
- choose design based on message type, not random taste
- make text-led pieces feel elegant and intentional
- make promotional pieces invitational, never aggressive
- keep typography and composition readable on social platforms

### Must avoid
- clickbait visual language
- overdecorated spirituality motifs
- random gradients and random gold/black “luxury” styling
- template-looking quote cards
- too many visual elements competing at once
- weak text contrast
- English-first layout logic applied badly to Arabic content
- overcrowding the canvas
- mismatched imagery and emotional tone

---

## Design Decision Logic
The system should map meaning → format.

### Reflective / spiritual posts
Use:
- more breathing room
- softer atmosphere
- quieter composition
- symbolic or text-first treatment
- emotional elegance

Avoid:
- infographic feel
- over-structured educational layout
- hard CTA energy

### Educational posts
Use:
- stronger hierarchy
- clearer segmentation
- more structure
- explanatory layout logic
- infographic/card logic when needed

Avoid:
- overly abstract symbolism
- decorative noise that reduces clarity

### Promotional posts
Use:
- clarity
- stronger CTA visibility
- structured composition
- confidence without pressure
- readable benefit-first hierarchy

Avoid:
- urgency/FOMO look
- cheap sales aesthetics
- loud offer posters

### Story / intimate posts
Use:
- warmth
- human softness
- emotional proximity
- less rigid visual structure

Avoid:
- cold “expert brand” look
- excessive polish that removes intimacy

### Quote / text-first posts
Use:
- strong typography
- careful spacing
- minimal visual support
- elegant restraint

Avoid:
- filler decorations
- template quote aesthetics

---

## Supported Visual Types
The system should be able to decide among:

- quote card
- educational post
- carousel cover
- infographic-style visual
- story visual
- symbolic emotional visual
- promotion/offer visual
- reflective text-first visual
- announcement visual

It should not treat all posts as the same design category.

---

## Platform Awareness
The visual logic should adapt to platform context.

### Instagram
- stronger visual polish
- stronger cover behavior
- grid consistency matters
- story/reel cover compatibility matters

### Facebook
- readability and directness matter more
- thumbnails and first-glance clarity matter
- less need for ultra-minimal abstraction

### Telegram
- practical clarity matters
- text-image relationship should support reading, not only visual branding

---

## What the Agent Should Produce
The coding/design agent should create:

1. **Visual decision engine logic**
2. **Titling layer logic**
3. **Typographic layout logic**
4. **Prompt generation rules**
5. **Design rules files**
6. **Taste guide / style logic**
7. **Do / Don’t file**
8. **JSON schema for visual outputs**
9. **Examples for multiple post types**
10. **Any missing support files needed for consistency**

### Recommended file outputs
- `VISUAL_IDENTITY_RULES.md`
- `VISUAL_TYPES.md`
- `DESIGN_DO_NOTS.md`
- `PROMPT_PATTERNS.md`
- `VISUAL_DECISION_MAP.md`
- `TITLING_LAYER.md`
- `TYPOGRAPHIC_LAYOUT_ENGINE.md`
- `POST_TO_DESIGN_TEXT_MAP.md`
- `GRAPHICS_DESIGNER_SCHEMA.json`

---

## Quality Bar
A good result should make it possible for the system to produce visuals that feel:

- consistent
- intentional
- tasteful
- emotionally intelligent
- platform-aware
- clearly aligned with Coach Sihame

A bad result would feel like:
- generic prompt engineering
- random aesthetics
- weak Arabic design sensitivity
- visual choices that do not match the meaning of the post

---

## Constraints
- Do not build a full design app here
- Do not overfocus on backend or database architecture
- Do not treat this as a full image-generation pipeline spec
- Focus on the **design brain** itself:
  - taste
  - rules
  - structure
  - visual logic
  - output schema

---

## Final Instruction
The result should feel like the foundation of a real **visual copilot** for Coach Sihame.

Do not optimize for generic output.
Optimize for:
- alignment
- taste
- restraint
- clarity
- emotional and brand coherence

All outputs should later be judged using a meaning-alignment evaluation system, not beauty alone.
The designer brain must be built with this assumption in mind.
