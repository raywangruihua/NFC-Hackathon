"""
Generate fake macroeconomic events and insert them into the database
to test the Gemini classification pipeline.

Usage:
    python seed_test_events.py
"""

import uuid
from datetime import datetime, timedelta, timezone

from databaselib.db import insert_event, Event


FAKE_EVENTS = [
    {
        "event_type": "news",
        "source": "reuters",
        "region": "Global",
        "asset_classes": ["commodities"],
        "content": "Global shipping delays worsened as Red Sea disruptions forced "
                   "major carriers to reroute around Africa. Container freight rates "
                   "surged 40% in two weeks, raising concerns about renewed supply "
                   "chain bottlenecks across manufacturing sectors.",
        "importance_score": 0.81,
        "entities": {"region": "Global"},
        "topic": "",
        "sentiment": "risk-off",
    },
    {
        "event_type": "news",
        "source": "ft",
        "region": "US",
        "asset_classes": ["bonds"],
        "content": "The Congressional Budget Office projected the US deficit will "
                   "reach $1.9 trillion in 2025, driven by rising interest costs on "
                   "federal debt. Analysts warn that sustained fiscal expansion could "
                   "crowd out private investment and push yields higher.",
        "importance_score": 0.78,
        "entities": {"organization": "CBO"},
        "topic": "",
        "sentiment": "risk-off",
    },
    {
        "event_type": "news",
        "source": "bloomberg",
        "region": "US",
        "asset_classes": ["fx"],
        "content": "The dollar index climbed to a six-month high as strong US "
                   "economic data widened the interest rate differential with Europe "
                   "and Japan. EUR/USD fell below 1.05 for the first time since 2023, "
                   "pressuring emerging market currencies.",
        "importance_score": 0.80,
        "entities": {"indicator": "DXY"},
        "topic": "",
        "sentiment": "risk-on",
    },
    {
        "event_type": "news",
        "source": "wsj",
        "region": "US",
        "asset_classes": ["equities"],
        "content": "Amazon announced a $100 billion capital expenditure plan focused "
                   "on AI data centers and custom silicon chips. The investment joins "
                   "similar commitments by Microsoft and Google, fueling a boom in "
                   "power infrastructure demand.",
        "importance_score": 0.88,
        "entities": {"organization": ["Amazon", "Microsoft", "Google"]},
        "topic": "",
        "sentiment": "risk-on",
    },
    {
        "event_type": "news",
        "source": "reuters",
        "region": "US",
        "asset_classes": ["equities", "bonds"],
        "content": "Existing home sales dropped 4.9% in February as mortgage rates "
                   "hovered near 7%. Inventory remains historically tight, keeping "
                   "prices elevated despite weakening demand. First-time buyer share "
                   "fell to a record low.",
        "importance_score": 0.72,
        "entities": {"indicator": "Existing Home Sales"},
        "topic": "",
        "sentiment": "risk-off",
    },
    {
        "event_type": "news",
        "source": "reuters",
        "region": "Global",
        "asset_classes": ["equities", "commodities"],
        "content": "The European Union introduced sweeping new tariffs on imported "
                   "solar panels and wind turbines to protect domestic manufacturers. "
                   "The policy aims to accelerate the green energy transition but may "
                   "temporarily raise costs for utility-scale renewable projects.",
        "importance_score": 0.85,
        "entities": {"region": "EU"},
        "topic": "",
        "sentiment": "risk-off",
    },
    {
        "event_type": "news",
        "source": "ft",
        "region": "Europe",
        "asset_classes": ["equities"],
        "content": "A sophisticated ransomware attack targeted major European clearinghouses, "
                   "causing temporary delays in transaction settlement. Regulators are now "
                   "demanding stricter cybersecurity protocols for critical financial infrastructure.",
        "importance_score": 0.89,
        "entities": {"region": "Europe"},
        "topic": "",
        "sentiment": "risk-off",
    },
    {
        "event_type": "news",
        "source": "wsj",
        "region": "US",
        "asset_classes": ["equities"],
        "content": "NASA awarded a multibillion-dollar contract to a private aerospace consortium "
                   "to develop next-generation lunar habitats and supply lines. The announcement "
                   "sparked a rally in space-related equities and defense contractors.",
        "importance_score": 0.77,
        "entities": {"organization": "NASA"},
        "topic": "",
        "sentiment": "risk-on",
    },
    {
        "event_type": "news",
        "source": "bloomberg",
        "region": "Japan",
        "asset_classes": ["equities", "bonds"],
        "content": "Japan announced sweeping pension reforms to address its rapidly aging population "
                   "and shrinking workforce. The government plans to incentivize later retirement "
                   "ages and increase mandatory corporate contributions.",
        "importance_score": 0.82,
        "entities": {"country": "Japan"},
        "topic": "",
        "sentiment": "risk-off",
    },
    {
        "event_type": "news",
        "source": "reuters",
        "region": "US",
        "asset_classes": ["cryptocurrency", "equities"],
        "content": "The SEC officially approved the first spot Ethereum ETFs for trading on major US "
                   "exchanges. Institutional interest in digital assets is expected to surge as "
                   "regulatory clarity improves under the new administration.",
        "importance_score": 0.91,
        "entities": {"organization": "SEC", "asset": "Ethereum"},
        "topic": "",
        "sentiment": "risk-on",
    },
]


def main():
    now = datetime.now(timezone.utc)

    print(f"Inserting {len(FAKE_EVENTS)} test events...")
    for i, fake in enumerate(FAKE_EVENTS):
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=fake["event_type"],
            source=fake["source"],
            published_at=(now - timedelta(days=i)).isoformat(),
            region=fake["region"],
            asset_classes=fake["asset_classes"],
            content=fake["content"],
            importance_score=fake["importance_score"],
            entities=fake["entities"],
            topic=fake["topic"],
            sentiment=fake["sentiment"],
            raw_payload_ref="",
        )
        result = insert_event(event)
        event_id = result.get("event_id", "?")
        print(f"  [{i+1}/{len(FAKE_EVENTS)}] {fake['topic'][:40]:40s} → event_id={event_id}")

    print("\nDone! Events inserted and auto-classified.")
    print("Check the timeline page to see events linked to themes.")


if __name__ == "__main__":
    main()
