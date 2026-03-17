#!/usr/bin/env python3
"""
第二系统 - 碎片收集器
自动收集对话中的边角料信息
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# 动态获取路径
try:
    from core.config import get_openclaw_home
    OPENCLAW_HOME = get_openclaw_home()
except ImportError:
    # 回退到默认路径
    OPENCLAW_HOME = os.path.expanduser("~/.openclaw")

DB_PATH = os.path.join(OPENCLAW_HOME, "workspace", "second-brain", "memories.db")

def init_db():
    """初始化数据库"""
    Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS fragments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            source TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fragments TEXT,
            insight TEXT NOT NULL,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_fragment(content: str, source: str = "chat", tags: list = None):
    """添加碎片"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO fragments (content, source, tags) VALUES (?, ?, ?)",
        (content, source, json.dumps(tags) if tags else None)
    )
    conn.commit()
    conn.close()

def get_unprocessed_fragments():
    """获取未处理的碎片"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, source, tags FROM fragments WHERE processed = 0 ORDER BY created_at DESC LIMIT 50")
    results = c.fetchall()
    conn.close()
    return results

def mark_processed(fragment_ids: list):
    """标记已处理"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"UPDATE fragments SET processed = 1 WHERE id IN ({','.join('?' * len(fragment_ids))})", fragment_ids)
    conn.commit()
    conn.close()

def add_insight(fragments: list, insight: str, confidence: float):
    """添加洞见"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO insights (fragments, insight, confidence) VALUES (?, ?, ?)",
        (json.dumps(fragments), insight, confidence)
    )
    conn.commit()
    conn.close()

def get_recent_insights(limit: int = 5):
    """获取最近洞见"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT insight, confidence, created_at FROM insights ORDER BY created_at DESC LIMIT ?", (limit,))
    results = c.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    init_db()
    print("第二系统数据库初始化完成")
