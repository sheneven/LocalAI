# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NmgItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    origin = scrapy.Field()
    label = scrapy.Field()
