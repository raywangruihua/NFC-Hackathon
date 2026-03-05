from backend.datalib.datalib import run_gdelt_spider


query_terms = [
    "inflation",
    "interest rate",
    "oil prices",
    "recession",
    "credit spread",
    "geopolitical risk",
]
run_gdelt_spider(query_terms, "7days", 100, True)
