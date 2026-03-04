# NFC-Hackathon

## Problem Statement

Handle information overload

- Frontend problem
- Display data in graphs, summaries, basic data analysis figures
  - AI section that displays graphs using AI generated python code? User can prompt what they want to see
  - Also include graphs

Do not overlook critical indicators or news

- Critical
  - What is critical? How to determine?
  - How to get news

Enhance risk management based on market developments

- Market developments = stocks, news?
  - News analysis
- Risk management
  - What assets does the user have?
  - Search for relevant data that affects those assets
    - Analyse the asset composition to narrow search effort

### Context

Asset managers

high volume of market-moving news:

- macroeconomic releases
  - periodic, scheduled reports issued by organisations that provide statistical data regarding overall health and performance of an economy
  - sources:
    - FRED (has python api)
    - IMF data portal
- central bank commentary
- geopolitical developments
- regulatory announcements
- sector-specific events

Essentially need to scrape websites directly or get data through apis.

information is fragmented across:

- news platforms
- research notes
- internal communications

monitoring is largely manual, dependent on keyword alerts and individual interpretation

### Expected Features

- Track how a particular topic evolves over time
  - Periodically scrape list of sources/apis for data
  - Collect data
  - Analyse data (AI probably)
  - Create timeline
- Identify when a theme becomes “hot” or “cool”
- Connect related developments across regions or asset classes
  - Have overall analysis of topics, general orchestrator
- Maintain institutional memory of past discussions
  - Chain of though reasoning in memory?
- Provide an intuitive dashboard to allow users to navigate and reference source articles as required
- (Bonus Consideration) Propose risk implications of each macro theme, e.g. Higher-than-expected inflation print in US → likely Fed hike → rates volatility ↑
  - Definitely AI

## Implementation

Features

- web scraper/data sourcing
- data analysis
- website

Tech stack

- Python backend - fastapi
- Next.js frontend

### Workflow

Collect data -> Store in memory -> Analysis -> Store analysis in memory
Store chain of thought reasoning by AI in memory

Fetch data from memory -> Display on dashboard

### Data pipeline

1. Source ingestion (scheduled + event-driven)

- Connectors for FRED, IMF, central bank feeds, major news APIs, and selected web scrapers
- Polling cadence by source type:
  - Macroeconomic series: hourly/daily
  - News and announcements: every 5-15 minutes
- Raw payload storage with source metadata (URL, publisher, timestamp, region, asset tags)

2. Normalization and enrichment

- Convert all records into a unified event schema:
  - `event_id`, `event_type`, `source`, `published_at`, `region`, `asset_classes`, `entities`, `content`, `importance_score`
- Clean text, deduplicate near-identical articles/releases, standardize timezone and units
- Add NLP enrichment:
  - Topic classification (inflation, rates, regulation, geopolitics, sector event)
  - Sentiment and directional signal (risk-on/risk-off bias)
  - Entity extraction (countries, institutions, tickers, sectors)

3. Analysis layer (AI + rules)

- Theme tracker:
  - Cluster related events into evolving themes and timeline updates
- Heat detection:
  - Detect "hot/cool" themes using mention velocity, source credibility weighting, and sentiment shift
- Portfolio impact engine:
  - Map user portfolio exposures to detected themes
  - Generate risk implications and recommended actions with confidence score
- Explainability:
  - Persist reasoning chain: event -> interpretation -> estimated impact -> suggestion

4. Storage architecture

- Raw store:
  - Immutable document/object store for original payloads and scrape output
- Processed store:
  - Structured database used by backend APIs and analytics jobs after cleaning/enrichment
  - Stores query-ready, typed data (not raw text blobs) for deterministic filtering and joins
  - Typical tables/collections:
    - `events`: normalized event records (`event_id`, `published_at`, `topic`, `region`, `entities`, `importance_score`)
    - `themes`: grouped event clusters with lifecycle fields (`theme_id`, `status`, `heat_score`, `first_seen_at`, `last_seen_at`)
    - `event_theme_map`: many-to-many link between events and themes
    - `portfolio_exposure`: user/account exposure by asset class, region, sector, ticker
    - `risk_alerts`: generated alerts with severity, trigger reason, and acknowledgement status
    - `recommendations`: suggested actions, confidence score, and explanation reference
  - Example query patterns:
    - "Show all inflation-related US events in last 7 days with importance > 0.8"
    - "Get active themes affecting portfolios with >20% duration exposure"
    - "Fetch unresolved high-severity alerts for user X"
- Memory store:
  - Semantic retrieval layer for unstructured text and historical reasoning
  - Stores embeddings + metadata for:
    - Source article chunks
    - Model-generated summaries
    - Prior recommendation rationales
    - Timeline notes and discussion memory
  - Main purpose:
    - Retrieve relevant past context by meaning, not exact keywords
    - Support "institutional memory" and explainability across time
  - Retrieval flow:
    - Embed user/query text -> nearest-neighbor search in vector index -> return top-k matches -> re-rank/filter by metadata (date, region, source trust)
  - Example query patterns:
    - "Have we seen a similar inflation shock before?"
    - "Find prior reasoning related to Fed hike + tech drawdown"
  - Guardrails:
    - Keep canonical truth (scores, statuses, IDs) in processed store
    - Use memory store for context retrieval, not as the system of record
- Cache:
  - Fast key-value cache for dashboard queries and recent alerts

5. Serving and product layer

- API endpoints (FastAPI) for:
  - Latest themes, timeline by topic, source drill-down, portfolio risk alerts, recommendation explanations
- Dashboard (Next.js):
  - Theme timeline, region/asset filters, source links, and alert center
- Notification service:
  - Trigger alerts when risk thresholds or theme heat thresholds are breached

6. Reliability, governance, and observability

- Data quality checks:
  - Freshness, null fields, duplicate rate, schema drift detection
- Monitoring:
  - Ingestion latency, pipeline failure rate, model inference latency, alert precision/recall (offline eval)
- Governance:
  - Source attribution preserved end-to-end
  - Audit trail for recommendation changes over time

### Frontend

## Review

### Robo Advisor

Common features in current Robo Advisors:

- Risk profiling questionnaire and goal-based onboarding
- Automated portfolio construction (mostly ETF-based, Modern Portfolio Theory variants)
- Auto-rebalancing and periodic drift correction
- Recurring deposits and basic retirement projections
- Tax features (tax-loss harvesting in some markets)
- Performance dashboards with simple allocation breakdowns

Strengths:

- Low-cost, scalable portfolio management
- Consistent, rules-based execution (less emotional bias)
- Good usability for beginner-to-intermediate investors
- Easy diversification through broad ETF baskets

Weaknesses:

- Generic risk models that miss personal context and behavioral factors
- Limited macro/news awareness in allocation decisions
- Weak explainability on why recommendations change
- Often static recommendation cadence (daily/weekly) vs real-time market signals
- Minimal support for non-traditional assets and cross-market exposures

What is missing in current implementations (opportunity for this project):

- Event-aware portfolio intelligence:
  - Connect macro/news events to likely portfolio impact by asset class and region
- Proactive risk alerts:
  - Alert users when portfolio exposures are vulnerable to emerging themes
- Explainable recommendation engine:
  - Show causal chain (event -> expected market effect -> portfolio implication -> action)
- Dynamic confidence scoring:
  - Indicate certainty of each recommendation and key assumptions
- Institutional memory and theme timeline:
  - Preserve historical reasoning, prior alerts, and how themes evolved over time
- Scenario + stress testing for retail UX:
  - "What if inflation surprises +1%?" style simulations with simple visuals
