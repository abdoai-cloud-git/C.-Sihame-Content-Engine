# Deployment

## Architecture

- Frontend: Vercel project rooted at `C.-Sihame-Content-Engine/ai_writer/frontend`
- Backend: Cloud Run service built from `C.-Sihame-Content-Engine/ai_writer/cloudbuild.yaml` with `backend/Dockerfile`

## Environments

We maintain two isolated deployment pipelines based on GitHub branches:

| Environment | GitHub Branch | Deployment Stage |
| :--- | :--- | :--- |
| **Production** | `main` | Official production URLs |
| **Development** | `dev` | Preview deployments for internal testing |

## Frontend Environment Variables (Vercel)

Set `NEXT_PUBLIC_API_URL` based on the environment in Vercel **Settings > Environment Variables**:

- **Production (main)**: `https://c--sihame-content-engine-qxtfqtai5q-ew.a.run.app`
- **Preview (dev)**: `https://sihame-backend-dev-qxtfqtai5q-ew.a.run.app`

*Tip: In Vercel, you can select "Preview" and check "Specific Branches" to target only the `dev` branch for your dev backend URL.*

## CI/CD (GitHub Actions)

We use GitHub Actions [deploy-backend.yml](file:///c:/Users/hello/OneDrive/Desktop/Abdo/SIham/C.-Sihame-Content-Engine/.github/workflows/deploy-backend.yml) to automate backend deployments to Cloud Run.

### 🔐 Required GitHub Secrets

These must be set in your GitHub repository under **Settings > Secrets and variables > Actions**:

| Secret Name | Description |
| :--- | :--- |
| `GCP_SA_KEY` | JSON service account key with `Cloud Run Admin` and `Storage Admin` roles. |
| `KIE_API_KEY` | AI Model API key. |
| `SUPABASE_URL` | Your Supabase project URL. |
| `SUPABASE_ANON_KEY` | Your Supabase anonymous (public) key. |
| `CORS_ORIGINS_PROD` | Production frontend URL (no trailing slash). |
| `CORS_ORIGINS_DEV` | Development frontend URL or `*` for internal testing. |

### 🛠️ Troubleshooting

- **Build Failures**: Check the 'ai_writer' context in the Dockerfile. The build expects to run from the root of the project to locate the `knowledge_pack`.
- **CORS Errors**: Ensure the `CORS_ORIGINS_PROD` or `CORS_ORIGINS_DEV` secrets in GitHub exactly match the URL shown in your browser (no trailing slash).
- **Service Not Found**: If a new branch is created, GitHub Actions will attempt to deploy to a service named `sihame-backend-dev`. If you want a different name, update the `vars` step in the workflow.

## Database Migration (Supabase)

The **Reject & Regenerate** workflow requires a new column in your `drafts` table:
```sql
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
```

## Health Checks & Monitoring

- **API Root**: `/` (Returns a welcome message)
- **Health Endpoint**: `/healthz` (Returns status: "ok")
- **Logs**: View real-time logs in the Google Cloud Console under **Cloud Run > [Service Name] > Logs**.

## Project Context for AI Agents
See [.ai_context.md](file:///c:/Users/hello/OneDrive/Desktop/Abdo/SIham/C.-Sihame-Content-Engine/.ai_context.md) for specialized guidance on the project's logic and naming conventions.
