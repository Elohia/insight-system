#!/bin/bash
# 多模态记忆系统 - 定时收集任务
# 每小时运行一次，将记忆文件中的内容同步到向量数据库

WORKSPACE="/workspace/projects/workspace"
LOG_FILE="$WORKSPACE/memory/multimodal-cron.log"

echo "=== 多模态记忆收集 $(date) ===" >> $LOG_FILE

cd $WORKSPACE

# 运行多模态记忆收集
DASHSCOPE_API_KEY=sk-53a98cafbf3743879685c95b54c8965d python3 -c "
import sys
sys.path.insert(0, 'scripts')
from multimodal_memory import MultimodalMemory
import glob

memory = MultimodalMemory()

# 1. 收集 memory 目录下的最新文件
memory_files = sorted(glob.glob('memory/2026-03-*.md'))
if memory_files:
    latest_file = memory_files[-1]
    print(f'📖 读取: {latest_file}')
    with open(latest_file, 'r') as f:
        content = f.read()
    
    # 提取重要段落（以 ## 开头的内容）
    import re
    sections = re.findall(r'## (.+?)(?=## |$)', content)
    
    for section in sections[-5:]:  # 最近5个段落
        if len(section) > 20:
            memory.add_text(section[:500], {'source': 'memory', 'file': latest_file})
            print(f'  ✅ 添加: {section[:50]}...')

# 2. 统计
stats = memory.get_stats()
print(f'📊 记忆库: {stats[\"total_memories\"]} 条')
print(f'  文本: {stats[\"text_memories\"]}')
print(f'  图片: {stats[\"image_memories\"]}')
" 2>&1 >> $LOG_FILE

echo "完成 $(date)" >> $LOG_FILE
echo "" >> $LOG_FILE
