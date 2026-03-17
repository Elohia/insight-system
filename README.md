# 洞见系统 (Insight System)

> 弱模型 + 强工具链 + 工具思维 > 单一大模型

**一键部署、自动激活的三层记忆系统**

---

## 新增功能：动态配置系统 (v2.2)

洞见系统现在支持通过配置文件动态管理所有路径和参数，**不再依赖硬编码路径**，方便迁移到不同环境。

### 配置文件

配置文件位于 `config.json`：

```json
{
  "_comment": "洞见系统配置文件 - 修改此文件以适应你的环境",
  
  "version": "2.2",
  
  "paths": {
    "_comment": "路径配置 - 修改为实际路径",
    "workspace": "/workspace/projects/workspace",
    "memory_dir": "{workspace}/memory",
    "state_file": "{workspace}/.openclaw/insight-state.json",
    "vector_db": "{workspace}/.openclaw/vector-db.json",
    "fuzzy_layer": "{workspace}/.openclaw/memory-fuzzy-layer.json",
    "message_queue": "{workspace}/.openclaw/message-queue.json",
    "tool_usage": "{workspace}/.openclaw/tool-usage-records.json"
  },
  
  "fuzzy_layer": {
    "_comment": "模糊层配置",
    "max_insights": 15,
    "max_tokens": 800,
    "update_interval_hours": 6,
    "working_buffer_size": 5
  },
  
  "precise_layer": {
    "_comment": "精确层配置",
    "max_insights": 50,
    "search_top_k": 10
  },
  
  "deep_layer": {
    "_comment": "深度层配置",
    "max_days": 7,
    "max_entries": 100
  },
  
  "multimodal": {
    "_comment": "多模态记忆配置",
    "model": "qwen3-vl-embedding",
    "dimension": 1024,
    "free_limit": 1000000
  },
  
  "insight": {
    "_comment": "洞见提取配置",
    "threshold": 0.7,
    "max_tokens_per_summary": 200,
    "forget_days": 30,
    "cache_size": 50
  }
}
```

### 路径占位符

配置文件支持使用 `{workspace}` 占位符，它会被自动替换为 `paths.workspace` 的值：

```json
{
  "paths": {
    "workspace": "/your/custom/workspace",
    "memory_dir": "{workspace}/memory"  // 自动展开为 /your/custom/workspace/memory
  }
}
```

### 迁移到新环境

只需修改 `config.json` 中的 `paths.workspace`：

```bash
# 1. 复制洞见系统到新位置
cp -r insight-system /new/location/

# 2. 编辑配置文件
nano config.json

# 3. 修改 workspace 路径
{
  "paths": {
    "workspace": "/your/new/workspace/path"
  }
}

# 4. 完成！系统会自动使用新路径
```

---

## 一键部署

```bash
# 1. 克隆并进入目录
git clone https://github.com/Elohia/insight-system.git
cd insight-system

# 2. 运行部署脚本
./deploy.sh
```

部署脚本会自动：
- 检查 Python 环境
- 安装依赖
- 配置环境变量（引导输入）
- 初始化洞见状态
- 生成模糊层
- 配置 OpenClaw Hook

---

## 手动部署（如果一键失败）

### 步骤 1：基础配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入 API Key（至少填一个）
nano .env
```

**.env 配置示例：**
```bash
# 智谱 AI（推荐，免费额度充足）
ZHIPU_API_KEY=your_zhipu_api_key_here

# 阿里云通义千问（可选，用于多模态）
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

获取 API Key：
- 智谱：https://open.bigmodel.cn
- 阿里云：https://dashscope.console.aliyun.com

### 步骤 2：配置路径（重要）

编辑 `config.json`，修改路径为你的实际工作目录：

```json
{
  "paths": {
    "workspace": "/your/actual/workspace"
  }
}
```

### 步骤 3：初始化洞见系统

```bash
cd /path/to/insight-system

# 生成模糊层
python core/insight_hook.py --update-fuzzy
```

### 步骤 4：激活 OpenClaw Hook

在 OpenClaw 的 `openclaw.json` 中添加：

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "insight-inject": {
          "enabled": true
        }
      }
    }
  }
}
```

重启 OpenClaw：
```bash
openclaw gateway restart
```

---

## 验证激活

### 方法 1：检查 Hook 状态

```bash
openclaw hooks list
```

应看到：
```
✓ ready  │ 🧠 insight-inject    │ 在 AI 运行前自动注入相关洞见到上下文中
```

### 方法 2：测试模糊层

```bash
python core/insight_hook.py --startup
```

应输出模糊层内容 + 反向提示。

### 方法 3：实际对话测试

开始新对话，检查是否自动加载洞见上下文。

---

## 核心功能

### 🔮 三层记忆

| 层级 | 触发时机 | 内容 | Token |
|------|---------|------|-------|
| 模糊层 | 每次启动 | 工具索引 + 决策模式 + 反向提示 | ~400 |
| 精确层 | 按需 `--precise` | 相关洞见详细内容 | 按需 |
| 深度层 | 按需 `--deep` | 原始记忆文件 | 按需 |

### 🛠️ 工具思维自动沉淀

系统自动从以下场景学习：
- 成功解决问题的案例 → 场景-工具索引
- 深度思考的洞见 → 决策模式
- 实践验证的经验 → 行动策略

### 📝 Working Buffer

在上下文压缩前捕获关键信息，防止丢失。

### 🎯 反向提示

主动提出未回答的问题，而非被动等待。

---

## 日常使用

### 自动运行（推荐）

配置定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务
# 每小时更新模糊层
0 * * * * cd /path/to/insight-system && python core/insight_hook.py --update-fuzzy >/dev/null 2>&1
```

