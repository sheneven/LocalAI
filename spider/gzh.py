import requests
import json
import math
import time
import random
from tqdm import tqdm
import pandas as pd

# 可选的User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36",
]

# 目标url
url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
cookie = "RK=dlfU1pDcV3; ptcz=9517a0b290759e72516957e5dd203760d910532ed6afca125d0dea8a3565ba62; o_cookie=1405516353; ua_id=aKMsAWXyRexPYnSfAAAAAGeSLBpuZpwL1qrxsnYcRsE=; mm_lang=zh_CN; _qimei_uuid42=18910121904100935264fc3c36652549cce33bf35b; pac_uid=0_cdmi2NWSefEmp; _qimei_q36=; _qimei_h38=4ba6c57d5264fc3c3665254902000007c18910; wxuin=27151621520234; suid=user_0_cdmi2NWSefEmp; pgv_pvid=8440601090; _qimei_fingerprint=1facd17b55437bdf315b976665efb89b; _clck=3874745028|1|fv2|0; uuid=d3b706a0d37203dd9da96631cfd3e859; rand_info=CAESIG0usVOBo0YcopWZd6uCujxyV3KdJzhqhlg9aC0Hayiv; slave_bizuin=3874745028; data_bizuin=3874745028; bizuin=3874745028; data_ticket=kMX3O9GkPtfTxVtxB//I7AWTXbZ+9w2JIDG2bS8DtVJldv6kEgzFushOZU4NPBGC; slave_sid=UHRTRHM5MmhVaXpkTjBFS2VxSDl4UmZWU29UdU1QRXo1V0xEZ1JtcEp6ZlEyYmcxYUFmV1oxajc2STFkM3pndDUyWGFWOWhZQThyaFZQZmZ0Y3pic200elUzaXVZRzZfXzVZUUZ2VDRmUU50YmFoOUk2ek9DdlpKeWY1Wk1tdHVwa1pERUVEa3BpRUZwbWFX; slave_user=gh_eb1d91fa6413; xid=b4c86fe03ed8b019e69ea59e695ba5a6; _clsk=1jol8p7|1744624279578|9|1|mp.weixin.qq.com/weheat-agent/payload/record"

headers = {
    "Cookie": cookie,
}

data = {
    "token": "1671697423",
    "lang": "zh_CN",
    "f": "json",
    "ajax": "1",
    "action": "list_ex",
    "begin": "0",
    "count": "20",
    "query": "",
    "fakeid": "MjM5NTQ4MTQyMg==",  # 自己的号，设置为空
    "type": "9",
}
goal = [
    {'name':"奔腾融媒",'fakeid':"MjM5NTQ4MTQyMg==",'token':"1671697423",'title':""},
    {'name':"新华网",'fakeid':"MjM5NzI3NDg4MA==",'token':"1671697423",'title':""}
]
'''
### 奔腾融媒
fake_id
MjM5NTQ4MTQyMg==
token
1671697423
### 新华网
fake_id
MjM5NzI3NDg4MA==
token
1671697423
'''

def get_total_count():
    headers["User-Agent"] = random.choice(USER_AGENTS)  # 每次请求动态更改 User-Agent
    content_json = requests.get(url, headers=headers, params=data).json()
    print(content_json)
    count = int(content_json["app_msg_cnt"])
    return count


# 每 20 篇文章休息 5 分钟
def get_content_list(title,count, per_page=5, pause_after=20, pause_time=10):
    page = int(math.ceil(count / per_page))
    total_fetched = 0

    for i in tqdm(range(page), desc="获取文章列表"):
        data["begin"] = i * per_page
        headers["User-Agent"] = random.choice(USER_AGENTS)  # 每次请求动态更改 User-Agent
        content_json = requests.get(url, headers=headers, params=data).json()
        app_msg_list = content_json["app_msg_list"]
        total_fetched += len(app_msg_list)
        
        # 保存成json
        with open("content_list.json", "w", encoding="utf-8") as f:
            json.dump(app_msg_list, f, ensure_ascii=False, indent=4)

        # 实时将数据保存到 CSV 文件中
        for item in app_msg_list:
            title = item["title"]
            link = item["url"]
            create_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["published_time"]))
            if create_time > "2025-04-03":
                return 
            result = [[title, link, create_time]]
            df = pd.DataFrame(result, columns=['title', 'url', 'published_time'])
            df.to_csv("data.csv", mode='a', header=False, index=False, encoding='utf-8')  # 追加模式写入

        # 延长请求间隔时间，模拟更自然的行为
        delay = random.uniform(20, 30)  # 延迟10-20秒s
        print(f"等待 {delay:.2f} 秒后继续...")
        time.sleep(delay)
        
        # 每爬取 pause_after 篇文章后，暂停 pause_time 秒
        if total_fetched >= pause_after:
            print(f"已爬取 {total_fetched} 篇文章，休息 {pause_time / 60} 分钟...")
            time.sleep(pause_time)  # 暂停 5 分钟（300秒）
            total_fetched = 0  # 重置计数器

def run(_goal):
    # 创建 CSV 文件并写入标题行
    df = pd.DataFrame(columns=['title', 'content', 'url', 'published_time'])
    df.to_csv("data.csv", mode='w', index=False, encoding='utf-8')

    count = get_total_count()
    get_content_list(title,count)

if __name__ == "__main__":
    #global goal
    run(goal)

