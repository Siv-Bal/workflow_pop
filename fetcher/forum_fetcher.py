"""
Forum workflow ingestion
Source: n8n Community (Discourse)
https://docs.discourse.org/
"""

import requests

from app.database import SessionLocal
from app.crud import upsert_workflow
from app.scoring import calculate_pcs,generate_explanation
from fetcher.google_trends import get_trend_score

BASE_URL = "https://community.n8n.io"
REQUEST_TIMEOUT = 10

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def extract_workflow_name(title: str) -> str:
    """
    Normalize forum titles into workflow-style names.
    Uses the same philosophy as YouTube normalization.
    """
    title_lower = title.lower()

    keywords = {
        "google sheets": "Google Sheets",
        "gmail": "Gmail",
        "slack": "Slack",
        "whatsapp": "WhatsApp",
        "notion": "Notion",
        "telegram": "Telegram",
        "ai": "AI",
    }

    found = [
        label
        for key, label in keywords.items()
        if key in title_lower
    ]

    if len(found) >= 2:
        return f"{found[0]} → {found[1]} Workflow"
    elif len(found) == 1:
        return f"{found[0]} Workflow"
    else:
        return "General n8n Workflow"


def fetch_latest_topics(limit: int = 50):
    """
    Fetch latest topics from the n8n Discourse forum.
    """
    url = f"{BASE_URL}/latest.json"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()["topic_list"]["topics"][:limit]

# -------------------------------------------------
# INGESTION PIPELINE
# -------------------------------------------------

def ingest_forum_workflows(country: str = "US", limit: int = 50):
    """
    Ingest forum workflows.
    Forum activity is sparse, so Google Trends is used
    as a primary popularity signal.
    """
    db = SessionLocal()

    try:
        topics = fetch_latest_topics(limit=limit)

        for topic in topics:
            title = topic.get("title", "")
            workflow_name = extract_workflow_name(title)

            replies = max(topic.get("posts_count", 1) - 1, 0)
            likes = topic.get("like_count", 0)
            views = topic.get("views", 0)
            contributors = len(topic.get("posters", []))

            # 🔥 GOOGLE TRENDS (PRIMARY SIGNAL FOR FORUM)
            trend = get_trend_score(
                keyword=workflow_name,
                country=country
            )

            # PCS using forum engagement + trend
            scores = calculate_pcs(
                views=views,
                likes=likes,
                comments=replies,
                trend_score=trend["trend_score"]
            )

            explanation = generate_explanation(
                views=views,
                likes=likes,
                comments=replies,
                trend_direction=trend["trend_direction"]
            )

            workflow_data = {
                "name": workflow_name,
                "platform": "Forum",
                "country": country,

                "views": views,
                "likes": likes,
                "comments": replies,
                "replies": replies,
                "contributors": contributors,

                "like_to_view_ratio": (likes / views) if views else 0,
                "comment_to_view_ratio": (replies / views) if views else 0,

                "popularity_score": scores["popularity_score"],
                "engagement_score": scores["engagement_score"],
                "volume_score": scores["volume_score"],
                "trend_score": scores["trend_score"],

                "explanation": explanation,
            }

            upsert_workflow(db, workflow_data)

    finally:
        db.close()

# -------------------------------------------------
# MANUAL RUN
# -------------------------------------------------

if __name__ == "__main__":
    ingest_forum_workflows(country="US", limit=50)
    ingest_forum_workflows(country="IN", limit=50)
    print("Forum workflows ingested successfully.")
