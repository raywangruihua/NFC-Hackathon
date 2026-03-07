# backend/analysislib/portfolio_analysis.py

from typing import List, Dict


def risk_level_from_percentage(overall_risk: float) -> str:
    """
    Map overall portfolio risk (%) to realistic investment risk levels.
    """
    if overall_risk <= 30:
        return "Low Risk"
    elif overall_risk <= 60:
        return "Moderate Risk"
    elif overall_risk <= 80:
        return "High Risk"
    else:
        return "Very High Risk"


def analyze_portfolio_risk(market_impacts: List[Dict], portfolio: List[Dict]) -> Dict:
    """
    Compare portfolio assets against market impacts
    and generate risk alerts with human-readable messages.

    Returns a dictionary with:
    - 'overall_risk': overall weighted portfolio risk (%)
    - 'overall_risk_level': realistic risk-level label
    - 'alerts': detailed per-theme risk alerts
    """
    alerts = []

    for impact in market_impacts:
        affected_assets = impact.get("affected_assets", [])
        theme = impact.get("theme_name")
        direction = impact.get("direction")
        heat = impact.get("heat_score", 0)

        exposure = 0.0

        for asset in portfolio:
            if asset["asset_class"] in affected_assets:
                exposure += asset.get("weight", 0)

        # determine per-theme risk level
        if exposure > 0.6:
            risk_level = "High"
        elif exposure > 0.3:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # human-readable message
        exposure_pct = round(exposure * 100, 1)
        message = (
            f"{exposure_pct}% of your portfolio is exposed to {direction} assets "
            f"affected by {theme}."
        )

        alerts.append({
            "theme": theme,
            "direction": direction,
            "heat_score": heat,
            "portfolio_exposure": round(exposure, 3),
            "risk_level": risk_level,
            "message": message
        })

    # -------------------------------
    # Compute overall weighted risk
    # -------------------------------
    if alerts:
        total_risk = sum(a["heat_score"] * a["portfolio_exposure"] for a in alerts)
        max_possible_risk = 2 * 1 * len(alerts)  # assuming max_heat=2, max_exposure=1 per theme
        overall_risk = round((total_risk / max_possible_risk) * 100, 1)
    else:
        overall_risk = 0.0

    overall_risk_level = risk_level_from_percentage(overall_risk)

    return {
        "overall_risk": overall_risk,
        "overall_risk_level": overall_risk_level,
        "alerts": alerts
    }