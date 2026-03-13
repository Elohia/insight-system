#!/usr/bin/env python3
"""
多模态记忆收集器
从 memory 目录收集内容并同步到向量数据库
"""

import sys
import glob
sys.path.insert(0, '/workspace/projects/workspace/insights/storage')

from multimodal_memory import MultimodalMemory

def main():
    print("🧠 多模态记忆收集器")
    print("=" * 40)
    
    memory = MultimodalMemory()
    
    # 收集 memory 目录下的最新文件
    memory_files = sorted(glob.glob('/workspace/projects/workspace/memory/2026-*.md'))
    
    if not memory_files:
        print("❌ 没有找到记忆文件")
        return
    
    for mf in memory_files[-3:]:  # 最近3个文件
        print(f"\n📖 读取: {mf}")
        with open(mf, 'r') as f:
            content = f.read()
        
        # 提取重要段落
        import re
        sections = re.findall(r'## (.+?)(?=## |$)', content, re.DOTALL)
        
        added = 0
        for section in sections:
            if len(section) > 50:
                # 检查是否已存在
                existing = [v for v in memory.db.get("vectors", []) 
                          if section[:50] in v.get("content", "")]
                if not existing:
                    memory.add_text(
                        section[:800],
                        {'source': 'memory', 'file': mf}
                    )
                    added += 1
        
        print(f"  ✅ 新增 {added} 条记忆")
    
    # 统计
    stats = memory.get_stats()
    print(f"\n📊 记忆库统计:")
    print(f"  总记忆: {stats['total_memories']}")
    print(f"  文本: {stats['text_memories']}")
    print(f"  图片: {stats['image_memories']}")
    
    print("\n✅ 收集完成!")

if __name__ == "__main__":
    main()
