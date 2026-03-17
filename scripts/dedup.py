#!/usr/bin/env python3
"""
洞见系统和向量数据库去重脚本
清理重复的洞见和向量记录
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

# 导入配置加载器
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))
from utils.config_loader import get_config, get_workspace, get_state_file

# 获取配置
_config = get_config()
WORKSPACE = str(_config.workspace)
STATE_FILE = str(_config.state_file)

VECTOR_DB = str(_config.vector_db)
BACKUP_DIR = f"{WORKSPACE}/.openclaw/backup"

def backup_file(filepath):
    """备份文件"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/{os.path.basename(filepath)}.{timestamp}.bak"
    with open(filepath, 'r') as f:
        content = f.read()
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"✅ 已备份: {backup_path}")
    return backup_path

def dedup_insights():
    """洞见去重"""
    print("\n" + "="*50)
    print("📊 洞见系统去重")
    print("="*50)
    
    if not os.path.exists(STATE_FILE):
        print("⚠️ 洞见状态文件不存在")
        return
    
    # 备份
    backup_file(STATE_FILE)
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    insights = state.get('insights', [])
    original_count = len(insights)
    print(f"原始洞见数: {original_count}")
    
    # 按内容去重，保留最新的
    # 洞见使用 text 或 insight_text 字段，不是 content
    seen_contents = {}
    unique_insights = []
    
    for insight in reversed(insights):  # 从新到旧，保留新版本
        # 优先使用 insight_text，其次 text
        content = insight.get('insight_text') or insight.get('text', '')
        if content and content not in seen_contents:
            seen_contents[content] = insight
            unique_insights.append(insight)
    
    # 反转回正确顺序
    unique_insights.reverse()
    
    removed_count = original_count - len(unique_insights)
    print(f"去重后洞见数: {len(unique_insights)}")
    print(f"移除重复: {removed_count}")
    
    # 保存
    state['insights'] = unique_insights
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print("✅ 洞见去重完成")
    return removed_count

def dedup_vectors():
    """向量数据库去重"""
    print("\n" + "="*50)
    print("📚 向量数据库去重")
    print("="*50)
    
    if not os.path.exists(VECTOR_DB):
        print("⚠️ 向量数据库文件不存在")
        return
    
    # 备份
    backup_file(VECTOR_DB)
    
    with open(VECTOR_DB, 'r') as f:
        db = json.load(f)
    
    vectors = db.get('vectors', [])
    original_count = len(vectors)
    print(f"原始向量数: {original_count}")
    
    # 分析重复
    contents = [v.get('content', '') for v in vectors]
    content_counts = Counter(contents)
    duplicates = {k: v for k, v in content_counts.items() if v > 1}
    
    print(f"重复内容组数: {len(duplicates)}")
    
    # 按内容去重，保留最新的
    seen_contents = {}
    unique_vectors = []
    
    for vector in reversed(vectors):
        content = vector.get('content', '')
        if content and content not in seen_contents:
            seen_contents[content] = vector
            unique_vectors.append(vector)
    
    # 反转回正确顺序
    unique_vectors.reverse()
    
    removed_count = original_count - len(unique_vectors)
    print(f"去重后向量数: {len(unique_vectors)}")
    print(f"移除重复: {removed_count}")
    print(f"压缩率: {removed_count/original_count*100:.1f}%")
    
    # 更新统计
    db['vectors'] = unique_vectors
    db['stats']['total'] = len(unique_vectors)
    
    # 重新计算各类型数量
    type_counts = Counter(v.get('type', 'text') for v in unique_vectors)
    db['stats']['text'] = type_counts.get('text', 0)
    db['stats']['image'] = type_counts.get('image', 0)
    db['stats']['video'] = type_counts.get('video', 0)
    
    # 保存
    with open(VECTOR_DB, 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print("✅ 向量数据库去重完成")
    return removed_count

def main():
    print("🔧 洞见系统去重工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_removed = 0
    
    # 洞见去重
    removed = dedup_insights()
    if removed:
        total_removed += removed
    
    # 向量去重
    removed = dedup_vectors()
    if removed:
        total_removed += removed
    
    print("\n" + "="*50)
    print(f"🎯 去重完成，共移除 {total_removed} 条重复记录")
    print("="*50)

if __name__ == "__main__":
    main()
