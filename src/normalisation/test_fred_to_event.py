"""
test_fred_to_event.py
Tests for fred_to_event.py

Run with:
    pytest test_fred_to_event.py -v
"""

import pytest
from fred_to_event import (
    deviation_score,
    recency_score,
    calculate_importance,
    observation_to_event,
    convert_fred_response,
)

# ---------------------------------------------------------------------------
# Mock FRED API responses
# ---------------------------------------------------------------------------

MOCK_FRED_CPI = {
    "units": "Percent Change from Year Ago",
    "observations": [
        {"realtime_start": "2026-03-04", "realtime_end": "2026-03-04",
         "date": "2025-12-01", "value": "3.8"},
        {"realtime_start": "2026-03-04", "realtime_end": "2026-03-04",
         "date": "2026-01-01", "value": "4.2"},
        {"realtime_start": "2026-03-04", "realtime_end": "2026-03-04",
         "date": "2026-02-01", "value": "4.5"},
    ]
}

MOCK_FRED_WITH_MISSING = {
    "units": "Percent",
    "observations": [
        {"date": "2026-01-01", "value": "3.8"},
        {"date": "2026-02-01", "value": "."},     # missing value
        {"date": "2026-03-01", "value": "4.2"},
    ]
}

MOCK_FRED_EMPTY = {
    "units": "Percent",
    "observations": []
}

MOCK_FRED_ALL_MISSING = {
    "units": "Percent",
    "observations": [
        {"date": "2026-01-01", "value": "."},
        {"date": "2026-02-01", "value": "."},
    ]
}

REQUIRED_EVENT_FIELDS = [
    "event_id", "event_type", "source", "timestamp",
    "topic", "asset_classes", "region", "importance_score",
    "series_id", "value", "units",
    "content", "entities", "sentiment", "signal", "url"
]


# ---------------------------------------------------------------------------
# deviation_score tests
# ---------------------------------------------------------------------------
class TestDeviationScore:

    def test_large_change_returns_1(self):
        """Change > 5% should return 1.0."""
        assert deviation_score(110.0, 100.0) == 1.0

    def test_medium_change_returns_0_7(self):
        """Change between 2-5% should return 0.7."""
        assert deviation_score(103.0, 100.0) == 0.7

    def test_small_change_returns_0_4(self):
        """Change between 1-2% should return 0.4."""
        assert deviation_score(101.5, 100.0) == 0.4

    def test_minimal_change_returns_0_1(self):
        """Change < 1% should return 0.1."""
        assert deviation_score(100.5, 100.0) == 0.1

    def test_zero_previous_returns_0_5(self):
        """Previous value of 0 should return 0.5 (avoid division by zero)."""
        assert deviation_score(100.0, 0.0) == 0.5

    def test_negative_change_uses_absolute(self):
        """Negative change should use absolute value."""
        assert deviation_score(90.0, 100.0) == 1.0   # 10% drop = 1.0

    def test_no_change_returns_0_1(self):
        assert deviation_score(100.0, 100.0) == 0.1


# ---------------------------------------------------------------------------
# recency_score tests
# ---------------------------------------------------------------------------
class TestRecencyScore:

    def test_very_recent_returns_1(self):
        """Date within 7 days should return 1.0."""
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        assert recency_score(recent) == 1.0

    def test_within_30_days_returns_0_7(self):
        from datetime import datetime, timedelta
        date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
        assert recency_score(date) == 0.7

    def test_within_90_days_returns_0_4(self):
        from datetime import datetime, timedelta
        date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        assert recency_score(date) == 0.4

    def test_old_date_returns_0_1(self):
        assert recency_score("2020-01-01") == 0.1

    def test_invalid_date_returns_0_5(self):
        """Malformed date should return 0.5 fallback."""
        assert recency_score("not-a-date") == 0.5


