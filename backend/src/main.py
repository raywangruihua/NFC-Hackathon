import os
import re
from typing import Any, Dict

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv

from datalib.datalib import (
    get_fred_indicator_data,
    list_fred_categories,
    list_fred_indicators,
)

load_dotenv()
FRONT_END_SERVER = os.getenv("FRONT_END_SERVER")
DEFAULT_FRONTEND_ORIGINS = {"http://localhost:3000", "https://localhost:3000"}
ALLOWED_ORIGINS = sorted(origin for origin in {FRONT_END_SERVER, *DEFAULT_FRONTEND_ORIGINS} if origin)

app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)


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


@app.get("/api/fred/categories")
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


@app.get("/api/fred/indicators")
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


@app.get("/api/fred/series")
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


if __name__ == "__main__":
    app.run(port=8000, debug=True)
