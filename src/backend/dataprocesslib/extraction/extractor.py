import pandas as pd, json, os
import re
from pyiceberg import io
import spacy
import urllib

CACHE = "ticker_cache.json"

# Spoof a browser user-agent — Wikipedia blocks Python's default urllib agent
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8")

def load_tickers() -> set[str]:
    if os.path.exists(CACHE):
        return set(json.load(open(CACHE)))

    try:
        sp500 = pd.read_html(io.StringIO(fetch_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")))[0]["Symbol"]
        ndx   = pd.read_html(io.StringIO(fetch_html("https://en.wikipedia.org/wiki/Nasdaq-100")))[4]["Ticker"]
        dji   = pd.read_html(io.StringIO(fetch_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")))[1]["Symbol"]

        tickers = set(sp500) | set(ndx) | set(dji)
        tickers = {t.replace(".", "-") for t in tickers if isinstance(t, str)}

        json.dump(list(tickers), open(CACHE, "w"))
        print(f"[ner] Loaded {len(tickers)} tickers, cached to {CACHE}")
        return tickers

    except Exception as e:
        print(f"[ner] Warning: could not load tickers ({e}). Using fallback.")
        return {"AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
                "USB",  "PNC",  "JPM",  "BAC",  "GS",   "SPY",  "TLT"}

TICKER_SET = load_tickers()


nlp = spacy.load("en_core_web_trf")

# ── Entity extraction ─────────────────────────────────────────────────────────
def extract_tickers(text: str) -> list[str]:
    """
    Finds stock tickers by matching uppercase 1-5 letter tokens
    against the inline TICKER_SET reference.
    """
    candidates = re.findall(r'\b[A-Z]{1,5}\b', text)
    return sorted(set(c for c in candidates if c in TICKER_SET))


def extract_countries(text: str) -> list[str]:
    """
    Uses spaCy GPE (geo-political entity) label to find
    countries, states, and cities in the text.
    """
    doc = nlp(text)
    return sorted({ent.text for ent in doc.ents if ent.label_ == "GPE"})


def extract_entities(text: str) -> dict:
    """
    Main entry point. Returns a dict matching the DB schema:

        {
            "tickers":   ["USB", "SPY"],
            "countries": ["United States"]
        }

    Args:
        text: Cleaned article text or headline.

    Returns:
        Dict with tickers and countries lists. Empty lists if none found.
    """
    if not text or not text.strip():
        return {"tickers": [], "countries": []}

    return {
        "tickers":   extract_tickers(text),
        "countries": extract_countries(text),
    }


# ── Batch extraction ──────────────────────────────────────────────────────────
def extract_entities_batch(texts: list[str], batch_size: int = 32) -> list[dict]:
    """
    Optimised batch version using spaCy's nlp.pipe() for large datasets.

    Args:
        texts:      List of article texts.
        batch_size: spaCy internal batch size. Tune based on available RAM.

    Returns:
        List of entity dicts, one per input text, in the same order.
    """
    results = []
    docs = list(nlp.pipe(texts, batch_size=batch_size))

    for text, doc in zip(texts, docs):
        tickers   = extract_tickers(text)
        countries = sorted({ent.text for ent in doc.ents if ent.label_ == "GPE"})
        results.append({"tickers": tickers, "countries": countries})

    return results


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = (
        "U.S. Bancorp (USB) is one of the largest regional banks in the United States. "
        "Meanwhile, its peer PNC has outperformed the S&P 500 (SPY) this year. "
        "The Federal Reserve's rate decisions continue to impact banks across the US and China."
    )

    result = extract_entities(sample)
    print("Tickers:  ", result["tickers"])
    print("Countries:", result["countries"])
