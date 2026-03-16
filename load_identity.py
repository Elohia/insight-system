#!/usr/bin/env python3
"""加载人格文件到洞见系统"""

import sys
import os
sys.path.insert(0, '/workspace/projects/extensions/insight-system')
sys.path.insert(0, '/workspace/projects/extensions/insight-system/core')

from core.insight_system import NeuronInsight

def load_identity_files():
    memory_dir = "/workspace/projects/workspace/memory"
    files = [
        ("IDENTITY.md", "identity"),
        ("SOUL.md", "soul"),
        ("MEMORY.md", "memory"),
        ("2026-03-10.md", "daily_log"),
        ("2026-03-12.md", "daily_log"),
        ("2026-03-13.md", "daily_log"),
    ]
    
    insight = NeuronInsight()
    total_added = 0
    
    print("🧠 正在加载人格文件到洞见系统...")
    print("=" * 50)
    
    for filename, source_type in files:
        filepath = os.path.join(memory_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 将文件内容作为记忆碎片添加
                if content.strip():
                    # 分块处理大文件
                    chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
                    for i, chunk in enumerate(chunks):
                        insight.add_fragment(
                            chunk,
                            source=f"{source_type}:{filename}#chunk{i+1}"
                        )
                    total_added += len(chunks)
                    print(f"✅ 已加载: {filename} ({len(chunks)} 个碎片)")
                else:
                    print(f"⚠️  空文件: {filename}")
            except Exception as e:
                print(f"❌ 错误 {filename}: {e}")
        else:
            print(f"❌ 未找到: {filename}")
    
    print("=" * 50)
    
    # 处理生成洞见
    if total_added > 0:
        print(f"🔄 正在处理 {total_added} 个记忆碎片...")
        insight.process()
        insight.save_state()
        print("✅ 洞见已生成并保存")
    
    print(f"\n📊 总计: 添加了 {total_added} 个记忆碎片")
    return total_added

if __name__ == "__main__":
    load_identity_files()
