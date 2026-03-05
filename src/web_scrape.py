from backend.datalib.datalib import run_gdelt_spider


query_terms = ["inflation", "oil prices"]
run_gdelt_spider(query_terms, "7days", 10)