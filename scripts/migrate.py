#!/usr/bin/env python3
"""
迁移脚本：将 OpenClaw 记忆迁移到洞见系统
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

# 添加洞见系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.memory_server import OpenClawMemorySystem


def migrate_from_openclaw(workspace="/workspace/projects/workspace"):
    """
    将 OpenClaw 的 Markdown 记忆迁移到洞见系统
    
    Args:
        workspace: OpenClaw workspace 路径
    """
    memory_dir = f"{workspace}/memory"
    
    if not os.path.exists(memory_dir):
        print(f"❌ 记忆目录不存在: {memory_dir}")
        return
    
    # 初始化洞见记忆系统
    memory_system = OpenClawMemorySystem(workspace)
    
    # 读取所有记忆文件
    memory_files = sorted(Path(memory_dir).glob("*.md"))
    
    print(f"📚 发现 {len(memory_files)} 个记忆文件")
    
    total_fragments = 0
    total_insights = 0
    
    for mf in memory_files:
        print(f"\n📝 处理 {mf.name}...")
        
        content = mf.read_text(encoding='utf-8')
        
        # 提取日期
        date_match = re.search(r'# (\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else mf.stem
        
        # 提取段落
        sections = re.split(r'\n##+\s*', content)
        
        fragments_in_file = 0
        
        for section in sections:
            if not section.strip():
                continue
            
            # 跳过标题
            if section.startswith('#'):
                continue
            
            # 清理内容
            clean_content = section.strip()
            
            if len(clean_content) < 50:  # 跳过太短的段落
                continue
            
            # 添加到洞见系统
            result = memory_system.create(
                clean_content,
                metadata={
                    "source": "migrated",
                    "date": date,
                    "original_file": mf.name
                }
            )
            
            if result.get("success"):
                fragments_in_file += 1
                total_insights += result.get("insights_generated", 0)
        
        total_fragments += fragments_in_file
        print(f"   ✅ 迁移 {fragments_in_file} 个碎片")
    
    print(f"\n{'='*50}")
    print(f"🎉 迁移完成！")
    print(f"{'='*50}")
    print(f"📊 统计:")
    print(f"   - 记忆文件: {len(memory_files)} 个")
    print(f"   - 迁移碎片: {total_fragments} 个")
    print(f"   - 生成洞见: {total_insights} 个")
    
    # 同步到 OpenClaw
    print(f"\n🔄 同步到 OpenClaw...")
    memory_system.sync_to_openclaw()
    
    # 显示状态
    status = memory_system.status()
    print(f"\n📈 系统状态:")
    print(f"   - 总洞见数: {status['total_insights']}")
    print(f"   - 总碎片数: {status['total_fragments']}")
    print(f"   - 连接数: {status['connections']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='迁移 OpenClaw 记忆到洞见系统')
    parser.add_argument('--workspace', default='/workspace/projects/workspace',
                       help='OpenClaw workspace 路径')
    parser.add_argument('--dry-run', action='store_true',
                       help='试运行，不实际迁移')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🏃 试运行模式")
        memory_dir = f"{args.workspace}/memory"
        if os.path.exists(memory_dir):
            files = list(Path(memory_dir).glob("*.md"))
            print(f"📚 发现 {len(files)} 个记忆文件")
            for f in files:
                print(f"   - {f.name}")
        else:
            print(f"❌ 记忆目录不存在: {memory_dir}")
    else:
        migrate_from_openclaw(args.workspace)


if __name__ == "__main__":
    main()
