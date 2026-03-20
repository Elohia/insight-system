# 涟漪意识流 ContextEngine v2.3.0

## 快速开始

### 1. 配置 OpenClaw

在 `openclaw.json` 中添加：

```json
{
  "plugins": {
    "slots": {
      "contextEngine": "insight-system"
    }
  },
  "env": {
    "INSIGHT_SYSTEM_PATH": "/workspace/projects/extensions/insight-system",
    "FUZZY_BUDGET": "250",
    "AUTO_COLLECT_MIN_TEMP": "60"
  }
}
```

### 2. 使用命令

```bash
cd extensions/insight-system

# 添加涟漪
./run.sh ripple "洞见内容" --temp 75 --tags 洞见,创新

# 查看模糊层
./run.sh fuzzy

# 精确检索
./run.sh precise 关键词

# 系统状态
./run.sh status
```

## 三层记忆架构

| 层级 | Token | 用途 | 加载时机 |
|------|-------|------|----------|
| 模糊层 | ~250 | 极简概要 | 启动加载 |
| 精确层 | 按需 | 条件检索 | 运行时检索 |
| 深度层 | 完整 | 数据导出 | 手动导出 |

## 核心概念

- **涟漪 (Ripple)**: 显意识片段，带温度(0-100)、标签
- **潜意识 (Subconscious)**: 水面状态快照
- **共振**: 涟漪叠加，条件：温度±15 + 标签重叠 + 时间24h

## TOON 格式

相比 JSON 减少 ~67% token：

```
# JSON 格式 (约 150 tokens)
{"content":"洞见内容","temp":75,"tags":["洞见","创新"],"timestamp":1774011073}

# TOON 格式 (约 50 tokens)
75|1774011073|洞见,创新|洞见内容
```

## 文件结构

```
insight-system/
├── core/
│   ├── ripple.py          # 涟漪模型
│   ├── subconscious.py    # 潜意识模型
│   └── three_layer_memory.py  # 三层记忆管理
├── utils/
│   ├── toon_format.py     # TOON 格式工具
│   └── config_loader.py   # 配置加载器
├── index.js               # ContextEngine 入口
├── openclaw.plugin.json   # 插件配置
├── run.sh                 # 命令行工具
└── README.md              # 说明文档
```

## 环境变量

所有配置统一在 `openclaw.json` 的 `env` 字段：

- `INSIGHT_SYSTEM_PATH`: 数据目录路径
- `FUZZY_BUDGET`: 模糊层 token 预算
- `AUTO_COLLECT_MIN_TEMP`: 自动收集最低温度
- `RESONANCE_TEMP_THRESHOLD`: 共振温度阈值
- `RESONANCE_TIME_THRESHOLD`: 共振时间阈值

## ContextEngine 七个钩子

1. `bootstrap()` - 初始化
2. `ingest(message)` - 消息摄入
3. `assemble(budget)` - 组装上下文
4. `compact()` - 压缩记忆
5. `afterTurn(turn)` - 轮次后处理
6. `prepareSubagentSpawn(parentContext)` - 子代理准备
7. `onSubagentEnded(result)` - 子代理结束

## 迁移指南

只需复制 `insight-system/` 目录到新环境，更新 `openclaw.json` 的 `env.INSIGHT_SYSTEM_PATH` 即可。
