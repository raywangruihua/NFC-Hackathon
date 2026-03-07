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
# dataprocesslib

NLP enrichment pipeline for financial news articles. Transforms raw article JSON into a structured event schema ready for database insertion.

---

## Folder Structure

```
dataprocesslib/
├── pipeline.py           # Main entry point — orchestrates the full enrichment pipeline
└── processors/
    ├── extractor.py      # Ticker and country extraction from article text
    ├── ticker_loader.py  # Fetches and caches ticker reference set from Wikipedia
    ├── importance.py     # Importance scoring (0.0 – 1.0)
    ├── sentiments.py     # Sentiment classification via FinBERT
    └── __init__.py
```

---

## Modules

### `pipeline.py`
Main entry point. Reads raw article JSON, runs all enrichment steps, and outputs records matching the unified event schema.

**Input**
```json
{
  "title": "...",
  "text": "...",
  "source": "finance.yahoo.com",
  "sourcecountry": "United States",
  "published_at": "2026-03-04T15:55:12.000Z",
  "url": "https://...",
  "fetch_error": null
}
```

**Output**
```json
{
  "event_id": "uuid",
  "event_type": "news",
  "source": "finance.yahoo.com",
  "published_at": "2026-03-04T15:55:12.000Z",
  "region": "US",
  "asset_classes": ["equities", "commodities"],
  "content": "cleaned article text",
  "importance_score": 0.61,
  "entities": { "tickers": ["USB", "SPY"], "countries": ["United States"] },
  "topic": null,
  "sentiment": "risk-off",
  "raw_payload_ref": "raw/https://...",
  "created_at": "2026-03-06T10:00:00.000Z"
}
```

**Usage**
```bash
python pipeline.py
# reads articles.json → writes output.json + skipped.json
```

Articles with `fetch_error` are skipped and written to `skipped.json`. Articles with content shorter than 150 characters or flagged as scrape failures are processed with null NLP fields.

---

### `processors/extractor.py`
Extracts tickers and countries from article text.

- **Tickers** — regex match (`[A-Z]{3,5}`) against a reference set loaded from `ticker_loader.py`. Two-letter tickers on a whitelist (`GE`, `GS`, `MS`, `BA` etc.) are also included.
- **Countries** — spaCy `en_core_web_trf` GPE entity label, filtered against a known country list to exclude cities, regions, and industrial sites.

```python
from processors.extractor import extract_entities

extract_entities("U.S. Bancorp (USB) outperformed the S&P 500 (SPY)...")
# → {"tickers": ["SPY", "USB"], "countries": ["United States"]}
```

---

### `processors/ticker_loader.py`
Fetches the ticker reference set from Wikipedia (S&P 500, NASDAQ-100, Dow Jones) and caches it locally to `ticker_cache.json`.

- First run fetches ~600 tickers from Wikipedia and writes the cache
- Subsequent runs load from cache instantly
- Falls back to a hardcoded set if network is unavailable

```python
from processors.ticker_loader import TICKER_SET, refresh

# Force a fresh fetch and overwrite cache
refresh()
```

Delete `ticker_cache.json` to trigger a refresh on the next run.

---

### `processors/importance.py`
Scores each article's market importance on a 0.0 – 1.0 scale using three signals:

| Signal | Weight | Logic |
|---|---|---|
| Source tier | 50% | Known sources rated 0.3 – 1.0 (Reuters/Bloomberg = 1.0, Yahoo Finance = 0.5) |
| Entities | 30% | Number of tickers and countries mentioned |
| Recency | 20% | Linear decay from 1.0 → 0.0 over 24 hours |

```python
from processors.importance import score_importance

score_importance(
    source       = "reuters.com",
    entities     = {"tickers": ["SPY", "TLT"], "countries": ["US", "China"]},
    published_at = "2026-03-06T10:00:00.000Z"
)
# → 0.87
```

---

