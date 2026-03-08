"""
Data collection library

Indicator data collected is based on whether it is valuable for asset management and risk assessment.
Functions that start with 'get' return data in json formats.
Functions that start with 'list' return a list of available data.

Collects data from the following APIs:
- Federal Reserve Economic Data (FRED)
  - US macro and regional economic time series
  - Annual, quarterly, monthly, weekly and daily updates
- World Bank Indicators API (WIP)
- OECD Data API (WIP)
- IMF Data API (WIP)
- Eurostat API (WIP)
- ECB Data Portal API (WIP)
- BLS Public Data API (WIP)
- BEA API (WIP)
- U.S. Census API (WIP)
- U.S. Treasury Fiscal Data API (WIP)
- EIA Open Data API (WIP)

Available and relevant macroeconomic factors (FRED):
- Growth/Activity
  - Real GDP, payrolls, industrial production, retail sales, PMI
- Inflation
  - CPI, core CPI, PCE, core PCE, PPI, breakevens
- Labour Market
  - Unemployment, participation, claims, wage growth
- Rates/Monetary Policy
  - Fed funds, SOFR, policy band
- Yield Curve/Duration
  - Treasury tenor yields, curve spreads
- Credit/Risk Premia
  - IG/HY spreads, TED spread, financial stress/conditions
- Money/Liquidity/Credit
  - M2, Fed balance sheet, bank credit, C&I loans
- Housing
  - Starts, permits, house prices, mortgage rates
- Consumer/Sentiment
  - Sentiment, consumption, saving rate
- FX/External/Commodities
  - Broad dollar, major FX, oil, gold

Issues:
- FRED
  - 'ism_manufacturing_pmi' and 'gold' series data not available

Webcrawler crawls news websites by searching key terms via the GDELT API. The crawler can be run via run_gdelt_spider()

TODO: Find optimal search query terms for unbiased article crawling
"""

#################### Economic Indicator Data API ####################

import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
REQUEST_TIMEOUT = 20

# Get API keys
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

########################### FRED ###########################

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


############################# webcrawler #############################

from scrapy.crawler import CrawlerProcess
from scrapy.settings import SETTINGS_PRIORITIES
from scrapy.utils.project import get_project_settings
from webcrawlerlib.spiders.gdelt_spider import GdeltSpider


# Main gdelt webcrawler API endpoint
def run_gdelt_spider(
        query_terms: str | List[str], 
        timespan: str, 
        maxrecords: int,
        output: Optional[bool] = False,
        language: Optional[str] = "english",
) -> None:
    """
    Run the GDELT spider to crawl and scrape news articles.

    Args:
        query_terms: List of query terms to search articles.
        timespan: Example formats = 1day, 7days, 24h, 1week, 3months
        maxrecords: The maximum number of articles to scrape.
        output: Output scraped data to gdelt_spider_output.json in current directory.
        language: Source language filter for GDELT (default: "english").
    """
    if isinstance(query_terms, List):
        quoted = []
        for term in query_terms:
            if " " in term:
                quoted.append(f'"{term}"')
            else:
                quoted.append(term)
        query = f"({' OR '.join(quoted)})"
    else:
        query = query_terms

    query = f"{query} sourcelang:{language}"

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "webcrawlerlib.settings")
    settings = get_project_settings()
    settings.set("LOG_LEVEL", "WARNING", priority=SETTINGS_PRIORITIES["cmdline"])
    settings.set("LOGSTATS_INTERVAL", 0, priority=SETTINGS_PRIORITIES["cmdline"])
    settings.set("GDELT_QUERY", query)
    settings.set("GDELT_TIMESPAN", timespan)
    settings.set("GDELT_MAXRECORDS", maxrecords)

    # debug
    if output:
        pipelines = dict(settings.getdict("ITEM_PIPELINES"))
        pipelines.pop("webcrawlerlib.pipelines.RawPayloadStoragePipeline", None)
        settings.set("ITEM_PIPELINES", pipelines) # disable pipeline
        settings.set(
            "FEEDS",
            {
                "gdelt_spider_output.json": {
                    "format": "json",
                    "encoding": "utf-8",
                    "indent": 2,
                    "overwrite": True,
                }
            },
        )

    process = CrawlerProcess(settings)
    process.crawl(GdeltSpider)
    process.start()


if __name__ == "__main__":
    print("Hello World!")
