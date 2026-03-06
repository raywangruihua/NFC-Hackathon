from backend.datalib.datalib import run_gdelt_spider
from backend.databaselib.db import get_unprocessed, get_raw_article


query_terms = [
    "inflation",
    "interest rate",
    "oil prices",
    "recession",
    "credit spread",
    "geopolitical risk",
]
run_gdelt_spider(query_terms, "1year", 10, False)


print("Printing raw payloads...")
unprocessed = get_unprocessed()
for item in unprocessed:
    article = get_raw_article(item["storage_path"])
    print(article)
