# Insight System Hook

洞见系统 Hook - 在 AI 运行前自动注入相关洞见到上下文中

## 功能

- 模糊层注入：启动时加载洞见摘要
- 精确层按需加载：根据查询动态加载相关记忆
- 深度层支持：访问完整对话历史

## 配置

在 openclaw.json 中启用：

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

## 验证

```bash
python /home/elohia/insight-system/core/insight_hook.py --startup
```
