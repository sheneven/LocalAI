import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import chardet
import sys
sys.stdout.reconfigure(encoding='utf-8')
colum_list = [
    {"name": "头条", "url": "http://www.etkqq.gov.cn/xwdt/xwdt_tt/"},
    {"name": "图片新闻", "url": "http://www.etkqq.gov.cn/xwdt/xwdt_tpxw/"},
    {"name": "今日鄂前旗", "url": "http://www.etkqq.gov.cn/xwdt/xwdt_jreqq/"},
    {"name": "乡镇动态", "url": "http://www.etkqq.gov.cn/xwdt/xwdt_xzdt/"},
    {"name": "部门动态", "url": "http://www.etkqq.gov.cn/xwdt/xwdt_bmdt/"},
    {"name": "通知公告", "url": "http://www.etkqq.gov.cn/xwdt/xwdt_tzgg/"}
]

def is_news_in_this_colum(_name, _title, _url):
    return _name in _title

def get_article_list_by_colum(colum_config, _date):
    try:
        done_list = []
        undo_list = []
        url = colum_config.get('url')
        name = colum_config.get('name')
        response = requests.get(url)
        print(response)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        for li in soup.select('ul.list li'):
            a = li.find('a')
            title = a.find('div', class_='text line_hide').text.strip()
            result = chardet.detect(title.encode())
            encoding = result['encoding']
            print("encoding:" + encoding)
            link = a['href']
            date = a.find('div', class_='date').text.strip()
            news = {'title': title, 'link': link, 'date': date}
            print(news)
            if date >= _date:
                print("this news is today or later")
            news_list.append(news)
            if is_news_in_this_colum(name, title, link):
                done_list.append(news)
            else:
                undo_list.append(news)
        return {"done": done_list, "undo": undo_list}
    except requests.RequestException as e:
        print(f"请求出现错误: {e}")
        return {"done": [], "undo": []}
    except Exception as e:
        print(f"发生错误: {e}")
        return {"done": [], "undo": []}

def write_article_to_file(json_data):
    df = pd.DataFrame(json_data)
    df.to_excel("news_result.xlsx", index=False, engine='openpyxl')
    print("新闻结果已写入本地文件 news_result.xlsx")

if __name__ == '__main__':
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    undo_list = []
    done_list = []

    result = get_article_list_by_colum(colum_list[0], today)
    undo_list.extend(result.get('undo', []))
    done_list.extend(result.get('done', []))

    if len(undo_list) > 0:
        write_article_to_file(undo_list)
    print("共检测到{0}个新闻，其中{1}个未通过检测".format(len(done_list) + len(undo_list), len(undo_list)))