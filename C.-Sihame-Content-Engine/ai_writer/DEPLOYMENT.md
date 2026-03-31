# Deployment

## Architecture

- Frontend: Vercel project rooted at `ai_writer/frontend`
- Backend: Cloud Run service built from `ai_writer/cloudbuild.yaml` with `backend/Dockerfile`

## Frontend environment variable

Set this in Vercel Preview and Production:

```bash
NEXT_PUBLIC_API_URL=https://YOUR_CLOUD_RUN_SERVICE_URL
```

Local development is wired through `frontend/.env.local`.

## Backend environment variables

Create `backend/.env` locally from `backend/.env.example`. In Cloud Run, set the same values as service environment variables:

```bash
CORS_ORIGINS=https://YOUR_VERCEL_DOMAIN
KIE_API_KEY=...
STORAGE_BACKEND=supabase
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_DRAFTS_TABLE=content_drafts
```

`STORAGE_BACKEND=supabase` is required in production so drafts survive Cloud Run restarts and scaling.
Do not add `PORT` manually in Cloud Run. Cloud Run injects that variable automatically.

## Supabase table

Before the first Cloud Run deployment, create the `content_drafts` table in Supabase using [create_content_drafts_table.sql](C:/Users/hello/OneDrive/Desktop/Abdo/SIham/ai_writer/backend/sql/create_content_drafts_table.sql).

## Vercel

1. Import the GitHub repository into Vercel.
2. Set the project root directory to `ai_writer/frontend`.
3. Add `NEXT_PUBLIC_API_URL`.
4. Push to GitHub to trigger deployments automatically.

## Cloud Run

1. Create a Cloud Build GitHub trigger from the `ai_writer` repo root.
2. Point the trigger config file to `ai_writer/cloudbuild.yaml`.
3. Set the Cloud Run service environment variables listed above.
4. Keep the request timeout at `900s` or higher if generation can run long.

The backend image builds from the `ai_writer` directory so it can include `knowledge_pack` and `feedback_log.md` at runtime.

## Health checks

- API root: `/`
- Health endpoint: `/healthz`
