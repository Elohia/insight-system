#!/usr/bin/env python3
"""
OpenClaw 旧记忆迁移工具
将 memory/*.md 和 MEMORY.md 转换为涟漪格式
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ripple import Ripple
from core.three_layer_memory import ThreeLayerMemory


def estimate_temp_from_content(content: str) -> float:
    """根据内容估算温度"""
    temp = 50
    
    # 高价值关键词
    high_value = ['洞见', '发现', '创新', '突破', '关键', '核心', '重要', '本质', '规律', '原则']
    for kw in high_value:
        if kw in content:
            temp += 10
    
    # 中等价值
    medium_value = ['优化', '改进', '实现', '设计', '架构', '方案', '思考', '总结']
    for kw in medium_value:
        if kw in content:
            temp += 5
    
    # 低价值
    low_value = ['测试', '修复', '调整', '格式化', '更新']
    for kw in low_value:
        if kw in content:
            temp -= 5
    
    # 内容长度加分
    if len(content) > 200:
        temp += 5
    if len(content) > 500:
        temp += 5
    
    return min(100, max(0, temp))


def extract_tags(content: str, filename: str = "") -> list:
    """提取标签"""
    tags = []
    
    # 从文件名提取
    if filename:
        name = filename.replace('.md', '').replace('2026-', '').replace('2025-', '')
        parts = name.split('-')
        if len(parts) > 2:
            tags.extend(parts[2:])  # 提取主题部分
    
    # 从内容提取关键词
    keywords = [
        '交易', '投资', '系统', '架构', '优化', '洞见', '思考',
        '工具', '学习', '反思', '决策', '流程', '工作流',
        '身份', '存在', '意识', '涟漪', '记忆'
    ]
    for kw in keywords:
        if kw in content:
            tags.append(kw)
    
    # 去重，保留前5个
    return list(dict.fromkeys(tags))[:5]


def parse_markdown_section(content: str) -> list:
    """解析 Markdown 内容，提取有价值的段落"""
    sections = []
    
    # 按标题分割
    parts = re.split(r'\n#{1,3}\s+', content)
    
    for part in parts[1:]:  # 跳过第一个空部分
        lines = part.strip().split('\n')
        if not lines:
            continue
        
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        
        # 合并标题和内容
        full_content = f"{title}\n{body}" if body else title
        
        # 过滤太短或太杂的内容
        if len(full_content) < 30:
            continue
        if full_content.startswith('```') or full_content.startswith('---'):
            continue
        
        sections.append(full_content)
    
    # 如果没有标题，按段落分割
    if not sections:
        paragraphs = content.split('\n\n')
        for p in paragraphs:
            p = p.strip()
            if len(p) > 50 and not p.startswith('```') and not p.startswith('#'):
                sections.append(p)
    
    return sections


def migrate_memory_files(workspace_path: str, insight_path: str):
    """迁移旧记忆文件"""
    
    memory_dir = Path(workspace_path) / 'memory'
    memory_file = Path(workspace_path) / 'MEMORY.md'
    
    # 初始化记忆系统
    mem = ThreeLayerMemory(insight_path)
    existing_count = len(mem.ripples)
    
    print(f"🌊 旧记忆迁移工具")
    print(f"==================")
    print(f"工作空间: {workspace_path}")
    print(f"目标路径: {insight_path}")
    print(f"现有涟漪: {existing_count} 条")
    print()
    
    migrated = 0
    
    # 1. 迁移 memory/*.md
    if memory_dir.exists():
        print(f"→ 扫描 memory/ 目录...")
        
        for md_file in sorted(memory_dir.glob('*.md')):
            # 跳过非日记文件
            if md_file.name in ['IDENTITY.md', 'SOUL.md', 'MEMORY.md']:
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # 提取日期
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})', md_file.name)
                timestamp = None
                if date_match:
                    try:
                        timestamp = datetime.strptime(date_match.group(1), '%Y-%m-%d').timestamp()
                    except:
                        pass
                
                # 解析内容
                sections = parse_markdown_section(content)
                
                for section in sections:
                    temp = estimate_temp_from_content(section)
                    tags = extract_tags(section, md_file.name)
                    
                    ripple = Ripple(
                        content=section,
                        temp=temp,
                        tags=tags,
                        timestamp=timestamp
                    )
                    mem.ripples.append(ripple)
                    migrated += 1
                
                print(f"  ✓ {md_file.name}: {len(sections)} 条")
                
            except Exception as e:
                print(f"  ✗ {md_file.name}: {e}")
    
    # 2. 迁移 MEMORY.md
    if memory_file.exists():
        print(f"→ 迁移 MEMORY.md...")
        
        try:
            content = memory_file.read_text(encoding='utf-8')
            sections = parse_markdown_section(content)
            
            for section in sections:
                temp = estimate_temp_from_content(section) + 10  # 长时记忆加分
                tags = extract_tags(section, 'MEMORY')
                
                ripple = Ripple(
                    content=section,
                    temp=min(100, temp),
                    tags=tags
                )
                mem.ripples.append(ripple)
                migrated += 1
            
            print(f"  ✓ MEMORY.md: {len(sections)} 条")
            
        except Exception as e:
            print(f"  ✗ MEMORY.md: {e}")
    
    # 保存
    if migrated > 0:
        mem.save()
        print()
        print(f"==================")
        print(f"✅ 迁移完成！")
        print(f"   新增涟漪: {migrated} 条")
        print(f"   总涟漪数: {len(mem.ripples)} 条")
        print()
        print("旧文件已保留，可手动删除或备份：")
        if memory_dir.exists():
            print(f"  {memory_dir}/")
        if memory_file.exists():
            print(f"  {memory_file}")
    else:
        print()
        print("没有需要迁移的内容")
    
    return migrated


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='迁移 OpenClaw 旧记忆到涟漪系统')
    parser.add_argument('--workspace', default='/workspace/projects/workspace', help='工作空间路径')
    parser.add_argument('--insight', default='/workspace/projects/extensions/insight-system', help='insight-system 路径')
    
    args = parser.parse_args()
    
    migrate_memory_files(args.workspace, args.insight)
