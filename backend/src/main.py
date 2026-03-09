import os
import re
from typing import Any, Dict

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv
from databaselib.db import get_active_themes


from datalib.datalib import (
    get_alpha_vantage_symbol_search,
    get_alpha_vantage_time_series_daily,
    get_alpha_vantage_time_series_daily_adjusted,
    get_alpha_vantage_time_series_intraday,
    get_alpha_vantage_time_series_monthly,
    get_alpha_vantage_time_series_monthly_adjusted,
    get_alpha_vantage_time_series_weekly,
    get_alpha_vantage_time_series_weekly_adjusted,
    get_fred_indicator_data,
    list_fred_categories,
    list_fred_indicators,
)

load_dotenv()
FRONT_END_SERVER = os.getenv("FRONT_END_SERVER")
# fallback to default
if FRONT_END_SERVER is None:
    FRONT_END_SERVER = "http://localhost:3000"

app = Flask(__name__)
CORS(app, origins=FRONT_END_SERVER)


########################## Helper functions ##########################

LABEL_TOKEN_MAP = {
    "fx": "FX",
    "usd": "USD",
    "eur": "EUR",
    "jpy": "JPY",
    "gdp": "GDP",
    "cpi": "CPI",
    "pce": "PCE",
    "ppi": "PPI",
    "pmi": "PMI",
    "fed": "Fed",
    "sofr": "SOFR",
    "ust": "UST",
    "ig": "IG",
    "hy": "HY",
    "oas": "OAS",
    "ted": "TED",
    "nfci": "NFCI",
    "stlfsi": "STLFSI",
    "m2": "M2",
    "u6": "U6",
    "wti": "WTI",
    "yoy": "YoY",
    "mom": "MoM",
}

# Placeholder news scroller articles
EXAMPLE_NEWS_ARTICLES = [
    {
        "id": "us-cpi-cools",
        "title": "US Core CPI Cools for a Second Month",
        "description": "Core inflation eased slightly, reinforcing expectations for a gradual policy pivot.",
    },
    {
        "id": "fed-minutes",
        "title": "Fed Minutes Signal Data-Dependent Approach",
        "description": "Officials flagged resilient services inflation and reiterated a cautious easing path.",
    },
    {
        "id": "oil-supply",
        "title": "Oil Gains on Fresh Supply Concerns",
        "description": "Crude prices moved higher after renewed disruptions increased near-term supply risk.",
    },
    {
        "id": "tech-guidance",
        "title": "Mega-Cap Tech Guidance Mixed into Q2",
        "description": "Cloud and AI capex remained strong, while margin outlooks diverged by company.",
    },
    {
        "id": "jobs-surprise",
        "title": "Payrolls Beat Forecasts, Wage Growth Stable",
        "description": "Labor data stayed firm, supporting a soft-landing narrative despite rate uncertainty.",
    },
]


def _format_label_token(token: str) -> str:
    lowered = token.lower()
    mapped = LABEL_TOKEN_MAP.get(lowered)
    if mapped:
        return mapped

    if re.fullmatch(r"\d+[a-z]+", token):
        prefix = "".join(ch for ch in token if ch.isdigit())
        suffix = "".join(ch for ch in token if ch.isalpha()).upper()
        return f"{prefix}{suffix}"

    return lowered.capitalize()


def _to_label(value: str) -> str:
    return " ".join(_format_label_token(token) for token in value.split("_"))


def _normalize_observations(raw: Dict[str, Any]) -> list[Dict[str, Any]]:
    observations = raw.get("observations", [])
    normalized: list[Dict[str, Any]] = []

    for row in observations:
        raw_value = row.get("value")
        if raw_value in (None, "."):
            continue
        normalized.append({"date": row.get("date"), "value": float(raw_value)})

    return normalized


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y"}:
        return True
    if lowered in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _json_error(message: str, status_code: int = 400) -> Response:
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


############################# Endpoints #############################

@app.get("/api/market/symbol-search")
def get_symbol_search() -> Response:
    """
    Search ticker symbols and return autocomplete-friendly results.
    """
    keywords = request.args.get("keywords", "").strip()
    if not keywords:
        return _json_error("Missing required query parameter: keywords")

    limit_raw = request.args.get("limit")
    try:
        limit = int(limit_raw) if limit_raw else 8
    except ValueError:
        limit = 8

    limit = max(1, min(limit, 20))

    try:
        payload = get_alpha_vantage_symbol_search(
            keywords=keywords,
            datatype=request.args.get("datatype"),
        )
        best_matches = payload.get("bestMatches", [])
        matches: list[Dict[str, Any]] = []
        for row in best_matches:
            if not isinstance(row, dict):
                continue
            symbol = row.get("1. symbol")
            name = row.get("2. name")
            if not symbol or not name:
                continue

            matches.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "type": row.get("3. type"),
                    "region": row.get("4. region"),
                    "market_open": row.get("5. marketOpen"),
                    "market_close": row.get("6. marketClose"),
                    "timezone": row.get("7. timezone"),
                    "currency": row.get("8. currency"),
                }
            )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(
        {
            "keywords": keywords,
            "matches": matches[:limit],
            "count": len(matches),
        }
    )


