from pytrends.request import TrendReq

# Initialize pytrends once (important for stability)
pytrends = TrendReq(hl="en-US", tz=360)


def get_trend_score(keyword: str, country: str = "US") -> dict:
    """
    Google Trends signal for a workflow keyword.

    Returns:
    {
        trend_score: int (0–20),
        trend_direction: "up" | "stable" | "down",
        trend_signal: str (human readable),
        avg_interest: float
    }
    """

    try:
        # Last 3 months = short-term momentum (ideal for trends)
        timeframe = "today 3-m"
        geo = country.upper()

        pytrends.build_payload(
            kw_list=[keyword],
            timeframe=timeframe,
            geo=geo,
        )

        data = pytrends.interest_over_time()

        # No data = weak / neutral signal
        if data.empty or keyword not in data:
            return {
                "trend_score": 5,
                "trend_direction": "stable",
                "trend_signal": "Low or insufficient search interest",
                "avg_interest": 0.0,
            }

        values = data[keyword].tolist()
        length = len(values)

        if length < 6:
            return {
                "trend_score": 5,
                "trend_direction": "stable",
                "trend_signal": "Insufficient data points",
                "avg_interest": round(sum(values) / max(length, 1), 2),
            }

        avg_interest = sum(values) / length

        third = length // 3
        start_avg = sum(values[:third]) / max(third, 1)
        end_avg = sum(values[-third:]) / max(third, 1)

        # Trend classification
        if end_avg > start_avg * 1.15:
            return {
                "trend_score": 20,
                "trend_direction": "up",
                "trend_signal": "Rising search interest in last 30–60 days",
                "avg_interest": round(avg_interest, 2),
            }

        elif end_avg < start_avg * 0.85:
            return {
                "trend_score": 5,
                "trend_direction": "down",
                "trend_signal": "Declining search interest",
                "avg_interest": round(avg_interest, 2),
            }

        else:
            return {
                "trend_score": 10,
                "trend_direction": "stable",
                "trend_signal": "Stable search interest",
                "avg_interest": round(avg_interest, 2),
            }

    except Exception:
        # Fail-safe: never break ingestion
        return {
            "trend_score": 5,
            "trend_direction": "stable",
            "trend_signal": "Trend data unavailable",
            "avg_interest": 0.0,
        }
