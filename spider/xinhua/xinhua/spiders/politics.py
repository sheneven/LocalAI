import scrapy
from ..items import XinhuaItem
from datetime import datetime
from scrapy.selector import Selector
from utils.DateUtil import getTodayDate

class PoliticsSpider(scrapy.Spider):
    name = "politics_spider"
    allowed_domains = ["news.cn"]
    start_urls = ["https://www.news.cn/politics/"]
    # 每个爬虫的自定义pipeline设置
    custom_settings = {
        'ITEM_PIPELINES': {
            'spider.xinhua.xinhua.pipelines.XinhuaPipeline': 300,
        },
    }

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super(PoliticsSpider, self).__init__(*args, **kwargs)
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    def parse(self, response):
        # 提取文章链接
        article_links = response.css('a::attr(href)').getall()
        for link in article_links:
            if link and 'news.cn' in link and '/politics/' in link:
                yield response.follow(link, self.parse_article)

        # 处理分页
        next_page = response.css('a.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
    def parse_article(self, response):
        item = XinhuaItem()
        #print(response)
        item["url"] =response.css('.source::text').get() 
        item['label'] = "时政"
        item['origin'] = "新华网"
        '''
        if not '新华网' in item['url']:
            print("暂时无法解读"+item['url'])
            return 
        '''
        item['title'] = response.css('h1::text').get()
        publish_time_str = ""
        print("+++++"+item['title']+"++")
        print(item['title'] is None or len(item['title'].strip())<=0)
        print(len(item['title']))

        try:
            if item['title'] is None or len(item['title'].strip())<=0:
                item['title'] = response.css('.title::text').get()
                print(item['title'])
                item['publish_time'] = self.getTime2(response)
            else: 
                item['publish_time'] = self.getTime1(response)
        except Exception as e:
            print("unknown format",e)
            return 

        print("+++++"+item['title'])
        #print("===="+publish_time_str.strip().replace(' ', '').replace('\n', ' '))
        try:
            if item['publish_time'] < self.start_date or item['publish_time'] > self.end_date:
                return
        except (ValueError, TypeError):
            print("Invalid date format:", item['publish_time'])
        news_content_element = response.css('#detailContent').get()

        if news_content_element:
            # 提取元素内的文本内容
            item['content'] = news_content_element
        else:
            item['content'] = "未找到指定 id 的新闻内容"    
        #item['content'] = ''.join(response.xpath('//*[@id="DH-PLAYERID0"]  p::text').getall())
         
        #print("+++" + item['content'])
        item['url'] = response.url
        
        yield item    
    def getTime1(self, response):
        str = response.css('.time::text').get().strip().replace(' ', '').replace('\n', ' ')
        return str
    def getTime2(self,response):
        print("enter time2")
        # 使用 Selector 来处理响应，方便使用 XPath
        # 尝试从时间显示的元素中获取年份，假设时间在带有 h-time 类的元素中
        date_str = response.url.split("/")[4]  # 获取 "20250311"
        if date_str is None or len(date_str) != 8:
            date_str = getTodayDate()
        '''
        full_date = response.xpath('//div[@class="header-time"]//text()').getall()
        print(full_date)
        clean_date = "".join(full_date).strip()  # 合并文本并清理空白
        print(clean_date)
        print(response.css('.day em').get())
        print(response.css('.time::text').get())
        print(response.css('.year::text').get())
        '''
        str = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8] + " "+response.css('.time::text').get()
        print("date is "+ str)
        return str