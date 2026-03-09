# backend/analysislib/sync_themes.py
from datetime import datetime, timedelta, timezone

from databaselib.db import get_events, get_active_themes, insert_theme, update_theme
from .logic.macro_themes import group_events_into_themes
from .logic.heat_score import calculate_theme_heat


def sync_theme_heat(days: int = 7) -> int:
    events = get_events(days=days)
    themes = calculate_theme_heat(group_events_into_themes(events))

    existing = get_active_themes()
    by_key = {(t.get("title"), t.get("region") or ""): t for t in existing}

    upserts = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    for t in themes:
        key = (t["title"], t.get("region") or "")
        payload = {
            "title": t["title"],
            "description": t.get("description", ""),
            "status": "active",
            "heat_score": t["heat_score"],
            "asset_classes": t.get("asset_classes", []),
            "region": t.get("region", ""),
            "first_seen_at": t.get("first_seen_at", now_iso),
            "last_seen_at": t.get("last_seen_at", now_iso),
        }

        if key in by_key:
            update_theme(by_key[key]["theme_id"], payload)
        else:
            insert_theme(payload)
        upserts += 1

    return upserts


if __name__ == "__main__":
    n = sync_theme_heat(days=7)
    print(f"Synced {n} themes")

