# backend/analysislib/macro_themes.py
from typing import List, Dict
import uuid
from datetime import datetime, timezone

def group_events_into_themes(events: List[Dict]) -> List[Dict]:
    """
    Groups events into macro themes, returning structures ready for `themes` and `event_theme_map`.
    """
    themes_dict: Dict[str, List[Dict]] = {}

    for event in events:
        key = event.get("topic") or "-".join(event.get("asset_classes", [])) or "misc"
        if key not in themes_dict:
            themes_dict[key] = []
        themes_dict[key].append(event)

    theme_objects = []
    for key, events_in_theme in themes_dict.items():
        first_seen = min(
            [datetime.fromisoformat(e["published_at"].replace("Z", "+00:00")) for e in events_in_theme]
        )
        last_seen = max(
            [datetime.fromisoformat(e["published_at"].replace("Z", "+00:00")) for e in events_in_theme]
        )
        asset_classes = list({a for e in events_in_theme for a in e.get("asset_classes", [])})

        theme_objects.append({
            "theme_id": str(uuid.uuid4()),
            "title": key,
            "events": events_in_theme,
            "heat_score": 0.0,  # placeholder, calculate later
            "first_seen_at": first_seen,
            "last_seen_at": last_seen,
            "asset_classes": asset_classes,
            "region": "",  # placeholder
            "status": "active",
            "description": ""
        })

    return theme_objects