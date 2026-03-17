#!/bin/bash
#
# 洞见系统一键部署脚本
# 自动完成环境检查、配置、初始化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSIGHT_DIR="$SCRIPT_DIR"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  洞见系统一键部署脚本${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 步骤 1：检查 Python
echo -e "${YELLOW}[1/6] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3 未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"

# 步骤 2：检查 pip
echo -e "${YELLOW}[2/6] 检查 pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误: pip3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 已安装${NC}"

# 步骤 3：安装依赖
echo -e "${YELLOW}[3/6] 安装依赖...${NC}"
cd "$INSIGHT_DIR"

# 检查 requirements.txt
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt
    echo -e "${GREEN}✓ 依赖已安装${NC}"
else
    echo -e "${YELLOW}⚠ 未找到 requirements.txt，跳过依赖安装${NC}"
fi

# 步骤 4：配置环境变量
echo -e "${YELLOW}[4/6] 配置环境变量...${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
else
    echo -e "${YELLOW}创建 .env 文件...${NC}"
    
    # 复制模板
    cp .env.example .env
    
    # 引导用户输入
    echo ""
    echo "请配置 API Key（至少需要一个）："
    echo ""
    
    read -p "智谱 AI API Key (可选，回车跳过): " ZHIPU_KEY
    if [ -n "$ZHIPU_KEY" ]; then
        sed -i "s|ZHIPU_API_KEY=.*|ZHIPU_API_KEY=$ZHIPU_KEY|" .env
    fi
    
    read -p "阿里云通义千问 API Key (可选，回车跳过): " DASHSCOPE_KEY
    if [ -n "$DASHSCOPE_KEY" ]; then
        sed -i "s|DASHSCOPE_API_KEY=.*|DASHSCOPE_API_KEY=$DASHSCOPE_KEY|" .env
    fi
    
    echo -e "${GREEN}✓ .env 文件已创建${NC}"
fi

# 步骤 5：初始化洞见状态
echo -e "${YELLOW}[5/6] 初始化洞见状态...${NC}"

# 创建必要目录
mkdir -p "$INSIGHT_DIR/../workspace/.openclaw"
mkdir -p "$INSIGHT_DIR/../workspace/memory"

# 初始化状态文件（如果不存在）
STATE_FILE="$INSIGHT_DIR/../workspace/.openclaw/insight-state.json"
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'EOF'
{
  "last_processed": null,
  "processed_hashes": [],
  "insights": [],
  "connections": {},
  "run_count": 0,
  "last_message_time": null
}
EOF
    echo -e "${GREEN}✓ 洞见状态已初始化${NC}"
else
    echo -e "${GREEN}✓ 洞见状态已存在${NC}"
fi

# 步骤 6：生成模糊层
echo -e "${YELLOW}[6/6] 生成模糊层...${NC}"
cd "$INSIGHT_DIR"

if python3 core/insight_hook.py --update-fuzzy 2>/dev/null; then
    echo -e "${GREEN}✓ 模糊层已生成${NC}"
else
    echo -e "${YELLOW}⚠ 模糊层生成失败，可能需要配置 API Key${NC}"
    echo "   编辑 .env 文件后手动运行: python core/insight_hook.py --update-fuzzy"
fi

# 完成
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "下一步："
echo ""
echo "1. 激活 OpenClaw Hook:"
echo "   在 openclaw.json 中添加:"
echo '   {'
echo '     "hooks": {'
echo '       "internal": {'
echo '         "enabled": true,'
echo '         "entries": {'
echo '           "insight-inject": { "enabled": true }'
echo '         }'
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "2. 重启 OpenClaw:"
echo "   openclaw gateway restart"
echo ""
echo "3. 验证激活:"
echo "   python core/insight_hook.py --startup"
echo ""
