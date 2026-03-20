---
name: insight-system
description: "涟漪意识流 ContextEngine - 三层记忆架构：模糊层（启动加载 ~250 tokens）+ 精确层（按需检索）+ 深度层（完整数据）。涟漪（显意识）+ 潜意识 = 完整意识流。"
homepage: https://github.com/Elohia/insight-system
metadata: { "openclaw": { "emoji": "🌊", "kind": "context-engine" } }
---

# 涟漪意识流 ContextEngine

> 弱模型 + 强工具链 + 工具思维 > 单一大模型

## 一键配置

在 `openclaw.json` 中添加：

```json
{
  "plugins": {
    "slots": {
      "contextEngine": "insight-system"
    }
  },
  "pluginsDir": ["./extensions"]
}
```

## 三层记忆架构

| 层级 | 触发时机 | 内容 | Token |
|------|---------|------|-------|
| 🌫️ 模糊层 | 启动加载 | 水面状态 + 热门标签 + 最近涟漪 + 反向提示 | **~250** |
| 🎯 精确层 | 按需检索 | 相关涟漪详情 + 共振分析 | 按需 |
| 📚 深度层 | 深度分析 | 完整涟漪池 + 潜意识快照 | 按需 |

## 七个钩子

| 钩子 | 时机 | 功能 |
|------|------|------|
| `bootstrap()` | 引擎初始化 | 加载涟漪数据、获取水面状态 |
| `ingest(message)` | 消息摄入 | 记录每条消息 |
| `assemble(budget)` | 组装上下文 | 注入模糊层 + 选择历史消息 |
| `compact()` | 压缩上下文 | 保留 30% + 自动收集涟漪 |
| `afterTurn(turn)` | 对话结束 | 自动收集高价值对话 |
| `prepareSubagentSpawn()` | 子 agent 准备 | 精确检索相关涟漪 |
| `onSubagentEnded()` | 子 agent 结束 | 收集重要结果 |

## 配置选项

```json
{
  "fuzzyLayerTokens": 300,
  "maxRipplesInContext": 5,
  "autoCollectMinTemp": 60,
  "resonanceThreshold": 15
}
```

## 核心概念

| 概念 | 说明 |
|------|------|
| 🌊 涟漪 | 水面上的波动（显意识），带水温、标签 |
| 🧠 潜意识 | 静默记录水面状态 |
| ⚡ 共振 | 涟漪叠加产生洞察（温度±15 + 标签重叠） |

## 命令行工具

```bash
# 添加涟漪
./run.sh ripple "发现AI的连续性是幻觉" --temp 65 --tags AI,意识

# 查看模糊层
./run.sh fuzzy

# 精确检索
./run.sh precise AI

# 系统状态
./run.sh status
```

## 核心理念

> **模糊而精准**
> - 启动时只加载模糊层，极简概要
> - 按需加载精确层，精准检索
> - 深度层用于复盘和分析
