import os
import re
import math
from datetime import datetime, timezone, date
from typing import Any, Dict

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv
from databaselib.db import get_active_themes, get_events, get_events_for_theme, get_theme_by_id


from datalib.datalib import (
    get_alpha_vantage_symbol_search,
    get_alpha_vantage_time_series_daily,
    get_alpha_vantage_time_series_daily_adjusted,
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


def _json_error(message: str, status_code: int = 400) -> Response:
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


def _parse_iso_date(value: str | None, field_name: str) -> date | None:
    if value is None or value.strip() == "":
        return None
    try:
        return datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}. Use YYYY-MM-DD.") from exc


def _filter_alpha_vantage_time_series(
    payload: Dict[str, Any],
    start_date: date | None,
    end_date: date | None,
) -> Dict[str, Any]:
    """
    Filter Alpha Vantage time-series payload rows by inclusive date range.
    """
    if start_date is None and end_date is None:
        return payload

    series_key = next(
        (
            key
            for key, value in payload.items()
            if "time series" in key.lower() and isinstance(value, dict)
        ),
        None,
    )
    if series_key is None:
        return payload

    series_rows = payload.get(series_key)
    if not isinstance(series_rows, dict):
        return payload

    filtered_rows: Dict[str, Any] = {}
    for raw_date, row in series_rows.items():
        try:
            row_date = date.fromisoformat(raw_date)
        except ValueError:
            continue

        if start_date is not None and row_date < start_date:
            continue
        if end_date is not None and row_date > end_date:
            continue
        filtered_rows[raw_date] = row

    return {
        **payload,
        series_key: filtered_rows,
    }


def _apply_market_date_filter(payload: Dict[str, Any]) -> Dict[str, Any]:
    start_date = _parse_iso_date(request.args.get("start_date"), "start_date")
    end_date = _parse_iso_date(request.args.get("end_date"), "end_date")
    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date cannot be after end_date.")
    return _filter_alpha_vantage_time_series(payload, start_date, end_date)


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
        payload = _apply_market_date_filter(payload)
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
        payload = _apply_market_date_filter(payload)
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
        payload = _apply_market_date_filter(payload)
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
        payload = _apply_market_date_filter(payload)
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
        payload = _apply_market_date_filter(payload)
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
        payload = _apply_market_date_filter(payload)
    except ValueError as exc:
        return _json_error(str(exc))
    except RuntimeError as exc:
        return _json_error(str(exc), status_code=500)

    return jsonify(payload)


@app.get("/api/macroeconomic/categories")
def get_macro_categories() -> Response:
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
def get_macro_indicators() -> Response:
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
def get_macro_series() -> Response:
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
                "theme_id": theme.get("theme_id"),
                "topic": theme.get("title", "Unknown"),
                "score": float(theme.get("heat_score") or 0.0),
                "region": theme.get("region"),
                "asset_classes": theme.get("asset_classes") or [],
                "status": theme.get("status"),
            }
            for theme in top_themes
        ]
    )


@app.get("/api/themes")
def get_themes_list() -> Response:
    """
    Return all active themes for the theme selector dropdown.
    """
    themes = get_active_themes()
    return jsonify(
        [
            {
                "theme_id": theme.get("theme_id"),
                "title": theme.get("title", "Unknown"),
                "heat_score": float(theme.get("heat_score") or 0.0),
            }
            for theme in themes
        ]
    )


def _importance_to_impact(score: float) -> str:
    if score >= 0.7:
        return "High"
    if score >= 0.4:
        return "Medium"
    return "Low"


@app.get("/api/themes/<theme_id>/timeline")
def get_theme_timeline(theme_id: str) -> Response:
    """
    Return a theme's metadata together with all its linked events,
    sorted by published_at descending.
    """
    theme = get_theme_by_id(theme_id)
    if theme is None:
        return _json_error("Theme not found.", status_code=404)

    raw_rows = get_events_for_theme(theme_id)
    events = []
    for row in raw_rows:
        ev = row.get("events")
        if not ev:
            continue
        events.append(ev)

    events.sort(key=lambda e: e.get("published_at", ""), reverse=True)

    return jsonify(
        {
            "theme": {
                "theme_id": theme.get("theme_id"),
                "title": theme.get("title"),
                "description": theme.get("description"),
                "heat_score": float(theme.get("heat_score") or 0.0),
                "status": theme.get("status"),
                "region": theme.get("region"),
                "asset_classes": theme.get("asset_classes") or [],
                "first_seen_at": theme.get("first_seen_at"),
                "last_seen_at": theme.get("last_seen_at"),
            },
            "events": [
                {
                    "event_id": ev.get("event_id"),
                    "date": ev.get("published_at"),
                    "title": (ev.get("content") or "")[:120],
                    "text": ev.get("content") or "",
                    "source": ev.get("source") or "Unknown",
                    "impact": _importance_to_impact(
                        float(ev.get("importance_score") or 0)
                    ),
                    "sentiment": ev.get("sentiment"),
                    "region": ev.get("region"),
                    "asset_classes": ev.get("asset_classes") or [],
                }
                for ev in events
            ],
        }
    )

@app.get("/api/news")
def get_news() -> Response:
    """
    Return recent news articles ranked by recency-weighted importance.
    Falls back to placeholders if DB events are unavailable.
    """
    limit_raw = request.args.get("limit")
    try:
        limit = int(limit_raw) if limit_raw else 8
    except ValueError:
        limit = 8

    limit = max(1, min(limit, 20))

    try:
        events = get_events(days=7)
    except Exception:
        events = []

    now = datetime.now(timezone.utc)
    ranked: list[Dict[str, Any]] = []

    for event in events:
        published_at = event.get("published_at")
        if not published_at:
            continue

        try:
            published_dt = datetime.fromisoformat(str(published_at).replace("Z", "+00:00"))
            age_hours = max((now - published_dt).total_seconds() / 3600, 0.0)
            recency_score = math.exp(-age_hours / 24.0)
        except Exception:
            recency_score = 0.0

        try:
            importance_score = float(event.get("importance_score") or 0.0)
        except Exception:
            importance_score = 0.0
        importance_score = max(0.0, min(1.0, importance_score))

        weighted_score = 0.7 * recency_score + 0.3 * importance_score

        title = event.get("title") or event.get("topic") or "Market Update"
        content = str(event.get("content") or "").strip()
        description = content[:220] if content else "No summary available."

        ranked.append(
            {
                "id": str(event.get("event_id") or f"{title}-{published_at}"),
                "title": str(title),
                "description": description,
                "score": round(weighted_score, 4),
            }
        )

    if not ranked:
        return jsonify({"articles": EXAMPLE_NEWS_ARTICLES[: min(limit, len(EXAMPLE_NEWS_ARTICLES))]})

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return jsonify({"articles": ranked[:limit]})


@app.route("/api/classify-events", methods=["POST"])
def classify_events():
    """
    Trigger Gemini classification for unlinked events.
    Query params:
        days – look-back window (default 30)
    """
    try:
        days = int(request.args.get("days", "30"))
    except (ValueError, TypeError):
        days = 30

    try:
        from analysislib.classify_events import backfill_events
        stats = backfill_events(days=days)
        return jsonify(stats)
    except Exception as exc:
        return _json_error(f"Classification error: {exc}", 500)


if __name__ == "__main__":
    app.run(port=8000, debug=True)


