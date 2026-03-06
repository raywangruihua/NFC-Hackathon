# backend/analysislib/macro_themes.py
from typing import List, Dict
import uuid

def group_events_into_themes(events: List[Dict]) -> List[Dict]:
    """
    Groups events into macro themes.
    For now, a simple rule-based placeholder: group by topic or asset_classes.
    Later, AI-based clustering can be plugged in.
    """
    themes: Dict[str, List[Dict]] = {}

    for event in events:
        # Use topic if available, otherwise asset_classes joined as a key
        key = event.get("topic") or "-".join(event.get("asset_classes", [])) or "misc"
        if key not in themes:
            themes[key] = []
        themes[key].append(event)

    # Build theme objects
    theme_objects = []
    for key, events_in_theme in themes.items():
        theme_objects.append({
            "theme_id": str(uuid.uuid4()),
            "title": key,
            "events": events_in_theme,
            "heat_score": 0.0,  # placeholder, calculate later
        })

    return theme_objects