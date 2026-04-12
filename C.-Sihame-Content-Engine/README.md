# Coach Sihame AI Content Engine

A full-stack AI content generation platform designed for Coach Sihame. This engine generates premium, brand-aligned Arabic content from raw inputs and provides a structured review workflow.

## 🚀 Environments & Deployment

We use a separate **Production** and **Development** environment to ensure stable releases.

| Environment | Branch | Frontend URL (Vercel) | Backend URL (Cloud Run) |
| :--- | :--- | :--- | :--- |
| **Production** | `main` | [c-sihame-content-engine.vercel.app](https://c-sihame-content-engine.vercel.app/) | `c--sihame-content-engine` |
| **Development** | `dev` | [dev.c-sihame-content-engine.vercel.app](https://c-sihame-content-engine-git-dev-abdo-ais-projects.vercel.app/) | `sihame-backend-dev` |

## 🏗️ Architecture

- **Frontend**: Next.js (TypeScript) with Tailwind CSS.
- **Backend**: FastAPI (Python) running on Google Cloud Run.
- **Database**: Supabase (PostgreSQL) for persistence.
- **AI Engine**: Kie.ai (Llama-based) with a custom structured "Knowledge Pack".

## 🔄 Core Workflows

### 1. Reject & Regenerate Loop
Located in the **Review** stage. Users can provide feedback on a generated draft.
- **Reject**: Transition draft to `REJECTED` status and store a `rejection_reason`.
- **Regenerate**: Triggers a fresh generation attempt using the stored draft context (`raw_input`, `post_type`, `platform`) plus the rejection feedback as an active correction constraint.

## 🛠️ Local Development

### Backend
```bash
cd ai_writer/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend
```bash
cd ai_writer/frontend
npm install
npm run dev
```

## 📍 CI/CD
- **GitHub Actions**: Push to `dev` or `main` automatically builds and deploys the backend to Cloud Run.
- **Vercel**: Automatically deploys the frontend based on branch pushes.
