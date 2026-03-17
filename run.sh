#!/bin/bash
# 洞见系统统一入口脚本
# 用法: ./run.sh [command] [options]

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSIGHTS_DIR="$SCRIPT_DIR"

# 自动检测 OpenClaw 目录
if [ -n "$OPENCLAW_HOME" ]; then
    WORKSPACE="$OPENCLAW_HOME/workspace"
elif [ -d "$HOME/.openclaw" ]; then
    WORKSPACE="$HOME/.openclaw/workspace"
    OPENCLAW_HOME="$HOME/.openclaw"
else
    WORKSPACE="/workspace/projects/workspace"
    echo -e "\033[1;33m⚠️ 未检测到 OpenClaw，使用默认路径\033[0m"
fi

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
    echo "  auto-drive           运行 AI 自我驱动（更新模糊层+碰撞引擎）"
    echo "  heartbeat            运行心跳任务（每小时）"
    echo "  optimize             运行优化任务（每3小时，含反思）"
    echo "  multimodal           运行多模态记忆收集"
    echo "  workflow-learn       运行工作流学习"
    echo "  search <query>       搜索记忆"
    echo "  status               显示系统状态"
    echo "  compat-check         检查兼容性"
    echo "  help                 显示此帮助"
    echo ""
    echo "Examples:"
    echo "  ./run.sh insight"
    echo "  ./run.sh collide"
    echo "  ./run.sh auto-drive"
    echo "  ./run.sh search '量化策略'"
    echo "  ./run.sh status"
    echo "  ./run.sh compat-check"
}

case "$1" in
    "insight"|"")
        echo "🧠 运行洞见系统..."
        python3 "$INSIGHTS_DIR/core/insight_system.py"
        ;;
    "collide")
        echo "⚡ 运行碰撞引擎..."
        cd "$INSIGHTS_DIR/collider"
        if [ -f ".env" ]; then
            export $(cat .env | xargs)
        fi
        python3 runner.py --status
        ;;
    "auto-drive")
        echo "🤖 运行 AI 自我驱动..."
        python3 "$INSIGHTS_DIR/core/auto_driver.py"
        ;;
    "auto-drive-dry")
        echo "🤖 AI 自我驱动 (dry-run)..."
        python3 "$INSIGHTS_DIR/core/auto_driver.py" --dry-run
        ;;
    "workflow-learn")
        echo "📚 运行工作流学习..."
        python3 "$INSIGHTS_DIR/core/workflow_learner.py"
        ;;
    "heartbeat")
        echo "💓 运行心跳任务..."
        LOG_FILE="$OPENCLAW_HOME/logs/heartbeat-cron.log"
        echo "=== 心跳任务 $(date) ===" >> "$LOG_FILE"
        python3 "$INSIGHTS_DIR/core/insight_system.py" 2>&1 >> "$LOG_FILE"
        echo "心跳完成 $(date)" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        ;;
    "optimize")
        echo "⚡ 运行洞见优化任务..."
        LOG_FILE="$OPENCLAW_HOME/logs/insight-cron.log"
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
    "compat-check")
        echo "🔧 兼容性检查:"
        python3 "$INSIGHTS_DIR/core/compat.py"
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
