# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from config.GlobalConfig import ConfigSingleton

class XinhuaPipeline:
    sections = "title,origin,published_time, content, del_flag,url"

    def process_item(self, item, spider):
        print("==========enter the process_item")
        globalconfig = ConfigSingleton()
        db = globalconfig.getMysql()
        row_id = db.insert_data('news_info', 
                       self.sections,
                    (item['title'], 
                    item['origin'], 
                    item['publish_time'],
                    item['content'],'0', item['url']))
        if row_id is not None:
            db.insert_data('news_label', 
                        'news_id,label', 
                        (row_id, item['label']))
        # 插入数据
        '''
        insert_query = """
        INSERT INTO quotes (text, author, tags) VALUES (%s, %s, %s)
        """
        data = (item['text'], item['author'], ','.join(item['tags']))
        self.cursor.execute(insert_query, data)
        self.conn.commit()
        '''
        return item
