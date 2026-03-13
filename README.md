# 洞见系统 (Insight System)

> 统一的洞见生成与管理系统 - 让碎片碰撞产生化学反应的信息炼金术平台

[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Extension-orange)](https://openclaw.ai)

## 简介

洞见系统融合了两种核心机制：
- **神经元洞见引擎**: 自动从记忆碎片中提取洞见，支持多模态记忆
- **碰撞引擎**: 强制不相关碎片"对话"，产生意外洞见和深度反思

通过这两种机制，系统能够：
- 自动收集和整理记忆碎片
- 发现碎片之间的隐藏连接
- 主动追问引发深度思考
- 探索潜在的可能性

## 核心功能

### 🧠 神经元洞见引擎
- 自动从记忆碎片中提取洞见
- 支持多模态（文本、图片、视频）
- 向量化存储，快速检索
- 多数据源接入（飞书、任务、文件）

### ⚡ 碰撞引擎
- 随机选择不相关碎片进行碰撞
- 通过 AI 生成新的洞见
- 积累 10+ 碎片时触发追问引擎
- 5% 概率触发变异模式

### ❓ 追问引擎
- 系统主动生成反思性问题
- 引导用户深入思考
- 帮助发现新的洞见

### 🧬 变异模式
- 生成假设性片段
- 通过 AI 验证合理性
- 探索隐藏的可能性

## 快速开始

### 1. 环境要求

- Python 3.8+
- 至少一个 AI 模型 API（推荐智谱 GLM-4-Flash）

### 2. 安装

```bash
# 克隆仓库
git clone https://github.com/Elohia/insight-system.git
cd insight-system

# 安装依赖
pip install -r requirements.txt  # 如果有
```

### 3. 配置环境变量

#### 方式一：创建 .env 文件（推荐）

在 `collider/` 目录下创建 `.env` 文件：

```bash
# 进入 collider 目录
cd collider

# 创建 .env 文件
cat > .env << 'EOF'
# 智谱 AI API Key（必填，用于碰撞引擎）
ZHIPU_API_KEY=your_zhipu_api_key_here

# 阿里云通义千问 API Key（可选，用于多模态记忆）
DASHSCOPE_API_KEY=your_dashscope_api_key_here
EOF
```

#### 方式二：使用环境变量

```bash
# 临时设置（当前会话有效）
export ZHIPU_API_KEY="your_zhipu_api_key_here"
export DASHSCOPE_API_KEY="your_dashscope_api_key_here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export ZHIPU_API_KEY="your_zhipu_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### 方式三：在代码中设置

```python
import os
os.environ['ZHIPU_API_KEY'] = 'your_zhipu_api_key_here'
```

### 4. 获取 API Key

| 服务商 | 环境变量 | 获取地址 | 免费额度 |
|--------|----------|----------|----------|
| 智谱 GLM-4-Flash | `ZHIPU_API_KEY` | https://open.bigmodel.cn | ✅ 充足 |
| 阿里云通义千问 | `DASHSCOPE_API_KEY` | https://dashscope.console.aliyun.com | ✅ 有 |
| MiniMax | `MINIMAX_API_KEY` | https://platform.minimax.io | ✅ 有 |
| Google Gemini | `GEMINI_API_KEY` | https://aistudio.google.com | ✅ 有 |

**推荐使用智谱 GLM-4-Flash**：免费额度充足，速度快，适合碰撞引擎使用。

## 使用方法

### 命令行

```bash
# 进入系统目录
cd insight-system

# 查看系统状态
./run.sh status

# 运行神经元洞见系统（自动洞察）
./run.sh insight

# 运行碰撞引擎（深度反思）
./run.sh collide

# 搜索记忆
./run.sh search "关键词"

# 运行心跳任务（每小时自动运行）
./run.sh heartbeat

# 运行优化任务（每3小时深度优化）
./run.sh optimize

# 查看帮助
./run.sh help
```

### Python 模块

#### 神经元洞见引擎

```python
from core.insight_system import NeuronInsight

# 创建实例
insight = NeuronInsight()

# 添加碎片
insight.add_fragment("今天学到了一个新概念：信息炼金术", source="user")

# 处理碎片
insight.process()

# 保存状态
insight.save_state()
```

#### 碰撞引擎

```python
import sys
sys.path.insert(0, 'collider')
from runner import main

# 运行碰撞
main()
```

## 项目结构

```
insight-system/
├── core/                      # 神经元洞见引擎
│   └── insight_system.py      # 核心洞见系统
├── collider/                  # 碰撞引擎
│   ├── collider.py            # 碰撞引擎
│   ├── questioner.py          # 追问引擎
│   ├── runner.py              # 主运行器
│   ├── client.py              # API 客户端
│   ├── collector.py           # 碎片收集器
│   ├── engine.py              # 核心引擎
│   ├── memories.db            # SQLite 数据库
│   └── .env                   # 环境变量配置（需创建）
├── storage/                   # 存储模块
│   └── multimodal_memory.py   # 多模态记忆
├── collectors/                # 收集器
│   └── multimodal_collect.py  # 多模态收集
├── utils/                     # 工具模块
│   ├── message_queue.py       # 消息队列
│   ├── search.py              # 记忆搜索
│   └── status.py              # 状态查询
├── run.sh                     # 统一入口脚本
├── PLUGIN.md                  # 扩展文档
├── SKILL.md                   # OpenClaw 技能配置
├── README.md                  # 本文件
└── .env.example               # 环境变量示例
```

## 两种模式对比

| 特性 | 神经元洞见 | 碰撞引擎 |
|------|-----------|---------|
| 数据源 | 自动收集 | 手动输入/对话 |
| 存储方式 | JSON 向量数据库 | SQLite |
| 多模态 | ✅ | ❌ |
| 向量化 | ✅ | ❌ |
| 追问引擎 | ❌ | ✅ |
| 变异模式 | ❌ | ✅ |
| 适用场景 | 自动洞察 | 深度反思 |
| 运行频率 | 高频（每小时） | 低频（每天） |

**建议**：定期运行碰撞引擎进行深度反思，同时让神经元洞见引擎自动运行。

## 定时任务配置

推荐配置 cron 任务实现自动化：

```cron
# 编辑 crontab
crontab -e

# 添加以下任务
# 每小时运行心跳任务
0 * * * * cd /path/to/insight-system && ./run.sh heartbeat

# 每3小时运行优化任务
0 */3 * * * cd /path/to/insight-system && ./run.sh optimize

# 每天3点运行碰撞引擎
0 3 * * * cd /path/to/insight-system && ./run.sh collide
```

## 数据存储

### 神经元洞见数据
存储在 OpenClaw workspace 的 `.openclaw/` 目录：
- `insight-state.json` - 洞见系统状态
- `vector-db.json` - 向量数据库
- `message-queue.json` - 消息队列

### 碰撞引擎数据
存储在 `collider/memories.db`：
- 碎片（Fragments）
- 洞见（Insights）
- 问题（Questions）

## 常见问题

### 1. 如何获取智谱 API Key？

1. 访问 https://open.bigmodel.cn
2. 注册/登录账号
3. 进入「API Keys」页面
4. 创建新的 API Key
5. 复制并保存到 `.env` 文件

### 2. 运行时提示 API Key 未找到？

检查 `.env` 文件：
- 确保文件位于 `collider/.env`
- 确保变量名正确（`ZHIPU_API_KEY`）
- 确保没有多余的引号或空格

### 3. 如何添加碎片？

**方式一：直接对话**
在 OpenClaw 中与机器人对话，系统会自动收集。

**方式二：手动添加**
```python
from core.insight_system import NeuronInsight
insight = NeuronInsight()
insight.add_fragment("你的碎片内容", source="manual")
insight.save_state()
```

### 4. 如何查看系统状态？

```bash
./run.sh status
```

输出示例：
```
📊 系统状态:
╔════════════════════════════════════╗
║      🧠 洞见系统状态              ║
╠════════════════════════════════════╣
║  总洞见数:     81                   ║
║  连接数:       7                    ║
║  运行次数:     95                   ║
╚════════════════════════════════════╝
```

## 开发计划

- [ ] Web UI 界面
- [ ] 更多 AI 模型支持
- [ ] 碎片导入/导出功能
- [ ] 协作功能
- [ ] 移动端支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

洞见系统脱胎于 Second Brain 项目，融合了神经元洞见引擎，成为统一的信息炼金术平台。

## 联系方式

- 项目主页：https://github.com/Elohia/insight-system
- Issues：https://github.com/Elohia/insight-system/issues

---

**口号**：不做更好的搜索引擎，要做"信息炼金术" 🔮
