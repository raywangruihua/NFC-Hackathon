# backend/analysislib/test.py
# This script seeds fake themes into database for frontend testing and verifies database connection.
import sys
from datetime import datetime, timezone

from backend.src.databaselib.db import supabase


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_theme(payload: dict) -> str:
    title = payload["title"]
    region = payload.get("region") or ""

    existing = (
        supabase.table("themes")
        .select("theme_id")
        .eq("title", title)
        .eq("region", region)
        .limit(1)
        .execute()
        .data
    )

    if existing:
        theme_id = existing[0]["theme_id"]
        supabase.table("themes").update(payload).eq("theme_id", theme_id).execute()
        return theme_id

    inserted = supabase.table("themes").insert(payload).execute().data
    return inserted[0]["theme_id"]


def seed_fake_themes() -> list[str]:
    now = _iso_now()
    fake_themes = [
        {"title": "Rate Cuts", "heat_score": 88.0, "region": "US", "asset_classes": ["bonds", "equities"]},
        {"title": "AI Capex", "heat_score": 73.0, "region": "US", "asset_classes": ["equities"]},
        {"title": "Energy Shock", "heat_score": 66.0, "region": "GLOBAL", "asset_classes": ["commodities"]},
        {"title": "Fiscal Risk", "heat_score": 54.0, "region": "US", "asset_classes": ["bonds"]},
        {"title": "China Demand", "heat_score": 49.0, "region": "APAC", "asset_classes": ["equities", "commodities"]},
        {"title": "Supply Chain", "heat_score": 44.0, "region": "GLOBAL", "asset_classes": ["equities"]},
        {"title": "Bank Stress", "heat_score": 61.0, "region": "US", "asset_classes": ["bonds", "equities"]},
        {"title": "Housing", "heat_score": 47.0, "region": "US", "asset_classes": ["real_estate"]},
        {"title": "USD Strength", "heat_score": 52.0, "region": "GLOBAL", "asset_classes": ["fx"]},
    ]

    ids: list[str] = []
    for theme in fake_themes:
        payload = {
            "title": theme["title"],
            "description": "Seeded for frontend heat grid",
            "status": "active",
            "heat_score": float(theme["heat_score"]),
            "asset_classes": theme["asset_classes"],
            "region": theme["region"],
            "first_seen_at": now,
            "last_seen_at": now,
        }
        ids.append(upsert_theme(payload))

    return ids


def verify_top9() -> None:
    rows = (
        supabase.table("themes")
        .select("title,heat_score,status")
        .eq("status", "active")
        .order("heat_score", desc=True)
        .limit(9)
        .execute()
        .data
    )

    assert_true(len(rows) == 9, f"Expected 9 rows, got {len(rows)}")

    scores = [float(r["heat_score"]) for r in rows]
    assert_true(all(0.0 <= s <= 100.0 for s in scores), "Found heat_score outside 0-100")
    assert_true(scores == sorted(scores, reverse=True), "Top-9 not sorted by heat_score desc")


if __name__ == "__main__":
    try:
        ids = seed_fake_themes()
        verify_top9()
        print("PASS: seeded fake themes for frontend")
        print(f"Seeded/updated theme_ids: {ids}")
    except Exception as exc:
        print(f"FAIL: {exc}")
        sys.exit(1)
