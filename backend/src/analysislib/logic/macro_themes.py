# backend/analysislib/macro_themes.py
from typing import List, Dict
import uuid
from datetime import datetime, timezone


def _safe_asset_classes(event: Dict) -> list[str]:
    asset_classes = event.get("asset_classes")
    if isinstance(asset_classes, list):
        return [asset for asset in asset_classes if isinstance(asset, str) and asset]
    return []


def _parse_published_at(value: str | None) -> datetime:
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            pass
    return datetime.now(timezone.utc)


def group_events_into_themes(events: List[Dict]) -> List[Dict]:
    themes_dict: Dict[str, List[Dict]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue
        topic = event.get("topic")
        assets = _safe_asset_classes(event)
        key = topic.strip() if isinstance(topic, str) and topic.strip() else "-".join(assets) or "misc"
        themes_dict.setdefault(key, []).append(event)

    theme_objects = []
    for key, events_in_theme in themes_dict.items():
        timestamps = [_parse_published_at(e.get("published_at")) for e in events_in_theme]
        first_seen = min(timestamps)
        last_seen = max(timestamps)
        asset_classes = list({asset for e in events_in_theme for asset in _safe_asset_classes(e)})
        regions = [r for r in (e.get("region") for e in events_in_theme) if isinstance(r, str) and r]
        region = max(set(regions), key=regions.count) if regions else ""

        theme_objects.append({
            "theme_id": str(uuid.uuid4()),
            "title": key,
            "events": events_in_theme,
            "heat_score": 0.0,
            "first_seen_at": first_seen,
            "last_seen_at": last_seen,
            "asset_classes": asset_classes,
            "region": region,
            "status": "active",
            "description": "",
        })

    return theme_objects
