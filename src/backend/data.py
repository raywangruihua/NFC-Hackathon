"""
Data library

Data collected is based on whether it is valuable for asset management and risk assessment.
Functions that start with 'get' return data in json formats.
Functions that start with 'list' return a list of available data.

Collects data from the following APIs:
- Federal Reserve Economic Data (FRED)
  - US macro and regional economic time series
  - Annual, quarterly, monthly, weekly and daily
- World Bank Indicators API
- OECD Data API
- IMF Data API
- Eurostat API
- ECB Data Portal API
- BLS Public Data API
- BEA API
- U.S. Census API
- U.S. Treasury Fiscal Data API
- EIA Open Data API

Available and relevant macroeconomic factors (FRED):
- Growth/Activity
  - Real GDP
  - Payrolls
  - Industrial Production
  - Retail Sales
  - PMI
- Inflation
  - CPI
  - Core CPI
  - PCE
  - Core PCE
  - PPI
  - Breakevens
- Labour Market
  - Unemployment
  - Participation
  - Claims
  - Wage Growth
- Rates/Monetary Policy
  - Fed Funds
  - SOFR
  - Policy Band
- Yield Curve/Duration
  - Treasury Tenor Yields
  - Curve Spreads
- Credit/Risk Premia
  - IG/HY Spreads
  - TED Spread
  - Financial Stress/Conditions
- Money/Liquidity/Credit
  - M2
  - Fed Balance Sheet
  - Bank Credit
  - C&I Loans
- Housing
  - Starts
  - Permits
  - House Prices
  - Mortgage Rates
- Consumer/Sentiment
  - Sentiment
  - Consumption
  - Saving Rate
- FX/External/Commodities
  - Broad Dollar
  - Major FX
  - Oil
  - Gold
"""

import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
REQUEST_TIMEOUT = 20

# Get API keys
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

######################### FRED Data API #########################

# All relevant FRED series data, maps keyterms to series_id
FRED_INDICATOR_MAP: Dict[str, Dict[str, str]] = {
    "growth_activity": {
        "real_gdp": "GDPC1",
        "nominal_gdp": "GDP",
        "industrial_production": "INDPRO",
        "nonfarm_payrolls": "PAYEMS",
        "retail_sales": "RSAFS",
        "durable_goods_orders": "DGORDER",
        # "ism_manufacturing_pmi": "NAPM", # 400 Client Error
        "capacity_utilization": "CUMFNS",
    },
    "inflation": {
        "headline_cpi": "CPIAUCSL",
        "core_cpi": "CPILFESL",
        "pce": "PCEPI",
        "core_pce": "PCEPILFE",
        "ppi": "PPIACO",
        "breakeven_5y": "T5YIE",
        "breakeven_10y": "T10YIE",
    },
    "labor": {
        "unemployment_rate": "UNRATE",
        "underemployment_u6": "U6RATE",
        "labor_force_participation": "CIVPART",
        "initial_claims": "ICSA",
        "avg_hourly_earnings_mfg": "AHEMAN",
    },
    "rates_policy": {
        "fed_funds_effective": "FEDFUNDS",
        "sofr": "SOFR",
        "fed_funds_daily": "DFF",
        "fed_target_upper": "DFEDTARU",
        "fed_target_lower": "DFEDTARL",
    },
    "yield_curve": {
        "ust_2y": "DGS2",
        "ust_10y": "DGS10",
        "ust_30y": "DGS30",
        "curve_10y_2y": "T10Y2Y",
        "curve_10y_3m": "T10Y3M",
    },
    "credit_risk": {
        "ig_oas": "BAMLC0A0CM",
        "hy_oas": "BAMLH0A0HYM2",
        "baa_tsy_spread": "BAA10Y",
        "ted_spread": "TEDRATE",
        "financial_conditions_nfci": "NFCI",
        "stress_index_stlfsi": "STLFSI4",
    },
    "liquidity_credit": {
        "m2_money_supply": "M2SL",
        "fed_balance_sheet": "WALCL",
        "total_bank_credit": "TOTBKCR",
        "ci_loans": "BUSLOANS",
    },
    "housing": {
        "housing_starts": "HOUST",
        "building_permits": "PERMIT",
        "case_shiller_us": "CSUSHPINSA",
        "mortgage_30y": "MORTGAGE30US",
    },
    "consumer_sentiment": {
        "umich_sentiment": "UMCSENT",
        "personal_consumption": "PCE",
        "personal_saving_rate": "PSAVERT",
    },
    "fx_commodities": {
        "usd_trade_weighted": "DTWEXBGS",
        "usd_eur": "DEXUSEU",
        "usd_jpy": "DEXJPUS",
        "wti_crude": "DCOILWTICO",
        # "gold": "GOLDAMGBD228NLBM", 400 Client Error
    },
}


