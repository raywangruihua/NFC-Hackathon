# backend/analysislib/market_impact.py
from typing import List, Dict
from collections import Counter


def _safe_asset_classes(event: Dict) -> list[str]:
    asset_classes = event.get("asset_classes")
    if isinstance(asset_classes, list):
        return [asset for asset in asset_classes if isinstance(asset, str) and asset]
    return []


def _safe_sentiment(event: Dict) -> str:
    sentiment = event.get("sentiment")
    if sentiment in {"risk-on", "risk-off", "neutral"}:
        return sentiment
    return "neutral"


def generate_market_impact(themes: List[Dict]) -> List[Dict]:
    impact_summary = []

    for theme in themes:
        events = theme.get("events", [])
        if not events:
            continue

        event_count = len(events)
        avg_importance = sum(e.get("importance_score", 0) for e in events) / event_count
        sentiments = [_safe_sentiment(e) for e in events]
        direction = Counter(sentiments).most_common(1)[0][0]
        affected_assets = list({asset for e in events for asset in _safe_asset_classes(e)})

        impact_summary.append({
            "theme_id": theme.get("theme_id"),
            "theme_name": theme.get("title"),
            "heat_score": theme.get("heat_score"),
            "event_count": event_count,
            "avg_importance": round(avg_importance, 3),
            "direction": direction,
            "affected_assets": affected_assets,
        })

    return impact_summary
