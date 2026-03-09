from typing import Any

from .logic.heat_score import calculate_theme_heat
from .logic.macro_themes import group_events_into_themes
from .logic.market_impact import generate_market_impact
from .logic.portfolio_analysis import analyze_portfolio_risk


JsonDict = dict[str, Any]


def run_analysis(
    events: list[JsonDict],
    user_id: str | None = None,
    portfolio: list[JsonDict] | None = None,
) -> JsonDict:
    """
    Single analysislib entrypoint.

    Flow:
    1) Group events into themes
    2) Score theme heat (0-100)
    3) Derive market impact summary
    4) Optionally derive portfolio risk if user_id + portfolio are provided

    Returns:
        {
            "themes": [...],
            "market_impacts": [...],
            "portfolio_risk": { ... } | None,
            "summary": {
                "events_input": int,
                "themes_count": int,
                "impacts_count": int,
                "alerts_count": int,
            }
        }
    """
    safe_events = events if isinstance(events, list) else []

    themes = group_events_into_themes(safe_events)
    themes = calculate_theme_heat(themes)
    market_impacts = generate_market_impact(themes)

    portfolio_risk = None
    alerts_count = 0
    if user_id and isinstance(portfolio, list):
        portfolio_risk = analyze_portfolio_risk(user_id, market_impacts, portfolio)
        alerts_count = len(portfolio_risk.get("risk_alerts", []))

    return {
        "themes": themes,
        "market_impacts": market_impacts,
        "portfolio_risk": portfolio_risk,
        "summary": {
            "events_input": len(safe_events),
            "themes_count": len(themes),
            "impacts_count": len(market_impacts),
            "alerts_count": alerts_count,
        },
    }

