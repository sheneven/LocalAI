from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import hashlib
import jieba
import requests

OLLAMA_API_URL = "http://192.168.3.65:11434/api/generate"
MODEL_NAME = "qwen2.5:32b"
'''
概要：近日，昆明机场一广告牌上的女性形象被发现有六根手指，经核实为某信息传 
媒公司的招商广告，且图像由AI生成。目前，该公司已对广告进行了更换
'''
#MODEL_NAME = "deepseek-v2:16b"
'''
概要：昆明机场的一处广告牌上出现了一个错误，女士伸出的大拇指被误显示为有6
根手指。这张图片实际上是由一家信息传媒公司的招商广告中的一部分。该传媒公司表示，这是由AI技术生成内容的失误，目前广
告画面已被更正。
'''
# 模拟从数据库中获取的中文新闻数据，每个元素是一个包含标题和内容的字典
news_data = [
    {
        "title": "中文新闻标题1",
        "content": "<p>近日，有网友在社交媒体报料，昆明机场的一处广告牌上，女士伸出大拇指点赞，出现了6根手指。3月12日，红星新闻记者核实到，该图片系某信息传媒公司的招商广告。 传媒公司工作人员告诉记者，画面是AI生成的，目前已经更换。</p>"
    },
    {
        "title": "中文新闻标题2",
        "content": "<p>这是一段包含html标签的中文新闻内容2</p>"
    },
    {
        "title": "中文新闻标题1",  # 重复标题，内容不同
        "content": "<p>这是另一段包含html标签的中文新闻内容1</p>"
    },
    {
        "title": "中文新闻标题1",  # 重复标题和内容
        "content": "<p>这是一段包含html标签的中文新闻内容1</p>"
    }
]

# 去除HTML标签的函数
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

# 计算文本哈希值的函数
def calculate_hash(text):
    hash_object = hashlib.sha256(text.encode())
    return hash_object.hexdigest()

# 总结新闻要点的函数
def summarize_text(text, num_sentences=3):
    # 使用jieba进行中文分词
    tokenized_text = " ".join(jieba.cut(text))
    print("====="+tokenized_text)
    # 指定中文语言
    parser = PlaintextParser.from_string(tokenized_text, Tokenizer("chinese"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, num_sentences)
    print(summary)
    # 恢复中文文本
    summary_text = "".join(str(sentence).replace(" ", "") for sentence in summary)
    return summary_text
# 总结新闻要点的函数
def generate_summary(news_content):
    """
    调用 Ollama API 为新闻内容生成概要
    :param news_content: 新闻的具体内容
    :return: 生成的概要
    """
    # 构建请求体
    payload = {
        "model": MODEL_NAME,
        "prompt": f"请为以下新闻内容生成一个简单概要：{news_content}",
        "stream": False
    }

    try:
        # 发送 POST 请求到 Ollama API
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应数据
        result = response.json()
        summary = result.get("response", "")
        return summary.strip()
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except ValueError as e:
        print(f"解析响应出错: {e}")
        return None
# 去除HTML标签并处理新闻数据
def process_news(news_data):
    print(news_data)
    processed_news = []
    for news in news_data:
        print(news)
        title = str(news["title"])
        content = remove_html_tags(news["content"])
        news_hash = calculate_hash(content)
        news['hash'] = news_hash
        processed_news.append(news)
    return processed_news

# 识别并去除重复新闻
def remove_duplicates(processed_news):
    unique_news = []
    hashes_seen = set()
    for news in processed_news:
        if news["hash"] not in hashes_seen:
            unique_news.append(news)
            hashes_seen.add(news["hash"])
    return unique_news

# 生成新闻简报
def generate_news_brief(unique_news):
    news_brief = []
    total = len(unique_news)
    index = 0
    for news in unique_news:
        title = news["title"]
        summary = generate_summary(news["content"])
        news['summary'] = summary
        #news_brief.append(news)
        index += 1
        print(f"共{total}，当前{index}")
    return unique_news
# 打印新闻简报
def print_news_brief(news_brief):
    str_return = []
    for item in news_brief:
        str_return.append(f"{item['title']} ：{item['summary']}")
        print(f"标题: {item['title']}")
        print(f"摘要: {item['summary']}")
        print("-" * 50)
    return str_return
def run(_news_data):
    processed_news = process_news(_news_data)
    print("处理后的新闻数据:")
    #print(processed_news)
    unique_news = remove_duplicates(processed_news)
    print("处理后的新闻数据:")
    #print(unique_news)
    news_brief = generate_news_brief(unique_news)
    print("处理后的新闻数据:")
    #print(news_brief)
    #print_news_brief(news_brief)
    return news_brief
#run(news_data)