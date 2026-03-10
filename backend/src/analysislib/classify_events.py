"""
Gemini-based event-to-theme classification.

Classifies events into existing themes using a closed-list prompt.
Creates new themes only when no existing theme fits.
"""

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from google import genai

from databaselib.db import (
    get_active_themes,
    get_event_theme_links,
    get_unlinked_events,
    insert_theme,
    link_event_to_theme,
)

load_dotenv()
log = logging.getLogger(__name__)

JsonDict = dict[str, Any]

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = "gemini-3.1-flash-lite-preview"


def _build_prompt(event: JsonDict, themes: list[JsonDict]) -> str:
    theme_lines = "\n".join(
        f'{i + 1}. {t["title"]} — {t.get("description") or "No description"}'
        for i, t in enumerate(themes)
    )

    content = (event.get("content") or "")[:500]
    topic = event.get("topic") or ""
    region = event.get("region") or ""
    assets = ", ".join(event.get("asset_classes") or [])

    return f"""You are a macroeconomic analyst. Classify this news event into ONE existing theme, or respond NEW if none fit.

EXISTING THEMES:
{theme_lines if theme_lines else "(none yet)"}

EVENT:
Topic: {topic}
Region: {region}
Assets: {assets}
Content: {content}

Rules:
- If an existing theme fits, respond with ONLY the theme number (e.g. "3").
- If no existing theme fits, respond with a JSON object on a single line:
  {{"new": true, "title": "Short Title", "description": "One sentence description", "region": "{region or 'Global'}", "asset_classes": [{', '.join(f'"{a}"' for a in (event.get("asset_classes") or []))}]}}
- Strongly prefer existing themes. Only create NEW for genuinely distinct macro topics.
- Do NOT add any extra text or explanation."""


def _parse_response(
    raw: str, themes: list[JsonDict]
) -> tuple[str | None, JsonDict | None]:
    """Return (existing_theme_id, None) or (None, new_theme_dict)."""
    text = raw.strip()

    # Try parsing as an integer index
    try:
        index = int(text) - 1
        if 0 <= index < len(themes):
            return themes[index]["theme_id"], None
    except ValueError:
        pass

    # Try parsing as JSON for a new theme
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and obj.get("new"):
            return None, obj
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from a larger response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            obj = json.loads(text[start:end])
            if isinstance(obj, dict) and obj.get("new"):
                return None, obj
        except json.JSONDecodeError:
            pass

    log.warning("Could not parse Gemini response: %s", text[:200])
    return None, None


def classify_and_link_event(event: JsonDict) -> list[str]:
    """
    Classify a single event into theme(s) and persist the link.

    Returns list of linked theme_ids.
    """
    event_id = event.get("event_id")
    if not event_id:
        return []

    # Skip if already linked
    existing_links = get_event_theme_links(event_id)
    if existing_links:
        return existing_links

    themes = get_active_themes()

    try:
        prompt = _build_prompt(event, themes)
        response = _client.models.generate_content(model=_MODEL, contents=prompt)
        raw_text = response.text or ""
    except Exception:
        log.exception("Gemini call failed for event %s", event_id)
        return []

    theme_id, new_theme = _parse_response(raw_text, themes)

    if theme_id:
        # Existing theme matched
        try:
            link_event_to_theme(event_id, theme_id)
            return [theme_id]
        except Exception:
            log.exception("Failed to link event %s to theme %s", event_id, theme_id)
            return []

    if new_theme:
        # Create new theme then link
        try:
            created = insert_theme(
                {
                    "title": new_theme.get("title", "Untitled Theme"),
                    "description": new_theme.get("description", ""),
                    "status": "active",
                    "heat_score": 0.0,
                    "region": new_theme.get("region", ""),
                    "asset_classes": new_theme.get("asset_classes", []),
                }
            )
            new_id = created["theme_id"]
            link_event_to_theme(event_id, new_id)
            log.info("Created new theme '%s' (%s)", new_theme.get("title"), new_id)
            return [new_id]
        except Exception:
            log.exception("Failed to create new theme for event %s", event_id)
            return []

    return []


def backfill_events(days: int = 7) -> JsonDict:
    """
    Classify and link all unlinked events from the last N days.
    """
    events = get_unlinked_events(days=days)
    stats: JsonDict = {"total": len(events), "linked": 0, "new_themes": 0, "skipped": 0, "errors": 0}

    themes_before = {t["theme_id"] for t in get_active_themes()}

    for event in events:
        try:
            result = classify_and_link_event(event)
            if result:
                stats["linked"] += 1
                for tid in result:
                    if tid not in themes_before:
                        stats["new_themes"] += 1
                        themes_before.add(tid)
            else:
                stats["skipped"] += 1
        except Exception:
            log.exception("Error classifying event %s", event.get("event_id"))
            stats["errors"] += 1

    return stats
