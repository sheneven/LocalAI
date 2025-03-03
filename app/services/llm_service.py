import aiohttp
from typing import Dict, Any
from flask import current_app

class LLMService:
    def __init__(self, base_url: str, port: int = None, model: str = None):
        self.base_url = base_url
        self.port = port
        self.model = model
        
    def format_url(self):
        """格式化URL，确保包含正确的API路径"""
        base = f"{self.base_url}:{self.port}" if self.port else self.base_url
        # 确保base_url不以/结尾
        base = base.rstrip('/')
        # 添加API路径
        return f"{base}/api/chat"
    
    async def chat_completion(self, messages: list, **kwargs) -> Dict[str, Any]:
        url = self.format_url()
        
        # 格式化消息以符合Ollama API要求
        payload = {
            "model": self.model,  # 使用智能体指定的模型
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'content': result.get('message', {}).get('content', ''),
                            'role': 'assistant'
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"LLM API调用失败: {error_text}")
            except Exception as e:
                raise Exception(f"LLM API调用失败: {str(e)}") 