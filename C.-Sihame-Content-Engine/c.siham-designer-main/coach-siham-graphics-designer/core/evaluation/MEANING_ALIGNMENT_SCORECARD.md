# MEANING ALIGNMENT SCORECARD

## Purpose
This scorecard evaluates whether a generated visual matches the **meaning** of the post, not just the mood.

It exists to stop the system from approving visuals that are:
- beautiful but generic
- calm but semantically weak
- brand-safe but conceptually off

---

## Core principle
A visual is successful only if it satisfies **both**:
1. **Brand consistency**
2. **Meaning alignment**

A mood-matching image alone is not enough.

---

## Scoring Method
Score each criterion from **0 to 5**.

### Score meanings
- **0** = failed completely
- **1** = weak / barely present
- **2** = partially present but not convincing
- **3** = acceptable baseline
- **4** = strong
- **5** = excellent / clearly right

---

## Criteria

### 1. Meaning Match
**Question:** Does the visual express the actual meaning/function of the post?

Examples:
- reflection post → should support contemplation
- guided practice post → should suggest embodied soothing / containment
- educational contrast post → should clarify the concept visually

### 2. Mood Match
**Question:** Does the visual carry the right emotional tone?

Examples:
- calm
- grounding
- invitational
- structured
- intimate

### 3. Symbol / Metaphor Relevance
**Question:** If symbolism is used, does it clarify the post meaning?

Good:
- contraction vs expansion
- knot vs untangled line
- contained warmth for guided practice

Bad:
- random soft fabric with no conceptual relation
- decorative symbolism with no meaning

### 4. Brand Consistency
**Question:** Does this feel like Coach Sihame’s visual world?

Check:
- premium softness
- restraint
- emotional safety
- non-generic composition
- no loud / corporate drift

### 5. Arabic Text-Friendliness
**Question:** Can Arabic typography live on this image comfortably?

Check:
- negative space
- hierarchy support
- contrast
- no clutter where text should sit

### 6. Non-Genericness
**Question:** Does the visual feel bespoke rather than stock / template / generic AI?

### 7. Functional Suitability
**Question:** Is this the right visual mode for the post?

Examples:
- reflection might need typography-first or atmospheric
- guided practice may need embodied cue
- concept contrast may need diagram/symbol split

---

## Total Score
### Out of 35

### Suggested interpretation
- **30–35** → strong / can approve
- **24–29** → promising but should iterate
- **18–23** → weak, likely too generic or semantically off
- **0–17** → reject

---

## Mandatory Gate Rules
Even if the total score is decent, reject the visual if either of these is true:

1. **Meaning Match < 3**
2. **Arabic Text-Friendliness < 3**

These are hard fail conditions.

---

## Review Template
```markdown
# Meaning Alignment Review

- Asset:
- Post type:
- Prompt version:
- Visual mode:

## Scores
- Meaning Match:
- Mood Match:
- Symbol / Metaphor Relevance:
- Brand Consistency:
- Arabic Text-Friendliness:
- Non-Genericness:
- Functional Suitability:

## Total:

## Verdict
- [ ] Approve
- [ ] Iterate
- [ ] Reject

## Top 2 fixes only
1.
2.
```

---

## Special notes by post type

### Reflection post
Main risk:
- too generic / moodboard-like

### Guided practice post
Main risk:
- calm but not embodied
- soft but not meaning-linked

### Educational post
Main risk:
- atmosphere over clarity

### Concept contrast post
Main risk:
- weak contrast or generic infographic feel

### Promo / offer post
Main risk:
- pretty but commercially unclear

---

## Rule for iterations
When a visual is scored:
- only fix the **top 2 problems** in the next prompt
- do not rewrite the whole visual direction unless the core meaning match failed

This keeps iteration focused and measurable.
