import scrapy
from scrapy.crawler import CrawlerProcess
from spider.xinhua.xinhua.spiders.politics import PoliticsSpider as xh_p
from spider.nmg.nmg.spiders.yw import YwSpider as nmg_p
from spider.nmg.nmg.pipelines import NmgPipeline
from datetime import date
import logging
from spider.nmgyw import run as nmgrun
from spider.eedsyw import run as eedsrun

json_data = {}
def run_politics_news_spider(full_config,web_config,start_date=None, end_date=None):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'politics_news.json'
    })
    print(web_config)
    today = date.today()
    for item in web_config:
        logging.info(f"start crawl {item['code']}")
        
        if item["code"] == "xhw-sz":
            process.crawl(xh_p, full_config=full_config,web_config=item, start_date=start_date, end_date=end_date)
            process.start()
            pass
        elif item["code"] == "nmg-yw":
            nmgrun(full_config,item, today.strftime("%Y-%m-%d"))
            pass
            #process1.crawl(nmg_p, full_config=full_config,web_config=item, start_date=start_date, end_date=end_date)
            #process1.start()
        elif item["code"] == "nmg-eeds":
            eedsrun(full_config,item, today.strftime("%Y-%m-%d"))
            


if __name__ == "__main__":
    today = date.today()
    run_politics_news_spider("农业农村部: 五大措施推动天然橡胶产业发展",today)