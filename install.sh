#!/bin/bash
# insight-system 一键安装脚本
# 完全取代 OpenClaw 内置记忆功能

set -e

echo "🌊 涟漪意识流 ContextEngine 安装脚本"
echo "======================================"

# 配置
INSIGHT_PATH="${INSIGHT_PATH:-/workspace/projects/extensions/insight-system}"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-/workspace/projects/openclaw.json}"

# 1. 检查 OpenClaw
echo ""
echo "→ 检查 OpenClaw..."
if ! command -v openclaw &> /dev/null; then
    echo "❌ 未找到 openclaw 命令，请先安装 OpenClaw"
    exit 1
fi
echo "✓ OpenClaw 已安装: $(openclaw --version 2>&1 | head -1)"

# 2. 下载插件
echo ""
echo "→ 下载 insight-system..."
if [ -d "$INSIGHT_PATH" ]; then
    echo "✓ 目录已存在: $INSIGHT_PATH"
    cd "$INSIGHT_PATH"
    git pull origin main 2>/dev/null || true
else
    mkdir -p "$(dirname $INSIGHT_PATH)"
    git clone https://github.com/Elohia/insight-system.git "$INSIGHT_PATH"
    echo "✓ 已克隆到: $INSIGHT_PATH"
fi

# 3. 检查配置文件
echo ""
echo "→ 配置 OpenClaw..."
if [ ! -f "$OPENCLAW_CONFIG" ]; then
    echo "❌ 未找到配置文件: $OPENCLAW_CONFIG"
    echo "   请设置环境变量 OPENCLAW_CONFIG 指向正确的配置文件"
    exit 1
fi

# 4. 备份配置
cp "$OPENCLAW_CONFIG" "${OPENCLAW_CONFIG}.bak.$(date +%Y%m%d%H%M%S)"
echo "✓ 已备份配置文件"

# 5. 应用配置
echo ""
echo "→ 应用配置..."

# 禁用 memoryFlush
openclaw config set agents.defaults.compaction.memoryFlush.enabled false 2>/dev/null || true

# 添加插件路径
openclaw config set plugins.load.paths.0 "$INSIGHT_PATH" 2>/dev/null || true

# 添加到 allow 列表
openclaw config set plugins.allow.3 "insight-system" 2>/dev/null || true

# 设置 slots
openclaw config set plugins.slots.memory "none" 2>/dev/null || true
openclaw config set plugins.slots.contextEngine "insight-system" 2>/dev/null || true

# 设置环境变量
openclaw config set env.INSIGHT_SYSTEM_PATH "$INSIGHT_PATH" 2>/dev/null || true
openclaw config set env.FUZZY_BUDGET "250" 2>/dev/null || true
openclaw config set env.AUTO_COLLECT_MIN_TEMP "60" 2>/dev/null || true

echo "✓ 配置已应用"

# 6. 清理旧记忆文件
echo ""
echo "→ 清理 OpenClaw 旧记忆文件..."
WORKSPACE="${WORKSPACE:-/workspace/projects/workspace}"
if [ -d "$WORKSPACE/memory" ] || [ -f "$WORKSPACE/MEMORY.md" ]; then
    BACKUP_DIR="/tmp/openclaw-memory-backup-$(date +%Y%m%d%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    [ -d "$WORKSPACE/memory" ] && mv "$WORKSPACE/memory" "$BACKUP_DIR/"
    [ -f "$WORKSPACE/MEMORY.md" ] && mv "$WORKSPACE/MEMORY.md" "$BACKUP_DIR/"
    echo "✓ 已备份旧记忆到: $BACKUP_DIR"
else
    echo "✓ 无需清理"
fi

# 7. 验证
echo ""
echo "→ 验证配置..."
if openclaw config validate 2>&1 | grep -q "Config valid"; then
    echo "✓ 配置验证通过"
else
    echo "⚠ 配置验证失败，请检查 openclaw.json"
fi

# 8. 测试插件
echo ""
echo "→ 测试插件..."
cd "$INSIGHT_PATH"
chmod +x run.sh

if ./run.sh status 2>/dev/null; then
    echo "✓ 插件运行正常"
else
    echo "⚠ 插件测试失败，请检查 Python 环境"
fi

# 9. 完成
echo ""
echo "======================================"
echo "✅ 安装完成！"
echo ""
echo "⚠️  旧记忆文件已备份到 /tmp/openclaw-memory-backup-*"
echo ""
echo "重启 OpenClaw 生效："
echo "  ./scripts/restart.sh"
echo ""
echo "验证安装："
echo "  openclaw plugins list | grep insight"
echo ""
echo "添加记忆："
echo "  cd $INSIGHT_PATH && ./run.sh ripple '测试记忆' --temp 70 --tags 测试"
echo ""
