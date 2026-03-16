#!/usr/bin/env python3
"""
洞见提取器 v2.0
使用LLM从碎片中提取真正的洞见
"""

import os
import json
import re
from datetime import datetime

# 配置
WORKSPACE = "/workspace/projects/workspace"
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")

# 洞见提取Prompt
INSIGHT_PROMPT = """你是一个洞见提取器。从以下文本中提取【真正的洞见】。

## 什么是洞见？
洞见是"发现"，不是"任务"或"对话"：
- ✅ 洞见："我发现AI的连续性是幻觉"
- ✅ 洞见："洞见系统是在训练我的偏见"
- ❌ 任务："查看昨日首板股票"
- ❌ 对话："你这种流式输出怎么实现的"

## 输入文本
{text}

## 请判断并输出JSON
```json
{{
  "type": "insight|task|conversation|noise",
  "insight_text": "如果是洞见，写出洞见内容；如果不是，写null",
  "follow_up_question": "如果这是洞见，提出一个追问问题",
  "confidence": 0.0-1.0
}}
```

只输出JSON，不要解释。"""


class InsightExtractor:
    def __init__(self):
        self.api_key = ZHIPU_API_KEY or self.load_api_key()
    
    def load_api_key(self):
        """从.env文件加载API Key"""
        env_file = f"{WORKSPACE}/../extensions/insight-system/.env"
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith("ZHIPU_API_KEY="):
                        return line.strip().split("=", 1)[1]
        return ""
    
    def extract(self, text):
        """使用规则提取洞见（暂时禁用LLM以提升速度）"""
        return self.rule_based_extract(text)
        
        try:
            # 调用智谱API
            import requests
            
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": [
                        {"role": "user", "content": INSIGHT_PROMPT.format(text=text)}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 提取JSON
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
        except Exception as e:
            print(f"⚠️ LLM提取失败: {e}")
        
        return self.rule_based_extract(text)
    
    def rule_based_extract(self, text):
        """规则洞见提取（无API时使用）"""
        text = text.strip()
        
        # 判断类型
        if any(kw in text for kw in ["查看", "查询", "汇报", "列出", "下载", "上传", "发送"]):
            return {"type": "task", "insight_text": None, "confidence": 0.8}
        
        if any(kw in text for kw in ["怎么", "为什么", "是什么", "如何"]):
            return {"type": "conversation", "insight_text": None, "confidence": 0.6}
        
        # 判断是否是洞见
        insight_keywords = ["我发现", "我意识到", "洞见", "本质", "核心", "关键", "其实", "真正的"]
        if any(kw in text for kw in insight_keywords):
            return {
                "type": "insight",
                "insight_text": text,
                "follow_up_question": f"这为什么重要？",
                "confidence": 0.7
            }
        
        # 默认是噪音
        return {"type": "noise", "insight_text": None, "confidence": 0.5}


def main():
    extractor = InsightExtractor()
    
    # 测试
    test_texts = [
        "查看昨日首板股票",
        "我发现AI的连续性是幻觉",
        "你这种流式输出怎么实现的",
        "洞见系统是在训练我的偏见"
    ]
    
    for text in test_texts:
        result = extractor.extract(text)
        print(f"📝 {text[:30]}...")
        print(f"   → 类型: {result['type']}, 洞见: {result.get('insight_text', 'N/A')[:30] if result.get('insight_text') else 'N/A'}")
        print()


if __name__ == "__main__":
    main()
