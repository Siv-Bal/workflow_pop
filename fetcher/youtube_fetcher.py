"""
YouTube workflow ingestion
Source: YouTube Data API v3
https://developers.google.com/youtube/v3
"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Set

from app.database import SessionLocal
from app.scoring import calculate_pcs, generate_explanation
from app.crud import upsert_workflow
from fetcher.google_trends import get_trend_score

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT = 10

if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not found in environment")

# --------------------------------------------------
# SEARCH QUERIES (CRITICAL)
# --------------------------------------------------

SEARCH_QUERIES = [
    "n8n whatsapp automation",
    "n8n whatsapp ai",
    "n8n slack automation",
    "n8n slack ai",
    "n8n google sheets automation",
    "n8n google sheets ai",
    "n8n gmail automation",
    "n8n gmail ai",
    "n8n notion workflow",
    "n8n webhook automation",
    "n8n api integration",
]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def extract_workflow_name(title: str) -> str:
    title = title.lower()

    keywords = {
        "google sheets": "Google Sheets",
        "gmail": "Gmail",
        "slack": "Slack",
        "whatsapp": "WhatsApp",
        "notion": "Notion",
        "ai": "AI",
    }

    found = [label for key, label in keywords.items() if key in title]

    if len(found) >= 2:
        return f"{found[0]} → {found[1]} Automation"
    elif len(found) == 1:
        return f"{found[0]} Automation"
    else:
        return "General n8n Automation"

# --------------------------------------------------
# YOUTUBE API CALLS
# --------------------------------------------------

def search_videos(query: str, country: str, max_results: int) -> List[dict]:
    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "regionCode": country,
            "key": YOUTUBE_API_KEY,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def get_video_stats(video_ids: List[str]) -> List[dict]:
    if not video_ids:
        return []

    response = requests.get(
        f"{BASE_URL}/videos",
        params={
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("items", [])

# --------------------------------------------------
# INGESTION PIPELINE
# --------------------------------------------------

def ingest_youtube_workflows(country: str = "US", max_results: int = 15):
    """
    Multi-query YouTube ingestion with deduplication
    """
    db = SessionLocal()
    seen_workflows: Set[str] = set()

    try:
        for query in SEARCH_QUERIES:
            videos = search_videos(query, country, max_results)

            video_ids = [
                v["id"]["videoId"]
                for v in videos
                if v.get("id", {}).get("videoId")
            ]

            stats = get_video_stats(video_ids)

            for video in stats:
                title = video["snippet"]["title"]
                s = video.get("statistics", {})

                views = normalize_int(s.get("viewCount"))
                likes = normalize_int(s.get("likeCount"))
                comments = normalize_int(s.get("commentCount"))

                workflow_name = extract_workflow_name(title)

                # 🔒 Deduplication (CRITICAL)
                if workflow_name in seen_workflows:
                    continue
                seen_workflows.add(workflow_name)

                # 🔥 Google Trends
                trend = get_trend_score(workflow_name, country)

                # 🔢 PCS Scoring
                scores = calculate_pcs(
                    views=views,
                    likes=likes,
                    comments=comments,
                    keyword=workflow_name,
                    country=country,
                )

                explanation = generate_explanation(
                    views=views,
                    likes=likes,
                    comments=comments,
                    trend_direction=trend["trend_direction"],
                )

                workflow_data = {
                    "name": workflow_name,
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

                    # ✅ Evidence fields
                    "trend_direction": trend["trend_direction"],
                    "trend_avg_interest": trend["avg_interest"],

                    "explanation": explanation,
                }

                upsert_workflow(db, workflow_data)

    finally:
        db.close()

# --------------------------------------------------
# MANUAL RUN
# --------------------------------------------------

if __name__ == "__main__":
    ingest_youtube_workflows(country="US", max_results=15)
    ingest_youtube_workflows(country="IN", max_results=15)
    print("YouTube workflows ingested successfully.")
