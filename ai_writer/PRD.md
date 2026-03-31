# Product Requirements Document (PRD)
**Product Name:** Coach Sihame AI Content Engine
**Document Version:** 1.1 (MVP)

## 1. Product Vision & Objective
To build a custom, secure, and highly specialized AI co-pilot for Coach Sihame Atamnia. This system will serve as her "digital right hand," helping her generate, refine, and **prepare ready-to-post content packages** (Telegram, Instagram, Facebook). 
Unlike generic AI tools, this system is **deeply guided by her curated methodology, voice files, and editorial boundaries** (e.g., P.E.A.T., Maestro) to ensure absolute alignment with her brand identity.

## 2. Target Audience & User
* **Primary User:** Coach Sihame Atamnia (sole operator).
* **Use Case:** Creating high-quality, methodologically accurate, and visually consistent posts from rough voice notes or text ideas without needing to "re-explain" her style every time.

## 3. Technology Stack (MVP)
* **Frontend:** Next.js (React) + TailwindCSS for a premium, fast, and clean dashboard.
* **Backend:** FastAPI (Python) for secure orchestration, routing, and prompt assembly.
* **Database & Auth:** Supabase (PostgreSQL) for capturing the critical "Improvement Loop" (analytics, history, and raw vs. approved logs).
* **AI Routing (via Kie.ai):**
  * *Primary Writer:* Gemini 3.1 Pro / Claude Sonnet (Deep content, mimicking the exact somatic voice).
  * *Worker/Editor:* Gemini 3 Flash (Formatting, shortening, CTA generation, drafting prompts).
  * *Visual Artist:* Nano Banana Pro (High-end, brand-consistent image generation).

## 4. Master Feature List (MVP)

### 4.1. Input Module
* **Raw Input:** Simple text box (or audio-to-text integration) to capture raw thoughts, unstructured ideas, or therapy session reflections.
* **Post Parameters:** Selection of target platform (Telegram vs. IG) and intended Post Type. Supported types for V1 include:
  * Reflection
  * Guided Practice
  * Promo
  * Clinic Story
  * Open Questions
  * Prayer / Reflection
  * Event / Invite
  * Monthly Intention

### 4.2. Dynamic Context Assembly (Backend)
* Instead of RAG in V1, FastAPI acts as a smart context builder, dynamically assembling the prompt:
  * **Always Injected (The Constitution):** `SYSTEM_PROMPT`, `CLINICAL_BOUNDARIES`, `OUTPUT_RULES`, `DECISION_POLICY`, `DO_NOT_IMITATE`.
  * **Task-Aware / Voice Layer (Conditional):** `STYLE_BIBLE`, `METHODOLOGY_MAP`, `POST_TYPES`, curated 2023 voice fragments.
  * **Selective Examples:** Fetches highly relevant matches from curated past posts to guide the model safely.

### 4.3. Drafting & Revision Dashboard
* **Structured Generation:** The AI returns JSON (Hook, Angle, Body, CTA, Safety Flags) to ensure predictable UI rendering.
* **One-Click Revisions:** Buttons powered by Gemini Flash (e.g., "Make it shorter", "Make it structured", "Add a P.E.A.T CTA").
* **Approval State Machine:** Tracks posts through granular states: `draft_generated` -> `under_review` -> `approved_text`.

### 4.4. Visual Generation Loop
* Upon text approval, the system auto-generates a highly specific image prompt and sends it to Nano Banana Pro.
* **Image Review Loop:** Displays Image v1. Allows Coach Sihame to request edits (via natural language) which regenerates the image until `image_final_approved`.

### 4.5. The "Improvement Loop" (Data Logging)
* Supabase logs every cycle: `Raw Input` -> `AI Output` -> `Human Edits` -> `Final Approved Text` + `Image URL`.
* This is the most crucial MVP feature, laying the structured data groundwork for future evaluation sets and fine-tuning.

## 5. User Workflow (The Happy Path)
1. Sihame opens the dashboard and types: *"Let's talk about nervous system regulation and P.E.A.T."*
2. Clicks **"Generate Draft"**.
3. FastAPI builds the smart context, routes to Gemini Pro, and returns a structured post.
4. Sihame reviews the draft in the UI. She tweaks a sentence and clicks **"Approve Text"**.
5. Supabase logs the approved text. Nano Banana Pro instantly returns an aesthetic, branded image matching the post's mood.
6. Sihame reviews the image. She clicks **"Approve Image"**.
7. System provides a **"Download Package"** (Text + Image) ready for manual posting.
* **CRITICAL:** **Human approval is mandatory before export. No final package is considered complete without explicit human approval.**

## 6. Out of Scope for V1 (Future Roadmap)
* **Full Vector RAG:** (Semantic Search over hundreds of past posts).
* **Custom LoRA / Fine-tuning:** (Will wait until Supabase collects 500+ perfectly approved logs).
* **Direct Auto-Publishing:** (Requires manual posting for now to ensure absolute safety and ultimate human overview).
* **Multi-user teams:** (Only Coach Sihame for V1).

## 7. Success Metrics for MVP
* **Time-to-Publish:** Reduces Coach Sihame's post creation time from ~45 minutes to **10–15 minutes**.
* **Zero-Shot Accuracy:** The first AI draft requires light editing in **60–70%** of cases (will improve as logs grow).
* **Safety Adherence:** 100% compliance with `CLINICAL_BOUNDARIES.md` (Zero diagnosing, zero absolute promises).

## 8. Core Product Principles
* **Human approval is mandatory.** The system assists, but the human decides.
* **No autonomous publishing in V1.** All exports are handled manually by the Coach.
* **Context-Guided, not Fine-Tuned.** The system relies on heavy contextual rules, not model fine-tuning (yet).
* **Voice over Rules.** 2023 recordings/messages are stylistic sources, not strictly instructional rules.
* **Safety > Stylistic Similarity.** Clinical safety boundaries override any attempt to sound purely motivational.
* **Invitational Promotions.** "Promo" posts must remain invitational and gentle; never pressure-based or rooted in urgency/FOMO.
