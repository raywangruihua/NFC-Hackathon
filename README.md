# NFC Hackathon

This initial prototype follows a monolithic structure.

## Source ingestion

Data is taken from publicly available APIs and scraped from reputable
financial news websites. Future work can include premium APIs such as BLPAPI
(Bloomberg API). For demonstration purposes, only free sources are used.

### APIs

Federal Reserve Economic Data (FRED)

- US macro and regional economic time series
- Annual, quarterly, monthly, weekly and daily

```python
# Return all available macroeconomic indicator categories.
def list_fred_categories() -> List[str]:

# Return all macroeconomic indicators for category.
def list_fred_indicators(category: str) -> Dict[str, str]:

# Fetch data for a macroeconomic indicator from FRED.
def get_fred_indicator_data(
    indicator_name: str,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict:

# Fetch data for all macroeconomic indicators in a category from FRED.
def get_fred_category_data(
    category: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict[str, Dict]:
```

GDELT-based webcrawler

Major news sites block webcrawlers unless users pay a subscription fee or
license. The GDELT endpoint offers keyword-based search to find news articles,
which our webcrawler then scrapes.

```python
# Run the GDELT spider to crawl and scrape news articles.
def run_gdelt_spider(
    query_terms: str | List[str],
    timespan: str,
    maxrecords: int,
    debug: Optional[bool] = False,
) -> None:
```

News article output format.

```json
{
    "title": "Title",
    "language": "English",
    "sourcecountry": "USA",
    "source": "USA News",
    "url": "www.news.com",
    "published_at": "2025-01-01",
    "author": "John USA",
    "raw": "...",
    "tone": "Positive",
    "fetch_error": null
}
```

## Normalisation and enrichment

## Analysis layer

## Storage

### Overview

The storage layer is split into three components, each serving a distinct
purpose:

| Store | Technology | Purpose |
| --- | --- | --- |
| Raw store | Supabase Storage | Immutable original payloads |
| Processed store | Supabase Postgres | Cleaned, query-ready structured data |
| Memory store | Supabase pgvector | Semantic retrieval over unstructured text |

---

## Processed Store Tables

### `events`

Normalized event records. The central table everything else references.

| Field | Type | Description |
| --- | --- | --- |
| event_id | uuid | Primary key, generated before DB insert |
| event_type | text | e.g. economic_release, news |
| source | text | Publisher name |
| published_at | timestamptz | Original publication time |
| region | text | e.g. US, EU |
| asset_classes | text[] | e.g. [bonds, equities] |
| content | text | Cleaned article text |
| importance_score | float | 0-1 |
| entities | dict | e.g. {"countries": ["US", "China"], "tickers": ["SPY", "TLT"]} |
| topic | text | e.g. inflation, rates, geopolitics |
| sentiment | text | risk-on, risk-off, neutral |
| raw_payload_ref | text | Path to raw file in Supabase Storage |
| created_at | timestamptz | row creation time |

### `themes`

Grouped clusters of related events identified by the analysis agent.

| Field | Type | Description |
| --- | --- | --- |
| theme_id | uuid | Primary key |
| title | text | Human-readable theme name |
| description | text | Description of theme |
| status | text | active, cooling, inactive |
| heat_score | float | How active/relevant the theme is |
| first_seen_at | timestamptz | When theme was first detected |
| last_seen_at | timestamptz | When theme last had new events |
| region | text | e.g. US, EU |
| asset_classes | text[] | e.g. [bonds, equities] |
| created_at | timestamptz | row creation time |

### `event_theme_map`

Many-to-many link between events and themes. One event can belong to multiple
themes.

### `portfolio_exposure`

Per-user portfolio holdings. Used to match themes to user risk.

### `risk_alerts`

Generated alerts when a theme breaches a severity threshold for a user.

### `recommendations`

Suggested actions with confidence score and a reference to the AI's reasoning
in the memory store.

---

## Raw Store

