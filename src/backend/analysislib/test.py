# backend/analysislib/test_analysis.py

from macro_themes import group_events_into_themes
from heat_score import calculate_theme_heat
from market_impact import generate_market_impact
from portfolio_analysis import analyze_portfolio_risk

# --------------------------
# Example events
# --------------------------
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

# --------------------------
# Run pipeline
# --------------------------
themes = group_events_into_themes(example_events)
themes_with_heat = calculate_theme_heat(themes)
market_summary = generate_market_impact(themes_with_heat)

portfolio = [
    {"ticker": "AAPL", "asset_class": "equities", "sector": "technology", "weight": 0.35},
    {"ticker": "JPM", "asset_class": "equities", "sector": "financials", "weight": 0.25},
    {"ticker": "TLT", "asset_class": "bonds", "sector": "treasury", "weight": 0.25},
    {"ticker": "GLD", "asset_class": "commodities", "sector": "gold", "weight": 0.15}
]

portfolio_risk = analyze_portfolio_risk(market_summary, portfolio)

# --------------------------
# Dashboard-style output
# --------------------------
print(f"\nOverall Portfolio Risk: {portfolio_risk['overall_risk']}% ({portfolio_risk['overall_risk_level']})")

print("\nDetailed Portfolio Risk Alerts:")
for alert in portfolio_risk['alerts']:
    print(f"- Theme: {alert['theme']}, Direction: {alert['direction']}, "
          f"Heat: {alert['heat_score']}, Exposure: {alert['portfolio_exposure']}, "
          f"Risk Level: {alert['risk_level']}")
    print(f"  Message: {alert['message']}")