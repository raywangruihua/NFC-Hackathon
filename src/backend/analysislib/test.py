# backend/analysislib/test_analysis.py
from macro_themes import group_events_into_themes
from heat_score import calculate_theme_heat
from market_impact import generate_market_impact

# Example events JSON (simulate what comes from your previous layer)
example_events = [
    {
        "topic": "inflation",
        "asset_classes": ["bonds", "equities"],
        "importance_score": 0.59,
        "sentiment": "risk-off",
        "published_at": "2026-03-04T10:00:00Z"
    },
    {
        "topic": "interest rate",
        "asset_classes": ["bonds"],
        "importance_score": 0.8,
        "sentiment": "risk-off",
        "published_at": "2026-03-04T11:00:00Z"
    },
    {
        "topic": "interest rate",
        "asset_classes": ["equities"],
        "importance_score": 1.2,
        "sentiment": "risk-on",
        "published_at": "2026-03-05T09:00:00Z"
    }
]

# 1. Group into themes
themes = group_events_into_themes(example_events)
print("Grouped themes:")
for t in themes:
    print(t["title"], "Events:", len(t["events"]))

# 2. Calculate heat
themes_with_heat = calculate_theme_heat(themes)
print("\nThemes with heat scores:")
for t in themes_with_heat:
    print(t["title"], "Heat:", t["heat_score"])

# 3. Generate market impact
market_summary = generate_market_impact(themes_with_heat)
print("\nMarket impact summary:")
for m in market_summary:
    print(m)
