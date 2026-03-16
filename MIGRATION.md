# 洞见系统：OpenClaw 记忆系统替代方案

> **目标**：取代 OpenClaw 的 Markdown 记忆系统，成为 OpenClaw 的核心记忆引擎

---

## 🎯 为什么替代？

### OpenClaw 原生记忆系统的局限

| 问题 | 影响 |
|------|------|
| **被动存储** | 只记录，不处理，不会自动生成洞见 |
| **缺乏关联** | 记忆之间没有连接，难以发现隐藏模式 |
| **静态存储** | 不会强化重要记忆，也不会遗忘过时信息 |
| **无洞见生成** | 不会主动追问、碰撞、变异 |
| **仅文本** | 不支持图片、视频等多模态记忆 |

### 洞见系统的优势

| 能力 | 说明 |
|------|------|
| **主动洞见** | 碰撞引擎、追问引擎、变异模式 |
| **智能关联** | 自动发现碎片间的隐藏连接 |
| **动态演化** | 强化重要记忆，遗忘过时信息 |
| **多模态** | 支持文本、图片、视频向量化 |
| **语义搜索** | 需配置 API |

---

## 📐 架构设计

### 当前架构

```
┌─────────────────────────────────────────────┐
│           OpenClaw Agent                     │
│  ┌───────────────────────────────────────┐  │
│  │   写入 Markdown 文件                   │  │
│  │   memory/YYYY-MM-DD.md                │  │
│  │   MEMORY.md                           │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### 替代后架构

```
┌──────────────────────────────────────────────────────┐
│                  OpenClaw Agent                       │
│  ┌────────────────────────────────────────────────┐  │
│  │         记忆系统兼容层                          │  │
│  │  - create()  创建记忆                          │  │
│  │  - read()    读取记忆                          │  │
│  │  - search()  搜索记忆                          │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│              洞见系统（主存储）                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  - 向量数据库                                   │  │
│  │  - 碰撞引擎                                     │  │
│  │  - 追问引擎                                     │  │
│  │  - 多模态记忆                                   │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│          Markdown 视图（兼容层，可选）                │
│  - 从洞见系统生成                                   │
│  - 保持 OpenClaw 格式兼容                           │
│  - 用于手动查看和备份                               │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 迁移现有记忆

```bash
# 进入洞见系统目录
cd /workspace/projects/extensions/insight-system

# 试运行，查看将迁移哪些文件
python3 scripts/migrate.py --dry-run

# 实际迁移
python3 scripts/migrate.py
```

输出示例：
```
📚 发现 3 个记忆文件

📝 处理 2026-03-10.md...
   ✅ 迁移 5 个碎片

📝 处理 2026-03-12.md...
   ✅ 迁移 12 个碎片

📝 处理 2026-03-13.md...
   ✅ 迁移 8 个碎片

==================================================
🎉 迁移完成！
==================================================
📊 统计:
   - 记忆文件: 3 个
   - 迁移碎片: 25 个
   - 生成洞见: 7 个
```

### 2. 启动记忆服务

```bash
# 方式一：命令行接口
python3 core/memory_server.py status

# 方式二：API 服务器（可选）
python3 core/memory_server.py serve --port 5001
```

### 3. 配置 OpenClaw Hook（可选）

创建 OpenClaw Hook，拦截记忆操作：

```bash
# 复制 Hook 到 OpenClaw hooks 目录
cp -r extension/hooks/memory-hook.ts ~/.openclaw/hooks/

# 启用 Hook
openclaw hooks enable memory-hook
```

---

## 🔧 使用方式

### 方式一：直接使用洞见系统（推荐）

洞见系统会自动管理记忆，无需手动调用：

```bash
# 定期运行洞见系统
crontab -e

# 添加以下任务
# 每小时运行洞见生成
0 * * * * cd /path/to/insight-system && ./run.sh run

# 每3小时运行碰撞引擎
0 */3 * * * cd /path/to/insight-system && ./run.sh collide
```

### 方式二：使用兼容 API

```python
from core.memory_server import OpenClawMemorySystem

# 初始化
memory = OpenClawMemorySystem()

# 创建记忆（替代写入 Markdown）
memory.create("今天学到了一个新概念", metadata={"source": "agent"})

# 读取记忆
content = memory.read("2026-03-13")
print(content)

# 搜索记忆
results = memory.search("新概念", max_results=10)
for r in results:
    print(f"- {r['text']}")

# 查看状态
status = memory.status()
print(f"总洞见数: {status['total_insights']}")
```

