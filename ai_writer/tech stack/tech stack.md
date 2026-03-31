# Sihame AI Content Engine - Tech Stack Architecture

This document outlines the chosen technology stack for Coach Sihame's custom AI application.

## Core Stack
**Next.js + FastAPI + Supabase + Kie.ai**

This is a robust, scalable-ready, production-friendly MVP architecture. It perfectly separates the frontend visuals from the backend logic while maintaining a structured database for future AI improvements.

---

### 1. Frontend: Next.js (React)
* **Role:** The Custom UI for Coach Sihame.
* **Why:** Provides a premium, app-like experience. It's fast, supports beautiful UI libraries (like TailwindCSS), and handles state management effortlessly.
* **Key Features:**
  * Input dashboard for voice/text ideas.
  * Review screen to approve/edit generated drafts.
  * Image preview, revision loop, and download interface.

### 2. Backend: FastAPI (Python)
* **Role:** The Orchestrator & API Gateway.
* **Why:** Python is the native language of AI. FastAPI is incredibly fast and enforces strict data validation. It will securely manage API keys, routing logic, and ensure the frontend remains lightweight.
* **Key Features:**
  * Endpoint to receive raw ideas from Next.js.
  * **Structured Outputs:** Enforces JSON responses from the LLM (e.g., `angle`, `hook`, `body`, `cta`, `image_prompt`, `safety_flags`, `platform_variant`) to prevent chaotic free-text outputs.
  * **RAG-Ready Context Builder:** Instead of a messy full dump, the FastAPI engine dynamically assembles the Context before injection:
    * *Static (Always injected):* `SYSTEM_PROMPT.md`, `STYLE_BIBLE.md`, `CLINICAL_BOUNDARIES.md`, `DO_NOT_IMITATE.md`, `DECISION_POLICY.md`.
    * *Semi-Static (Condition-based):* e.g., injects `POST_TYPES.md` and `METHODOLOGY_MAP.md` rules only relevant to the chosen type (Reflection vs Promo).
    * *Selective Examples:* Retrieves only 3-5 relevant matches from `GOLD_EXAMPLES.md` based on the requested post angle, leaving room for a true RAG setup later without rewriting the core logic.
  * Manages the Image Generation revision loop.
  * Handles logging data and state updates to Supabase asynchronously.

### 3. Database & Auth: Supabase (PostgreSQL)
* **Role:** The Logging & Improvement Engine.
* **Why:** Built on Postgres, it handles structured data beautifully and offers an instant API. Provides the critical feedback loop needed to improve the system over time.
* **Key Features:**
  * Logs every `Raw Input` and `Generated Output`.
  * Tracks granular **Approval States**: `draft_generated`, `under_review`, `approved_text`, `image_generated`, `image_revision_requested`, `final_approved`, `rejected`.
  * Saves all `Image URLs` and prompt revisions.
  * *Future:* Approved logs can be used for evaluation sets, retrieval memory (RAG), and possibly fine-tuning later if needed.

### 4. AI Provider: Kie.ai
* **Role:** The Intelligence Layer.
* **Why:** Provides a unified API to access state-of-the-art models without managing multiple billing accounts.

#### The Model Router
It is critical to assign the right model to the right task to maintain Coach Sihame's deep voice while keeping costs and speeds optimized.
* **Gemini 3.1 Pro (or Claude Sonnet): Primary Writer.** Used for deep content generation, creating the core angles, and applying her specific somatic-spiritual voice.
* **Gemini 3 Flash: Worker / Editor.** Used for quick, simple tasks: simplifying text, shortening posts, generating CTAs, adapting content for different platforms, and drafting image prompts.
* **Nano Banana Pro: The Visual Artist.** Dedicated solely to generating high-end, brand-consistent images based on final approved text.

---

## The Workflow Cycle
1. **[Next.js]** Sihame enters an idea -> Sends to FastAPI.
2. **[FastAPI Router]** Routes to **Gemini 3.1 Pro** (Primary Writer) with the Knowledge Pack to generate structured JSON.
3. **[Kie.ai]** Returns the crafted text (JSON) -> FastAPI -> Next.js. State: `draft_generated` -> `under_review`.
4. **[Next.js]** Sihame reviews. (Optional: Requests simplification or shortening, routed to **Gemini Flash**).
5. **[Next.js]** Sihame clicks "Approve Text" -> State: `approved_text`.
6. **[FastAPI]** Logs text to **Supabase**. Sends core theme to **Kie.ai (Nano Banana Pro)** to generate initial image. State: `image_generated`.
7. **[Next.js] Image Review Loop:**
   * Sihame views Image v1.
   * If edit needed: Sends edit request -> New prompt routed to **Gemini Flash** -> Image v2 from **Nano Banana**. State: `image_revision_requested`.
   * Loop repeats until perfect.
8. **[Next.js]** Sihame approves final image. State: `final_approved`.
9. **[FastAPI]** Updates the **Supabase** log with the final states and URLs.
10. **[Next.js]** Sihame downloads the final ready-to-post package.
