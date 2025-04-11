import os
from spider.operation.Process import run as pr

#config = ConfigSingleton()
column_names = ["id","title","content","summary"]
#从数据库读取数据
def getDataFromMysql(mysqlUtil, _date):
    data = mysqlUtil.select_data("news_info", "id,title,content,summary", f"published_time > {_date}")
    #print(data)
    dict_list = [dict(zip(column_names, row)) for row in data]
    return dict_list
    
#数据处理
def processData(news_data):
    #print(typeof(news_data))
    return pr(news_data)
    
#数据保存到数据库
def saveDataToMysql(mysqlUtil,news_data):
    for news in news_data:
        update_str = f"summary='{news['summary']}'"
        mysqlUtil.update_data("news_info", update_str, f"id={news['id']}")
    pass

#按照日期处理数据
def run(_date,config):
    mysqlUtil = config.getMysql()
    data = getDataFromMysql(mysqlUtil,"'"+_date+"'")
    if data is not None:
        processed_data = processData(data)
        saveDataToMysql(mysqlUtil, processed_data)
'''
if __name__ == "__main__":
    run("2025-03-13")
'''
    
    