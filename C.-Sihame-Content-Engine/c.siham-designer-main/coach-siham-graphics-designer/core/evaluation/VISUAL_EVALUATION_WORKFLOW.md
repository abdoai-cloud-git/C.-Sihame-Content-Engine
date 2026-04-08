# VISUAL EVALUATION WORKFLOW

## Purpose
Define how Coach Sihame visuals should be evaluated after generation.

---

## Workflow

### Step 1 — Generate candidate visual
Input:
- post text
- visual decision JSON
- image prompt

### Step 2 — Identify visual mode
Label candidate as:
- Typography-first
- Symbolic/conceptual
- Embodied/atmospheric
- Educational/diagrammatic
- Promotional/offer

### Step 3 — Score it
Use `MEANING_ALIGNMENT_SCORECARD.md`.

### Step 4 — Decide
- Approve
- Iterate
- Reject

### Step 5 — If iterating
Fix only the top 2 failures.

---

## Rule
No image should be approved just because it is beautiful.
It must pass:
- meaning
- brand
- Arabic usability

---

## Preferred loop
V1 → score → fix top 2 issues → V2 → score → approve or V3

Avoid endless aesthetic wandering.
