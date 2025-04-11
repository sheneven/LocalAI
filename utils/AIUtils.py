import pandas as pd
import requests
import json

g_ollama_url = "http://10.0.0.10:11434/"

def model_generate(prompt, model="qwq:latest", system_message=""):
    global g_ollama_url
    feedback = ""
    url = g_ollama_url + "api/generate"
    for res in ollama_util(url, model, prompt,system_message):
        if "response" in res:
            res['response']
            feedback += res['response']
    return feedback
def model_chat(prompt, model="qwq:latest"):
    global g_ollama_url
    url = g_ollama_url + "api/chat"
    return ollama_util(url, model_name, prompt)

# 定义一个函数，用于通过 Ollama 调用大模型
def ollama_util(ollama_url, model_name, prompt,system_message=""):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_message,
        "stream": True
    }
    print(ollama_url)
    '''
    with requests.post(ollama_url, headers=headers, json=payload, stream=True) as res:
        res.raise_for_status()
        for line in res.iter_lines(decode_unicode=True):
            if line:
                yield json.loads(line)

    '''
    response = requests.post(ollama_url, headers=headers, data=json.dumps(payload))
    print("=========")
    print(response.json())
    return response.json().get('response', '')+"\n"
    