#!/usr/bin/env python3
"""
飞书消息碎片收集器
在主会话运行时将消息写入队列，供定时任务处理
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import sys

# 导入配置加载器
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from config_loader import get_config

# 获取配置
_config = get_config()
QUEUE_FILE = str(_config.message_queue_file)

def add_to_queue(message_text, source="feishu-dm"):
    """添加消息到队列"""
    queue = []
    
    # 读取现有队列
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, 'r') as f:
                queue = json.load(f)
        except:
            queue = []
    
    # 添加新消息
    queue.append({
        "text": message_text[:200],
        "source": source,
        "timestamp": datetime.now().isoformat()
    })
    
    # 只保留最近50条
    queue = queue[-50:]
    
    # 写入
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)
    
    print(f"✅ 已加入队列，当前 {len(queue)} 条")

def read_queue():
    """读取队列"""
    if not os.path.exists(QUEUE_FILE):
        return []
    
    with open(QUEUE_FILE, 'r') as f:
        return json.load(f)

def clear_queue():
    """清空队列"""
    with open(QUEUE_FILE, 'w') as f:
        json.dump([], f)
    print("🗑️ 队列已清空")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "add":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "test"
            add_to_queue(text)
        elif sys.argv[1] == "read":
            queue = read_queue()
            print(f"📋 队列有 {len(queue)} 条消息")
            for q in queue[-5:]:
                print(f"  - {q['text'][:50]}")
        elif sys.argv[1] == "clear":
            clear_queue()
    else:
        print("用法: python3 message_queue.py add <消息> | read | clear")
