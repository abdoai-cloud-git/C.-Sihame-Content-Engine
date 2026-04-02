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


from app.api.routes import generate
app.include_router(generate.router, prefix=f"{settings.API_V1_STR}/content", tags=["Content Generation"])

