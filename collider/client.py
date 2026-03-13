#!/usr/bin/env python3
"""
小模型客户端 - 统一接口
支持智谱/Gemini/MiniMax
"""

import os
import json
import requests

class SmallModelClient:
    """轻量模型客户端"""
    
    def __init__(self):
        self.zhipu_key = os.getenv("ZHIPU_API_KEY")
        self.minimax_key = os.getenv("MINIMAX_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
    
    def chat(self, prompt: str, system: str = None) -> str:
        """统一聊天接口"""
        # 优先智谱
        if self.zhipu_key:
            return self._call_zhipu(prompt, system)
        if self.minimax_key:
            return self._call_minimax(prompt, system)
        if self.gemini_key:
            return self._call_gemini(prompt, system)
        return ""
    
    def _call_zhipu(self, prompt: str, system: str = None) -> str:
        try:
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {"Authorization": f"Bearer {self.zhipu_key}", "Content-Type": "application/json"}
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            payload = {"model": "glm-4-flash", "messages": messages}
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"智谱调用失败: {e}")
        return ""
    
    def _call_minimax(self, prompt: str, system: str = None) -> str:
        try:
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {"Authorization": f"Bearer {self.minimax_key}", "Content-Type": "application/json"}
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            payload = {"model": "abab6.5s-chat", "messages": messages}
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"MiniMax调用失败: {e}")
        return ""
    
    def _call_gemini(self, prompt: str, system: str = None) -> str:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
            
            content = prompt
            if system:
                content = f"{system}\n\n{prompt}"
            
            payload = {"contents": [{"parts": [{"text": content}]}]}
            resp = requests.post(url, json=payload, timeout=30)
            
            if resp.status_code == 200:
                return resp.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini调用失败: {e}")
        return ""

if __name__ == "__main__":
    client = SmallModelClient()
    print(client.chat("你好"))
