#!/usr/bin/env python3
"""
洞见系统状态显示
"""

import json
import os
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
STATE_FILE = f"{WORKSPACE}/.openclaw/insight-state.json"
MEMORY_DIR = f"{WORKSPACE}/memory"

def load_state():
    """加载系统状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "insights": [],
        "connections": [],
        "run_count": 0,
        "last_run": None
    }

def count_memory_files():
    """统计记忆文件数量"""
    if os.path.exists(MEMORY_DIR):
        return len([f for f in os.listdir(MEMORY_DIR) if f.endswith('.md')])
    return 0

def format_time(iso_time):
    """格式化时间"""
    if not iso_time:
        return "从未"
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_time

def main():
    state = load_state()
    
    insights = state.get('insights', [])
    connections = state.get('connections', [])
    run_count = state.get('run_count', 0)
    last_run = state.get('last_run')
    memory_files = count_memory_files()
    
    print("╔════════════════════════════════════╗")
    print("║      🧠 洞见系统状态              ║")
    print("╠════════════════════════════════════╣")
    print(f"║  总洞见数:     {len(insights):<20} ║")
    print(f"║  连接数:       {len(connections):<20} ║")
    print(f"║  运行次数:     {run_count:<20} ║")
    print(f"║  记忆文件:     {memory_files:<20} ║")
    print("╠════════════════════════════════════╣")
    print(f"║  上次运行: {format_time(last_run):<17} ║")
    print("╚════════════════════════════════════╝")
    
    # 显示最新洞见
    if insights:
        print("\n📌 最新洞见:")
        for insight in insights[-3:]:
            text = insight.get('text', '')[:60]
            print(f"  • {text}...")

if __name__ == "__main__":
    main()