### 方式三：HTTP API（可选）

启动 API 服务器后，可以通过 REST API 访问：

```bash
# 启动服务器
python3 core/memory_server.py serve --port 5001

# 创建记忆
curl -X POST http://localhost:5001/api/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "今天学到了一个新概念"}'

# 读取记忆
curl http://localhost:5001/api/memory?date=2026-03-13

# 搜索记忆
curl "http://localhost:5001/api/memory/search?query=新概念&max_results=10"

# 查看状态
curl http://localhost:5001/api/memory/status
```

---

## 📊 功能对比

### 与 OpenClaw 原生记忆系统对比

| 功能 | OpenClaw 原生 | 洞见系统 |
|------|--------------|----------|
| **存储方式** | Markdown 文件 | 向量数据库 + SQLite |
| **洞见生成** | ❌ 无 | ✅ 碰撞、追问、变异 |
| **记忆关联** | ❌ 无 | ✅ 自动发现连接 |
| **动态演化** | ❌ 静态 | ✅ 强化、遗忘、权重 |
| **多模态** | ❌ 仅文本 | ✅ 文本、图片、视频 |
| **语义搜索** | ⚠️ 需配置 API | ✅ 内置 |
| **追问引擎** | ❌ 无 | ✅ 主动反思 |
| **变异模式** | ❌ 无 | ✅ 探索可能性 |
| **API 兼容** | ✅ | ✅ 完全兼容 |

### 数据流对比

#### OpenClaw 原生
```
Agent → Markdown 文件 → (静态存储)
```

#### 洞见系统
```
Agent → 洞见系统 → 洞见生成 → Markdown 视图
                     ↓
                   向量数据库
                     ↓
                  语义搜索
```

---

## 🔄 同步机制

### 双向同步

洞见系统会自动同步到 OpenClaw 的 Markdown 文件：

1. **写入同步**：洞见系统 → Markdown 文件
   - 每日记忆：`memory/YYYY-MM-DD.md`
   - 长期记忆：`MEMORY.md`

2. **读取同步**：Markdown 文件 → 洞见系统
   - 迁移脚本：`scripts/migrate.py`
   - 索引命令：`memory.index()`

### 自动同步

```bash
# 每小时同步一次
crontab -e

# 添加任务
0 * * * * cd /path/to/insight-system && python3 -c "from core.memory_server import OpenClawMemorySystem; OpenClawMemorySystem().sync_to_openclaw()"
```

---

## 📋 实施路线图

### Phase 1: 准备（已完成 ✅）

- [x] 分析 OpenClaw 记忆系统架构
- [x] 设计替代方案
- [x] 实现记忆兼容层
- [x] 创建迁移脚本

### Phase 2: 部署（当前阶段）

- [ ] 迁移现有记忆数据
- [ ] 配置定期同步
- [ ] 测试 API 兼容性
- [ ] 监控系统运行

### Phase 3: 优化（下一步）

- [ ] 性能优化
- [ ] 添加更多洞见模式
- [ ] 改进 UI 展示
- [ ] 集成到 OpenClaw Dashboard

---

## 🎯 最终目标

### 短期（1-2 周）

- ✅ 洞见系统稳定运行
- ✅ 所有记忆数据迁移
- ✅ API 完全兼容
- ⏳ OpenClaw 无感知切换

### 中期（1-2 月）

- ⏳ 完全取代 Markdown 存储层
- ⏳ 提供可视化 Dashboard
- ⏳ 支持更多多模态类型

### 长期（3-6 月）

- ⏳ 成为 OpenClaw 官方记忆系统
- ⏳ 提供云端同步
- ⏳ 支持多用户协作

---

## 🚨 注意事项

### 兼容性

- ✅ 保持 Markdown 文件格式兼容
- ✅ 保持 API 接口兼容
- ✅ 支持回滚到原生系统

### 性能

- ⚠️ 向量搜索可能比文本搜索慢（已优化）
- ✅ 使用缓存加速频繁查询
- ✅ 异步处理洞见生成

### 数据安全

- ✅ 定期备份 Markdown 文件
- ✅ 支持导出所有数据
- ✅ 提供数据恢复机制

---

## 📚 相关文档

- [架构设计](./ARCHITECTURE.md)
- [集成方案](./INTEGRATION.md)
- [API 文档](./API.md)（待创建）
- [迁移指南](./scripts/migrate.py)

---

## 🤝 贡献

欢迎贡献代码和想法！

1. Fork 仓库
2. 创建功能分支
3. 提交 Pull Request

---

## 📄 License

MIT License
