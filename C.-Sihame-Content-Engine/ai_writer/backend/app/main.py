from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://c-sihame-content-engine.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Coach Sihame AI Content Engine API"}


@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}


@app.get("/healthz/db")
def healthcheck_db():
    """
    Lightweight Supabase connectivity check.
    Returns {"db": "ok"} if reachable, or {"db": "paused_or_unreachable", "error": "..."} if not.
    Can also be used as a keep-alive ping target (e.g., from Cloud Scheduler or GitHub Actions).
    """
    from app.core.config import settings as s
    try:
        from supabase import create_client
        client = create_client(s.SUPABASE_URL, s.SUPABASE_ANON_KEY)
        client.table(s.SUPABASE_DRAFTS_TABLE).select("draft_id").limit(1).execute()
        return {"db": "ok"}
    except Exception as exc:
        return {"db": "paused_or_unreachable", "error": str(exc)}


from app.api.routes import generate
app.include_router(generate.router, prefix=f"{settings.API_V1_STR}/content", tags=["Content Generation"])

