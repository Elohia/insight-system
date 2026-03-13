---
name: insight-system
description: "统一的洞见生成与管理系统。融合神经元洞见和碰撞引擎两种核心机制，支持多模态记忆、主动追问和碎片碰撞。使用方式：用户提到'洞见'、'记忆系统'、'碎片'、'碰撞'、'追问'、'思考'时使用。需要配置 ZHIPU_API_KEY 环境变量。"
homepage: https://github.com/Elohia/second-brain
metadata: { "openclaw": { "emoji": "🧠", "requires": { "env": ["ZHIPU_API_KEY"], "bins": ["python3"] } } }
---

# 洞见系统 (Insight System)

统一的洞见生成与管理系统，融合神经元洞见和碰撞引擎。

## 触发关键词

- "洞见"
- "记忆系统"
- "碎片"
- "碰撞"
- "追问"
- "思考"
- "运行洞见系统"
- "神经元"

## 当触发时

执行以下命令：

```bash
# 运行神经元洞见系统
cd /workspace/projects/extensions/insight-system && ./run.sh insight

# 运行碰撞引擎
cd /workspace/projects/extensions/insight-system && ./run.sh collide

# 查看状态
cd /workspace/projects/extensions/insight-system && ./run.sh status
```

## 核心功能

| 引擎 | 功能 | 触发条件 |
|------|------|----------|
| 🧠 神经元洞见 | 自动从记忆碎片中提取洞见 | 每次运行 |
| ⚡ 碰撞引擎 | 强制不相关碎片"对话"，产生意外洞见 | 每次运行 |
| ❓ 追问引擎 | 系统主动提问，引发深度反思 | 积累 10+ 碎片 |
| 🧬 变异模式 | 低概率(5%)生成假设片段验证 | 5% 概率 |

## 使用方式

### 1. 神经元洞见模式（自动洞察）

```bash
cd /workspace/projects/extensions/insight-system
./run.sh insight
```

特点：
- 自动收集记忆碎片
- 支持多模态（文本、图片、视频）
- 向量化存储
- 快速检索

### 2. 碰撞引擎模式（深度反思）

```bash
cd /workspace/projects/extensions/insight-system
./run.sh collide
```

特点：
- 碎片碰撞产生洞见
- 主动追问引发思考
- 变异模式探索可能

## 配置

在 `collider/.env` 中设置智谱 API Key：

```bash
export ZHIPU_API_KEY="your-key"
```

获取地址：https://open.bigmodel.cn

## 口号

> 不做更好的搜索引擎，要做"信息炼金术"
