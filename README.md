# 洞见系统 (Insight System)

> 弱模型 + 强工具链 + 工具思维 > 单一大模型

**一键部署、自动激活的三层记忆系统**

## 一键部署

```bash
# 1. 克隆并进入目录
git clone https://github.com/Elohia/insight-system.git
cd insight-system

# 2. 运行部署脚本
./deploy.sh
```

部署脚本会自动：
- 检查 Python 环境
- 安装依赖
- 配置环境变量（引导输入）
- 初始化洞见状态
- 生成模糊层
- 配置 OpenClaw Hook

---

## 手动部署（如果一键失败）

### 步骤 1：基础配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入 API Key（至少填一个）
nano .env
```

**.env 配置示例：**
```bash
# 智谱 AI（推荐，免费额度充足）
ZHIPU_API_KEY=your_zhipu_api_key_here

# 阿里云通义千问（可选，用于多模态）
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

获取 API Key：
- 智谱：https://open.bigmodel.cn
- 阿里云：https://dashscope.console.aliyun.com

### 步骤 2：初始化洞见系统

```bash
cd /path/to/insight-system

# 生成模糊层
python core/insight_hook.py --update-fuzzy
```

### 步骤 3：激活 OpenClaw Hook

在 OpenClaw 的 `openclaw.json` 中添加：

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

重启 OpenClaw：
```bash
openclaw gateway restart
```

---

## 验证激活

### 方法 1：检查 Hook 状态

```bash
openclaw hooks list
```

应看到：
```
✓ ready  │ 🧠 insight-inject    │ 在 AI 运行前自动注入相关洞见到上下文中
```

### 方法 2：测试模糊层

```bash
python core/insight_hook.py --startup
```

应输出模糊层内容 + 反向提示。

### 方法 3：实际对话测试

开始新对话，检查是否自动加载洞见上下文。

---

## 核心功能

### 🔮 三层记忆

| 层级 | 触发时机 | 内容 | Token |
|------|---------|------|-------|
| 模糊层 | 每次启动 | 工具索引 + 决策模式 + 反向提示 | ~400 |
| 精确层 | 按需 `--precise` | 相关洞见详细内容 | 按需 |
| 深度层 | 按需 `--deep` | 原始记忆文件 | 按需 |

### 🛠️ 工具思维自动沉淀

系统自动从以下场景学习：
- 成功解决问题的案例 → 场景-工具索引
- 深度思考的洞见 → 决策模式
- 实践验证的经验 → 行动策略

### 📝 Working Buffer

在上下文压缩前捕获关键信息，防止丢失。

### 🎯 反向提示

主动提出未回答的问题，而非被动等待。

---

## 日常使用

### 自动运行（推荐）

配置定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务
# 每小时更新模糊层
0 * * * * cd /path/to/insight-system && python core/insight_hook.py --update-fuzzy >/dev/null 2>&1
```

### 手动命令

```bash
# 启动加载（带反向提示）
python core/insight_hook.py --startup

# 精确查询
python core/insight_hook.py --precise "关键词"

# 深度查询
python core/insight_hook.py --deep "关键词"

# 更新模糊层
python core/insight_hook.py --update-fuzzy

# 数据去重
python scripts/dedup.py
```

---

## 故障排查

### 问题：Hook 显示未就绪

```bash
# 检查 Hook 日志
openclaw hooks logs insight-inject

# 手动测试
python core/insight_hook.py --startup
```

### 问题：模糊层为空

```bash
# 重新生成
python core/insight_hook.py --update-fuzzy
```

### 问题：API 错误

检查 `.env` 文件：
```bash
cat .env
# 确认 ZHIPU_API_KEY 或 DASHSCOPE_API_KEY 已设置
```

---

## 项目结构

```
insight-system/
├── core/
│   ├── three_layer_memory.py      # 三层记忆核心
│   ├── insight_hook.py            # Hook 入口
│   ├── insight_system.py          # 洞见系统主逻辑
│   └── tool_usage_recorder.py     # 工具使用记录
├── storage/
│   └── multimodal_memory.py       # 多模态记忆存储
├── scripts/
│   ├── dedup.py                   # 去重脚本
│   └── deploy.sh                  # 一键部署脚本
├── .env.example                   # 环境变量模板
└── README.md                      # 本文件
```

---

## 设计理念

1. **一键部署**：最小化配置，最大化自动化
2. **自动激活**：Hook 自动注入，无需手动干预
3. **自然沉淀**：工具思维从实践中学习，非预设
4. **按需加载**：启动最小化，需要时再加载

---

## 参考

- [OpenClaw](https://openclaw.ai) - AI Agent 框架
- [proactive-agent](https://github.com/OpenClaw-AI/proactive-agent) - 主动式 Agent 架构

---

## License

MIT
