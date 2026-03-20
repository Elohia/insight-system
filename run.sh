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
    echo "涟漪意识流系统 - 弱模型 + 强工具链"
    echo ""
    echo "用法: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  涟漪操作:"
    echo "    ripple <content> [--temp N] [--tags T1,T2]  添加涟漪"
    echo "    surface                                       查看水面状态"
    echo "    think                                         触发思考"
    echo "    resonances                                    查看共振"
    echo ""
    echo "  潜意识操作:"
    echo "    subconscious                                  查看潜意识状态"
    echo "    patterns                                      查看发现的模式"
    echo ""
    echo "  三层记忆（核心）:"
    echo "    fuzzy                                         查看模糊层（~400 tokens）"
    echo "    fuzzy-toon                                    查看模糊层 TOON 格式"
    echo "    precise [query] [--tags T] [--min-temp N]     查看精确层（按需检索）"
    echo "    deep                                          查看深度层（完整数据）"
    echo "    context                                       获取启动上下文"
    echo ""
    echo "  系统操作:"
    echo "    export                                        导出 TOON 格式"
    echo "    status                                        显示系统状态"
    echo ""
    echo "  兼容命令 (旧版):"
    echo "    insight                                       运行核心洞见系统"
    echo "    collide                                       运行碰撞引擎"
    echo "    auto-drive                                    运行 AI 自我驱动"
    echo "    search <query>                                搜索记忆"
    echo "    help                                          显示此帮助"
    echo ""
    echo "Examples:"
    echo "  # 添加涟漪"
    echo "  ./run.sh ripple '发现AI的连续性是幻觉' --temp 65 --tags AI,意识"
    echo ""
    echo "  # 查看模糊层（启动时注入）"
    echo "  ./run.sh fuzzy"
    echo ""
    echo "  # 精确检索"
    echo "  ./run.sh precise AI"
    echo "  ./run.sh precise --tags AI,意识"
    echo "  ./run.sh precise --min-temp 60 --max-temp 80"
    echo ""
    echo "  # 深度分析"
    echo "  ./run.sh deep"
    echo ""
    echo "水温范围:"
    echo "  0-30   冷静 - 逻辑分析、技术细节"
    echo "  31-60  活跃 - 日常思考、问题解决"
    echo "  61-80  沸腾 - 创意迸发、洞见产生"
    echo "  81-100 灼热 - 突破性想法、顿悟"
    echo ""
    echo "三层记忆架构:"
    echo "  模糊层: 启动加载，极简概要 (~250 tokens)"
    echo "  精确层: 按需检索，相关详情"
    echo "  深度层: 完整数据，深度分析"
}

case "$1" in
    # === 涟漪操作 ===
    "ripple")
        shift
        TEMP=50
        TAGS=""
        CONTENT=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --temp)
                    TEMP="$2"
                    shift 2
                    ;;
                --tags)
                    TAGS="$2"
                    shift 2
                    ;;
                *)
                    if [ -z "$CONTENT" ]; then
                        CONTENT="$1"
                    else
                        CONTENT="$CONTENT $1"
                    fi
                    shift
                    ;;
            esac
        done
        
        if [ -z "$CONTENT" ]; then
            echo "❌ 请提供涟漪内容"
            echo "用法: ./run.sh ripple <内容> [--temp 温度] [--tags 标签1,标签2]"
            exit 1
        fi
        
        echo "🌊 添加涟漪..."
        python3 -c "
from core.consciousness import add_ripple
tags = '$TAGS'.split(',') if '$TAGS' else None
r = add_ripple('$CONTENT', temperature=$TEMP, tags=tags)
print(f'✅ 涟漪已添加: [{r.temperature}°] {r.content}')
print(f'   ID: {r.id}')
print(f'   标签: {r.tags}')
"
        ;;
    
    "surface")
        echo "🌊 水面状态:"
        python3 -c "
from core.consciousness import get_consciousness
cs = get_consciousness()
state = cs.get_state()
surface = state['surface']