def list_fred_categories() -> List[str]:
    """
    Return all available macroeconomic indicator categories.
    """
    return list(FRED_INDICATOR_MAP.keys())


def list_fred_indicators(category: str) -> Dict[str, str]:
    """
    Return all macroeconomic indicators for category.
    """
    if category not in FRED_INDICATOR_MAP:
        valid = ", ".join(list_fred_categories())
        raise ValueError(f"Unknown category '{category}'. Valid categories: {valid}")
    return FRED_INDICATOR_MAP[category]


def _flatten_indicators() -> Dict[str, str]:
    """
    Return a flat map of {indicator_name: series_id} across all categories.
    """
    out: Dict[str, str] = {}
    for indicators in FRED_INDICATOR_MAP.values():
        out.update(indicators)
    return out


def get_fred_series_id(indicator_name: str, category: Optional[str] = None) -> str:
    """
    Return series_id based on macroeconomic indicator name. Takes category for narrower search.
    """
    if category is not None:
        indicators = list_fred_indicators(category)
        if indicator_name not in indicators:
            valid = ", ".join(indicators.keys())
            raise ValueError(
                f"Unknown indicator '{indicator_name}' for category '{category}'. "
                f"Valid indicators: {valid}"
            )
        return indicators[indicator_name]

    all_indicators = _flatten_indicators()
    if indicator_name not in all_indicators:
        valid = ", ".join(all_indicators.keys())
        raise ValueError(f"Unknown indicator '{indicator_name}'. Valid indicators: {valid}")
    return all_indicators[indicator_name]


def _assert_fred_api_key() -> None:
    """
    Check for FRED API key.
    """
    if not FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is not set.")


def get_fred_data(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict:
    """
    Fetch observations for a FRED series.

    Args:
        series_id: FRED series ID, e.g. 'GDPC1'.
        start_date: Optional observation start date (YYYY-MM-DD).
        end_date: Optional observation end date (YYYY-MM-DD).
        sort_order: 'asc' or 'desc'.
        limit: Optional max number of observations.

    Returns:
        Dict: Raw JSON response from FRED.
    """
    _assert_fred_api_key()

    if sort_order not in {"asc", "desc"}:
        raise ValueError("sort_order must be 'asc' or 'desc'")

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": sort_order,
    }

    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date
    if limit is not None:
        params["limit"] = limit

    resp = requests.get(FRED_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# Main FRED API endpoint
def get_fred_indicator_data(
    indicator_name: str,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict:
    """
    Fetch data for a macroeconomic indicator from Federal Reserve Economic Data.

    See also
    --------
    :py:func:`list_fred_categories`
    :py:func:`list_fred_indicators`
    """
    series_id = get_fred_series_id(indicator_name, category=category)
    return get_fred_data(
        series_id=series_id,
        start_date=start_date,
        end_date=end_date,
        sort_order=sort_order,
        limit=limit,
    )


# Main FRED API endpoint
def get_fred_category_data(
    category: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict[str, Dict]:
    """
    Fetch data for all macroeconomic indicators in a category from Federal Reserve Economic Data.

    See also
    --------
    :py:func:`list_fred_categories`
    """
    indicators = list_fred_indicators(category)
    results: Dict[str, Dict] = {}

    for indicator_name, series_id in indicators.items():
        results[indicator_name] = get_fred_data(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            sort_order=sort_order,
            limit=limit,
        )

    return results


def test_fred() -> None:
    """
    Test if macroeconomic indicators are retrievable.
    """
    for category in FRED_INDICATOR_MAP.values(): 
        for indicator in category.keys():
            status = "ok" if get_fred_indicator_data(indicator_name=indicator, limit=1) else "not ok"
            print(f"{indicator} {status}")


if __name__ == "__main__":
    test_fred()
