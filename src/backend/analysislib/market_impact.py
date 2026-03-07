# backend/analysislib/market_impact.py
from typing import List, Dict
from collections import Counter

def generate_market_impact(themes: List[Dict]) -> List[Dict]:
    """
    Generates market impact info per theme.
    Returns a list of dicts ready for portfolio analysis.
    """
    impact_summary = []

    for theme in themes:
        events = theme.get("events", [])
        if not events:
            continue

        event_count = len(events)
        avg_importance = sum(e.get("importance_score", 0) for e in events) / event_count

        sentiments = [e.get("sentiment", "neutral") for e in events]
        direction = Counter(sentiments).most_common(1)[0][0]

        asset_list = [asset for e in events for asset in e.get("asset_classes", [])]
        affected_assets = list(set(asset_list))

        impact_summary.append({
            "theme_id": theme.get("theme_id"),
            "theme_name": theme.get("title"),
            "heat_score": theme.get("heat_score"),
            "event_count": event_count,
            "avg_importance": round(avg_importance, 3),
            "direction": direction,
            "affected_assets": affected_assets
        })

    return impact_summary