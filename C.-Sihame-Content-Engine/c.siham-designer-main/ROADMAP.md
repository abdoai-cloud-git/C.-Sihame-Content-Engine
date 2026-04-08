# ROADMAP

## Phase 1 — Stabilize the current system
Goal: keep what already works and remove ambiguity.

Targets:
- lock the current working logic
- make post-type decisions clearer
- preserve Arabic readability first
- preserve premium, emotionally safe brand behavior

Success looks like:
- the system produces usable outputs consistently on known post types
- text hierarchy is predictable
- visual direction matches meaning more often than mood alone

---

## Phase 2 — Refactor into a cleaner designer engine
Goal: turn the current collection of files into a more coherent operating system.

Targets:
- define a single decision flow
- separate core logic from examples and outputs
- make prompt construction easier to audit
- make evaluation part of the pipeline, not an afterthought

Possible structure:
- core identity
- decision logic
- typography/layout
- symbol logic
- generation rules
- evaluation
- benchmarks/examples

Success looks like:
- easier maintenance
- easier onboarding into the system
- less duplicated guidance across files

---

## Phase 3 — Benchmark and score
Goal: validate the system against real posts.

Targets:
- create benchmark posts across multiple categories
- score meaning match, Arabic readability, and brand fit
- identify repeated failure modes
- tune only the top defects each round

Success looks like:
- a benchmark set with review notes
- visible improvement over iterations
- fewer generic outputs

---

## Phase 4 — Production readiness
Goal: make the system robust enough for repeated real use.

Targets:
- standardize output schema
- standardize title / body / signature behavior
- define final generation defaults
- define retry / rerun policy
- document how to use the system from a fresh session

Success looks like:
- consistent workflow from post text to image
- predictable output quality
- low-friction reuse
