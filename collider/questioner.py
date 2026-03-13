#!/usr/bin/env python3
"""
追问循环引擎 - 系统主动提问，引发反思
核心理念：最好的洞见往往来自好的问题，而非答案
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Optional

DB_PATH = os.path.expanduser("~/.openclaw/workspace/second-brain/memories.db")

def get_recent_context(days: int = 7) -> dict:
    """获取近期上下文摘要"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 获取近期碎片
    c.execute("""
        SELECT content, source, tags 
        FROM fragments 
        WHERE created_at > datetime('now', '-7 days')
        ORDER BY created_at DESC
        LIMIT 50
    """)
    fragments = c.fetchall()
    
    # 获取近期洞见
    c.execute("""
        SELECT insight, confidence, created_at 
        FROM insights 
        WHERE created_at > datetime('now', '-7 days')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    insights = c.fetchall()
    
    conn.close()
    
    return {
        "fragments": [{"content": f[0], "source": f[1], "tags": json.loads(f[2]) if f[2] else []} for f in fragments],
        "insights": [{"insight": i[0], "confidence": i[1], "created_at": i[2]} for i in insights]
    }

def detect_question_opportunities(context: dict, model_client) -> List[dict]:
    """
    检测可以提问的机会
    基于上下文中的空白、矛盾或趋势
    """
    fragments_text = "\n".join([f"[{f['source']}] {f['content']}" for f in context['fragments'][:20]])
    insights_text = "\n".join([i['insight'] for i in context['insights']])
    
    prompt = f"""你是一个苏格拉底式提问者，擅长通过问题引发深度思考。

近期背景信息：
{fragments_text}

已有洞见：
{insights_text}

请分析以上信息，找出3个"问题的机会"：
- 用户可能忽略的问题
- 值得反思的假设
- 可能产生新方向的问题

每个问题应该：
1. 简短有力（20字以内）
2. 指向未来而非过去
3. 有一定的"不舒服感"（让人停下来想）

输出JSON数组格式：
[
    {{
        "question": "...",
        "trigger": "什么触发这个问题",
        "depth": "shallow/deep/transformation"
    }}
]"""

    try:
        response = model_client.chat(prompt)
        import re
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"问题生成失败: {e}")
    
    return []

def generate_follow_up(best_insight: dict, model_client) -> Optional[str]:
    """
    基于最佳洞见生成追问
    """
    prompt = f"""基于以下洞见，生成一个追问：

洞见: {best_insight['insight']}
置信度: {best_insight['confidence']}

要求：
1. 追问应该是"如果...会怎样"的形式
2. 指向行动或新的可能性
3. 不超过15字

直接输出问题，不要其他内容。"""

    try:
        response = model_client.chat(prompt).strip()
        if response and len(response) < 50:
            return response
    except:
        pass
    
    return None

def run_questioner(model_client, min_insights: int = 3) -> List[dict]:
    """
    运行追问引擎
    """
    context = get_recent_context()
    
    # 需要有一定积累才提问
    if len(context['fragments']) < 10:
        return []
    
    opportunities = detect_question_opportunities(context, model_client)
    
    # 保存到数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    questions = []
    for opp in opportunities[:3]:
        c.execute("""
            INSERT INTO questions (question, trigger, depth, created_at)
            VALUES (?, ?, ?, ?)
        """, (opp['question'], opp.get('trigger', ''), opp.get('depth', 'shallow'), datetime.now().isoformat()))
        questions.append(opp)
    
    conn.commit()
    conn.close()
    
    return questions

# 数据库初始化需要添加questions表
def init_questions_table():
    """初始化问题表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            trigger TEXT,
            depth TEXT,
            asked BOOLEAN DEFAULT 0,
            answered BOOLEAN DEFAULT 0,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_questions_table()
    print("追问引擎就绪")