Original payloads are stored in Supabase Storage under the `raw-payloads`
bucket.

Storage path format: `{event_id}.json`

The `raw_payload_ref` field on each event row points to this path. To retrieve
the full article:

```text
memory.metadata.event_id -> events.raw_payload_ref -> Supabase Storage
```

The UUID is generated in Python **before** the DB insert so the storage path
and event row can reference the same ID:

```python
import uuid

event_id = str(uuid.uuid4())
storage_path = f"{event_id}.json"

# upload to storage first
insert_storage(storage_path, raw_payload)

# then insert into database with known id
insert_event({"event_id": event_id, "raw_payload_ref": storage_path, ...})
```

---

## Memory Store

The memory store enables semantic retrieval - finding relevant past context by
meaning, not keywords.

### What gets stored

| content_type | When | Example |
| --- | --- | --- |
| article_chunk | After enrichment | Chunked article text (~500 words) |
| summary | After analysis | AI-generated theme or event summary |
| recommendation_rationale | After recommendation generated | AI reasoning |
| timeline_note | During theme lifecycle | Notes on theme evolution |

### How retrieval works

```text
User query
    ->
embed_query(query)          <- uses RETRIEVAL_QUERY task type
    ->
match_memory(embedding)     <- nearest-neighbor search in pgvector
    ->
top-k results ranked by cosine similarity
    ->
filter by metadata (date, region, content_type)
```

### Task types

Always use the correct task type when embedding:

- `RETRIEVAL_DOCUMENT` - when inserting into memory
- `RETRIEVAL_QUERY` - when searching memory

Using mismatched types degrades retrieval quality.

## Storage API

All database interactions go through `db.py`.

### Events

```python
# Insert a new event (status defaults to pending)
insert_event(event: Event) -> JsonDict

# Get events with optional filters
get_events(
    topic: str | None,
    region: str | None,
    min_importance: float | None,
    days: int | None,
) -> list[JsonDict]
```

### Themes

```python
# Insert a new theme
insert_theme(theme: Theme) -> JsonDict

# Get all active themes
get_active_themes(min_heat: float | None) -> list[JsonDict]

# Get a theme by id
get_theme_by_id(theme_id: str) -> JsonDict | None

# Update a theme (e.g. heat_score, status)
update_theme(theme_id: str, updates: JsonDict) -> JsonDict
```

### Event-Theme Map

```python
# Link an event to a theme
link_event_to_theme(event_id: str, theme_id: str) -> JsonDict

# Get all events for a theme
get_events_for_theme(theme_id: str) -> list[JsonDict]
```

## Example Usage

```python
import json
import uuid

event_id = str(uuid.uuid4())
storage_path = f"{event_id}.json"

raw_payload = json.dumps(
    {
        "event_id": event_id,
        "source": "reuters",
        "published_at": "2026-03-04T10:00:00Z",
        "title": "US Inflation Surges to 4.2%",
        "full_text": (
            "US inflation rose to 4.2% in March, exceeding expectations of 3.8%. "
            "The Federal Reserve is expected to respond with further rate hikes."
        ),
        "url": "https://reuters.com/example",
    }
)

<<<<<<< HEAD
=======
event_id = str(uuid.uuid4())
storage_path = f"{event_id}.json"

>>>>>>> 91f862080299ae2bbead17396b385ffa8d7792d8
# upload to storage first
insert_storage(storage_path, raw_payload)

# then insert event with the known id
event = insert_event(
    Event(
        event_id=event_id,
        event_type="economic_release",
        source="reuters",
        published_at="2026-03-04",
        region="US",
        asset_classes=["bonds", "equities"],
        content="US inflation rose to 4.2% in March, exceeding expectations of 3.8%.",
        importance_score=0.9,
        entities={"countries": ["US"]},
        topic="inflation",
        sentiment="risk-off",
        raw_payload_ref=storage_path,
    )
)
```

## Serving and product layer

## Reliability, governance, and observability
