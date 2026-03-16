#!/bin/bash
# 洞见系统统一入口脚本
# 用法: ./run.sh [command] [options]

WORKSPACE="/workspace/projects/workspace"
INSIGHTS_DIR="/workspace/projects/extensions/insight-system"

# 设置 Python 路径
export PYTHONPATH="$INSIGHTS_DIR:$INSIGHTS_DIR/storage:$INSIGHTS_DIR/utils:$PYTHONPATH"

# 加载环境变量（优先从插件目录加载）
if [ -f "$INSIGHTS_DIR/.env" ]; then
    set -a
    source "$INSIGHTS_DIR/.env"
    set +a
fi

# 兼容旧版本：也从 collider/.env 加载
if [ -f "$INSIGHTS_DIR/collider/.env" ]; then
    set -a
    source "$INSIGHTS_DIR/collider/.env"
    set +a
fi

show_help() {
    echo "洞见系统 - 神经元式洞见生成与管理"
    echo ""
    echo "用法: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  insight              运行核心洞见系统 (默认)"
    echo "  collide              运行碰撞引擎（碎片碰撞产生洞见）"
    echo "  heartbeat            运行心跳任务（每小时）"
    echo "  optimize             运行优化任务（每3小时，含反思）"
    echo "  multimodal           运行多模态记忆收集"
    echo "  search <query>       搜索记忆"
    echo "  status               显示系统状态"
    echo "  help                 显示此帮助"
    echo ""
    echo "Examples:"
    echo "  ./run.sh insight"
    echo "  ./run.sh collide"
    echo "  ./run.sh search '量化策略'"
    echo "  ./run.sh status"
}

case "$1" in
    "insight"|"")
        echo "🧠 运行洞见系统..."
        python3 "$INSIGHTS_DIR/core/insight_system.py"
        ;;
    "collide")
        echo "⚡ 运行碰撞引擎..."
        cd "$INSIGHTS_DIR/collider"
        export $(cat .env | xargs) && python3 runner.py --status
        ;;
    "heartbeat")
        echo "💓 运行心跳任务..."
        LOG_FILE="$WORKSPACE/memory/heartbeat-cron.log"
        echo "=== 心跳任务 $(date) ===" >> "$LOG_FILE"
        python3 "$INSIGHTS_DIR/core/insight_system.py" 2>&1 >> "$LOG_FILE"
        echo "心跳完成 $(date)" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        ;;
    "optimize")
        echo "⚡ 运行洞见优化任务..."
        LOG_FILE="$WORKSPACE/memory/insight-cron.log"
        DATE=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[$DATE] === 洞见系统优化任务开始 ===" >> "$LOG_FILE"
        python3 "$INSIGHTS_DIR/core/insight_system.py" >> "$LOG_FILE" 2>&1
        echo "[$DATE] ✅ 优化完成" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        ;;
    "multimodal")
        echo "🧠 运行多模态记忆收集..."
        python3 "$INSIGHTS_DIR/collectors/multimodal_collect.py"
        ;;
    "search")
        if [ -z "$2" ]; then
            echo "❌ 请提供搜索关键词"
            echo "用法: ./run.sh search <关键词>"
            exit 1
        fi
        echo "🔍 搜索记忆: $2"
        python3 "$INSIGHTS_DIR/utils/search.py" "$2"
        ;;
    "status")
        echo "📊 系统状态:"
        python3 "$INSIGHTS_DIR/utils/status.py"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ 未知命令: $1"
        show_help
        exit 1
        ;;
esac