### 手动命令

```bash
# 启动加载（带反向提示）
python core/insight_hook.py --startup

# 精确查询
python core/insight_hook.py --precise "关键词"

# 深度查询
python core/insight_hook.py --deep "关键词"

# 更新模糊层
python core/insight_hook.py --update-fuzzy

# 数据去重
python scripts/dedup.py

# 检查系统状态
python utils/status.py

# 搜索记忆
python utils/search.py "关键词"
```

---

## 开发者接口

### 配置加载模块

所有模块通过 `utils/config_loader.py` 加载配置：

```python
from utils.config_loader import get_config

# 获取配置实例
config = get_config()

# 获取路径
workspace = config.workspace  # Path 对象
memory_dir = config.memory_dir
state_file = config.state_file

# 获取任意配置值
threshold = config.get("insight.threshold", 0.7)
max_insights = config.get("fuzzy_layer.max_insights", 15)

# 重新加载配置（运行时热更新）
config.reload()
```

### 向后兼容函数

```python
from utils.config_loader import get_workspace, get_memory_dir, get_state_file

# 这些函数返回字符串路径，兼容旧代码
workspace = get_workspace()
memory_dir = get_memory_dir()
state_file = get_state_file()
```

---

## 故障排查

### 问题：配置文件不存在

```bash
# 系统会自动使用默认配置
# 如需自定义，创建 config.json 文件
cp config.example.json config.json
```

### 问题：路径错误

```bash
# 检查配置文件路径
cat config.json | grep workspace

# 验证路径是否存在
ls -la $(python -c "from utils.config_loader import get_workspace; print(get_workspace())")
```

### 问题：Hook 显示未就绪

```bash
# 检查 Hook 日志
openclaw hooks logs insight-inject

# 手动测试
python core/insight_hook.py --startup
```

### 问题：模糊层为空

```bash
# 重新生成
python core/insight_hook.py --update-fuzzy
```

### 问题：API 错误

检查 `.env` 文件：
```bash
cat .env
# 确认 ZHIPU_API_KEY 或 DASHSCOPE_API_KEY 已设置
```

---

## 项目结构

```
insight-system/
├── config.json                    # 动态配置文件
├── utils/
│   ├── config_loader.py           # 配置加载模块（新增）
│   ├── message_queue.py           # 消息队列
│   ├── search.py                  # 搜索工具
│   └── status.py                  # 状态显示
├── core/
│   ├── three_layer_memory.py      # 三层记忆核心
│   ├── insight_hook.py            # Hook 入口
│   ├── insight_system.py          # 洞见系统主逻辑
│   ├── insight_extractor.py       # 洞见提取器
│   ├── growth_engine.py           # 生长引擎
│   └── tool_usage_recorder.py     # 工具使用记录
├── storage/
│   └── multimodal_memory.py       # 多模态记忆存储
├── scripts/
│   ├── dedup.py                   # 去重脚本
│   └── deploy.sh                  # 一键部署脚本
├── .env.example                   # 环境变量模板
└── README.md                      # 本文件
```

---

## 设计理念

1. **一键部署**：最小化配置，最大化自动化
2. **自动激活**：Hook 自动注入，无需手动干预
3. **自然沉淀**：工具思维从实践中学习，非预设
4. **按需加载**：启动最小化，需要时再加载
5. **配置驱动**：所有路径和参数可通过配置文件管理，方便迁移

---

## 更新日志

### v2.2 - 动态配置系统
- 新增 `config.json` 配置文件
- 新增 `utils/config_loader.py` 配置加载模块
- 所有模块移除硬编码路径，改为动态配置
- 支持路径占位符 `{workspace}`
- 支持配置热重载

### v2.1 - 三层记忆系统
- 引入模糊层/精确层/深度层架构
- 优化 Token 使用效率

### v2.0 - 初始版本
- 洞见提取器
- 工具思维沉淀
- OpenClaw Hook 集成

---

## 参考

- [OpenClaw](https://openclaw.ai) - AI Agent 框架
- [proactive-agent](https://github.com/OpenClaw-AI/proactive-agent) - 主动式 Agent 架构

---

## License

MIT
