
from pytrends.request import TrendReq
from statistics import mean

pytrends = TrendReq(hl="en-US", tz=360)

# Rough category-based baseline volumes
BASE_KEYWORD_VOLUME = {
    "automation": 10000,
    "workflow": 8000,
    "integration": 12000,
    "ai": 15000,
    "default": 5000,
}


def _estimate_base_volume(keyword: str) -> int:
    keyword = keyword.lower()

    for k, v in BASE_KEYWORD_VOLUME.items():
        if k in keyword:
            return v

    return BASE_KEYWORD_VOLUME["default"]


def get_trend_score(keyword: str, country: str = "US") -> dict:
    """
    Google Search popularity evidence:
    - Relative interest (Trends)
    - Estimated monthly search volume
    - 60-day growth percentage
    """

    try:
        pytrends.build_payload(
            [keyword],
            timeframe="today 3-m",
            geo=country
        )

        data = pytrends.interest_over_time()

        if data.empty or keyword not in data:
            return {
                "trend_score": 5,
                "trend_direction": "stable",
                "avg_interest": 0,
                "monthly_search_volume": 0,
                "growth_60d_pct": 0,
            }

        values = data[keyword].tolist()
        avg_interest = mean(values)

        mid = len(values) // 2
        early_avg = mean(values[:mid])
        recent_avg = mean(values[mid:])

        if early_avg == 0:
            growth_pct = 0
        else:
            growth_pct = round(((recent_avg - early_avg) / early_avg) * 100, 1)

        # Direction + score
        if growth_pct > 30:
            direction = "up"
            score = 20
        elif growth_pct < -20:
            direction = "down"
            score = 5
        else:
            direction = "stable"
            score = 10

        base_volume = _estimate_base_volume(keyword)
        monthly_volume = int((avg_interest / 100) * base_volume)

        return {
            "trend_score": score,
            "trend_direction": direction,
            "avg_interest": round(avg_interest, 2),
            "monthly_search_volume": monthly_volume,
            "growth_60d_pct": growth_pct,
        }

    except Exception:
        return {
            "trend_score": 5,
            "trend_direction": "stable",
            "avg_interest": 0,
            "monthly_search_volume": 0,
            "growth_60d_pct": 0,
        }
