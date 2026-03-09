# backend/analysislib/test.py
# Simulates upstream caller passing event JSON into run_analysis,
# then persists resulting themes for frontend demo.

import sys
from datetime import datetime, timedelta, timezone

from backend.src.analysislib import run_analysis
from backend.src.databaselib.db import supabase


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def clear_previous_seeded_themes() -> None:
    (
        supabase.table("themes")
        .delete()
        .eq("description", "Seeded for frontend heat grid")
        .execute()
    )


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


def _make_fake_events() -> list[dict]:
    now = datetime.now(timezone.utc)

    # Target display order from highest to lowest.
    # More events + higher importance + fresher timestamps => higher heat.
    plan = [
        ("Rate Cuts", "US", ["bonds", "equities"], "risk-on", 0.96, 6),
        ("AI Capex", "US", ["equities"], "risk-on", 0.90, 5),
        ("Energy Shock", "GLOBAL", ["commodities"], "risk-off", 0.85, 4),
        ("Bank Stress", "US", ["bonds", "equities"], "risk-off", 0.80, 4),
        ("Fiscal Risk", "US", ["bonds"], "risk-off", 0.74, 3),
        ("USD Strength", "GLOBAL", ["fx"], "risk-off", 0.70, 3),
        ("China Demand", "APAC", ["equities", "commodities"], "neutral", 0.66, 3),
        ("Housing", "US", ["real_estate"], "neutral", 0.62, 2),
        ("Supply Chain", "GLOBAL", ["equities"], "neutral", 0.58, 2),
    ]

    events: list[dict] = []
    for topic, region, assets, sentiment, importance, count in plan:
        for i in range(count):
            # Keep events recent so recency score remains high.
            published_at = now - timedelta(hours=i * 3)
            events.append(
                {
                    "topic": topic,
                    "asset_classes": assets,
                    "importance_score": importance - (i * 0.01),
                    "sentiment": sentiment,
                    "region": region,
                    "published_at": _iso(published_at),
                    "content": f"{topic} update #{i+1}",
                }
            )
    return events


def seed_fake_themes() -> list[str]:
    clear_previous_seeded_themes()
    now = _iso(datetime.now(timezone.utc))

    fake_events = _make_fake_events()
    analysis_output = run_analysis(events=fake_events)
    themes = analysis_output.get("themes", [])

    # Scale analysis heat (0-100 but often compressed) for demo visibility.
    # This preserves relative ranking while making cards look "alive".
    ids: list[str] = []
    for theme in themes:
        raw_heat = float(theme.get("heat_score") or 0.0)
        demo_heat = min(100.0, round(raw_heat * 2.4, 1))

        payload = {
            "title": theme.get("title"),
            "description": "Seeded for frontend heat grid",
            "status": "active",
            "heat_score": demo_heat,
            "asset_classes": theme.get("asset_classes") or [],
            "region": theme.get("region") or "",
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
        print("PASS: seeded fake themes via run_analysis")
        print(f"Seeded/updated theme_ids: {ids}")
    except Exception as exc:
        print(f"FAIL: {exc}")
        sys.exit(1)
