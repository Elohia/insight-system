#!/usr/bin/env python3
"""
碰撞引擎 - 让不相关的信息碎片强制"对话"
核心理念：真正的洞见来自意外碰撞，而非被动分析
"""

import os
import json
import random
import sqlite3
from datetime import datetime
from typing import List, Tuple

DB_PATH = os.path.expanduser("~/.openclaw/workspace/second-brain/memories.db")

def get_all_fragments(limit: int = 100) -> List[dict]:
    """获取所有碎片"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, source, tags FROM fragments ORDER BY created_at DESC LIMIT ?", (limit,))
    results = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "content": r[1], "source": r[2], "tags": json.loads(r[3]) if r[3] else []}
        for r in results
    ]

def calculate_relevance(f1: dict, f2: dict, model_client) -> float:
    """
    使用小模型计算两个碎片的相关度
    返回 0-1 之间的分数
    """
    prompt = f"""判断以下两条信息是否相关：

A: {f1['content']}
B: {f2['content']}

只需回答一个数字（0-1），表示相关程度。0表示完全不相关，1表示高度相关。
不要输出其他内容。"""

    try:
        response = model_client.chat(prompt)
        # 尝试提取数字
        import re
        match = re.search(r'0?\.?\d+', response)
        if match:
            return min(1.0, max(0.0, float(match.group())))
    except:
        pass
    return 0.5  # 默认值

def find_surprising_pairs(fragments: List[dict], model_client, top_k: int = 5) -> List[Tuple[dict, dict, float]]:
    """
    找出"意外配对" - 低相关度但可能产生洞见的组合
    核心理念：高度相关的内容不会有新洞见，意外配对才有可能
    """
    pairs = []
    n = len(fragments)
    
    # 随机采样配对（避免O(n²)全量计算）
    samples = min(50, n * (n - 1) // 2)
    
    for _ in range(samples):
        i, j = random.sample(range(n), 2)
        f1, f2 = fragments[i], fragments[j]
        
        # 跳过同源碎片
        if f1['source'] == f2['source']:
            continue
            
        relevance = calculate_relevance(f1, f2, model_client)
        
        # 相关度越低越"意外"，但太低也不行（0.2-0.5区间最佳）
        if 0.15 <= relevance <= 0.5:
            pairs.append((f1, f2, relevance))
    
    # 按相关度排序（越低越意外）
    pairs.sort(key=lambda x: x[2])
    return pairs[:top_k]

def generate_collision_insight(f1: dict, f2: dict, model_client) -> dict:
    """
    让两个意外配对的碎片"碰撞"，产生新洞见
    """
    prompt = f"""你是一个"信息炼金师"，擅长把看似不相关的信息结合起来，产生新洞察。

信息A: {f1['content']}
信息B: {f2['content']}

请分析这两条信息的潜在联系，产生一个"意外洞见"。
这个洞见应该是：
1. 不是简单叠加，而是真正的化学反应
2. 对用户的长期发展可能有价值
3. 至少有一点出乎意料

输出JSON格式：
{{
    "insight": "...",
    "connection_type": "类比/因果/互补/矛盾/扩展",
    "confidence": 0.0-1.0,
    "action_suggestion": "可选的建议行动"
}}"""

    try:
        response = model_client.chat(prompt)
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"碰撞失败: {e}")
    
    return None

def run_collider(model_client):
    """运行碰撞引擎"""
    fragments = get_all_fragments()
    if len(fragments) < 5:
        return []
    
    surprising_pairs = find_surprising_pairs(fragments, model_client)
    
    insights = []
    for f1, f2, relevance in surprising_pairs:
        result = generate_collision_insight(f1, f2, model_client)
        if result and result.get('confidence', 0) > 0.6:
            result['fragments'] = [f1['content'], f2['content']]
            result['relevance'] = relevance
            insights.append(result)
    
    return insights

if __name__ == "__main__":
    # 简单测试
    print("碰撞引擎就绪")
