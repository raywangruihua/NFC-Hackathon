import sys
import uuid
from datetime import datetime, timezone

from backend.src.analysislib.macro_themes import group_events_into_themes
from backend.src.analysislib.heat_score import calculate_theme_heat
from backend.src.databaselib.db import supabase

def _to_iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value

def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def upsert_theme_by_title_region(theme: dict) -> str:
    title = theme["title"]
    region = theme.get("region") or ""

    existing = (
        supabase.table("themes")
        .select("theme_id")
        .eq("title", title)
        .eq("region", region)
        .limit(1)
        .execute()
        .data
    )

    payload = {
        "title": title,
        "description": theme.get("description", ""),
        "status": "active",
        "heat_score": float(theme.get("heat_score", 0.0)),
        "asset_classes": theme.get("asset_classes", []),
        "region": region,
        "first_seen_at": _to_iso(theme.get("first_seen_at")) or datetime.now(timezone.utc).isoformat(),
        "last_seen_at": _to_iso(theme.get("last_seen_at")) or datetime.now(timezone.utc).isoformat(),
    }

    if existing:
        theme_id = existing[0]["theme_id"]
        supabase.table("themes").update(payload).eq("theme_id", theme_id).execute()
        return theme_id

    inserted = supabase.table("themes").insert(payload).execute().data
    return inserted[0]["theme_id"]


def run_pipeline_db_test() -> None:
    run_id = str(uuid.uuid4())[:8]
    test_topic_a = f"test-inflation-{run_id}"
    test_topic_b = f"test-rates-{run_id}"

    example_events = [
        {
            "topic": test_topic_a,
            "asset_classes": ["bonds", "equities"],
            "importance_score": 0.72,
            "sentiment": "risk-off",
            "published_at": "2026-03-04T10:00:00Z",
            "region": "US",
        },
        {
            "topic": test_topic_b,
            "asset_classes": ["bonds"],
            "importance_score": 0.81,
            "sentiment": "risk-off",
            "published_at": "2026-03-05T09:00:00Z",
            "region": "US",
        },
        {
            "topic": test_topic_b,
            "asset_classes": ["equities"],
            "importance_score": 0.93,
            "sentiment": "risk-on",
            "published_at": "2026-03-05T12:00:00Z",
            "region": "US",
        },
    ]

    # 1) Pipeline compute
    themes = group_events_into_themes(example_events)
    themes = calculate_theme_heat(themes)

    assert_true(len(themes) >= 2, "Expected at least 2 themes")
    for t in themes:
        assert_true(0.0 <= float(t["heat_score"]) <= 100.0, "heat_score must be 0-100")

    # 2) Store to DB
    stored_ids = [upsert_theme_by_title_region(t) for t in themes]
    assert_true(len(stored_ids) == len(themes), "Not all themes were stored")

    # 3) Read-back verify
    fetched = (
        supabase.table("themes")
        .select("theme_id,title,region,heat_score,status")
        .in_("theme_id", stored_ids)
        .execute()
        .data
    )

    assert_true(len(fetched) == len(themes), "Stored themes not found on read-back")
    by_title = {row["title"]: row for row in fetched}

    assert_true(test_topic_a in by_title, f"Missing stored row for {test_topic_a}")
    assert_true(test_topic_b in by_title, f"Missing stored row for {test_topic_b}")

    for row in fetched:
        assert_true(row["status"] in {"active", "cooling", "inactive"}, "Invalid status")
        assert_true(0.0 <= float(row["heat_score"]) <= 100.0, "DB heat_score out of range")

    print("PASS: pipeline -> themes DB integration test")
    print(f"Stored theme_ids: {stored_ids}")


if __name__ == "__main__":
    try:
        run_pipeline_db_test()
    except Exception as exc:
        print(f"FAIL: {exc}")
        sys.exit(1)
