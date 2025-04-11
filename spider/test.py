import scrapy
from scrapy.crawler import CrawlerProcess
from spider.xinhua.xinhua.spiders.politics import PoliticsSpider

def run_politics_news_spider(start_date=None, end_date=None):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'politics_news.json'
    })

    process.crawl(PoliticsSpider, start_date=start_date, end_date=end_date)
    process.start()

if __name__ == "__main__":
    run_politics_news_spider('2025-03-12')