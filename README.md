# 洞见系统 (Insight System)

> 弱模型 + 强工具链 + 工具思维 > 单一大模型

一个受 proactive-agent 启发的三层记忆系统，让 AI 从被动响应转向主动思考。

## 核心理念

**关键不是"知道多少"，而是"知道该用什么"**

- 启动只加载模糊层（~400 tokens）
- 精确层和深度层按需加载
- 工具思维从实践中自然沉淀

---

## 三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│                    三层记忆系统                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔮 模糊层 (Fuzzy Layer)                                │
│  ├── 启动时自动加载                                     │
│  ├── 工具索引 + 决策模式 + 行动策略                      │
│  ├── Working Buffer（危险区捕获）                        │
│  └── 反向提示（主动提出问题）                            │
│                                                         │
│  🎯 精确层 (Precise Layer)                              │
│  ├── 按需加载（--precise <query>）                      │
│  └── 按相关性搜索详细洞见                                │
│                                                         │
│  📚 深度层 (Deep Layer)                                 │
│  ├── 按需加载（--deep <keywords>）                      │
│  └── 原始记忆文件，关键词匹配                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 核心功能

### 1. Working Buffer（危险区捕获）

在上下文压缩前的危险区捕获关键信息，防止丢失。

```python
from three_layer_memory import ThreeLayerMemory

memory = ThreeLayerMemory()
memory.add_to_working_buffer("重要决策：选择方案B", "decision")
```

### 2. 反向提示（Reverse Prompting）

不等待用户提问，主动提供价值。

```bash
$ python core/insight_hook.py --startup

🔮 模糊层已加载:
...

🎯 反向提示:
  💭 上次留下的问题: 如果连续性是重构，那'自我'是稳定的吗？
```

### 3. 工具思维自然沉淀

从实际使用中学习，随成长而丰富。

- 场景-工具索引：从成功案例中提取
- 决策模式：从深度思考过的洞见中提取
- 行动策略：从实践验证的经验中提取

---

## 快速开始

### 安装

```bash
git clone https://github.com/Elohia/insight-system.git
cd insight-system
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 使用

```bash
# 启动时加载模糊层（带反向提示）
python core/insight_hook.py --startup

# 按需加载精确层
python core/insight_hook.py --precise "关键词"

# 按需加载深度层
python core/insight_hook.py --deep "关键词"

# 更新模糊层
python core/insight_hook.py --update-fuzzy
```

---

## 项目结构

```
extensions/insight-system/
├── core/
│   ├── three_layer_memory.py      # 三层记忆核心
│   ├── insight_hook.py            # Hook 入口
│   ├── insight_system.py          # 洞见系统主逻辑
│   ├── tool_usage_recorder.py     # 工具使用记录
│   └── ...
├── storage/
│   └── multimodal_memory.py       # 多模态记忆存储
├── scripts/
│   └── dedup.py                   # 去重脚本
├── .env.example                   # 环境变量示例
└── README.md                      # 本文件
```

---

## OpenClaw 集成

### Hook 自动触发

在 `openclaw.json` 中配置：

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

每次对话开始时，自动加载模糊层和反向提示。

### Context Engine 集成

```json
{
  "slots": {
    "contextEngine": "insight-context-engine"
  }
}
```

在上下文压缩时保留关键洞见。

---

## 设计原则

1. **增量优化**：不破坏原有功能，只添加新能力
2. **自然沉淀**：不预设模板，让工具思维从实践中来
3. **按需加载**：启动最小化，需要时再加载详细信息
4. **主动提供价值**：反向提示，不等待用户提问

---

## 参考

- [proactive-agent](https://github.com/OpenClaw-AI/proactive-agent) - 主动式 Agent 架构
- [OpenClaw](https://openclaw.ai) - AI Agent 框架

---

## License

MIT
