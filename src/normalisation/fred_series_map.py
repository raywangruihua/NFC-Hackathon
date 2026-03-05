"""
fred_series_map.py

Lookup table mapping every FRED series_id from the data library
to topic, asset_classes, region, and base_importance.

Mirrors the FRED_INDICATOR_MAP structure from the data library:
- growth_activity
- inflation
- labor
- rates_policy
- yield_curve
- credit_risk
- liquidity_credit
- housing
- consumer_sentiment
- fx_commodities
"""

from typing import Dict, Any

# ---------------------------------------------------------------------------
# Main lookup table
# Maps series_id → enrichment metadata
# ---------------------------------------------------------------------------
FRED_SERIES_MAP: Dict[str, Dict[str, Any]] = {

    # -----------------------------------------------------------------------
    # Growth / Activity
    # -----------------------------------------------------------------------
    "GDPC1": {
        "indicator":        "real_gdp",
        "topic":            "gdp",
        "asset_classes":    ["equities", "rates", "fx", "credit"],
        "base_importance":  0.95,
    },
    "GDP": {
        "indicator":        "nominal_gdp",
        "topic":            "gdp",
        "asset_classes":    ["equities", "rates", "fx"],
        "base_importance":  0.90,
    },
    "INDPRO": {
        "indicator":        "industrial_production",
        "topic":            "gdp",
        "asset_classes":    ["equities", "commodities"],
        "base_importance":  0.75,
    },
    "PAYEMS": {
        "indicator":        "nonfarm_payrolls",
        "topic":            "employment",
        "asset_classes":    ["equities", "rates", "fx"],
        "base_importance":  0.95,
    },
    "RSAFS": {
        "indicator":        "retail_sales",
        "topic":            "gdp",
        "asset_classes":    ["equities", "consumer"],
        "base_importance":  0.80,
    },
    "DGORDER": {
        "indicator":        "durable_goods_orders",
        "topic":            "gdp",
        "asset_classes":    ["equities", "industrials"],
        "base_importance":  0.75,
    },
    "CUMFNS": {
        "indicator":        "capacity_utilization",
        "topic":            "gdp",
        "asset_classes":    ["equities", "industrials"],
        "base_importance":  0.65,
    },

    # -----------------------------------------------------------------------
    # Inflation
    # -----------------------------------------------------------------------
    "CPIAUCSL": {
        "indicator":        "headline_cpi",
        "topic":            "inflation",
        "asset_classes":    ["rates", "equities", "fx", "bonds"],
        "base_importance":  0.95,
    },
    "CPILFESL": {
        "indicator":        "core_cpi",
        "topic":            "inflation",
        "asset_classes":    ["rates", "equities", "fx", "bonds"],
        "base_importance":  0.95,
    },
    "PCEPI": {
        "indicator":        "pce",
        "topic":            "inflation",
        "asset_classes":    ["rates", "bonds"],
        "base_importance":  0.90,
    },
    "PCEPILFE": {
        "indicator":        "core_pce",
        "topic":            "inflation",
        "asset_classes":    ["rates", "bonds"],
        "base_importance":  0.95,
    },
    "PPIACO": {
        "indicator":        "ppi",
        "topic":            "inflation",
        "asset_classes":    ["equities", "commodities"],
        "base_importance":  0.80,
    },
    "T5YIE": {
        "indicator":        "breakeven_5y",
        "topic":            "inflation",
        "asset_classes":    ["bonds", "rates"],
        "base_importance":  0.85,
    },
    "T10YIE": {
        "indicator":        "breakeven_10y",
        "topic":            "inflation",
        "asset_classes":    ["bonds", "rates"],
        "base_importance":  0.85,
    },

    # -----------------------------------------------------------------------
    # Labour Market
    # -----------------------------------------------------------------------
    "UNRATE": {
        "indicator":        "unemployment_rate",
        "topic":            "employment",
        "asset_classes":    ["equities", "rates", "fx"],
        "base_importance":  0.90,
    },
    "U6RATE": {
        "indicator":        "underemployment_u6",
        "topic":            "employment",
        "asset_classes":    ["equities", "rates"],
        "base_importance":  0.80,
    },
    "CIVPART": {
        "indicator":        "labor_force_participation",
        "topic":            "employment",
        "asset_classes":    ["equities", "rates"],
        "base_importance":  0.75,
    },
    "ICSA": {
        "indicator":        "initial_claims",
        "topic":            "employment",
        "asset_classes":    ["equities", "rates"],
        "base_importance":  0.80,
    },
    "AHEMAN": {
        "indicator":        "avg_hourly_earnings_mfg",
        "topic":            "employment",
        "asset_classes":    ["rates", "equities"],
        "base_importance":  0.75,
    },

    # -----------------------------------------------------------------------
    # Rates / Monetary Policy
    # -----------------------------------------------------------------------
    "FEDFUNDS": {
        "indicator":        "fed_funds_effective",
        "topic":            "monetary_policy",
        "asset_classes":    ["rates", "bonds", "fx", "equities"],
        "base_importance":  0.95,
    },
    "SOFR": {
        "indicator":        "sofr",
        "topic":            "monetary_policy",
        "asset_classes":    ["rates", "bonds"],
        "base_importance":  0.85,
    },
    "DFF": {
        "indicator":        "fed_funds_daily",
        "topic":            "monetary_policy",
        "asset_classes":    ["rates", "bonds", "fx"],
        "base_importance":  0.90,
    },
    "DFEDTARU": {
        "indicator":        "fed_target_upper",
        "topic":            "monetary_policy",
        "asset_classes":    ["rates", "bonds"],
        "base_importance":  0.95,
    },
    "DFEDTARL": {
        "indicator":        "fed_target_lower",
        "topic":            "monetary_policy",
        "asset_classes":    ["rates", "bonds"],
        "base_importance":  0.95,
    },

    # -----------------------------------------------------------------------
    # Yield Curve / Duration
    # -----------------------------------------------------------------------
    "DGS2": {
        "indicator":        "ust_2y",
        "topic":            "yield_curve",
        "asset_classes":    ["bonds", "rates"],
        "base_importance":  0.85,
    },
    "DGS10": {
        "indicator":        "ust_10y",
        "topic":            "yield_curve",
        "asset_classes":    ["bonds", "rates", "equities"],
        "base_importance":  0.90,
    },
    "DGS30": {
        "indicator":        "ust_30y",
        "topic":            "yield_curve",
        "asset_classes":    ["bonds", "rates"],
        "base_importance":  0.80,
    },
    "T10Y2Y": {
        "indicator":        "curve_10y_2y",
        "topic":            "yield_curve",
        "asset_classes":    ["bonds", "rates", "equities"],
        "base_importance":  0.90,
    },
    "T10Y3M": {
        "indicator":        "curve_10y_3m",
        "topic":            "yield_curve",
        "asset_classes":    ["bonds", "rates"],
        "base_importance":  0.85,
    },

    # -----------------------------------------------------------------------
    # Credit / Risk Premia
    # -----------------------------------------------------------------------
    "BAMLC0A0CM": {
        "indicator":        "ig_oas",
        "topic":            "credit",
        "asset_classes":    ["credit", "bonds", "equities"],
        "base_importance":  0.85,
    },
    "BAMLH0A0HYM2": {
        "indicator":        "hy_oas",
        "topic":            "credit",
        "asset_classes":    ["credit", "bonds", "equities"],
        "base_importance":  0.85,
    },
    "BAA10Y": {
        "indicator":        "baa_tsy_spread",
        "topic":            "credit",
        "asset_classes":    ["credit", "bonds"],
        "base_importance":  0.80,
    },
    "TEDRATE": {
        "indicator":        "ted_spread",
        "topic":            "credit",
        "asset_classes":    ["credit", "rates"],
        "base_importance":  0.80,
    },
    "NFCI": {
        "indicator":        "financial_conditions_nfci",
        "topic":            "credit",
        "asset_classes":    ["equities", "credit", "rates"],
        "base_importance":  0.85,
    },
    "STLFSI4": {
        "indicator":        "stress_index_stlfsi",
        "topic":            "credit",
        "asset_classes":    ["equities", "credit", "rates"],
        "base_importance":  0.85,
    },

    # -----------------------------------------------------------------------
    # Money / Liquidity / Credit
    # -----------------------------------------------------------------------
    "M2SL": {
        "indicator":        "m2_money_supply",
        "topic":            "liquidity",
        "asset_classes":    ["rates", "fx", "equities"],
        "base_importance":  0.70,
    },
    "WALCL": {
        "indicator":        "fed_balance_sheet",
        "topic":            "liquidity",
        "asset_classes":    ["rates", "bonds", "equities"],
        "base_importance":  0.85,
    },
    "TOTBKCR": {
        "indicator":        "total_bank_credit",
        "topic":            "liquidity",
        "asset_classes":    ["credit", "equities"],
        "base_importance":  0.70,
    },
    "BUSLOANS": {
        "indicator":        "ci_loans",
        "topic":            "liquidity",
        "asset_classes":    ["credit", "equities"],
        "base_importance":  0.70,
    },

    # -----------------------------------------------------------------------
    # Housing
    # -----------------------------------------------------------------------
    "HOUST": {
        "indicator":        "housing_starts",
        "topic":            "housing",
        "asset_classes":    ["equities", "reits"],
        "base_importance":  0.75,
    },
    "PERMIT": {
        "indicator":        "building_permits",
        "topic":            "housing",
        "asset_classes":    ["equities", "reits"],
        "base_importance":  0.70,
    },
    "CSUSHPINSA": {
        "indicator":        "case_shiller_us",
        "topic":            "housing",
        "asset_classes":    ["reits", "equities", "credit"],
        "base_importance":  0.75,
    },
    "MORTGAGE30US": {
        "indicator":        "mortgage_30y",
        "topic":            "housing",
        "asset_classes":    ["rates", "reits", "bonds"],
        "base_importance":  0.80,
    },

    # -----------------------------------------------------------------------
    # Consumer / Sentiment
    # -----------------------------------------------------------------------
    "UMCSENT": {
        "indicator":        "umich_sentiment",
        "topic":            "consumer_sentiment",
        "asset_classes":    ["equities", "consumer"],
        "base_importance":  0.75,
    },
    "PCE": {
        "indicator":        "personal_consumption",
        "topic":            "consumer_sentiment",
        "asset_classes":    ["equities", "consumer"],
        "base_importance":  0.80,
    },
    "PSAVERT": {
        "indicator":        "personal_saving_rate",
        "topic":            "consumer_sentiment",
        "asset_classes":    ["equities", "consumer"],
        "base_importance":  0.65,
    },

    # -----------------------------------------------------------------------
    # FX / External / Commodities
    # -----------------------------------------------------------------------
    "DTWEXBGS": {
        "indicator":        "usd_trade_weighted",
        "topic":            "fx",
        "asset_classes":    ["fx", "commodities", "equities"],
        "base_importance":  0.85,
    },
    "DEXUSEU": {
        "indicator":        "usd_eur",
        "topic":            "fx",
        "asset_classes":    ["fx"],
        "base_importance":  0.75,
    },
    "DEXJPUS": {
        "indicator":        "usd_jpy",
        "topic":            "fx",
        "asset_classes":    ["fx"],
        "base_importance":  0.75,
    },
    "DCOILWTICO": {
        "indicator":        "wti_crude",
        "topic":            "commodities",
        "asset_classes":    ["commodities", "equities", "fx"],
        "base_importance":  0.85,
    },
}

# ---------------------------------------------------------------------------
# Default fallback for unknown series
# ---------------------------------------------------------------------------
DEFAULT_SERIES_META: Dict[str, Any] = {
    "indicator":        "unknown",
    "topic":            "macro",
    "asset_classes":    ["equities"],
    "base_importance":  0.50,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_series_meta(series_id: str) -> Dict[str, Any]:
    """Return metadata for a series_id, falling back to default if unknown."""
    return FRED_SERIES_MAP.get(series_id, DEFAULT_SERIES_META)


def list_topics() -> list:
    """Return all unique topics across the map."""
    return list(set(v["topic"] for v in FRED_SERIES_MAP.values()))


def get_series_by_topic(topic: str) -> Dict[str, Dict]:
    """Return all series belonging to a given topic."""
    return {
        sid: meta
        for sid, meta in FRED_SERIES_MAP.items()
        if meta["topic"] == topic
    }


if __name__ == "__main__":
    print(f"Total series mapped: {len(FRED_SERIES_MAP)}")
    print(f"\nTopics: {list_topics()}")
    print(f"\nInflation series: {list(get_series_by_topic('inflation').keys())}")