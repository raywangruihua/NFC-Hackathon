from datetime import datetime
from macro_themes import group_events_into_themes
from heat_score import calculate_theme_heat
from market_impact import generate_market_impact
from portfolio_analysis import analyze_portfolio_risk
import uuid

# -------------------------
# Placeholder user portfolio
# -------------------------
user_id = str(uuid.uuid4())
portfolio = [
    {"ticker": "AAPL", "asset_class": "equities", "region": "US", "sector": "tech", "weight": 0.4},
    {"ticker": "GOOGL", "asset_class": "equities", "region": "US", "sector": "tech", "weight": 0.2},
    {"ticker": "US10Y", "asset_class": "bonds", "region": "US", "sector": "government", "weight": 0.25},
    {"ticker": "SP500", "asset_class": "equities", "region": "US", "sector": "index", "weight": 0.15}
]

# -------------------------
# Example incoming events
# -------------------------
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

# -------------------------
# 1. Group events into themes
# -------------------------
themes = group_events_into_themes(example_events)
print("=== Grouped Themes ===")
for t in themes:
    print(f"- Theme: {t['title']}, Events: {len(t['events'])}, First Seen: {t['first_seen_at']}, Last Seen: {t['last_seen_at']}")
print("\n")

# -------------------------
# 2. Calculate heat scores
# -------------------------
themes_with_heat = calculate_theme_heat(themes)
print("=== Themes with Heat Scores ===")
for t in themes_with_heat:
    print(f"- Theme: {t['title']}, Heat Score: {t['heat_score']}, Asset Classes: {t['asset_classes']}")
print("\n")

# -------------------------
# 3. Generate market impact
# -------------------------
market_summary = generate_market_impact(themes_with_heat)
print("=== Market Impact Summary ===")
for m in market_summary:
    print(f"- Theme: {m['theme_name']}, Heat: {m['heat_score']}, Direction: {m['direction']}, Affected Assets: {m['affected_assets']}")
print("\n")

# -------------------------
# 4. Analyze portfolio risk
# -------------------------
portfolio_risk = analyze_portfolio_risk(user_id, market_summary, portfolio)
print("=== Portfolio Exposure ===")
for p in portfolio_risk['portfolio_exposure']:
    print(f"- Ticker: {p['ticker']}, Asset Class: {p['asset_class']}, Exposure: {p['exposure_pct']}%")

print("\n=== Portfolio Risk Alerts ===")
for alert in portfolio_risk['risk_alerts']:
    print(f"- Theme: {alert['theme_id']}, Severity: {alert['severity']}, Trigger: {alert['trigger_reason']}")
print("\n")

# -------------------------
# 5. Compute Overall Portfolio Risk (dynamic)
# -------------------------
overall_risk = 0.0
for alert in portfolio_risk['risk_alerts']:
    # Find corresponding theme
    theme = next(t for t in themes_with_heat if t['theme_id'] == alert['theme_id'])
    # Compute exposure to affected assets
    exposure = sum(
        asset["weight"] for asset in portfolio 
        if asset["asset_class"] in theme['asset_classes']
    )
    overall_risk += exposure * theme['heat_score']

# Scale to percentage for display (max heat ~2, max exposure ~1)
max_possible_risk = len(portfolio_risk['risk_alerts']) * 2 * 1  # max heat * max exposure
overall_risk_pct = round((overall_risk / max_possible_risk) * 100, 1)

print(f"=== Overall Portfolio Risk (weighted placeholder) === {overall_risk_pct}%")