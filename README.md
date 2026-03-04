# NFC Hackathon

This initial prototype follows a monolithic structure.

## Source ingestion

Data is taken from publicly available APIs and scraped from reputable financial news websites. Future work can be done to include premium APIs such as BLPAPI (Bloomberg API). For demonstration purposes, only free sources are used.

### APIs

Federal Reserve Economic Data (FRED)

- US macro and regional economic time series
- Annual, quarterly, monthly, weekly and daily

``` python
def list_fred_categories() -> List[str]:
    """
    Return all available macroeconomic indicator categories.
    """

def list_fred_indicators(category: str) -> Dict[str, str]:
    """
    Return all macroeconomic indicators for category.
    """

def get_fred_indicator_data(
    indicator_name: str,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict:
    """
    Fetch data for a macroeconomic indicator from Federal Reserve Economic Data.
    """

def get_fred_category_data(
    category: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_order: str = "asc",
    limit: Optional[int] = None,
) -> Dict[str, Dict]:
    """
    Fetch data for all macroeconomic indicators in a category from Federal Reserve Economic Data.
    """
```

## Normalisation and enrichment

## Analysis layer

## Storage

## Serving and product layer

## Reliability, governance, and observability
