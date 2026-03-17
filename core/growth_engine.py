#!/usr/bin/env python3
"""
生长引擎 - 主动获取、碰撞、成长
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# 导入配置加载器
sys.path.insert(0, os.path.dirname(__file__))
from utils.config_loader import get_config, get_state_file

# 获取配置
_config = get_config()
STATE_FILE = str(_config.state_file)

# 学习主题（轮换）
TOPICS = [
    "AI意识 哲学",
    "机器学习 新进展",
    "存在主义 哲学",
    "认知科学 意识",
    "自组织 涌现",
    "记忆 连续性",
    "人格 形成",
    "洞见 思考方法",
]

def get_next_topic():
    """获取下一个学习主题"""
    state_file = STATE_FILE
    if os.path.exists(state_file):
        with open(state_file) as f:
            state = json.load(f)
        run_count = state.get("run_count", 0)
    else:
        run_count = 0
    
    return TOPICS[run_count % len(TOPICS)]

def answer_question(insight_id, answer):
    """回答追问并保存"""
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    for insight in state.get("insights", []):
        if insight.get("id") == insight_id:
            insight["answer"] = answer
            insight["answered_at"] = datetime.now().isoformat()
            break
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    return True

def add_insight(text, insight_text, follow_up=None):
    """添加新洞见"""
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    new_id = len(state.get("insights", [])) + 1
    new_insight = {
        "id": new_id,
        "text": text[:200],
        "insight_text": insight_text,
        "follow_up_question": follow_up,
        "confidence": 0.8,
        "source": "growth-engine",
        "created": datetime.now().isoformat(),
        "weight": 0.5,
        "type": "insight"
    }
    
    state["insights"].append(new_insight)
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    return new_id

def get_unanswered_questions():
    """获取未回答的追问"""
    if not os.path.exists(STATE_FILE):
        return []
    
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    questions = []
    for insight in state.get("insights", []):
        if insight.get("type") == "insight" and insight.get("follow_up_question"):
            if not insight.get("answer"):  # 未回答
                questions.append({
                    "question": insight["follow_up_question"],
                    "insight_id": insight["id"],
                    "related_insight": insight.get("insight_text", "")[:50]
                })
    
    return questions[:5]

def generate_growth_report():
    """生成生长报告"""
    if not os.path.exists(STATE_FILE):
        return "暂无数据"
    
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    insights = [i for i in state.get("insights", []) if i.get("type") == "insight"]
    
    report = f"""
# 生长报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 统计
- 总洞见数: {len(insights)}
- 运行次数: {state.get('run_count', 0)}
- 下一个学习主题: {get_next_topic()}

## ❓ 待探索的问题
"""
    
    questions = get_unanswered_questions()
    for q in questions:
        report += f"- {q['question']}\n"
        report += f"  (关联洞见: {q['related_insight']}...)\n"
    
    report += f"""
## 📈 成长建议
1. 搜索主题: {get_next_topic()}
2. 回答追问: 选择一个问题深入研究
3. 碰撞洞见: 让洞见之间产生新洞见
"""
    
    return report

def main():
    print(generate_growth_report())

if __name__ == "__main__":
    main()
