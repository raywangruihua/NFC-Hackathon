import json
from db import supabase, insert_memory, search_memory, get_full_article
from embeddings import embed_document, embed_query

# ── 0. Cleanup previous test data ────────────────────────────────────────────
supabase.table("event_theme_map").delete().neq(
    "id", "00000000-0000-0000-0000-000000000000"
).execute()
supabase.table("memory").delete().neq(
    "id", "00000000-0000-0000-0000-000000000000"
).execute()
supabase.table("recommendations").delete().neq(
    "id", "00000000-0000-0000-0000-000000000000"
).execute()
supabase.table("risk_alerts").delete().neq(
    "id", "00000000-0000-0000-0000-000000000000"
).execute()
supabase.table("themes").delete().neq(
    "theme_id", "00000000-0000-0000-0000-000000000000"
).execute()
supabase.table("events").delete().neq(
    "event_id", "00000000-0000-0000-0000-000000000000"
).execute()

print("✓ Cleaned up previous test data")

# ── 1. Insert a test event ────────────────────────────────────────────────────

event = supabase.table("events").insert({
    "event_type": "economic_release",
    "source": "reuters",
    "published_at": "2026-03-04T10:00:00Z",
    "region": "US",
    "asset_classes": ["bonds", "equities"],
    "content": "US inflation rose to 4.2% in March, exceeding expectations of 3.8%.",
    "importance_score": 0.9,
    "topic": "inflation",
    "sentiment": "risk-off"
}).execute().data[0]

print(f"✓ Inserted event: {event['event_id']}")

# ── 2. Insert a test theme ────────────────────────────────────────────────────

theme = supabase.table("themes").insert({
    "title": "US Inflation Surge",
    "description": "Persistent above-target inflation in the US",
    "status": "active",
    "heat_score": 0.85,
    "region": "US",
    "asset_classes": ["bonds", "equities"]
}).execute().data[0]

print(f"✓ Inserted theme: {theme['theme_id']}")

# ── 3. Link event to theme ────────────────────────────────────────────────────

supabase.table("event_theme_map").insert({
    "event_id": event["event_id"],
    "theme_id": theme["theme_id"]
}).execute()

print(f"✓ Linked event to theme")

# ── 4. Insert into memory store ───────────────────────────────────────────────

embedding = embed_document(event["content"])
memory = insert_memory(
    content=event["content"],
    embedding=embedding,
    content_type="article_chunk",
    metadata={
        "event_id": event["event_id"],
        "source": "reuters",
        "published_at": "2026-03-04",
        "region": "US",
        "topic": "inflation",
        "source_trust": 0.9
    }
)

print(f"✓ Inserted memory: {memory['id']}")

# ── 5. Search memory ──────────────────────────────────────────────────────────

query_embedding = embed_query("high inflation exceeding expectations")
results = search_memory(query_embedding, top_k=3)

print(f"\n✓ Search results for 'high inflation exceeding expectations':")
for r in results:
    print(f"  similarity: {r['similarity']:.4f} | {r['content'][:80]}")

# ── 6. Upload a raw article to storage ───────────────────────────────────────

event_id = event["event_id"]  # reuse event from earlier tests

raw_payload = json.dumps(
    {
        "event_id": event_id,
        "source": "reuters",
        "published_at": "2026-03-04T10:00:00Z",
        "title": "US Inflation Surges to 4.2%",
        "full_text": "US inflation rose to 4.2% in March, exceeding expectations of 3.8%. The Federal Reserve is expected to respond with further rate hikes as price pressures remain elevated across energy and food categories.",
        "url": "https://reuters.com/example",
    }
)

storage_path = f"{event_id}.json"

supabase.storage.from_("raw-payloads").upload(
    path=storage_path,
    file=raw_payload.encode("utf-8"),
    file_options={"content-type": "application/json"},
)

print(f"✓ Uploaded raw article to storage: {storage_path}")

# ── 7. Update event with storage reference ────────────────────────────────────

supabase.table("events").update({"raw_payload_ref": storage_path}).eq(
    "event_id", event_id
).execute()

print(f"✓ Updated event with raw_payload_ref")

# ── 8. Retrieve full article ──────────────────────────────────────────────────

article = get_full_article(event_id)

assert article is not None, "Article not found"
assert article["event"]["event_id"] == event_id
assert "full_text" in json.loads(article["raw_content"])

print(f"✓ Retrieved full article")
print(f"  title: {json.loads(article['raw_content'])['title']}")
print(f"  full_text: {json.loads(article['raw_content'])['full_text']}")
