def calculate_engagement_score(views: int, likes: int, comments: int) -> int:
    if views <= 0:
        return 0

    like_ratio = likes / views
    comment_ratio = comments / views

    like_score = min(like_ratio * 800, 25)       # caps at 25
    comment_score = min(comment_ratio * 3000, 15)  # caps at 15

    return int(like_score + comment_score)


def calculate_volume_score(views: int) -> int:
    if views > 100_000:
        return 40
    elif views > 50_000:
        return 30
    elif views > 10_000:
        return 20
    else:
        return 10


def calculate_trend_score() -> int:
    # Placeholder for Day 3 (Google Trends)
    return 10


def calculate_pcs(views: int, likes: int, comments: int) -> dict:
    engagement = calculate_engagement_score(views, likes, comments)
    volume = calculate_volume_score(views)
    trend = calculate_trend_score()

    pcs = engagement + volume + trend

    return {
        "popularity_score": pcs,
        "engagement_score": engagement,
        "volume_score": volume,
        "trend_score": trend
    }


def generate_explanation(scores: dict) -> str:
    reasons = []

    if scores["engagement_score"] > 25:
        reasons.append("strong audience engagement")
    if scores["volume_score"] >= 30:
        reasons.append("high visibility")
    if scores["trend_score"] >= 15:
        reasons.append("rising interest")

    if not reasons:
        return "Moderate popularity based on overall engagement and reach."

    return "Ranks high due to " + ", ".join(reasons) + "."
