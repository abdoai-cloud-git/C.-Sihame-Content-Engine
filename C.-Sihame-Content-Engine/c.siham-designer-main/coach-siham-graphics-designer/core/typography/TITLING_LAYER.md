# TITLING LAYER

## Purpose
Create a meaning-linked title/headline layer for visual design.

The title is not just a shortened caption.
It is the **visual entry point** of the post.
It should make the design clearer, more memorable, and more connected to the post meaning.

---

## Core rule
Every post should answer:
1. Does it need a title on the design?
2. If yes, what kind of title?
3. Should the title be the hero, or should body text remain the hero?

---

## Title types

### 1. Concept Title
Use for educational or contrast posts.
Examples:
- التنظيم ليس التهدئة
- الجذر لا السطح
- الحدود ليست جدارًا

### 2. Reflective Line
Use for reflection visuals.
Examples:
- ليس كل بطء تعطّلًا
- أحيانًا ما تشعرين به ليس مبالغة

### 3. Practice Title
Use for guided practice posts.
Examples:
- رسالة أمان إلى الجسد
- عندما يهدأ الداخل
- تمرين قصير للعودة إلى الأمان

### 4. Offer Title
Use for promo visuals.
Examples:
- التسجيل مفتوح الآن
- مساحة جديدة تبدأ قريبًا

---

## Titling rules
- Must be shorter than the full caption
- Must preserve the meaning, not flatten it
- Must sound like Coach Sihame, not like ad copy
- Must support the visual mode
- Must not become clickbait
- Must leave visual room for a quiet bottom brand sign-off when used
- Must consider typography treatment: default to clean geometric sans-serif materiality. Allow calligraphic ink materiality (flowing strokes, gold leaf diacritics) only when the title is 3 words or less and the result still feels premium and readable.
- When outputting font decisions, use **materiality descriptors** (see `references/TYPOGRAPHY_RULES.md`) rather than font names for prompt compatibility.

---

## When NOT to use a title
Do not force titles when:
- the post is better as an editorial text block
- the reflection loses depth when compressed
- the typography should remain paragraph-led

In that case:
- body text becomes the hero
- title may be omitted or reduced to a very quiet line

---

## Output format for titling layer
```json
{
  "needs_title": true,
  "title_type": "Practice Title",
  "primary_title": "رسالة أمان إلى الجسد",
  "alternate_titles": [
    "عندما يهدأ الداخل",
    "عودة لطيفة إلى الأمان"
  ],
  "body_role": "supporting",
  "reasoning": "This post is a guided practice, so it benefits from a short meaning-led title that helps the design communicate safety and embodiment quickly."
}
```