### `processors/sentiments.py`
Classifies article text as `risk-on`, `risk-off`, or `neutral` using [ProsusAI/FinBERT](https://huggingface.co/ProsusAI/finbert), a BERT model fine-tuned on financial news.

FinBERT's native labels (`positive`, `negative`, `neutral`) are remapped to risk appetite language:

| FinBERT | Output |
|---|---|
| positive | risk-on |
| negative | risk-off |
| neutral | neutral |

```python
from processors.sentiments import predict_one, predict_scalar

predict_one("Apple beats earnings expectations by 20%")
# → "risk-on"

predict_scalar(["Fed signals rate hikes", "Markets steady"], batch_size=32)
# → ["risk-off", "neutral"]
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Known Limitations

- **Country extraction** tags cities and regions as countries if not filtered — articles with heavy geopolitical content may over-report country counts
- **Ticker extraction** misses companies referenced by full name only (e.g. "U.S. Bancorp" without the `USB` symbol)
- **FinBERT** was trained on short financial headlines — sentiment reliability degrades on long-form articles (>512 tokens are truncated)
- **`published_at`** is null for a significant portion of ingested articles, defaulting recency score to 0.5
- **`topic`** field is reserved for a future classifier and is always `null`
## Analysis layer

### Overview
**READ**
`analysislib` handles event aggregation, market impact, and portfolio risk. **Database storage is not yet active**, so the pipeline runs in-memory.

The analysis layer classifies events into themes, calculates heat scores for each of them, generates market impact and evaluates user portfolios based on that result. 

The module is functional locally with **placeholder classification logic** and can be executed end-to-end currently with **example data** due to current lack of stateful portfolio representation.

```
analysislib/
├── __init__.py               
├── macro_themes.py                   
├── heat_score.py           
├── market_impact.py                      
├── portfolio_analysis.py     
├── test_connection.py      # Test harness for database connection
└── test.py                 # Test harness for analysis pipeline
```

### Pipeline Flow
---

1. **Event Input** – Load enriched article JSON.  
2. **Theme Grouping** (`macro_themes.py`) – Cluster related events.  
3. **Heat Score** (`heat_score.py`) – Calculate numeric activity score per theme.  
4. **Market Impact** (`market_impact.py`) – Generate impact direction and affected assets.  
5. **Portfolio Analysis** (`portfolio_analysis.py`) – Compare portfolio against theme impacts and produce risk alerts.  


**Note:** Storage function does not yet exist; outputs remain in-memory.

### Modules
---
### `macro_themes.py`
Groups enriched events into themes based on topic and timing.

- **Themes** — clusters of related events, grouped by topic similarity and temporal proximity.
- **Event assignment** — each event is assigned to an existing theme or starts a new theme if no suitable match is found.

```python
from analysislib.macro_themes import group_events_into_themes

example_events = [
    {"event_id": "uuid1", "topic": "inflation", "asset_classes": ["bonds"], "importance_score": 0.5, "sentiment": "risk-off", "published_at": "2026-03-04T10:00:00Z"},
    {"event_id": "uuid2", "topic": "inflation", "asset_classes": ["equities"], "importance_score": 0.7, "sentiment": "risk-off", "published_at": "2026-03-04T11:00:00Z"}
]

themes = group_events_into_themes(example_events)
# → [{"title": "inflation", "events": [...], "first_seen_at": "...", "last_seen_at": "..."}]
```

### `heat_score.py`
Calculates heat scores for each theme based on event importance and frequency.

- **Heat Score** — numeric value representing how active/relevant a theme is.
- **Factors** — includes number of events, sum of importance scores, and recency of events.
- **Output** — updates the theme dict with `heat_score` and retains asset class info.

```python
from analysislib.heat_score import calculate_theme_heat

themes_with_heat = calculate_theme_heat(themes)
# → [{"title": "inflation", "heat_score": 0.75, "asset_classes": ["bonds", "equities"]}]
```

### `market_impact.py`
Generates market impact summaries for macroeconomic themes.

- **Direction** — determines if the market impact is `risk-on` or `risk-off` based on aggregated theme sentiment.
- **Affected Assets** — identifies which asset classes (e.g., bonds, equities, commodities) are influenced by each theme.
- **Purpose** — provides a concise view of which markets may be affected and in what direction, supporting portfolio risk analysis.
- **Output** — a list of dicts, each containing:
  - `theme_name`: human-readable theme title
  - `heat_score`: numeric activity/relevance metric
  - `direction`: `risk-on` or `risk-off`
  - `affected_assets`: list of impacted asset classes

```python
from analysislib.market_impact import generate_market_impact

# Example usage:
market_summary = generate_market_impact(themes_with_heat)
# → [
#     {
#         "theme_name": "inflation",
#         "heat_score": 0.75,
#         "direction": "risk-off",
#         "affected_assets": ["bonds", "equities"]
#     },
#     {
#         "theme_name": "interest rate",
#         "heat_score": 0.9,
#         "direction": "risk-off",
#         "affected_assets": ["bonds"]
#     }
# ]
```

### `portfolio_analysis.py`
Analyzes a user's portfolio exposure relative to market themes and identifies risk alerts.

- **User ID** — the portfolio is associated with a unique user identifier.
- **Portfolio Exposure** — evaluates holdings per asset class and ticker.
- **Risk Alerts** — generates alerts when a theme impacts assets in the portfolio, with severity and trigger reason.
- **Overall Risk** — aggregates all alerts to give an overall portfolio risk percentage and level (Low, Medium, High).

**Output** — a dictionary containing:
  - `risk_alerts`: list of alerts with fields:
    - `theme_id`: linked theme UUID
    - `severity`: Low / Medium / High
    - `trigger_reason`: explanation for why the alert was triggered
  - `overall_risk`: numeric percentage (0–100%)
  - `overall_risk_level`: human-readable risk level

```python
from analysislib.portfolio_analysis import analyze_portfolio_risk

user_id = "123e4567-e89b-12d3-a456-426614174000"
portfolio = [
    {"ticker": "AAPL", "asset_class": "equities", "weight": 0.4},
    {"ticker": "US10Y", "asset_class": "bonds", "weight": 0.25},
]

market_summary = [
    {"theme_name": "inflation", "heat_score": 0.75, "direction": "risk-off", "affected_assets": ["bonds", "equities"]}
]

portfolio_risk = analyze_portfolio_risk(user_id, market_summary, portfolio)

# → {
#       "risk_alerts": [
#           {
#               "theme_id": "33a1bbfb-4683-4c0d-88e7-077d250077d2",
#               "severity": "High",
#               "trigger_reason": "100% of your portfolio is exposed to risk-off assets affected by inflation."
#           }
#       ],
#       "overall_risk": 100.0,
#       "overall_risk_level": "High"
#   }
```


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

### `raw_ingestions`

Info on articles that have been ingested to storage. Contains both processed and unprocessed articles.

| Field | Type | Description |
| --- | --- | --- |
| id | uuid | Primary key |
| storage_path | text | Storage path of article in Supabase Storage |
| source | text | Source of article |
| ingested_at | timestamptz | When article was ingested |
| processed | bool | Whether article is processed or not |
| processed_at | timestamptz | When article was processed |
| event_id | uuid | Foreign key to events table |

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
# Insert a new event
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

### Memory Store

```python
# Insert into memory store
insert_memory(content: str, embedding: list[float], content_type: str, metadata: JsonDict
) -> JsonDict

# Search from memory store (top-k)
search_memory(
    embedding: list[float], top_k: int = 5, content_type: str | None = None
) -> list[JsonDict]
```

### Storage
```python
# Ingest raw article to storage
ingest_raw_article(raw_payload: str, source: str) -> JsonDict

# Get all unprocessed articles and returns rows from raw_ingestions table
# Example usage below
get_unprocessed() -> list[JsonDict]

# Mark article as processed
mark_processed(ingestion_id: str, event_id: str) -> None

# Get article from storage
get_full_article(event_id: str) -> JsonDict | None
```

## Example Usage

```python
import json

# mock payload
source = "reuters"
raw_payload = json.dumps(
    {
        "source": source,
        "published_at": "2026-03-04T10:00:00Z",
        "title": "US Inflation Surges to 4.2%",
        "full_text": (
            "US inflation rose to 4.2% in March, exceeding expectations of 3.8%. "
            "The Federal Reserve is expected to respond with further rate hikes."
        ),
        "url": "https://reuters.com/example",
    }
)

# ingests article to storage
# also adds a row to raw_ingestions
ingest = ingest_raw_article(raw_payload, source)

# gets all unprocessed articles from table raw_ingestions
unprocessed = get_unprocessed()

for ingestion in unprocessed:
    # download the raw article 
    raw = supabase.storage.from_("raw-payloads").download(ingestion["storage_path"])
    # this is the same dict as raw_payload above 
    payload = json.loads(raw)

    # DO PROCESSING ON ARTICLE HERE

    # create event with processed info
    # data is mocked here for this example
    event_id = str(uuid.uuid4())
    event = insert_event(
        Event(
            event_id=event_id,
            raw_payload_ref=ingestion["storage_path"],
            source=ingestion["source"],
            event_type="economic_release",
            published_at="2026-03-04",
            region="US",
            asset_classes=["bonds", "equities"],
            content="US inflation rose to 4.2% in March, exceeding expectations of 3.8%.",
            importance_score=0.9,
            entities={"countries": ["US"]},
            topic="inflation",
            sentiment="risk-off",
        )
    )

    mark_processed(ingestion["id"], event_id)
```

## Serving and product layer

## Reliability, governance, and observability
