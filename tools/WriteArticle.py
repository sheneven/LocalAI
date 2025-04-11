import requests
import json

# 定义 Ollama API 的地址
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODLE="deepseek-r1:32b"

def generate_document(prompt, model="llama2"):
    """
    调用 Ollama API 生成文本
    :param prompt: 输入的提示信息
    :param model: 使用的模型名称，默认为 llama2
    :return: 生成的文本
    """
    data = {
        "model": model,
        "prompt": prompt
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = ""
        for line in response.text.splitlines():
            if line:
                data = json.loads(line)
                if 'response' in data:
                    result += data['response']
        return result
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None

# 读取知识库中的样例文章
def read_sample_articles(file_paths):
    """
    读取样例文章内容
    :param file_paths: 样例文章的文件路径列表
    :return: 文章内容字符串
    """
    articles = ""
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                articles += file.read() + "\n"
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
    return articles

# 生成公文的主函数
def generate_official_document_by_ex(sample_article_paths, doc_type, doc_topic):
    """
    根据样例文章生成公文
    :param sample_article_paths: 样例文章的文件路径列表
    :param doc_type: 公文类型，如通知、报告等
    :param doc_topic: 公文主题
    :return: 生成的公文内容
    """
    # 读取样例文章
    sample_articles = read_sample_articles(sample_article_paths)
    # 构建提示信息
    prompt = f"以下是一些相关的样例文章：{sample_articles}。请根据这些样例文章，撰写一篇 {doc_type}，主题是 {doc_topic}。"
    # 调用 Ollama API 生成公文
    document = generate_document(prompt)
    return document
#文档总结
def generate_summary(document_content, model="llama2"):
    """
    调用 Ollama API 生成文档摘要
    :param document_content: 文档内容
    :param model: 使用的模型名称，默认为 llama2
    :return: 生成的摘要内容
    """
    prompt = f"请总结以下文档内容：{document_content}"
    data = {
        "model": model,
        "prompt": prompt
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = ""
        for line in response.text.splitlines():
            if line:
                data = json.loads(line)
                if 'response' in data:
                    result += data['response']
        return result
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None

def summarize_document(file_path, model="llama2"):
    """
    读取文档并生成摘要
    :param file_path: 文档的文件路径
    :param model: 使用的模型名称，默认为 llama2
    :return: 生成的摘要内容
    """
    document_content = read_document(file_path)
    if document_content:
        return generate_summary(document_content, model)
    return None
if __name__ == "__main__":
    '''
    # 替换为你的样例文章文件路径列表
    sample_article_paths = ["article1.txt", "article2.txt"]
    # 公文类型
    doc_type = "通知"
    # 公文主题
    doc_topic = "会议安排"
    # 生成公文
    official_document = generate_official_document(sample_article_paths, doc_type, doc_topic)
    if official_document:
        print(official_document)
    '''
    # 替换为你要总结的文档的文件路径
    document_path = r"d:\document.txt"
    summary = summarize_document(document_path)
    if summary:
        print("文档摘要：")
        print(summary)
    else:
        print("未能生成摘要。")