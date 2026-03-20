# 涟漪意识流 ContextEngine

> OpenClaw 三层记忆插件 - 让 AI 拥有长期记忆

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/Elohia/insight-system)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.3.11-green.svg)](https://openclaw.ai)

---

## 一句话介绍

**给 OpenClaw 加上三层记忆：模糊层（启动加载）、精确层（按需检索）、深度层（完整导出）**

---

## 快速安装（3步）

### 第 1 步：下载插件

```bash
# 方式一：Git clone
cd /workspace/projects/extensions
git clone https://github.com/Elohia/insight-system.git

# 方式二：直接下载
wget https://github.com/Elohia/insight-system/archive/refs/heads/main.zip
unzip main.zip -d insight-system
```

### 第 2 步：配置 OpenClaw

在 `openclaw.json` 中添加以下内容：

```json
{
  "plugins": {
    "load": {
      "paths": ["/workspace/projects/extensions/insight-system"]
    },
    "allow": ["insight-system"],
    "slots": {
      "contextEngine": "insight-system"
    }
  },
  "env": {
    "INSIGHT_SYSTEM_PATH": "/workspace/projects/extensions/insight-system",
    "FUZZY_BUDGET": "250"
  }
}
```

### 第 3 步：重启 OpenClaw

```bash
./scripts/restart.sh

# 验证安装
openclaw plugins list | grep insight
# 应该看到: insight-system | loaded
```

---

## 命令行使用

```bash
cd /workspace/projects/extensions/insight-system

# 添加涟漪（记忆）
./run.sh ripple "发现 TOON 格式可节省 67% token" --temp 75 --tags 优化,TOON

# 查看模糊层（启动时加载的记忆概要）
./run.sh fuzzy

# 精确检索
./run.sh precise TOON
./run.sh precise --temp 70-80  # 温度范围
./run.sh precise --tags 优化   # 按标签

# 深度导出
./run.sh deep > backup.toon

# 系统状态
./run.sh status
```

---

## API 调用

### Python SDK

```python
import sys
sys.path.insert(0, '/workspace/projects/extensions/insight-system')

from core.three_layer_memory import ThreeLayerMemory
from core.ripple import Ripple

# 初始化
mem = ThreeLayerMemory('/workspace/projects/extensions/insight-system')

# 添加涟漪
ripple = Ripple(
    content="关键发现：三层架构可实现动态上下文管理",
    temp=80,
    tags=["洞见", "架构"]
)
mem.ripples.append(ripple)
mem.save()

# 获取模糊层（~250 tokens）
fuzzy = mem.get_fuzzy_layer()
print(fuzzy)

# 精确检索
results = mem.query_precise(
    tags=["洞见"],
    temp_range=(70, 90),
    limit=5
)
for r in results:
    print(f"[{r.temp}] {r.content}")

# 深度导出
deep = mem.export_deep_layer(format='toon')
```

### JavaScript/Node.js

```javascript
const { execSync } = require('child_process');

// 添加涟漪
function addRipple(content, temp = 50, tags = []) {
  const tagsStr = tags.join(',');
  execSync(`cd /workspace/projects/extensions/insight-system && ./run.sh ripple "${content}" --temp ${temp} --tags ${tagsStr}`);
}

// 获取模糊层
function getFuzzy() {
  return execSync(`cd /workspace/projects/extensions/insight-system && ./run.sh fuzzy`, { encoding: 'utf-8' });
}

// 精确检索
function search(keyword) {
  return execSync(`cd /workspace/projects/extensions/insight-system && ./run.sh precise "${keyword}"`, { encoding: 'utf-8' });
}

// 使用示例
addRipple("API 调用示例", 60, ["demo"]);
console.log(getFuzzy());
console.log(search("demo"));
```

---

## 向量搜索（高级）

### 安装向量依赖

```bash
pip install tiktoken
```

### 启用语义搜索

```python
from core.three_layer_memory import ThreeLayerMemory
from utils.vector_search import VectorSearch  # 需要额外实现

mem = ThreeLayerMemory('/workspace/projects/extensions/insight-system')

# 语义搜索（需要 embedding 模型）
# results = mem.semantic_search("性能优化相关内容", top_k=5)
```

### 配置 OpenClaw 向量搜索

在 `openclaw.json` 中：

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "openai"
      }
    }
  },
  "env": {
    "OPENAI_API_KEY": "your-api-key"
  }
}
```

---

## 三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│                     模糊层 (~250 tokens)                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │ • 水面状态（潜意识摘要）                          │   │
│  │ • 热门标签 Top 5                                 │   │
│  │ • 高温涟漪 Top 3                                 │   │
│  └─────────────────────────────────────────────────┘   │
│  启动时自动加载，作为系统提示                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     精确层（按需检索）                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ query_precise(                                   │   │
│  │   tags=["洞见"],           # 标签过滤            │   │
│  │   temp_range=(70, 90),     # 温度范围            │   │
│  │   keyword="架构",           # 关键词             │   │
│  │   limit=10                 # 返回数量            │   │
│  │ )                                               │   │
│  └─────────────────────────────────────────────────┘   │
│  运行时按条件检索，返回相关涟漪                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     深度层（完整数据）                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ export_deep_layer(format='toon')                │   │
│  │ export_deep_layer(format='json')                │   │
│  └─────────────────────────────────────────────────┘   │
│  完整数据导出，用于备份和迁移                            │
└─────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 涟漪 (Ripple)

```python
Ripple(
    content="记忆内容",      # 必填
    temp=75,                 # 温度 0-100，越高越重要
    tags=["洞见", "优化"],   # 标签，用于检索
    timestamp=1774011073.0,  # 自动生成
    resonances=[]            # 共振链
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

两个涟漪发生共振需要同时满足：

1. **温度相近** - 差值 ≤ 15
2. **标签重叠** - 至少有一个共同标签
3. **时间相近** - 时间差 ≤ 24 小时

---

## TOON 格式

相比 JSON 减少 ~67% token：

```python
# JSON (约 150 tokens)
{
  "content": "洞见内容",
  "temp": 75,
  "tags": ["洞见", "创新"],
  "timestamp": 1774011073
}

# TOON (约 50 tokens)
75|1774011073|洞见,创新|洞见内容
```

---

## 文件结构

```
insight-system/
├── openclaw.plugin.json     # 插件配置
├── index.js                 # ContextEngine 入口
├── run.sh                   # 命令行工具
├── README.md                # 本文档
│
├── core/                    # 核心逻辑
│   ├── ripple.py           # 涟漪模型
│   ├── subconscious.py     # 潜意识模型
│   └── three_layer_memory.py  # 三层记忆管理
│
├── utils/                   # 工具
│   ├── toon_format.py      # TOON 格式
│   └── config_loader.py    # 配置加载
│
├── ripples.toon            # 涟漪数据
└── subconscious.toon       # 潜意识数据
```

---

## ContextEngine 七个钩子

| 钩子 | 触发时机 | 用途 |
|------|----------|------|
| `bootstrap()` | 插件加载 | 初始化 |
| `ingest(message)` | 消息摄入 | 记录对话 |
| `assemble(budget)` | 组装上下文 | 返回记忆 |
| `compact()` | 压缩记忆 | 清理旧数据 |
| `afterTurn(turn)` | 轮次结束 | 自动收集 |
| `prepareSubagentSpawn()` | 子代理启动 | 传递上下文 |
| `onSubagentEnded()` | 子代理结束 | 收集结果 |

---

## 迁移指南

### 导出到新环境

```bash
# 1. 打包数据
cd /workspace/projects/extensions/insight-system
tar -czvf insight-backup.tar.gz ripples.toon subconscious.toon

# 2. 复制到新环境
scp insight-backup.tar.gz user@new-server:/workspace/projects/extensions/insight-system/

# 3. 解压
tar -xzvf insight-backup.tar.gz
```

### 更新路径

修改 `openclaw.json`：

```json
{
  "env": {
    "INSIGHT_SYSTEM_PATH": "/新的/路径/insight-system"
  }
}
```

---

## 常见问题

### Q: 插件加载失败？

```bash
# 检查路径
ls -la /workspace/projects/extensions/insight-system/openclaw.plugin.json

# 验证配置
openclaw config validate

# 查看日志
tail -n 50 /app/work/logs/bypass/dev.log | grep insight
```

### Q: 如何查看当前记忆？

```bash
./run.sh status
./run.sh fuzzy
./run.sh deep
```

### Q: 如何清空记忆？

```bash
rm ripples.toon subconscious.toon
touch ripples.toon subconscious.toon
```

---

## 许可证

MIT License

---

## 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [ContextEngine 插件开发](https://docs.openclaw.ai/tools/plugin)
- [GitHub 仓库](https://github.com/Elohia/insight-system)
