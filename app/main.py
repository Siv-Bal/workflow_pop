from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app.crud import get_workflows
from app.schemas import WorkflowOut

# Ingestion runner
from scripts.run_ingestion import run_all_ingestions

# --------------------------------------------------
# APP SETUP
# --------------------------------------------------

app = FastAPI(
    title="n8n Workflow Popularity API",
    description="Ranks n8n workflows using YouTube, Forum activity, and Google Trends",
    version="1.0.0"
)

# Create tables (safe for SQLite)
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# DATABASE DEPENDENCY
# --------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# --------------------------------------------------
# INGESTION ENDPOINT (IMPORTANT)
# --------------------------------------------------

@app.post("/ingest")
def ingest_workflows():
    """
    Triggers YouTube + Forum ingestion and scoring.
    Safe to call manually or via cron.
    """
    run_all_ingestions()
    return {"status": "ingestion completed"}

# --------------------------------------------------
# WORKFLOWS API
# --------------------------------------------------

@app.get("/workflows", response_model=list[WorkflowOut])
def list_workflows(
    platform: str | None = None,
    country: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return get_workflows(
        db,
        platform=platform,
        country=country,
        limit=limit
    )
