---
name: insight-inject
description: "在 AI 运行前自动注入相关洞见到上下文中"
metadata:
  openclaw:
    emoji: "🧠"
    events:
      - "agent:start"
      - "command:new"
---

# Insight Inject Hook

洞见系统 Hook - 在 AI 运行前自动注入相关洞见到上下文中

## 功能

- 模糊层注入：启动时加载洞见摘要
- 精确层按需加载：根据查询动态加载相关记忆
- 深度层支持：访问完整对话历史

## 触发事件

- `agent:start` - Agent 启动时
- `command:new` - 新建会话时
