#!/bin/bash
# 洞见系统优化脚本 - 每3小时运行
# 包含反思环节

LOG_FILE="/workspace/projects/workspace/memory/insight-cron.log"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$DATE] === 洞见系统优化任务开始 ===" >> $LOG_FILE

# 1. 运行核心处理
cd /workspace/projects/workspace
python3 scripts/insight_system.py >> $LOG_FILE 2>&1

# 2. 反思环节
echo "[$DATE] 💭 反思环节..." >> $LOG_FILE

# 读取运行状态
STATE_FILE="/workspace/projects/workspace/.openclaw/insight-state.json"
if [ -f "$STATE_FILE" ]; then
    RUN_COUNT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('run_count', 0))")
    INSIGHTS=$(python3 -c "import json; print(len(json.load(open('$STATE_FILE')).get('insights', [])))")
    
    echo "[$DATE] 📊 运行次数: $RUN_COUNT, 洞见数: $INSIGHTS" >> $LOG_FILE
    
    # 如果连续3次没有新洞见，提示可能需要调整
    if [ "$INSIGHTS" -lt 3 ]; then
        echo "[$DATE] ⚠️ 洞见较少，可能需要调整阈值或输入源" >> $LOG_FILE
    fi
fi

echo "[$DATE] ✅ 优化完成" >> $LOG_FILE
echo "" >> $LOG_FILE
