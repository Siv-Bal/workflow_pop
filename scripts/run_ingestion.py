"""
Unified ingestion runner
Used for cron / scheduled execution
"""

from fetcher.youtube_fetcher import ingest_youtube_workflows
from fetcher.forum_fetcher import ingest_forum_workflows


def run_all():
    print("Starting ingestion job...")

    ingest_youtube_workflows(country="US", max_results=20)
    ingest_youtube_workflows(country="IN", max_results=20)

    ingest_forum_workflows(country="US")
    ingest_forum_workflows(country="IN")

    print("Ingestion completed successfully.")


if __name__ == "__main__":
    run_all()
