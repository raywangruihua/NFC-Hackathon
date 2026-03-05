# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    language = scrapy.Field()
    sourcecountry = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    published_at = scrapy.Field()
    author = scrapy.Field()
    section = scrapy.Field()
    body = scrapy.Field()
    tone = scrapy.Field()
    fetch_error = scrapy.Field()
