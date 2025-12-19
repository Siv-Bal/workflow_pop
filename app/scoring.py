from fetcher.google_trends import get_trend_score

# -------------------------------------------------
# ENGAGEMENT SCORE
# -------------------------------------------------

def calculate_engagement_score(views: int, likes: int, comments: int) -> int:
    if views <= 0:
        return 0

    like_ratio = likes / views
    comment_ratio = comments / views

    like_score = min(like_ratio * 800, 25)
    comment_score = min(comment_ratio * 3000, 15)

    return int(like_score + comment_score)


# -------------------------------------------------
# VOLUME SCORE
# -------------------------------------------------

def calculate_volume_score(views: int) -> int:
    if views > 100_000:
        return 40
    elif views > 50_000:
        return 30
    elif views > 10_000:
        return 20
    else:
        return 10


# -------------------------------------------------
# POPULARITY SCORE (PCS)
# -------------------------------------------------

def calculate_pcs(
    views: int,
    likes: int,
    comments: int,
    keyword: str,
    country: str,
) -> dict:
    engagement = calculate_engagement_score(views, likes, comments)
    volume = calculate_volume_score(views)

    trend_data = get_trend_score(keyword, country)
    trend_score = trend_data["trend_score"]

    return {
        "popularity_score": engagement + volume + trend_score,
        "engagement_score": engagement,
        "volume_score": volume,
        "trend_score": trend_score,
        "trend_direction": trend_data["trend_direction"],
    }


# -------------------------------------------------
# HUMAN-READABLE EXPLANATION
# -------------------------------------------------

def generate_explanation(
    views: int,
    likes: int,
    comments: int,
    trend_direction: str,
) -> str:
    if views <= 0:
        return "No engagement data available."

    reasons = []

    if likes / views >= 0.02:
        reasons.append("strong like engagement")

    if comments / views >= 0.003:
        reasons.append("active discussion")

    if views >= 50_000:
        reasons.append("high reach")

    if trend_direction == "up":
        reasons.append("rising search interest")

    if not reasons:
        return "Moderate popularity based on engagement, reach, and trend signals."

    return "Ranks high due to " + ", ".join(reasons) + "."
