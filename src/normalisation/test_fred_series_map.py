"""
test_fred_series_map.py
Tests for fred_series_map.py

Run with:
    pytest test_fred_series_map.py -v
"""

import pytest
from fred_series_map import (
    FRED_SERIES_MAP,
    get_series_meta,
    list_topics,
    get_series_by_topic,
)

ALL_KNOWN_SERIES = [
    # Growth / Activity
    "GDPC1", "GDP", "INDPRO", "PAYEMS", "RSAFS", "DGORDER", "CUMFNS",
    # Inflation
    "CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE", "PPIACO", "T5YIE", "T10YIE",
    # Labour
    "UNRATE", "U6RATE", "CIVPART", "ICSA", "AHEMAN",
    # Rates / Monetary Policy
    "FEDFUNDS", "SOFR", "DFF", "DFEDTARU", "DFEDTARL",
    # Yield Curve
    "DGS2", "DGS10", "DGS30", "T10Y2Y", "T10Y3M",
    # Credit / Risk
    "BAMLC0A0CM", "BAMLH0A0HYM2", "BAA10Y", "TEDRATE", "NFCI", "STLFSI4",
    # Liquidity
    "M2SL", "WALCL", "TOTBKCR", "BUSLOANS",
    # Housing
    "HOUST", "PERMIT", "CSUSHPINSA", "MORTGAGE30US",
    # Consumer / Sentiment
    "UMCSENT", "PCE", "PSAVERT",
    # FX / Commodities
    "DTWEXBGS", "DEXUSEU", "DEXJPUS", "DCOILWTICO",
]

REQUIRED_META_FIELDS = ["indicator", "topic", "asset_classes", "base_importance"]


# ---------------------------------------------------------------------------
# Coverage tests — every series from library must be present
# ---------------------------------------------------------------------------
class TestCoverage:

    def test_all_known_series_present(self):
        """Every series_id from the data library must be in the map."""
        missing = [s for s in ALL_KNOWN_SERIES if s not in FRED_SERIES_MAP]
        assert missing == [], f"Missing series from map: {missing}"

    def test_total_series_count(self):
        """Map should have at least 47 entries (one per series in data library)."""
        assert len(FRED_SERIES_MAP) >= 47


# ---------------------------------------------------------------------------
# Schema tests — every entry must have required fields with correct types
# ---------------------------------------------------------------------------
class TestSchema:

    @pytest.mark.parametrize("series_id", ALL_KNOWN_SERIES)
    def test_required_fields_present(self, series_id):
        """Every series must have all required metadata fields."""
        meta = FRED_SERIES_MAP[series_id]
        for field in REQUIRED_META_FIELDS:
            assert field in meta, f"{series_id} missing field: '{field}'"

    @pytest.mark.parametrize("series_id", ALL_KNOWN_SERIES)
    def test_topic_is_string(self, series_id):
        meta = FRED_SERIES_MAP[series_id]
        assert isinstance(meta["topic"], str), f"{series_id}: topic must be a string"
        assert len(meta["topic"]) > 0, f"{series_id}: topic must not be empty"

    @pytest.mark.parametrize("series_id", ALL_KNOWN_SERIES)
    def test_asset_classes_is_list(self, series_id):
        meta = FRED_SERIES_MAP[series_id]
        assert isinstance(meta["asset_classes"], list), \
            f"{series_id}: asset_classes must be a list"
        assert len(meta["asset_classes"]) > 0, \
            f"{series_id}: asset_classes must not be empty"

    @pytest.mark.parametrize("series_id", ALL_KNOWN_SERIES)
    def test_base_importance_range(self, series_id):
        """base_importance must be a float between 0.0 and 1.0."""
        meta = FRED_SERIES_MAP[series_id]
        score = meta["base_importance"]
        assert isinstance(score, float), \
            f"{series_id}: base_importance must be a float"
        assert 0.0 <= score <= 1.0, \
            f"{series_id}: base_importance {score} out of range [0.0, 1.0]"

    @pytest.mark.parametrize("series_id", ALL_KNOWN_SERIES)
    def test_indicator_is_string(self, series_id):
        meta = FRED_SERIES_MAP[series_id]
        assert isinstance(meta["indicator"], str), \
            f"{series_id}: indicator must be a string"


# ---------------------------------------------------------------------------
# get_series_meta tests
# ---------------------------------------------------------------------------
class TestGetSeriesMeta:

    def test_known_series_returns_meta(self):
        meta = get_series_meta("CPIAUCSL")
        assert meta["topic"] == "inflation"
        assert "rates" in meta["asset_classes"]
        assert meta["base_importance"] == 0.95

    def test_unknown_series_raises_key_error(self):
        """Unknown series must raise KeyError — they should be dropped."""
        with pytest.raises(KeyError):
            get_series_meta("UNKNOWN_XYZ")

    def test_unknown_series_error_message(self):
        """Error message should mention the series_id."""
        with pytest.raises(KeyError, match="FAKE123"):
            get_series_meta("FAKE123")

    def test_fed_funds_meta(self):
        meta = get_series_meta("FEDFUNDS")
        assert meta["topic"] == "monetary_policy"
        assert meta["base_importance"] >= 0.90

    def test_gdp_meta(self):
        meta = get_series_meta("GDPC1")
        assert meta["topic"] == "gdp"
        assert "equities" in meta["asset_classes"]


# ---------------------------------------------------------------------------
# list_topics tests
# ---------------------------------------------------------------------------
class TestListTopics:

    def test_returns_list(self):
        topics = list_topics()
        assert isinstance(topics, list)

    def test_expected_topics_present(self):
        topics = list_topics()
        expected = [
            "inflation", "gdp", "employment", "monetary_policy",
            "yield_curve", "credit", "liquidity", "housing",
            "consumer_sentiment", "fx", "commodities"
        ]
        for t in expected:
            assert t in topics, f"Expected topic '{t}' not found in list_topics()"

    def test_no_duplicate_topics(self):
        topics = list_topics()
        assert len(topics) == len(set(topics)), "list_topics() returned duplicates"


# ---------------------------------------------------------------------------
# get_series_by_topic tests
# ---------------------------------------------------------------------------
class TestGetSeriesByTopic:

    def test_inflation_series(self):
        result = get_series_by_topic("inflation")
        assert "CPIAUCSL" in result
        assert "CPILFESL" in result
        assert "PCEPILFE" in result

    def test_employment_series(self):
        result = get_series_by_topic("employment")
        assert "UNRATE" in result
        assert "PAYEMS" in result

    def test_unknown_topic_returns_empty(self):
        result = get_series_by_topic("nonexistent_topic")
        assert result == {}

    def test_all_results_match_topic(self):
        """Every result returned must actually have the requested topic."""
        for topic in list_topics():
            results = get_series_by_topic(topic)
            for sid, meta in results.items():
                assert meta["topic"] == topic, \
                    f"{sid} returned for topic '{topic}' but has topic '{meta['topic']}'"