print(f\"   状态: {surface['surface_state']}\")
print(f\"   涟漪: {surface['ripple_count']} 条\")
print(f\"   平均温度: {surface['avg_temperature']}°\")
if surface['hot_tags']:
    print(f\"   热门标签: {', '.join(surface['hot_tags'])}\")
"
        ;;
    
    "think")
        echo "💭 触发思考..."
        python3 -c "
from core.consciousness import think
result = think()
if result:
    print(f'💭 {result}')
else:
    print('ℹ️ 暂无足够涟漪进行思考')
"
        ;;
    
    "resonances")
        echo "⚡ 共振状态:"
        python3 -c "
from core.ripple import get_ripple_pool
pool = get_ripple_pool()
resonances = pool.get_resonances()

if resonances:
    print(f'发现 {len(resonances)} 组共振:')
    for i, r in enumerate(resonances, 1):
        print(f\"\\n共振 {i}:\")
        print(f\"  涟漪: {r['ripple_ids']}\")
        print(f\"  模式: {r['pattern']}\")
        print(f\"  时间: {r['timestamp'][:19]}\")
else:
    print('暂无共振')
"
        ;;
    
    # === 潜意识操作 ===
    "subconscious")
        echo "🧠 潜意识状态:"
        python3 -c "
from core.subconscious import get_subconscious
sub = get_subconscious()
state = sub.get_current_state()

print(f\"   状态: {state['status']}\")
print(f\"   快照数: {state.get('snapshot_count', 0)}\")

if 'latest_snapshot' in state:
    latest = state['latest_snapshot']['raw_state']
    print(f\"   最新快照:\")
    print(f\"     涟漪数: {latest['ripple_count']}\")
    print(f\"     平均温度: {latest['avg_temperature']}°\")
    print(f\"     水面状态: {latest['state']}\")

patterns = state.get('patterns', [])
if patterns:
    print(f\"\\n   发现模式:\")
    for p in patterns[:3]:
        print(f\"     - {p['description']} (×{p.get('occurrences', 1)})\")
"
        ;;
    
    "patterns")
        echo "🧠 发现的模式:"
        python3 -c "
from core.subconscious import get_subconscious
sub = get_subconscious()
patterns = sub.get_patterns()

if patterns:
    for i, p in enumerate(patterns, 1):
        print(f\"{i}. {p['description']} (出现 {p.get('occurrences', 1)} 次)\")
else:
    print('暂未发现模式')
"
        ;;
    
    # === 系统操作 ===
    "export")
        echo "📄 导出 TOON:"
        python3 -c "
from core.consciousness import get_consciousness
cs = get_consciousness()
print(cs.export_toon())
"
        ;;
    
    "context")
        echo "🚀 启动上下文（模糊层）:"
        python3 -c "
from core.three_layer_memory import get_fuzzy_layer
print(get_fuzzy_layer())
"
        ;;
    
    "fuzzy")
        echo "🌫️ 模糊层:"
        python3 -c "
from core.three_layer_memory import get_three_layer_memory
memory = get_three_layer_memory()
content = memory.get_fuzzy()
print(content)
print()
print(f'Token 数: {memory.fuzzy.get_token_count()}')
"
        ;;
    
    "fuzzy-toon")
        echo "📄 模糊层 TOON 格式:"
        python3 -c "
from core.three_layer_memory import get_three_layer_memory
print(get_three_layer_memory().get_fuzzy_toon())
"
        ;;
    
    "precise")
        shift
        QUERY=""
        TAGS=""
        MIN_TEMP=""
        MAX_TEMP=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --query|-q)
                    QUERY="$2"
                    shift 2
                    ;;
                --tags|-t)
                    TAGS="$2"
                    shift 2
                    ;;
                --min-temp)
                    MIN_TEMP="$2"
                    shift 2
                    ;;
                --max-temp)
                    MAX_TEMP="$2"
                    shift 2
                    ;;
                *)
                    if [ -z "$QUERY" ]; then
                        QUERY="$1"
                    fi
                    shift
                    ;;
            esac
        done
        
        echo "🎯 精确层:"
        python3 -c "
from core.three_layer_memory import get_three_layer_memory
memory = get_three_layer_memory()

query = '$QUERY' if '$QUERY' else None
tags = '$TAGS'.split(',') if '$TAGS' else None
min_temp = int('$MIN_TEMP') if '$MIN_TEMP' else None
max_temp = int('$MAX_TEMP') if '$MAX_TEMP' else None

print(memory.get_precise(query=query, tags=tags, min_temp=min_temp, max_temp=max_temp))
"
        ;;
    
    "deep")
        echo "📚 深度层:"
        python3 -c "
from core.three_layer_memory import get_deep_layer
print(get_deep_layer())
"
        ;;
    
    "status")
        echo "📊 系统状态:"
        python3 -c "
from core.three_layer_memory import get_three_layer_memory
memory = get_three_layer_memory()
state = memory.fuzzy.ripple_pool.get_surface_state()

print('🌊 三层记忆状态:')
print(f'   模糊层: {memory.fuzzy.get_token_count()} tokens')
print(f'   涟漪数: {state[\"ripple_count\"]}')
print(f'   共振数: {len(memory.precise.get_resonances())}')
print(f'   快照数: {len(memory.deep.get_all_snapshots())}')
print()
print('🌊 水面状态:')
print(f'   状态: {state[\"surface_state\"]}')
print(f'   温度: {state[\"avg_temperature\"]}°')
print(f'   热门标签: {\", \".join(state[\"hot_tags\"])}')
"
        ;;
    
    # === 兼容旧命令（已归档）===
    "insight"|"")
        echo "⚠️ 旧洞见系统已归档，请使用新命令："
        echo "  ./run.sh fuzzy      - 查看模糊层"
        echo "  ./run.sh precise    - 精确检索"
        echo "  ./run.sh ripple     - 添加涟漪"
        ;;
    "collide")
        echo "⚠️ 碰撞引擎已归档，请使用涟漪共振："
        echo "  ./run.sh resonances - 查看共振"
        echo "  ./run.sh ripple     - 添加涟漪（自动检测共振）"
        ;;
    "auto-drive")
        echo "⚠️ AI 自我驱动已归档，请使用涟漪系统"
        ;;
    "auto-drive-dry")
        echo "⚠️ AI 自我驱动已归档"
        ;;
    "workflow-learn")
        echo "📚 运行工作流学习..."
        python3 "$INSIGHTS_DIR/core/workflow_learner.py"
        ;;
    "heartbeat")
        echo "⚠️ 心跳任务已归档，请使用定时任务运行 ./run.sh fuzzy"
        ;;
    "optimize")
        echo "⚠️ 优化任务已归档，请使用 ./run.sh fuzzy"
        ;;
    "multimodal")
        echo "⚠️ 多模态收集已归档"
        ;;
    "search")
        if [ -z "$2" ]; then
            echo "❌ 请提供搜索关键词"
            echo "用法: ./run.sh search <关键词>"
            exit 1
        fi
        echo "🔍 搜索涟漪: $2"
        python3 -c "
from core.three_layer_memory import get_three_layer_memory
memory = get_three_layer_memory()
results = memory.search('$2')
if results:
    for r in results:
        print(f'[{r.temperature}°] {r.content}')
        print(f'   标签: {r.tags}')
        print()
else:
    print('未找到相关涟漪')
"
        ;;
    "compat-check")
        echo "✅ 系统已简化，无需兼容性检查"
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
