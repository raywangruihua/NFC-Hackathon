from dotenv import load_dotenv
from supabase import create_client, Client
from dataclasses import dataclass
from datetime import datetime
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
assert url is not None, "SUPABASE_URL is not set in .env"

key = os.getenv("SUPABASE_KEY")
assert key is not None, "SUPABASE_KEY is not set in .env"

supabase: Client = create_client(url, key)


# ── Events ────────────────────────────────────────────────────────────────────


@dataclass
class Event:
    event_id: str
    event_type: str
    source: str
    published_at: str
    region: str
    asset_classes: list[str]
    content: str
    importance_score: float
    entities: dict
    topic: str
    sentiment: str
    raw_payload_ref: str

def get_events(
    topic: str | None = None,
    region: str | None = None,
    min_importance: float | None = None,
    days: int | None = None,
) -> list[dict]:
    """Get events with optional filters. Supports the query pattern:
    'Show all inflation-related US events in last 7 days with importance > 0.8'
    """
    query = supabase.table("events").select("*")

    if topic:
        query = query.eq("topic", topic)
    if region:
        query = query.eq("region", region)
    if min_importance is not None:
        query = query.gte("importance_score", min_importance)
    if days:
        from datetime import datetime, timedelta, timezone

        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        query = query.gte("published_at", since)

    return query.order("published_at", desc=True).execute().data


def insert_event(event: Event) -> dict:
    return supabase.table("events").insert(vars(event)).execute().data[0]


# ── Themes ────────────────────────────────────────────────────────────────────

@dataclass
class Theme:
    title: str
    description: str
    status: str
    heat_score: str
    asset_classes: list[str]
    region: str

def get_active_themes(min_heat: float | None = None) -> list[dict]:
    query = supabase.table("themes").select("*").eq("status", "active")

    if min_heat is not None:
        query = query.gte("heat_score", min_heat)

    return query.order("heat_score", desc=True).execute().data


def get_theme_by_id(theme_id: str) -> dict | None:
    result = supabase.table("themes").select("*").eq("theme_id", theme_id).execute()
    return result.data[0] if result.data else None


def insert_theme(theme: Theme) -> dict:
    return supabase.table("themes").insert(vars(theme)).execute().data[0]


def update_theme(theme_id: str, updates: dict) -> dict:
    return (
        supabase.table("themes")
        .update(updates)
        .eq("theme_id", theme_id)
        .execute()
        .data[0]
    )


# ── Event-theme map ───────────────────────────────────────────────────────────


def link_event_to_theme(event_id: str, theme_id: str) -> dict:
    return (
        supabase.table("event_theme_map")
        .insert({"event_id": event_id, "theme_id": theme_id})
        .execute()
        .data[0]
    )


def get_events_for_theme(theme_id: str) -> list[dict]:
    return (
        supabase.table("event_theme_map")
        .select("events(*)")
        .eq("theme_id", theme_id)
        .execute()
        .data
    )


# ── Portfolio exposure ────────────────────────────────────────────────────────


def get_portfolio(user_id: str) -> list[dict]:
    return (
        supabase.table("portfolio_exposure")
        .select("*")
        .eq("user_id", user_id)
        .execute()
        .data
    )


def upsert_portfolio_exposure(exposure: dict) -> dict:
    return supabase.table("portfolio_exposure").upsert(exposure).execute().data[0]


# ── Risk alerts ───────────────────────────────────────────────────────────────


def get_unresolved_alerts(user_id: str, severity: str | None = None) -> list[dict]:
    """Get unresolved alerts for a user. Supports the query pattern:
    'Fetch unresolved high-severity alerts for user X'
    """
    query = (
        supabase.table("risk_alerts")
        .select("*")
        .eq("user_id", user_id)
        .eq("acknowledged", False)
    )

    if severity:
        query = query.eq("severity", severity)

    return query.order("created_at", desc=True).execute().data


def acknowledge_alert(alert_id: str) -> dict:
    from datetime import datetime, timezone

    return (
        supabase.table("risk_alerts")
        .update(
            {
                "acknowledged": True,
                "acknowledged_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .eq("id", alert_id)
        .execute()
        .data[0]
    )


def insert_alert(alert: dict) -> dict:
    return supabase.table("risk_alerts").insert(alert).execute().data[0]


# ── Recommendations ───────────────────────────────────────────────────────────


def get_recommendations(user_id: str) -> list[dict]:
    return (
        supabase.table("recommendations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
        .data
    )


def insert_recommendation(recommendation: dict) -> dict:
    return supabase.table("recommendations").insert(recommendation).execute().data[0]


# ── Memory store ──────────────────────────────────────────────────────────────


def insert_memory(
    content: str, embedding: list[float], content_type: str, metadata: dict
) -> dict:
    return (
        supabase.table("memory")
        .insert(
            {
                "content": content,
                "embedding": embedding,
                "content_type": content_type,
                "metadata": metadata,
            }
        )
        .execute()
        .data[0]
    )


def search_memory(
    embedding: list[float], top_k: int = 5, content_type: str | None = None
) -> list[dict]:
    """Nearest-neighbor semantic search over memory store."""
    query = supabase.rpc(
        "match_memory",
        {
            "query_embedding": embedding,
            "match_count": top_k,
        },
    )

    result = query.execute().data

    if content_type:
        result = [r for r in result if r.get("content_type") == content_type]

    return result

# ── Storage ──────────────────────────────────────────────────────────────

def insert_storage(storage_path: str, raw_payload: str) -> str:
    supabase.storage.from_("raw-payloads").upload(
        path=storage_path,
        file=raw_payload.encode("utf-8"),
        file_options={"content-type": "application/json"},
    )

def get_full_article(event_id: str) -> dict | None:
    event = supabase.table("events").select("*").eq("event_id", event_id).execute()
    if not event.data:
        return None

    raw_payload_ref = event.data[0].get("raw_payload_ref")
    if not raw_payload_ref:
        return None

    # fetch from Supabase Storage
    file = supabase.storage.from_("raw-payloads").download(raw_payload_ref)
    return {"event": event.data[0], "raw_content": file.decode("utf-8")}
