# BENCHMARK TEST PLAN

## Purpose
Create a structured test plan for validating the Coach Siham graphics designer brain.

The goal is not to generate random pretty images.
The goal is to verify whether the system can repeatedly produce visuals that are:
- meaning-aligned
- brand-consistent
- Arabic-friendly
- non-generic

---

## Test objective
Evaluate the full chain:

**post text → visual decision → title decision → typography decision → image prompt → generated image → evaluation**

---

## Benchmark set
Use a minimum of **15 benchmark posts**.

### Distribution
- 3 reflection posts
- 3 guided practice posts
- 3 educational posts
- 3 concept contrast posts
- 3 promotional / invitational posts

---

## What each benchmark entry must contain
For every benchmark post, record:

1. **Post text**
2. **Post type**
3. **Intended meaning**
4. **Desired emotional tone**
5. **Preferred visual mode**
6. **Expected symbol logic**
7. **Expected titling behavior**
8. **Expected text-on-image behavior**
9. **Generated prompt**
10. **Generated image**
11. **Meaning alignment score**
12. **Revision notes**

---

## Test workflow

### Step 1 — Choose benchmark post
Select one real Coach Siham post.

### Step 2 — Define expected outcome before generation
Write:
- what this post means
- what visual mode it should use
- what should appear visually
- what should not appear visually

### Step 3 — Run the designer brain
Generate:
- visual decision JSON
- titling recommendation
- typography/layout recommendation
- image prompt

### Step 4 — Generate image
Use Nano Banana Pro.

### Step 5 — Evaluate
Use:
- `MEANING_ALIGNMENT_SCORECARD.md`
- `VISUAL_EVALUATION_WORKFLOW.md`

### Step 6 — Iterate if needed
Fix only the top 2 problems.
Then rerun.

---

## Approval conditions
A benchmark candidate passes only if:
- Meaning Match >= 4
- Brand Consistency >= 4
- Arabic Text-Friendliness >= 4
- Non-Genericness >= 4
- no hard fail condition is triggered

---

## Hard fail conditions
Reject immediately if:
- the image is only mood-based with no meaning cue
- Arabic text cannot live on the image
- the visual mode is wrong for the post
- the symbolism is irrelevant or cliché
- the image looks like generic wellness content

---

## Benchmark success criteria
The system is considered to be improving if:
- later iterations score higher than earlier ones
- different post types stop collapsing into the same visual style
- guided practice stops looking like generic linen moodboards
- concept contrast visuals become immediately understandable
- promotional visuals remain invitational and premium

---

## What to learn from the benchmark phase
At the end of the benchmark phase, extract:
- what modes work best
- what symbols work best
- what prompts repeatedly fail
- what patterns should become defaults
- where the system still confuses mood with meaning

---

## Recommended order of testing
1. Reflection
2. Guided practice
3. Educational
4. Concept contrast
5. Promo

Reason:
This starts with simpler calm modes and moves toward higher semantic precision.

---

## Final rule
Do not call the system “working” because one image looks beautiful.
Call it working only when it passes multiple benchmark posts across multiple post types with consistent meaning alignment.
