# backend/analysislib/market_impact.py
from typing import List, Dict
from collections import Counter

def generate_market_impact(themes: List[Dict]) -> List[Dict]:
    """
    Generate a market impact summary for each theme.
    
    Placeholder logic:
    - direction: majority sentiment from events ('risk-on', 'risk-off', 'neutral')
    - avg_importance: average of event importance scores
    - event_count: number of events
    - affected_assets: union of all asset_classes in events
    """
    impact_summary = []

    for theme in themes:
        events = theme.get("events", [])
        if not events:
            continue

        # Event count
        event_count = len(events)

        # Average importance
        avg_importance = sum(e.get("importance_score", 0) for e in events) / event_count

        # Aggregate direction (majority sentiment)
        sentiments = [e.get("sentiment", "neutral") for e in events]
        direction_counts = Counter(sentiments)
        direction = direction_counts.most_common(1)[0][0]  # pick the most common

        # Aggregate affected assets
        asset_list = [asset for e in events for asset in e.get("asset_classes", [])]
        affected_assets = list(set(asset_list))  # unique asset classes

        # Build summary dict
        impact_summary.append({
            "theme_name": theme.get("title"),
            "theme_id": theme.get("theme_id"),
            "heat_score": theme.get("heat_score"),
            "event_count": event_count,
            "avg_importance": round(avg_importance, 3),
            "direction": direction,
            "affected_assets": affected_assets
        })

    return impact_summary


# Example usage
if __name__ == "__main__":
    # Example input: themes from heat_score.py
    example_themes = [
        {
            "theme_id": "1111",
            "title": "inflation",
            "heat_score": 0.59,
            "events": [
                {"importance_score": 0.59, "sentiment": "risk-off", "asset_classes": ["bonds", "equities"]}
            ]
        },
        {
            "theme_id": "2222",
            "title": "interest rate",
            "heat_score": 1.686,
            "events": [
                {"importance_score": 0.8, "sentiment": "risk-off", "asset_classes": ["bonds"]},
                {"importance_score": 1.2, "sentiment": "risk-on", "asset_classes": ["equities"]}
            ]
        }
    ]

    market_impact = generate_market_impact(example_themes)
    for m in market_impact:
        print(m)