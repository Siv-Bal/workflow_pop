"""
YouTube workflow ingestion
Source: YouTube Data API v3
https://developers.google.com/youtube/v3
"""

import os
import requests
from dotenv import load_dotenv

from app.database import SessionLocal
from app.scoring import calculate_pcs, generate_explanation
from app.crud import create_workflow

# -------------------------------------------------------------------
# ENVIRONMENT SETUP
# -------------------------------------------------------------------

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not found. Check .env file.")

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def normalize_int(value):
    """Safely convert YouTube API values to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def extract_workflow_name(title: str) -> str:
    """
    Extract a clean workflow name from a YouTube title.
    Rule-based and explainable.
    """
    title = title.lower()

    keywords = {
        "google sheets": "Google Sheets",
        "gmail": "Gmail",
        "slack": "Slack",
        "whatsapp": "WhatsApp",
        "notion": "Notion",
        "ai": "AI"
    }

    found = [label for key, label in keywords.items() if key in title]

    if len(found) >= 2:
        return f"{found[0]} → {found[1]} Automation"
    elif len(found) == 1:
        return f"{found[0]} Automation"
    else:
        return "General n8n Automation"

# -------------------------------------------------------------------
# YOUTUBE API CALLS
# -------------------------------------------------------------------

def search_videos(query: str, region: str = "US", max_results: int = 10):
    url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "regionCode": region,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("items", [])


def get_video_stats(video_ids: list[str]):
    if not video_ids:
        return []

    url = f"{BASE_URL}/videos"
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

# -------------------------------------------------------------------
# INGESTION PIPELINE
# -------------------------------------------------------------------

def ingest_youtube_workflows(
    query: str = "n8n workflow automation",
    country: str = "US",
    max_results: int = 10
):
    """
    Full pipeline:
    YouTube → normalize → PCS → SQLite
    """
    db = SessionLocal()

    try:
        videos = search_videos(query, region=country, max_results=max_results)
        video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]

        stats = get_video_stats(video_ids)

        for video in stats:
            title = video["snippet"]["title"]
            statistics = video.get("statistics", {})

            views = normalize_int(statistics.get("viewCount"))
            likes = normalize_int(statistics.get("likeCount"))
            comments = normalize_int(statistics.get("commentCount"))

            scores = calculate_pcs(
                views=views,
                likes=likes,
                comments=comments
            )

            explanation = generate_explanation(scores)

            workflow_data = {
                "name": extract_workflow_name(title),
                "platform": "YouTube",
                "country": country,

                "views": views,
                "likes": likes,
                "comments": comments,

                "like_to_view_ratio": (likes / views) if views else 0,
                "comment_to_view_ratio": (comments / views) if views else 0,

                "popularity_score": scores["popularity_score"],
                "engagement_score": scores["engagement_score"],
                "volume_score": scores["volume_score"],
                "trend_score": scores["trend_score"],

                "explanation": explanation
            }

            create_workflow(db, workflow_data)

    finally:
        db.close()

# -------------------------------------------------------------------
# MANUAL RUN
# -------------------------------------------------------------------

if __name__ == "__main__":
    ingest_youtube_workflows()
    print("YouTube workflows ingested successfully.")