@app.get("/api/market/time-series/intraday")
def get_time_series_intraday() -> Response:
    """
    Return intraday stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_intraday(
            symbol=symbol,
            interval=request.args.get("interval", "5min"),
            adjusted=_parse_bool(request.args.get("adjusted")),
            extended_hours=_parse_bool(request.args.get("extended_hours")),
            month=request.args.get("month"),
            outputsize=request.args.get("outputsize"),
            datatype=request.args.get("datatype"),
            entitlement=request.args.get("entitlement"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/market/time-series/daily")
def get_time_series_daily() -> Response:
    """
    Return daily stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_daily(
            symbol=symbol,
            outputsize=request.args.get("outputsize"),
            datatype=request.args.get("datatype"),
            entitlement=request.args.get("entitlement"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/market/time-series/daily-adjusted")
def get_time_series_daily_adjusted() -> Response:
    """
    Return adjusted daily stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_daily_adjusted(
            symbol=symbol,
            outputsize=request.args.get("outputsize"),
            datatype=request.args.get("datatype"),
            entitlement=request.args.get("entitlement"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/market/time-series/weekly")
def get_time_series_weekly() -> Response:
    """
    Return weekly stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_weekly(
            symbol=symbol,
            datatype=request.args.get("datatype"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/market/time-series/weekly-adjusted")
def get_time_series_weekly_adjusted() -> Response:
    """
    Return adjusted weekly stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_weekly_adjusted(
            symbol=symbol,
            datatype=request.args.get("datatype"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/market/time-series/monthly")
def get_time_series_monthly() -> Response:
    """
    Return monthly stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_monthly(
            symbol=symbol,
            datatype=request.args.get("datatype"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/market/time-series/monthly-adjusted")
def get_time_series_monthly_adjusted() -> Response:
    """
    Return adjusted monthly stock time series from Alpha Vantage.
    """
    symbol = request.args.get("symbol")
    if not symbol:
        return _json_error("Missing required query parameter: symbol")

    try:
        payload = get_alpha_vantage_time_series_monthly_adjusted(
            symbol=symbol,
            datatype=request.args.get("datatype"),
        )
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/macroeconomic/categories")
def get_fred_categories() -> Response:
    """
    Return all categories available for the country chosen.
    TODO: Add more APIs to support more countries
    """
    country = request.args.get("country", "usa")
    categories = list_fred_categories()
    return jsonify(
        {
            "country": country.upper(),
            "categories": [
                {"key": category, "label": _to_label(category)} for category in categories
            ],
        }
    )


@app.get("/api/macroeconomic/indicators")
def get_fred_indicators() -> Response:
    """
    Return all indicators that fall under the category requested.
    """
    category = request.args["category"]
    indicators = list_fred_indicators(category)
    return jsonify(
        {
            "category": category,
            "indicators": [
                {"key": name, "label": _to_label(name), "series_id": series_id}
                for name, series_id in indicators.items()
            ],
        }
    )


@app.get("/api/macroeconomic/series")
def get_fred_series() -> Response:
    """
    Return series data for indicator requested.
    """
    indicator_name = request.args["indicator"]
    category = request.args.get("category")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_order = request.args.get("sort_order", "asc")
    limit_raw = request.args.get("limit")
    limit = int(limit_raw) if limit_raw else 60

    raw = get_fred_indicator_data(
        indicator_name=indicator_name,
        category=category,
        start_date=start_date,
        end_date=end_date,
        sort_order=sort_order,
        limit=limit,
    )
    observations = _normalize_observations(raw)
    latest = observations[-1] if observations else None
    previous = observations[-2] if len(observations) > 1 else None
    points = [row["value"] for row in observations]

    absolute_change = (
        latest["value"] - previous["value"] if latest is not None and previous is not None else 0.0
    )
    percent_change = (
        (absolute_change / previous["value"]) * 100
        if previous is not None and previous["value"] != 0
        else 0.0
    )

    return jsonify(
        {
            "category": category,
            "indicator": indicator_name,
            "indicator_label": _to_label(indicator_name),
            "series_id": raw.get("observations", [{}])[0].get("series_id"),
            "observations": observations,
            "points": points,
            "latest": latest,
            "previous": previous,
            "change": {
                "absolute": absolute_change,
                "percent": percent_change,
            },
        }
    )

@app.get("/api/themes/hottest")
def get_hottest_themes() -> Response:
    """
    Return top N active themes ordered by heat score descending.
    Default limit is 9 for frontend heat grid.
    """
    limit_raw = request.args.get("limit", "9")
    try:
        limit = max(1, min(int(limit_raw), 50))
    except ValueError:
        limit = 9

    themes = get_active_themes()
    top_themes = themes[:limit]

    return jsonify(
        [
            {
                "topic": theme.get("title", "Unknown"),
                "score": float(theme.get("heat_score") or 0.0),
                "region": theme.get("region"),
                "asset_classes": theme.get("asset_classes") or [],
                "status": theme.get("status"),
            }
            for theme in top_themes
        ]
    )

@app.get("/api/news")
def get_news() -> Response:
    """
    Return news articles.
    TODO: Get news articles from database (raw)
    """
    limit_raw = request.args.get("limit")
    try:
        limit = int(limit_raw) if limit_raw else len(EXAMPLE_NEWS_ARTICLES)
    except ValueError:
        limit = len(EXAMPLE_NEWS_ARTICLES)

    limit = max(1, min(limit, len(EXAMPLE_NEWS_ARTICLES)))
    return jsonify({"articles": EXAMPLE_NEWS_ARTICLES[:limit]})


if __name__ == "__main__":
    app.run(port=8000, debug=True)
