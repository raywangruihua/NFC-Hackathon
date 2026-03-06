# src/backend/analysislib/test_analysis.py
from macro_themes import group_events_into_themes
from heat_score import calculate_theme_heat
import datetime
import uuid

# Mock processed events (like what your pipeline would output)
processed_events = [
    {
        "event_id": str(uuid.uuid4()),
        "event_type": "news",
        "source": "finance.yahoo.com",
        "published_at": "2026-03-04T15:55:12.000Z",
        "region": "US",
        "asset_classes": ["equities", "commodities"],
        "content": "US inflation rose to 4.2% in March...",
        "importance_score": 0.61,
        "entities": {"tickers": ["USB", "SPY"], "countries": ["United States"]},
        "topic": "inflation",
        "sentiment": "risk-off",
        "raw_payload_ref": "raw/https://...",
        "created_at": datetime.datetime.now().isoformat(),
    },
    {
        "event_id": str(uuid.uuid4()),
        "event_type": "news",
        "source": "bloomberg.com",
        "published_at": "2026-03-05T10:00:00.000Z",
        "region": "US",
        "asset_classes": ["bonds"],
        "content": "Fed hints at interest rate hike...",
        "importance_score": 0.9,
        "entities": {"tickers": ["TLT"], "countries": ["US"]},
        "topic": "interest rate",
        "sentiment": "risk-off",
        "raw_payload_ref": "raw/https://...",
        "created_at": datetime.datetime.now().isoformat(),
    },
    {
        "event_id": str(uuid.uuid4()),
        "event_type": "news",
        "source": "bloomberg.com",
        "published_at": "2026-03-05T10:00:00.000Z",
        "region": "US",
        "asset_classes": ["bonds"],
        "content": "Fed hints at interest rate hike...",
        "importance_score": 0.9,
        "entities": {"tickers": ["TLT"], "countries": ["US"]},
        "topic": "interest rate",
        "sentiment": "risk-off",
        "raw_payload_ref": "raw/https://...",
        "created_at": datetime.datetime.now().isoformat(),
    }
]

# Example usage (Add to README):
# with open("processed_articles.json") as f:
#    processed_events = json.load(f)


# Run analysis layer
themes = group_events_into_themes(processed_events)
themes_with_heat = calculate_theme_heat(themes)

for t in themes_with_heat:
    print(f"Theme: {t['title']}, Heat: {t['heat_score']}, Events: {len(t['events'])}")