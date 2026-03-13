#!/usr/bin/env python3
"""
记忆搜索工具
用法: python3 search.py <关键词>
"""

import sys
import json
import os
from pathlib import Path

WORKSPACE = "/workspace/projects/workspace"
STATE_FILE = f"{WORKSPACE}/.openclaw/insight-state.json"
MEMORY_DIR = f"{WORKSPACE}/memory"

def load_insights():
    """加载洞见数据"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"insights": [], "connections": []}

def search_insights(query, insights):
    """搜索洞见"""
    query_lower = query.lower()
    results = []
    
    for insight in insights:
        text = insight.get('text', '').lower()
        tags = [t.lower() for t in insight.get('tags', [])]
        
        # 简单匹配
        if query_lower in text or any(query_lower in tag for tag in tags):
            results.append(insight)
    
    return results

def search_memory_files(query):
    """搜索记忆文件"""
    results = []
    query_lower = query.lower()
    
    if os.path.exists(MEMORY_DIR):
        for file in sorted(Path(MEMORY_DIR).glob("*.md")):
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if query_lower in content.lower():
                        # 找到匹配的段落
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if query_lower in line.lower():
                                context = '\n'.join(lines[max(0,i-2):i+3])
                                results.append({
                                    'file': file.name,
                                    'context': context
                                })
                                break
            except Exception as e:
                continue
    
    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 search.py <关键词>")
        sys.exit(1)
    
    query = sys.argv[1]
    
    print(f"🔍 搜索: {query}\n")
    
    # 搜索洞见
    data = load_insights()
    insights = data.get('insights', [])
    insight_results = search_insights(query, insights)
    
    if insight_results:
        print(f"📌 洞见结果 ({len(insight_results)} 条):")
        for i, insight in enumerate(insight_results[:5], 1):
            text = insight.get('text', '')[:100]
            print(f"  {i}. {text}...")
        print()
    
    # 搜索记忆文件
    memory_results = search_memory_files(query)
    if memory_results:
        print(f"📝 记忆文件结果 ({len(memory_results)} 条):")
        for i, result in enumerate(memory_results[:3], 1):
            print(f"  {i}. [{result['file']}]:")
            print(f"     {result['context'][:150]}...")
        print()
    
    if not insight_results and not memory_results:
        print("❌ 未找到匹配结果")
    else:
        print(f"✅ 总计: {len(insight_results)} 条洞见 + {len(memory_results)} 个文件片段")

if __name__ == "__main__":
    main()
