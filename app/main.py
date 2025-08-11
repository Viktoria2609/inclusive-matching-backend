import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  
from app.routers import profiles
from app.routers import ai_match

# Create DB tables on startup (simple projects). For bigger apps use Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KIDNECT API",
    description="Inclusive matching platform for families with children of all abilities.",
    version="1.0.0",
)

# --- CORS configuration ---
# Allow your local Vite dev server and your Vercel domain(s).
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://inclusive-matching-frontend2.vercel.app",
]
# Optionally extend via env: ALLOWED_ORIGINS="https://foo.app,https://bar.app"
EXTRA = os.getenv("ALLOWED_ORIGINS", "")
EXTRA_LIST = [o.strip() for o in EXTRA.split(",") if o.strip()]
ALLOWED_ORIGINS = DEFAULT_ALLOWED_ORIGINS + EXTRA_LIST

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Allow all Vercel preview deployments like https://your-app-git-*.vercel.app
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# NOTE: profiles router defines routes at "/" under this prefix → call as /profiles/
app.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
app.include_router(ai_match.router)  # /ai/match

# --- Health ---
@app.get("/")
def root():
    return {"message": "Inclusive Matching API is running!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}