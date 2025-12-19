from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app.crud import get_workflows
from app.schemas import WorkflowOut

from scripts.run_ingestion import run_all_ingestions

app = FastAPI(title="n8n Workflow Popularity API")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/workflows", response_model=list[WorkflowOut])
def list_workflows(
    platform: str | None = None,
    country: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return get_workflows(db, platform=platform, country=country, limit=limit)


@app.post("/ingest")
def ingest_workflows():
    """
    Triggers YouTube + Forum ingestion.
    Safe to call manually or via cron.
    """
    try:
        run_all_ingestions()
        return {
            "status": "success",
            "message": "Ingestion triggered successfully"
        }
    except Exception as e:
        # 👇 VERY IMPORTANT
        return {
            "status": "failed",
            "error": str(e)
        }
