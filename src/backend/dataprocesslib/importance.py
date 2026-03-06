# importance.py

# temporary rule-based scoring function to rank news importance for prioritization and filtering
# combines source credibility, entity impact, and recency into a single 0.0-1.0 score

from datetime import datetime, timezone

# ── Source tier ───────────────────────────────────────────────────────────────
SOURCE_TIERS = {
    "reuters.com":        1.0,
    "bloomberg.com":      1.0,
    "federalreserve.gov": 1.0,
    "ecb.europa.eu":      1.0,
    "wsj.com":            0.9,
    "ft.com":             0.9,
    "cnbc.com":           0.7,
    "marketwatch.com":    0.7,
    "seekingalpha.com":   0.6,
    "finance.yahoo.com":  0.5,
    "benzinga.com":       0.5,
}
DEFAULT_SOURCE_SCORE = 0.3

# ── Weights ───────────────────────────────────────────────────────────────────
WEIGHTS = {
    "source":   0.5,  # who published it — biggest signal
    "entities": 0.3,  # how many assets are affected
    "recency":  0.2,  # how fresh the article is
}

# ── Recency decay ─────────────────────────────────────────────────────────────
# Score drops linearly from 1.0 → 0.0 over RECENCY_WINDOW hours
RECENCY_WINDOW_HOURS = 24


def _source_score(source: str) -> float:
    return next(
        (v for k, v in SOURCE_TIERS.items() if k in source),
        DEFAULT_SOURCE_SCORE
    )


def _entity_score(entities: dict) -> float:
    """More tickers + countries = broader market impact."""
    n_tickers   = len(entities.get("tickers",   []))
    n_countries = len(entities.get("countries", []))
    # Cap at 5 tickers and 3 countries for full score
    ticker_score  = min(n_tickers   / 5, 1.0)
    country_score = min(n_countries / 3, 1.0)
    return round((ticker_score + country_score) / 2, 4)


def _recency_score(published_at: str) -> float:
    """
    Returns 1.0 if just published, decaying to 0.0 after RECENCY_WINDOW_HOURS.
    Expects published_at as ISO 8601 string e.g. '2026-03-04T15:55:12.000Z'
    """
    try:
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        now       = datetime.now(timezone.utc)
        age_hours = (now - published).total_seconds() / 3600
        return max(1.0 - (age_hours / RECENCY_WINDOW_HOURS), 0.0)
    except Exception:
        return 0.5  # neutral fallback if timestamp is malformed


def score_importance(source: str, entities: dict, published_at: str) -> float:
    """
    Returns an importance score between 0.0 and 1.0.

    Args:
        source:       Publisher domain e.g. 'finance.yahoo.com'
        entities:     Dict with 'tickers' and 'countries' lists
        published_at: ISO 8601 timestamp string

    Returns:
        Float importance score rounded to 4 decimal places.
    """
    s = _source_score(source)
    e = _entity_score(entities)
    r = _recency_score(published_at)

    score = (
        s * WEIGHTS["source"]   +
        e * WEIGHTS["entities"] +
        r * WEIGHTS["recency"]
    )
    return round(score, 4)


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(score_importance(
        source       = "finance.yahoo.com",
        entities     = {"tickers": ["USB", "PNC", "SPY"], "countries": ["United States"]},
        published_at = "2026-03-04T15:55:12.000Z"
    ))
    # → ~0.47  (low source, decent entities, stale recency)

    print(score_importance(
        source       = "reuters.com",
        entities     = {"tickers": ["SPY", "TLT", "GLD"], "countries": ["US", "China", "EU"]},
        published_at = datetime.now(timezone.utc).isoformat()
    ))
    # → ~0.93  (top source, broad entities, fresh)