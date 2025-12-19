from sqlalchemy.orm import Session
from .models import Workflow


# --------------------------------------------------
# CREATE (used rarely, mostly for testing)
# --------------------------------------------------
def create_workflow(db: Session, workflow_data: dict):
    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


# --------------------------------------------------
# READ (API endpoint)
# --------------------------------------------------
def get_workflows(
    db: Session,
    platform: str | None = None,
    country: str | None = None,
    limit: int = 50
):
    query = db.query(Workflow)

    if platform:
        query = query.filter(Workflow.platform == platform)

    if country:
        query = query.filter(Workflow.country == country)

    workflows = (
        query
        .order_by(Workflow.popularity_score.desc())
        .limit(limit)
        .all()
    )

    # 🔥 NORMALIZE NULL VALUES (CRITICAL FOR API STABILITY)
    for w in workflows:
        w.views = w.views or 0
        w.likes = w.likes or 0
        w.comments = w.comments or 0

        w.like_to_view_ratio = w.like_to_view_ratio or 0.0
        w.comment_to_view_ratio = w.comment_to_view_ratio or 0.0

        w.popularity_score = w.popularity_score or 0
        w.engagement_score = w.engagement_score or 0
        w.volume_score = w.volume_score or 0
        w.trend_score = w.trend_score or 0

        w.explanation = w.explanation or ""

    return workflows


# --------------------------------------------------
# UPSERT (used by fetchers)
# --------------------------------------------------
def upsert_workflow(db: Session, workflow_data: dict):
    existing = (
        db.query(Workflow)
        .filter(
            Workflow.name == workflow_data["name"],
            Workflow.platform == workflow_data["platform"],
            Workflow.country == workflow_data["country"],
        )
        .first()
    )

    if existing:
        for key, value in workflow_data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow
