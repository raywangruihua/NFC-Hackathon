# backend/analysislib/heat_score.py
from typing import List, Dict
from datetime import datetime, timezone


def _clamp_importance(value: object) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(float(value), 1.0))
    return 0.0


def _recency_factor(published_at: object) -> float:
    if not isinstance(published_at, str) or not published_at:
        return 1.0
    try:
        pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        delta_days = max((datetime.now(timezone.utc) - pub_dt).days, 0)
        return 1 / (1 + delta_days / 30)
    except Exception:
        return 1.0


def calculate_theme_heat(themes: List[Dict]) -> List[Dict]:
    """
    Heat score is normalized to 0-100 for frontend display.
    """
    for theme in themes:
        events = theme.get("events", [])
        if not events:
            theme["heat_score"] = 0.0
            continue

        avg_importance = sum(_clamp_importance(e.get("importance_score")) for e in events) / len(events)
        avg_recency = sum(_recency_factor(e.get("published_at")) for e in events) / len(events)

        # Event volume saturates toward 1.0 as count increases.
        event_volume = len(events) / (len(events) + 4)

        # Final normalized score in [0, 100].
        raw = avg_importance * avg_recency * event_volume
        theme["heat_score"] = round(raw * 100, 1)

    return themes
