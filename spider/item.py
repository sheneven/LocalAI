import scrapy

class NewsCrawlerItem(scrapy.Item):
    title = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    origin = scrapy.Field()
    label = scrapy.Field()