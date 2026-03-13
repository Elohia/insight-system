# 洞见系统 (Insight System)

统一的洞见生成与管理系统，融合了神经元洞见和碰撞引擎两种核心机制。

## 描述

洞见系统是一个信息炼金术平台，通过神经元式洞见生成和碎片碰撞两种机制，从碎片化信息中提取深度洞察。支持多数据源、多模态记忆和主动追问。

## 功能特性

### 🧠 核心能力

- **神经元洞见引擎**: 自动从记忆碎片中提取洞见
- **碰撞引擎**: 强制不相关碎片"对话"，产生意外洞见
- **追问引擎**: 系统主动提问，引发深度反思
- **变异模式**: 低概率(5%)生成假设片段验证
- **多模态支持**: 文本、图片、视频向量化存储
- **闭环自动化**: 自动收集、生成、优化洞见

### 📊 多数据源

- 飞书消息
- 任务记录
- 文件变化
- 手动输入/对话

### 🎨 双模式存储

- **JSON 向量数据库**: 用于快速检索和多模态记忆
- **SQLite 数据库**: 用于深度反思和碰撞引擎

## 安装位置

```
/workspace/projects/extensions/insight-system/
├── core/                      # 核心洞见系统
│   └── insight_system.py      # 神经元洞见引擎
├── collider/                  # 碰撞引擎（原 second-brain）
│   ├── collider.py            # 碰撞引擎
│   ├── questioner.py          # 追问引擎
│   ├── runner.py              # 主运行器
│   ├── memories.db            # SQLite 数据库
│   └── .env                   # 环境变量配置
├── storage/                   # 存储模块
│   └── multimodal_memory.py   # 多模态记忆存储
├── collectors/                # 收集器
│   └── multimodal_collect.py  # 多模态收集器
├── utils/                     # 工具模块
│   ├── message_queue.py       # 消息队列
│   ├── search.py              # 记忆搜索
│   └── status.py              # 状态查询
└── run.sh                     # 统一入口脚本
```

## 使用方法

### 命令行调用

```bash
# 进入洞见系统目录
cd /workspace/projects/extensions/insight-system

# 运行神经元洞见系统
./run.sh insight

# 运行碰撞引擎
./run.sh collide

# 运行心跳任务（每小时）
./run.sh heartbeat

# 运行优化任务（每3小时，含反思）
./run.sh optimize

# 运行多模态记忆收集
./run.sh multimodal

# 搜索记忆
./run.sh search "关键词"

# 显示系统状态
./run.sh status
```

### Python 模块调用

```python
# 神经元洞见引擎
from core.insight_system import NeuronInsight
insight = NeuronInsight()
insight.add_fragment("这是一条测试消息", source="user")
insight.process()
insight.save_state()

# 碰撞引擎
import sys
sys.path.insert(0, 'collider')
from runner import run_collide
run_collide()
```

## 核心机制

### 1. 神经元洞见引擎

自动从记忆碎片中提取洞见，支持多模态和向量化：

- 自动收集记忆碎片
- 计算相似度建立连接
- 生成洞见并存储到向量数据库
- 支持文本、图片、视频

### 2. 碰撞引擎

让碎片碰撞产生化学反应：

- 随机选择不相关的碎片
- 通过 AI 生成新的洞见
- 积累 10+ 碎片时触发追问引擎
- 5% 概率触发变异模式

### 3. 追问引擎

系统主动提问，引发深度反思：

- 基于碎片生成反思性问题
- 帮助用户深入思考
- 引导新的洞见产生

### 4. 变异模式

探索潜在可能性：

- 生成假设性片段
- 通过 AI 验证合理性
- 发现隐藏的连接

## 配置说明

### 环境变量

在 `collider/.env` 中配置：

```env
ZHIPU_API_KEY=your_api_key_here
```

### 获取 API Key

| 服务商 | 环境变量 | 获取地址 |
|--------|----------|----------|
| 智谱 GLM-4-Flash | ZHIPU_API_KEY | https://open.bigmodel.cn |
| 阿里云通义千问 | DASHSCOPE_API_KEY | https://dashscope.console.aliyun.com |

### 系统配置

在 `core/insight_system.py` 中配置：

```python
CONFIG = {
    "threshold": 0.7,              # 洞见相似度阈值
    "max_tokens_per_summary": 200, # 每个摘要最大 token 数
    "forget_days": 30,             # 记忆遗忘周期（天）
    "cache_size": 50,              # 缓存大小
}
```

## 数据存储

所有数据存储在 `workspace/.openclaw/` 目录下：

- `insight-state.json` - 洞见系统状态
- `vector-db.json` - 向量数据库
- `message-queue.json` - 消息队列

碰撞引擎数据存储在 `collider/memories.db`：

- 碎片（Fragments）
- 洞见（Insights）
- 问题（Questions）

## 定时任务

推荐配置 cron 任务：

```cron
# 每小时运行心跳任务
0 * * * * /workspace/projects/extensions/insight-system/run.sh heartbeat

# 每3小时运行优化任务
0 */3 * * * /workspace/projects/extensions/insight-system/run.sh optimize

# 每天3点运行碰撞引擎
0 3 * * * /workspace/projects/extensions/insight-system/run.sh collide
```

## 两种模式的区别

| 特性 | 神经元洞见 | 碰撞引擎 |
|------|-----------|---------|
| 数据源 | 自动收集 | 手动输入/对话 |
| 存储方式 | JSON 向量数据库 | SQLite |
| 多模态 | ✅ | ❌ |
| 向量化 | ✅ | ❌ |
| 追问引擎 | ❌ | ✅ |
| 变异模式 | ❌ | ✅ |
| 适用场景 | 自动洞察 | 深度反思 |

**两种模式互补，建议定期运行碰撞引擎进行深度反思！**

## 版本

v2.0 - 2024-03

## 作者

OpenClaw Team

## 项目主页

https://github.com/Elohia/second-brain

## 致谢

洞见系统脱胎于 Second Brain 项目，融合了神经元洞见引擎，成为统一的信息炼金术平台。
