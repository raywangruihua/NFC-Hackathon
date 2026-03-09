# backend/analysislib/portfolio_analysis.py
from typing import List, Dict
from datetime import datetime, timezone
import uuid


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


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
        if not isinstance(asset, dict):
            continue

        asset_class = asset.get("asset_class")
        if not isinstance(asset_class, str) or not asset_class:
            continue

        weight = max(0.0, min(1.0, _safe_float(asset.get("weight"), 0.0)))

        portfolio_exposure.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "asset_class": asset_class,
            "region": asset.get("region", ""),
            "sector": asset.get("sector", ""),
            "ticker": asset.get("ticker", ""),
            "exposure_pct": weight * 100,
            "created_at": now,
            "updated_at": now,
        })

    risk_alerts = []
    for impact in market_impacts:
        if not isinstance(impact, dict):
            continue

        affected_assets = impact.get("affected_assets")
        if not isinstance(affected_assets, list):
            affected_assets = []

        exposure = 0.0
        for asset in portfolio:
            if not isinstance(asset, dict):
                continue
            asset_class = asset.get("asset_class")
            if asset_class in affected_assets:
                exposure += max(0.0, min(1.0, _safe_float(asset.get("weight"), 0.0)))

        exposure = max(0.0, min(1.0, exposure))

        direction = impact.get("direction") if isinstance(impact.get("direction"), str) else "neutral"
        theme_name = impact.get("theme_name") if isinstance(impact.get("theme_name"), str) else "Unknown"

        risk_alerts.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "theme_id": impact.get("theme_id"),
            "severity": map_risk_level(exposure),
            "trigger_reason": (
                f"{round(exposure * 100, 1)}% of your portfolio is exposed to "
                f"{direction} assets affected by {theme_name}."
            ),
            "acknowledged": False,
            "acknowledged_at": None,
            "created_at": now,
        })

    return {"portfolio_exposure": portfolio_exposure, "risk_alerts": risk_alerts}
