"""
Unified ingestion runner
Used for cron / scheduled execution
"""

from fetcher.youtube_fetcher import ingest_youtube_workflows
from fetcher.forum_fetcher import ingest_forum_workflows

def run_all_ingestions():
    # YouTube
    ingest_youtube_workflows(country="US", max_results=30)
    ingest_youtube_workflows(country="IN", max_results=30)

    # Forum
    ingest_forum_workflows(country="US", limit=50)
    ingest_forum_workflows(country="IN", limit=50)


    print("Ingestion completed successfully.")


if __name__ == "__main__":
    run_all_ingestions()