# ---------------------------------------------------------------------------
# calculate_importance tests
# ---------------------------------------------------------------------------
class TestCalculateImportance:

    def test_returns_float(self):
        score = calculate_importance("CPIAUCSL", 4.2, 3.8, "2026-03-01")
        assert isinstance(score, float)

    def test_score_in_range(self):
        """Score must always be between 0.0 and 1.0."""
        score = calculate_importance("CPIAUCSL", 4.2, 3.8, "2026-03-01")
        assert 0.0 <= score <= 1.0

    def test_high_importance_series_scores_higher(self):
        """CPI (0.95 base) should score higher than housing starts (0.75 base)
        given same deviation and recency."""
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        cpi_score   = calculate_importance("CPIAUCSL", 110.0, 100.0, recent)
        houst_score = calculate_importance("HOUST",    110.0, 100.0, recent)
        assert cpi_score > houst_score

    def test_score_never_exceeds_1(self):
        """Score should be capped at 1.0."""
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        score = calculate_importance("CPIAUCSL", 200.0, 100.0, recent)
        assert score <= 1.0

    def test_score_is_rounded_to_2dp(self):
        score = calculate_importance("UNRATE", 4.2, 3.8, "2026-03-01")
        assert score == round(score, 2)


# ---------------------------------------------------------------------------
# observation_to_event tests
# ---------------------------------------------------------------------------
class TestObservationToEvent:

    def setup_method(self):
        self.obs = {"date": "2026-03-01", "value": "4.2"}
        self.event = observation_to_event(self.obs, 3.8, "CPIAUCSL", "Percent")

    def test_all_required_fields_present(self):
        for field in REQUIRED_EVENT_FIELDS:
            assert field in self.event, f"Missing field: '{field}'"

    def test_event_type_is_macro(self):
        assert self.event["event_type"] == "macro"

    def test_source_is_fred(self):
        assert self.event["source"] == "FRED"

    def test_region_is_us(self):
        assert self.event["region"] == "US"

    def test_value_is_float(self):
        assert isinstance(self.event["value"], float)
        assert self.event["value"] == 4.2

    def test_timestamp_preserved(self):
        assert self.event["timestamp"] == "2026-03-01"

    def test_series_id_preserved(self):
        assert self.event["series_id"] == "CPIAUCSL"

    def test_units_preserved(self):
        assert self.event["units"] == "Percent"

    def test_topic_from_map(self):
        assert self.event["topic"] == "inflation"

    def test_asset_classes_from_map(self):
        assert "rates" in self.event["asset_classes"]

    def test_news_fields_are_null(self):
        """News-specific fields must be null for FRED events."""
        assert self.event["content"]   is None
        assert self.event["sentiment"] is None
        assert self.event["signal"]    is None
        assert self.event["url"]       is None

    def test_entities_is_empty_list(self):
        assert self.event["entities"] == []

    def test_event_id_is_string(self):
        assert isinstance(self.event["event_id"], str)
        assert len(self.event["event_id"]) > 0

    def test_importance_score_in_range(self):
        score = self.event["importance_score"]
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# convert_fred_response tests
# ---------------------------------------------------------------------------
class TestConvertFredResponse:

    def test_returns_list(self):
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        assert isinstance(result, list)

    def test_correct_count(self):
        """Should return one event per valid observation."""
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        assert len(result) == 3

    def test_skips_missing_values(self):
        """Observations with value '.' must be skipped."""
        result = convert_fred_response(MOCK_FRED_WITH_MISSING, "CPIAUCSL")
        assert len(result) == 2

    def test_empty_observations_returns_empty_list(self):
        result = convert_fred_response(MOCK_FRED_EMPTY, "CPIAUCSL")
        assert result == []

    def test_all_missing_values_returns_empty_list(self):
        result = convert_fred_response(MOCK_FRED_ALL_MISSING, "CPIAUCSL")
        assert result == []

    def test_unknown_series_returns_empty_list(self):
        """Unknown series_id should be dropped — return empty list with warning."""
        result = convert_fred_response(MOCK_FRED_CPI, "UNKNOWN_XYZ")
        assert result == []

    def test_units_propagated_to_all_events(self):
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        for event in result:
            assert event["units"] == "Percent Change from Year Ago"

    def test_series_id_propagated_to_all_events(self):
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        for event in result:
            assert event["series_id"] == "CPIAUCSL"

    def test_events_ordered_by_observation_order(self):
        """Events should preserve the order of observations."""
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        timestamps = [e["timestamp"] for e in result]
        assert timestamps == sorted(timestamps)

    def test_all_events_have_unique_ids(self):
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        ids = [e["event_id"] for e in result]
        assert len(ids) == len(set(ids)), "event_ids are not unique"

    def test_values_are_floats(self):
        result = convert_fred_response(MOCK_FRED_CPI, "CPIAUCSL")
        for event in result:
            assert isinstance(event["value"], float)