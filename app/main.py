from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app import models
from app.crud import get_workflows
from app.schemas import WorkflowOut

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
    db: Session = Depends(get_db)
):
    return get_workflows(db, platform, country, limit)
