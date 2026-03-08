# backend/analysislib/portfolio_analysis.py
from typing import List, Dict
from datetime import datetime
import uuid

def map_risk_level(exposure: float) -> str:
    if exposure <= 0.3:
        return "Low"
    elif exposure <= 0.6:
        return "Medium"
    else:
        return "High"

def analyze_portfolio_risk(user_id: str, market_impacts: List[Dict], portfolio: List[Dict]) -> Dict:
    """
    Returns structured data ready for DB insertion:
    - portfolio_exposure: list of dicts per asset
    - risk_alerts: list of dicts per theme
    """
    # ---- portfolio_exposure ----
    now = datetime.utcnow()
    portfolio_exposure = []
    for asset in portfolio:
        portfolio_exposure.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "asset_class": asset["asset_class"],
            "region": asset.get("region", ""),
            "sector": asset.get("sector", ""),
            "ticker": asset.get("ticker", ""),
            "exposure_pct": asset["weight"] * 100,
            "created_at": now,
            "updated_at": now
        })

    # ---- risk_alerts ----
    risk_alerts = []
    for impact in market_impacts:
        exposure = sum(
            asset["weight"] for asset in portfolio if asset["asset_class"] in impact["affected_assets"]
        )
        severity = map_risk_level(exposure)
        message = f"{round(exposure*100,1)}% of your portfolio is exposed to {impact['direction']} assets affected by {impact['theme_name']}."

        risk_alerts.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "theme_id": impact["theme_id"],
            "severity": severity,
            "trigger_reason": message,
            "acknowledged": False,
            "acknowledged_at": None,
            "created_at": now
        })

    return {
        "portfolio_exposure": portfolio_exposure,
        "risk_alerts": risk_alerts
    }