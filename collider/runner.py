#!/usr/bin/env python3
"""
第二系统 - 主运行脚本
整合：收集器 + 碰撞引擎 + 追问引擎 + 变异模式
"""

import os
import sys
import json
import random
import sqlite3
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collector import add_fragment, get_unprocessed_fragments, mark_processed, add_insight, init_db, get_recent_insights
from collider import run_collider
from questioner import run_questioner, init_questions_table
from client import SmallModelClient

DB_PATH = os.path.expanduser("~/.openclaw/workspace/second-brain/memories.db")
MUTATION_PROBABILITY = 0.05  # 5%变异概率

def init_all():
    """初始化所有表"""
    init_db()
    init_questions_table()

def run_mutation(model_client):
    """
    变异模式 - 低概率生成假设片段
    只有5%概率触发
    """
    if random.random() > MUTATION_PROBABILITY:
        return None
    
    # 获取近期碎片作为"养分"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, source FROM fragments ORDER BY created_at DESC LIMIT 10")
    fragments = c.fetchall()
    conn.close()
    
    if len(fragments) < 3:
        return None
    
    fragments_text = "\n".join([f[0] for f in fragments])
    
    prompt = f"""基于以下信息碎片，生成一个"假设性片段"：
    
{fragments_text}

要求：
1. 这是可能存在但尚未被证实的想法
2. 必须基于现有信息合理推断
3. 用[假设]标记

直接输出片段内容，不要其他解释。"""

    try:
        hypothesis = model_client.chat(prompt).strip()
        if hypothesis and len(hypothesis) > 10:
            # 添加到碎片库，标记为假设
            add_fragment(f"[假设] {hypothesis}", source="mutation", tags=["hypothesis"])
            return hypothesis
    except Exception as e:
        print(f"变异失败: {e}")
    
    return None

def save_collision_insights(insights):
    """保存碰撞产生的洞见"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for insight in insights:
        c.execute("""
            INSERT INTO insights (fragments, insight, confidence)
            VALUES (?, ?, ?)
        """, (json.dumps(insight.get('fragments', [])), insight['insight'], insight.get('confidence', 0.5)))
    
    conn.commit()
    conn.close()

def save_questions(questions):
    """保存问题"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for q in questions:
        c.execute("""
            INSERT OR IGNORE INTO questions (question, trigger, depth, asked)
            VALUES (?, ?, ?, 0)
        """, (q.get('question', ''), q.get('trigger', ''), q.get('depth', 'shallow')))
    
    conn.commit()
    conn.close()

def run_cycle():
    """运行一个完整的循环"""
    print(f"\n{'='*50}")
    print(f"🧠 第二系统 运行中... {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    model_client = SmallModelClient()
    
    results = {
        "collisions": [],
        "questions": [],
        "mutation": None
    }
    
    # 1. 碰撞引擎
    print("\n⚡ 运行碰撞引擎...")
    collision_insights = run_collider(model_client)
    if collision_insights:
        save_collision_insights(collision_insights)
        results["collisions"] = collision_insights
        print(f"   产生 {len(collision_insights)} 个碰撞洞见")
        for i in collision_insights:
            print(f"   💡 {i['insight'][:80]}...")
    else:
        print("   (暂无足够碎片产生碰撞)")
    
    # 2. 追问引擎
    print("\n❓ 运行追问引擎...")
    questions = run_questioner(model_client)
    if questions:
        save_questions(questions)
        results["questions"] = questions
        print(f"   生成 {len(questions)} 个问题")
        for q in questions:
            print(f"   ❔ {q['question']}")
    else:
        print("   (积累不足，跳过)")
    
    # 3. 变异模式（5%概率）
    print("\n🧬 变异模式检查...")
    mutation = run_mutation(model_client)
    if mutation:
        results["mutation"] = mutation
        print(f"   ⚠️  触发变异: {mutation[:60]}...")
    else:
        print(f"   ✓ 未触发 (概率 {MUTATION_PROBABILITY*100}%)")
    
    print(f"\n✅ 循环完成")
    return results

def get_status():
    """获取系统状态"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM fragments")
    frag_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM insights")
    insight_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM questions WHERE asked = 0")
    pending_questions = c.fetchone()[0]
    
    conn.close()
    
    return {
        "fragments": frag_count,
        "insights": insight_count,
        "pending_questions": pending_questions
    }

if __name__ == "__main__":
    init_all()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            status = get_status()
            print(f"📊 状态: {status['fragments']} 碎片, {status['insights']} 洞见, {status['pending_questions']} 待问问题")
        elif sys.argv[1] == "--insights":
            insights = get_recent_insights(5)
            for i, (insight, conf, created) in enumerate(insights, 1):
                print(f"{i}. [{conf:.0%}] {insight[:100]}")
        else:
            print("用法: python runner.py [--status|--insights]")
    else:
        run_cycle()
