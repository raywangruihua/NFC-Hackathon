# NFC Hackathon

This initial prototype follows a monolithic structure.

## Source ingestion

Data is taken from publicly available APIs and scraped from reputable financial news websites. Future work can be done to include premium APIs such as BLPAPI (Bloomberg API). For demonstration purposes, only free sources are used.

### APIs

Federal Reserve Economic Data (FRED)

- US macro and regional economic time series
- Annual, quarterly, monthly, weekly and daily

``` python
# Return all available macroeconomic indicator categories.
def list_fred_categories() -> List[str]:

# Return all macroeconomic indicators for category.
def list_fred_indicators(category: str) -> Dict[str, str]:

# Fetch data for a macroeconomic indicator from Federal Reserve Economic Data.
def get_fred_indicator_data(
    indicator_name: str,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict:

# Fetch data for all macroeconomic indicators in a category from Federal Reserve Economic Data.
def get_fred_category_data(
    category: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict[str, Dict]:
```

GDELT based webcrawler

Major news sites block webcrawlers unless users pay a subscription fee or license. GDELT endpoint offers keyword based search to look for news articles, which our webscrawler scrapes.

```python
# Run the GDELT spider to crawl and scrape news articles.
# TODO: Implement pipeline.py to save scraped data into raw database.
def run_gdelt_spider(
        query_terms: str | List[str], 
        timespan: str, 
        maxrecords: int
) -> None:
```

News article output format

```json
{
    "title": "Title",
    "language": "English",
    "sourcecountry": "USA",
    "source": "USA News",
    "url": "www.news.com",
    "published_at": "2025-01-01", 
    "author": "John USA", 
    "section": "Breaking news: bla bla bla",
    "body": "Suspect is on the run", 
    "tone": "Positive", // Initial tone/semantic analysis provided by GDELT API
    "fetch_error": null
}
```

## Normalisation and enrichment

## Analysis layer

## Storage

## Serving and product layer

## Reliability, governance, and observability
