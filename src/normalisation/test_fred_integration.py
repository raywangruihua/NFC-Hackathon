"""
test_integration.py
Integration tests between Kai Jie's data library and the normalisation pipeline.

Tests the full flow:
    get_fred_indicator_data() / get_fred_category_data()
        → convert_fred_response()
            → validated EnrichedEvent output

Run with:
    pytest test_integration.py -v -s

The -s flag shows print output in the terminal.

Requirements:
    - FRED_API_KEY set in .env
    - pip install pytest python-dotenv requests
"""

import pytest
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(Path(__file__).parent / ".env")

pytestmark = pytest.mark.skipif(
    not os.getenv("FRED_API_KEY"),
    reason="FRED_API_KEY not set in .env — skipping integration tests"
)

from backend.datalib import (
    get_fred_indicator_data,
    get_fred_category_data,
    get_fred_series_id,
    list_fred_categories,
    list_fred_indicators,
    FRED_INDICATOR_MAP,
)
from fred_to_event import convert_fred_response
from fred_series_map import FRED_SERIES_MAP

REQUIRED_EVENT_FIELDS = [
    "event_id", "event_type", "source", "timestamp",
    "topic", "asset_classes", "region", "importance_score",
    "series_id", "value", "units",
    "content", "entities", "sentiment", "signal", "url"
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def print_events(events: list, label: str) -> None:
    """Print a human readable summary of converted events."""
    print(f"\n{'='*60}")
    print(f"  {label} — {len(events)} event(s)")
    print(f"{'='*60}")
    for i, event in enumerate(events):
        print(f"\n  [{i+1}] {event['series_id']} — {event['indicator_name']}")
        print(f"       date:       {event['timestamp']}")
        print(f"       value:      {event['value']} {event['units']}")
        print(f"       topic:      {event['topic']}")
        print(f"       assets:     {', '.join(event['asset_classes'])}")
        print(f"       importance: {event['importance_score']}")
    print()


def assert_valid_event(event: dict, series_id: str) -> None:
    """Assert a single event has the correct shape and values."""
    for field in REQUIRED_EVENT_FIELDS:
        assert field in event, f"Missing field '{field}' in event for {series_id}"

    assert event["event_type"]  == "macro"
    assert event["source"]      == "FRED"
    assert event["region"]      == "US"
    assert event["series_id"]   == series_id
    assert isinstance(event["value"], float)
    assert isinstance(event["asset_classes"], list)
    assert len(event["asset_classes"]) > 0
    assert 0.0 <= event["importance_score"] <= 1.0

    assert event["content"]   is None
    assert event["sentiment"] is None
    assert event["signal"]    is None
    assert event["url"]       is None
    assert event["entities"]  == []


# ---------------------------------------------------------------------------
# Single indicator tests
# ---------------------------------------------------------------------------
class TestSingleIndicator:

    def test_cpi_full_flow(self):
        raw       = get_fred_indicator_data(indicator_name="headline_cpi", category="inflation", limit=3)
        series_id = get_fred_series_id("headline_cpi", category="inflation")
        events    = convert_fred_response(raw, series_id)

        print_events(events, "CPI (headline_cpi)")

        assert len(events) == 3
        for event in events:
            assert_valid_event(event, "CPIAUCSL")
            assert event["topic"] == "inflation"

    def test_fed_funds_full_flow(self):
        raw       = get_fred_indicator_data(indicator_name="fed_funds_effective", category="rates_policy", limit=3)
        series_id = get_fred_series_id("fed_funds_effective", category="rates_policy")
        events    = convert_fred_response(raw, series_id)

        print_events(events, "Fed Funds (fed_funds_effective)")

        assert len(events) == 3
        for event in events:
            assert_valid_event(event, "FEDFUNDS")
            assert event["topic"] == "monetary_policy"

    def test_unemployment_full_flow(self):
        raw       = get_fred_indicator_data(indicator_name="unemployment_rate", category="labor", limit=3)
        series_id = get_fred_series_id("unemployment_rate", category="labor")
        events    = convert_fred_response(raw, series_id)

        print_events(events, "Unemployment (unemployment_rate)")

        assert len(events) == 3
        for event in events:
            assert_valid_event(event, "UNRATE")
            assert event["topic"] == "employment"

    def test_wti_crude_full_flow(self):
        raw       = get_fred_indicator_data(indicator_name="wti_crude", category="fx_commodities", limit=3)
        series_id = get_fred_series_id("wti_crude", category="fx_commodities")
        events    = convert_fred_response(raw, series_id)

        print_events(events, "WTI Crude (wti_crude)")

        assert len(events) == 3
        for event in events:
            assert_valid_event(event, "DCOILWTICO")
            assert event["topic"] == "commodities"

    def test_units_propagated_from_api(self):
        raw    = get_fred_indicator_data(indicator_name="headline_cpi", limit=2)
        events = convert_fred_response(raw, "CPIAUCSL")

        expected_units = raw.get("units", "")
        print(f"\n  Units from API: '{expected_units}'")
        print(f"  Units in event: '{events[0]['units']}'")

        for event in events:
            assert event["units"] == expected_units

    def test_event_ids_are_unique(self):
        raw    = get_fred_indicator_data(indicator_name="headline_cpi", limit=5)
        events = convert_fred_response(raw, "CPIAUCSL")
        ids    = [e["event_id"] for e in events]

        print(f"\n  Generated {len(ids)} unique event IDs:")
        for eid in ids:
            print(f"    {eid}")

        assert len(ids) == len(set(ids))

    def test_observations_respect_limit(self):
        raw    = get_fred_indicator_data(indicator_name="unemployment_rate", limit=2)
        events = convert_fred_response(raw, "UNRATE")

        print(f"\n  Requested limit: 2, got: {len(events)} events")
        assert len(events) <= 2


# ---------------------------------------------------------------------------
# Category-level tests
# ---------------------------------------------------------------------------
class TestCategoryFlow:

    def test_inflation_category_all_indicators(self):
        results    = get_fred_category_data(category="inflation", limit=2)
        indicators = list_fred_indicators("inflation")

        print(f"\n{'='*60}")
        print(f"  Inflation category — {len(indicators)} indicators")
        print(f"{'='*60}")

        for indicator_name, series_id in indicators.items():
            assert indicator_name in results
            events = convert_fred_response(results[indicator_name], series_id)

            print(f"\n  {series_id} ({indicator_name})")
            print(f"    events:     {len(events)}")
            if events:
                print(f"    latest:     {events[-1]['timestamp']} — {events[-1]['value']} {events[-1]['units']}")
                print(f"    importance: {events[-1]['importance_score']}")

            assert len(events) > 0
            for event in events:
                assert_valid_event(event, series_id)
                assert event["topic"] == "inflation"

    def test_all_categories_produce_events(self):
        missing_from_map = []

        print(f"\n{'='*60}")
        print(f"  Checking all categories against fred_series_map")
        print(f"{'='*60}")

        for category in list_fred_categories():
            indicators = list_fred_indicators(category)
            covered    = [s for s in indicators.values() if s in FRED_SERIES_MAP]
            missing    = [s for s in indicators.values() if s not in FRED_SERIES_MAP]

            print(f"\n  {category}: {len(covered)}/{len(indicators)} covered", end="")
            if missing:
                print(f" — missing: {missing}")
                missing_from_map.extend(missing)
            else:
                print(" ✓")

        assert missing_from_map == [], \
            f"Series in data library but missing from fred_series_map: {missing_from_map}"


# ---------------------------------------------------------------------------
# Date filtering tests
# ---------------------------------------------------------------------------
class TestDateFiltering:

    def test_start_date_filters_correctly(self):
        raw    = get_fred_indicator_data(indicator_name="headline_cpi", start_date="2024-01-01", limit=5)
        events = convert_fred_response(raw, "CPIAUCSL")

        print(f"\n  Filtering CPI from 2024-01-01, got {len(events)} events:")
        for event in events:
            print(f"    {event['timestamp']} — {event['value']} {event['units']}")

        for event in events:
            assert event["timestamp"] >= "2024-01-01"

    def test_date_range_filtering(self):
        raw    = get_fred_indicator_data(
                    indicator_name="unemployment_rate",
                    start_date="2023-01-01",
                    end_date="2023-12-31"
                )
        events = convert_fred_response(raw, "UNRATE")

        print(f"\n  Unemployment 2023 range, got {len(events)} events:")
        for event in events:
            print(f"    {event['timestamp']} — {event['value']}%")

        for event in events:
            assert "2023-01-01" <= event["timestamp"] <= "2023-12-31"


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------
class TestEdgeCases:

    def test_missing_value_dots_are_skipped(self):
        raw = get_fred_indicator_data(indicator_name="headline_cpi", limit=3)

        raw_with_missing = dict(raw)
        raw_with_missing["observations"] = list(raw["observations"])
        raw_with_missing["observations"][1] = {
            **raw["observations"][1],
            "value": "."
        }

        events = convert_fred_response(raw_with_missing, "CPIAUCSL")

        print(f"\n  Injected 1 missing value into 3 observations")
        print(f"  Expected 2 events, got {len(events)}")

        assert len(events) == 2

    def test_unknown_series_returns_empty(self):
        raw    = get_fred_indicator_data(indicator_name="headline_cpi", limit=2)
        events = convert_fred_response(raw, "NOT_A_REAL_SERIES")

        print(f"\n  Unknown series 'NOT_A_REAL_SERIES' → {len(events)} events (expected 0)")

        assert events == []