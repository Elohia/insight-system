#!/usr/bin/env python3
"""
第二系统 - 模式关联引擎
使用小模型进行跨领域模式匹配
"""

import os
import json
import requests

from collector import get_unprocessed_fragments, mark_processed, add_insight

def call_small_model(text: str) -> dict:
    """调用小模型进行分析 - 支持智谱/Gemini/MiniMax"""

    # 1. 尝试智谱 (推荐，免费额度充足)
    zhipu_key = os.getenv("ZHIPU_API_KEY")
    if zhipu_key:
        try:
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Authorization": f"Bearer {zhipu_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {"role": "system", "content": "你是一个模式识别专家，找出信息间的隐藏联系。"},
                    {"role": "user", "content": f"分析以下信息碎片，找出隐藏联系：\n{text}\n输出JSON：{{\"insight\": \"...\", \"confidence\": 0.0}}"}
                ]
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            print(f"智谱失败: {e}")

    # 2. 尝试 MiniMax
    minimax_key = os.getenv("MINIMAX_API_KEY")
    if minimax_key:
        try:
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {
                "Authorization": f"Bearer {minimax_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {"role": "system", "content": "你是一个模式识别专家。"},
                    {"role": "user", "content": f"分析：{text}\n输出JSON：{{\"insight\": \"...\", \"confidence\": 0.0}}"}
                ]
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return json.loads(data['choices'][0]['message']['content'])
        except Exception as e:
            print(f"MiniMax失败: {e}")

    # 3. 尝试 Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": f"分析：{text}\n输出JSON: {{\"insight\": \"...\", \"confidence\": 0.0}}"}]}]
            }
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            print(f"Gemini失败: {e}")

    return None

def analyze_patterns():
    """分析模式"""
    fragments = get_unprocessed_fragments()
    if not fragments:
        return []

    texts = [f[1] for f in fragments]
    combined_text = "\n---\n".join(texts)

    result = call_small_model(combined_text)

    if result and result.get('confidence', 0) > 0.7:
        add_insight(
            fragments=[f[1] for f in fragments],
            insight=result['insight'],
            confidence=result['confidence']
        )
        mark_processed([f[0] for f in fragments])
        return [result]

    return []

if __name__ == "__main__":
    results = analyze_patterns()
    for r in results:
        print(f"💡 {r['insight']} (置信度: {r['confidence']})")
