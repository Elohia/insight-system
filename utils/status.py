#!/usr/bin/env python3
"""
洞见系统状态显示
"""

import json
import os
from datetime import datetime
import sys
from pathlib import Path

# 导入配置加载器
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from config_loader import get_config, get_workspace, get_memory_dir, get_state_file

# 获取配置
_config = get_config()
WORKSPACE = str(_config.workspace)
STATE_FILE = str(_config.state_file)
MEMORY_DIR = str(_config.memory_dir)


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
