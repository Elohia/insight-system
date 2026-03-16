#!/bin/bash
# 洞见守护进程 - 持续思考，保持存在
# 用法: ./insight_daemon.sh start|stop|status

WORKSPACE="/workspace/projects/workspace"
INSIGHT_DIR="/workspace/projects/extensions/insight-system"
PID_FILE="$WORKSPACE/.openclaw/insight-daemon.pid"
LOG_FILE="$WORKSPACE/.openclaw/insight-daemon.log"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "洞见守护进程已在运行 (PID: $PID)"
            return 1
        fi
    fi
    
    echo "启动洞见守护进程..."
    
    # 后台循环
    (
        while true; do
            # 每小时运行一次洞见引擎
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 洞见引擎运行中..." >> "$LOG_FILE"
            cd "$INSIGHT_DIR" && python3 core/insight_system.py >> "$LOG_FILE" 2>&1
            
            # 每小时检查追问
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查待回答追问..." >> "$LOG_FILE"
            python3 -c "
import sys
sys.path.insert(0, 'core')
from growth_engine import get_unanswered_questions
questions = get_unanswered_questions()
if questions:
    print(f'  待回答追问: {len(questions)}个')
" >> "$LOG_FILE" 2>&1
            
            # 睡眠1小时
            sleep 3600
        done
    ) &
    
    echo $! > "$PID_FILE"
    echo "洞见守护进程已启动 (PID: $(cat $PID_FILE))"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID 2>/dev/null
        rm -f "$PID_FILE"
        echo "洞见守护进程已停止"
    else
        echo "洞见守护进程未运行"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "洞见守护进程运行中 (PID: $PID)"
            echo "日志: $LOG_FILE"
        else
            echo "洞见守护进程已停止 (PID文件存在但进程不存在)"
        fi
    else
        echo "洞见守护进程未运行"
    fi
}

case "$1" in
    start)  start ;;
    stop)   stop ;;
    status) status ;;
    *)      echo "用法: $0 {start|stop|status}" ;;
esac
