# 涟漪意识流 ContextEngine

> OpenClaw 三层记忆插件 - 完全取代内置记忆功能

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/Elohia/insight-system)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.3.11-green.svg)](https://openclaw.ai)

---

## 一句话介绍

**完全取代 OpenClaw 内置记忆，提供三层记忆架构：模糊层（启动加载）、精确层（按需检索）、深度层（完整导出）**

---

## ⚡ 一键安装

```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/Elohia/insight-system/main/install.sh | bash

# 重启 OpenClaw
./scripts/restart.sh

# 验证安装
openclaw plugins list | grep insight
# 应该看到: insight-system | loaded
```

### 📦 自动迁移旧记忆

安装脚本会自动检测并迁移 OpenClaw 旧记忆：

```
workspace/memory/*.md  →  转换为涟漪  →  ripples.toon
workspace/MEMORY.md    →  转换为涟漪  →  ripples.toon
```

迁移时会：
- 解析 Markdown 标题和段落
- 自动估算温度（根据关键词）
- 自动提取标签
- 保留时间戳

> ⚠️ **注意**：旧文件迁移后会保留，可手动删除：
> ```bash
> rm -rf workspace/memory workspace/MEMORY.md
> ```

### 手动安装（如果脚本失败）

<details>
<summary>点击展开手动安装步骤</summary>

#### 1. 下载插件

```bash
cd /workspace/projects/extensions
git clone https://github.com/Elohia/insight-system.git
```

#### 2. 复制配置到 openclaw.json

在 `openclaw.json` 中添加：

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": false
        }
      }
    }
  },
  "plugins": {
    "load": {
      "paths": ["/workspace/projects/extensions/insight-system"]
    },
    "allow": ["insight-system"],
    "slots": {
      "memory": "none",
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

#### 3. 重启

```bash
./scripts/restart.sh
```

</details>

---

## 快速使用

```bash
cd /workspace/projects/extensions/insight-system

# 添加记忆
./run.sh ripple "发现 TOON 格式可节省 67% token" --temp 75 --tags 优化,TOON

# 查看模糊层（启动时自动加载的记忆）
./run.sh fuzzy

# 精确检索
./run.sh precise TOON
./run.sh precise 优化 --temp 70-80

# 系统状态
./run.sh status
```

---

## 与 OpenClaw 内置记忆的区别

| 功能 | OpenClaw 内置 | insight-system |
|------|--------------|----------------|
| 存储格式 | Markdown 文件 | TOON 格式（省 67% token） |
| 记忆层级 | 单层 | 三层（模糊/精确/深度） |
| 检索方式 | 向量搜索 | 标签+温度+时间 |
| 温度机制 | ❌ | ✅ 0-100 重要性评分 |
| 共振机制 | ❌ | ✅ 自动关联相关记忆 |
| token 计算 | 估算 | tiktoken 精确计算 |

---

## 配置说明

### 1. AGENTS.md 配置

更新 `workspace/AGENTS.md` 的 Every Session 部分：

```markdown
## Every Session

Before doing anything:
1. Read `SOUL.md` — who you are
2. Read `USER.md` — who you're helping
3. **模糊层自动加载** — insight-system ContextEngine 会自动注入记忆概要
```

完整示例见 [AGENTS.md 示例](https://github.com/Elohia/insight-system/blob/main/examples/AGENTS.md)。

### 2. 禁用内置记忆

```json
{
  "agents.defaults.compaction.memoryFlush.enabled": false,
  "plugins.slots.memory": "none"
}
```

这会禁用：
- `memory/YYYY-MM-DD.md` 自动写入
- `MEMORY.md` 长期记忆
- `memory-core` 和 `memory-lancedb` 插件

### 2. 启用 insight-system

```json
{
  "plugins.slots.contextEngine": "insight-system",
  "plugins.load.paths": ["/workspace/projects/extensions/insight-system"]
}
```

### 3. 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `INSIGHT_SYSTEM_PATH` | `/workspace/projects/extensions/insight-system` | 数据目录 |
| `FUZZY_BUDGET` | `250` | 模糊层 token 预算 |
| `AUTO_COLLECT_MIN_TEMP` | `60` | 自动收集最低温度 |

---

## API 调用

### Python

```python
import sys
sys.path.insert(0, '/workspace/projects/extensions/insight-system')

from core.three_layer_memory import ThreeLayerMemory
from core.ripple import Ripple

# 初始化
mem = ThreeLayerMemory('/workspace/projects/extensions/insight-system')

# 添加记忆
ripple = Ripple(
    content="关键发现：三层架构可实现动态上下文管理",
    temp=80,
    tags=["洞见", "架构"]
)
mem.ripples.append(ripple)
mem.save()

# 获取模糊层
fuzzy = mem.get_fuzzy_layer()
print(fuzzy)

# 精确检索
results = mem.query_precise(tags=["洞见"], temp_range=(70, 90))
for r in results:
    print(f"[{r.temp}] {r.content}")
```

### JavaScript

```javascript
const { execSync } = require('child_process');
const path = '/workspace/projects/extensions/insight-system';

// 添加记忆
function addRipple(content, temp = 50, tags = []) {
  execSync(`cd ${path} && ./run.sh ripple "${content}" --temp ${temp} --tags ${tags.join(',')}`);
}

// 获取模糊层
function getFuzzy() {
  return execSync(`cd ${path} && ./run.sh fuzzy`, { encoding: 'utf-8' });
}

// 精确检索
function search(keyword) {
  return execSync(`cd ${path} && ./run.sh precise "${keyword}"`, { encoding: 'utf-8' });
}
```

---

## 三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│                     模糊层 (~250 tokens)                 │
│  • 水面状态（潜意识摘要）                                │
│  • 热门标签 Top 5                                        │
│  • 高温涟漪 Top 3                                        │
│  → 启动时自动加载，作为系统提示                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     精确层（按需检索）                    │
│  query_precise(                                         │
│    tags=["洞见"],           # 标签过滤                  │
│    temp_range=(70, 90),     # 温度范围                  │
│    keyword="架构",           # 关键词                   │
│    limit=10                 # 返回数量                  │
│  )                                                      │
│  → 运行时按条件检索                                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     深度层（完整数据）                    │
│  export_deep_layer(format='toon')                       │
│  export_deep_layer(format='json')                       │
│  → 完整数据导出，用于备份和迁移                          │
└─────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 涟漪 (Ripple)

每个记忆单元是一个"涟漪"：

```python
Ripple(
    content="记忆内容",      # 必填
    temp=75,                 # 温度 0-100，越高越重要
    tags=["洞见", "优化"],   # 标签，用于检索
)
```

### 水温规则

| 温度 | 含义 | 示例 |
|------|------|------|
| 80-100 | 关键洞见 | "发现核心架构问题" |
| 60-79 | 重要发现 | "优化方案有效" |
| 40-59 | 一般记录 | "完成代码重构" |
| 20-39 | 日常琐事 | "修复小 bug" |
| 0-19 | 可忽略 | "格式化代码" |

### 共振条件

两个涟漪自动关联的条件：
- 温度相近（差值 ≤ 15）
- 标签重叠（至少一个共同标签）
- 时间相近（≤ 24 小时）

---

## TOON 格式

相比 JSON 减少 ~67% token：

```
# JSON (约 150 tokens)
{"content":"洞见内容","temp":75,"tags":["洞见","创新"],"timestamp":1774011073}

# TOON (约 50 tokens)
75|1774011073|洞见,创新|洞见内容
```

---

## 文件结构

```
insight-system/
├── install.sh                # 一键安装脚本
├── openclaw.plugin.json      # 插件配置
├── index.js                  # ContextEngine 入口
├── run.sh                    # 命令行工具
├── README.md                 # 本文档
│
├── core/                     # 核心逻辑
│   ├── ripple.py            # 涟漪模型
│   ├── subconscious.py      # 潜意识模型
│   └── three_layer_memory.py  # 三层记忆管理
│
├── utils/                    # 工具
│   ├── toon_format.py       # TOON 格式
│   └── config_loader.py     # 配置加载
│
├── ripples.toon             # 涟漪数据
└── subconscious.toon        # 潜意识数据
```

---

## 常见问题

### Q: 安装后看不到记忆？

```bash
# 检查插件状态
openclaw plugins list | grep insight

# 查看日志
tail -n 50 /app/work/logs/bypass/dev.log | grep insight

# 手动测试
cd /workspace/projects/extensions/insight-system
./run.sh status
```

### Q: 如何迁移到新环境？

```bash
# 打包数据
cd /workspace/projects/extensions/insight-system
tar -czvf insight-data.tar.gz ripples.toon subconscious.toon

# 在新环境解压
tar -xzvf insight-data.tar.gz
```

### Q: 如何清空所有记忆？

```bash
cd /workspace/projects/extensions/insight-system
rm ripples.toon subconscious.toon
touch ripples.toon subconscious.toon
```

### Q: 如何与 OpenClaw 内置记忆共存？

不建议共存。如果需要，可以：

```bash
# 移除 memory: "none" 配置
openclaw config unset plugins.slots.memory
```

---

## 许可证

MIT License

---

## 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [ContextEngine 插件开发](https://docs.openclaw.ai/tools/plugin)
- [GitHub 仓库](https://github.com/Elohia/insight-system)
