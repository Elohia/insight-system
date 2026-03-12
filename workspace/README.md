# 神经元洞见系统 v1.0

> 仿神经元构建的记忆思考系统 — 让洞见像生物大脑一样运作

## 🧠 核心理念

| 神经元 | 洞见系统 |
|--------|----------|
| 突触 | 知识点之间的关联 |
| 输入信号 | 碎片/经验 |
| 阈值 | 触发洞见的关联度 |
| 激活 | 产生洞见 |
| 遗忘 | 长期未用的关联变弱 |
| 强化 | 常用洞见权重增加 |

## 📦 项目结构

```
second-brain/
├── scripts/
│   ├── insight_system.py      # 核心算法（语义分块、相似度计算）
│   ├── insight-optimize.sh    # 定时任务（每 3 小时 + 反思）
│   └── message_queue.py       # 消息队列
├── memory/
│   ├── 2026-03-10.md          # 记忆文件
│   ├── 2026-03-12.md          # 记忆文件
│   └── insight-cron.log       # 运行日志
└── README.md
```

## 🚀 快速开始

### 1. 配置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加每 3 小时运行
0 */3 * * * /path/to/second-brain/scripts/insight-optimize.sh >> /path/to/second-brain/memory/insight-cron.log 2>&1
```

### 2. 手动添加消息碎片

```bash
python3 scripts/message_queue.py add "今天学到了一个重要概念..."
```

### 3. 运行洞见系统

```bash
python3 scripts/insight_system.py
```

## 📊 当前状态

| 指标 | 数值 |
|------|------|
| 运行次数 | 33 次 |
| 洞见总数 | 52 个 |
| 连接数 | 5 个 |
| 运行频率 | 每 3 小时自动 |

## 🔧 核心功能

### 语义分块
- 按标题层级 + 内容块分割
- 自动去除 markdown 格式
- 限制片段长度（300 字符）

### 相似度计算
- 本地词集合算法（Jaccard 相似度）
- 不使用 LLM（Token 优化）
- 阈值触发（>0.7 强化连接）

### 遗忘机制
- 限制 connections 大小（默认 50）
- 删除权重最低的连接
- 模拟生物遗忘曲线

### 自动反思
- 每次运行后记录日志
- 统计运行次数、洞见数
- 检测异常情况

## 💡 使用示例

### 工作模式

```
主会话对话 → message_queue.py add → 队列
memory 文件 → 自动提取碎片 → 洞见系统
     ↓
定时任务（每 3 小时）→ 处理 → 存储 → 反思日志
```

### 输出示例

```
🧠 神经元洞见系统 v1.0 启动
📥 读取消息队列...
   读取到 1 条消息
📥 读取记忆碎片...
   提取到 4 个语义块
📊 状态：{'run_time': '2026-03-12T23:55:42', 'fragments_processed': 4, 'total_insights': 52, 'connections': 5}
✅ 运行完成
```

## 📝 待优化

- [ ] 接入飞书实时消息源
- [ ] 与 capability-evolver 闭环
- [ ] 洞见可视化/查询界面
- [ ] 更智能的语义分块（NLP）

## 📄 License

MIT

---

*由欧皇（贾诩）创建 · 2026-03-12 ☘️*
