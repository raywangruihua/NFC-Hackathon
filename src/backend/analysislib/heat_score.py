# backend/analysislib/heat_score.py
from typing import List, Dict
from datetime import datetime, timezone

def calculate_theme_heat(themes: List[Dict]) -> List[Dict]:
    """
    Calculate a heat score for each theme based on:
    - Importance of events
    - Number of events
    - Optional recency decay
    """
    for theme in themes:
        events = theme["events"]
        if not events:
            theme["heat_score"] = 0.0
            continue

        # simple heat: avg importance * number of events
        avg_importance = sum(e.get("importance_score", 0) for e in events) / len(events)
        heat = avg_importance * len(events)

        # optional: decay older events by days
        for e in events:
            pub_date = e.get("published_at")
            if pub_date:
                try:
                    delta_days = (datetime.now(timezone.utc) - datetime.fromisoformat(pub_date.replace("Z", "+00:00"))).days
                    heat *= 1 / (1 + delta_days / 30)  # 30-day decay factor
                except Exception:
                    pass

        theme["heat_score"] = round(heat, 3)

    return themes