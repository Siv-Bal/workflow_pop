from sqlalchemy.orm import Session
from .models import Workflow


def create_workflow(db: Session, workflow_data: dict):
    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow

def get_workflows(
    db,
    platform: str | None = None,
    country: str | None = None,
    limit: int = 50
):
    query = db.query(Workflow)

    if platform:
        query = query.filter(Workflow.platform == platform)

    if country:
        query = query.filter(Workflow.country == country)

    return (
        query
        .order_by(Workflow.popularity_score.desc())
        .limit(limit)
        .all()
    )

