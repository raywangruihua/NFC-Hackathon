# backend/analysislib/portfolio_analysis.py
from typing import List, Dict
from datetime import datetime, timezone
import uuid


def map_risk_level(exposure: float) -> str:
    if exposure <= 0.3:
        return "low"
    if exposure <= 0.6:
        return "medium"
    if exposure <= 0.85:
        return "high"
    return "critical"


def analyze_portfolio_risk(user_id: str, market_impacts: List[Dict], portfolio: List[Dict]) -> Dict:
    now = datetime.now(timezone.utc).isoformat()

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
            "updated_at": now,
        })

    risk_alerts = []
    for impact in market_impacts:
        exposure = sum(
            asset["weight"] for asset in portfolio
            if asset["asset_class"] in impact.get("affected_assets", [])
        )
        risk_alerts.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "theme_id": impact["theme_id"],
            "severity": map_risk_level(exposure),
            "trigger_reason": (
                f"{round(exposure * 100, 1)}% of your portfolio is exposed to "
                f"{impact['direction']} assets affected by {impact['theme_name']}."
            ),
            "acknowledged": False,
            "acknowledged_at": None,
            "created_at": now,
        })

    return {"portfolio_exposure": portfolio_exposure, "risk_alerts": risk_alerts}
