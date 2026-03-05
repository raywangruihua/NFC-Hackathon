"""
fred_to_event.py
Converts raw FRED API response to unified EnrichedEvent JSON format.

Usage:
    python fred_to_event.py --input fred_data.json --series CPIAUCSL
    python fred_to_event.py --input fred_data.json --series GDP --output events.json
"""

import json
import uuid
from datetime import datetime

from fred_series_map import FRED_SERIES_MAP, get_series_meta


# ---------------------------------------------------------------------------
# Importance scoring
# ---------------------------------------------------------------------------
def deviation_score(current: float, previous: float) -> float:
    """Score based on % change from previous observation."""
    if previous == 0:
        return 0.5
    change = abs((current - previous) / previous)
    if change > 0.05:   return 1.0
    elif change > 0.02: return 0.7
    elif change > 0.01: return 0.4
    else:               return 0.1


def recency_score(timestamp: str) -> float:
    """Score based on how recent the observation is."""
    try:
        date = datetime.strptime(timestamp, "%Y-%m-%d")
        days_old = (datetime.now() - date).days
        if days_old <= 7:    return 1.0
        elif days_old <= 30: return 0.7
        elif days_old <= 90: return 0.4
        else:                return 0.1
    except ValueError:
        return 0.5


def calculate_importance(
    series_id: str,
    current: float,
    previous: float,
    timestamp: str
) -> float:
    """
    Weighted importance score:
      50% series significance (from fred_series_map)
      30% deviation from previous value
      20% recency
    """
    meta      = get_series_meta(series_id)
    base      = meta["base_importance"]
    deviation = deviation_score(current, previous)
    recency   = recency_score(timestamp)

    score = (base * 0.5) + (deviation * 0.3) + (recency * 0.2)
    return round(min(score, 1.0), 2)


# ---------------------------------------------------------------------------
# Core converter
# ---------------------------------------------------------------------------
def observation_to_event(
    obs: dict,
    previous_value: float,
    series_id: str,
    units: str,
) -> dict:
    """Convert a single FRED observation to a unified event dict."""
    value     = float(obs["value"])
    timestamp = obs["date"]
    meta      = get_series_meta(series_id)

    return {
        # --- Shared fields (same shape as news events) ---
        "event_id":         str(uuid.uuid4()),
        "event_type":       "macro",
        "source":           "FRED",
        "timestamp":        timestamp,
        "topic":            meta["topic"],
        "asset_classes":    meta["asset_classes"],
        "region":           "US",
        "importance_score": calculate_importance(
                                series_id, value, previous_value, timestamp
                            ),

        # --- FRED specific ---
        "series_id":        series_id,
        "indicator_name":   meta["indicator"],
        "value":            value,
        "units":            units,

        # --- News specific (null for FRED) ---
        "content":          None,
        "entities":         [],
        "sentiment":        None,
        "signal":           None,
        "url":              None,
    }


def convert_fred_response(raw: dict, series_id: str) -> list:
    """
    Convert a full FRED API JSON response to a list of unified event dicts.
    Skips observations where value is missing (".").
    Drops unknown series entirely.
    """
    if series_id not in FRED_SERIES_MAP:
        print(f"Warning: Unknown series '{series_id}' — not in lookup table, skipping")
        return []

    observations   = raw.get("observations", [])
    units          = raw.get("units", "")
    events         = []
    previous_value = 0.0

    for obs in observations:
        if obs.get("value") == ".":
            continue
        event = observation_to_event(obs, previous_value, series_id, units)
        previous_value = float(obs["value"])
        events.append(event)

    return events
