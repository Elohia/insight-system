# 架构设计：洞见系统作为 OpenClaw 记忆系统

## 🎯 目标

将洞见系统从"集成"模式升级为 OpenClaw 的**唯一记忆系统**，取代原有的 Markdown 文件系统。

---

## 📊 现状分析

### OpenClaw 现有记忆系统

#### 存储结构
```
workspace/
├── memory/
│   ├── 2026-03-13.md      # 每日记忆（Markdown）
│   ├── 2026-03-12.md
│   └── 2026-03-10.md
├── MEMORY.md              # 长期记忆（Markdown）
└── .openclaw/
    └── memory/
        └── main.sqlite    # 向量索引（SQLite）
```

#### 工作机制
1. **写入**：Agent 直接写入 Markdown 文件
2. **读取**：会话开始时读取今天 + 昨天 + MEMORY.md
3. **搜索**：`openclaw memory search` 调用嵌入 API 进行语义搜索
4. **索引**：`openclaw memory index` 更新 SQLite 向量索引

#### 问题
- ❌ **被动存储**：只记录，不处理
- ❌ **缺乏洞见**：不会自动生成洞见、追问
- ❌ **无关联**：记忆之间没有连接
- ❌ **静态**：不会强化、遗忘、演化

---

### 洞见系统当前状态

#### 存储结构
```
workspace/
├── .openclaw/
│   ├── insight-state.json          # 洞见状态
│   ├── vector-db.json              # 向量数据库
│   └── message-queue.json          # 消息队列
└── memory/                         # （兼容层）Markdown 视图
    ├── 2026-03-13.md
    └── ...
```

#### 核心能力
- ✅ **主动洞见**：碰撞引擎、追问引擎、变异模式
- ✅ **智能关联**：发现碎片间的隐藏连接
- ✅ **动态演化**：强化、遗忘、权重调整
- ✅ **多模态**：文本、图片、视频向量化

#### 问题
- ⚠️ **独立运行**：需要手动触发
- ⚠️ **不兼容**：OpenClaw 不知道洞见系统的存在
- ⚠️ **双重存储**：洞见数据库 + Markdown 文件

---

## 🚀 替代方案

### 方案一：记忆提供者插件（推荐）

#### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     OpenClaw Core                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │          Memory Provider Interface                │  │
│  │  - create(memory) → void                          │  │
│  │  - search(query) → results[]                      │  │
│  │  - read(date) → memory                            │  │
│  │  - sync() → void                                  │  │
│  └───────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Insight Memory Provider                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  OpenClaw API ←→ 洞见系统                          │  │
│  │  - 实现记忆提供者接口                              │  │
│  │  - 背后使用洞见数据库                              │  │
│  │  - 保持 Markdown 视图同步（可选）                  │  │
│  └───────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Insight System Core                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  - NeuronInsight（神经元洞见引擎）                │  │
│  │  - Collider（碰撞引擎）                           │  │
│  │  - Questioner（追问引擎）                         │  │
│  │  - VectorDB（向量数据库）                         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

#### 实现步骤

##### 1. 创建 OpenClaw 插件

创建 `extensions/insight-memory-provider/`：

```
extensions/insight-memory-provider/
├── package.json
├── index.ts              # 主入口
├── provider.ts           # 记忆提供者实现
├── adapter.ts            # 洞见系统适配器
└── README.md
```

##### 2. 实现记忆提供者接口

```typescript
// provider.ts
import { MemoryProvider, MemoryEntry, SearchResult } from '@openclaw/core';
import { InsightAdapter } from './adapter';

export class InsightMemoryProvider implements MemoryProvider {
  private adapter: InsightAdapter;

  constructor() {
    this.adapter = new InsightAdapter();
  }

  /**
   * 创建新记忆
   * 写入洞见系统，而非 Markdown 文件
   */
  async create(entry: MemoryEntry): Promise<void> {
    // 1. 添加到洞见系统
    await this.adapter.addFragment(entry.content, {
      source: entry.source || 'agent',
      tags: entry.tags || [],
      timestamp: entry.timestamp,
    });

    // 2. 触发洞见生成
    await this.adapter.processFragments();

    // 3. 可选：同步到 Markdown 视图
    if (this.config.syncToMarkdown) {
      await this.adapter.syncToMarkdown(entry);
    }
  }

  /**
   * 搜索记忆
   * 使用洞见系统的向量数据库
   */
  async search(query: string, options?: SearchOptions): Promise<SearchResult[]> {
    return await this.adapter.searchInsights(query, {
      maxResults: options?.maxResults || 10,
      includeInsights: true,
      includeFragments: true,
    });
  }

  /**
   * 读取指定日期的记忆
   * 从洞见系统生成 Markdown 视图
   */
  async read(date: string): Promise<string> {
    return await this.adapter.generateDailyMarkdown(date);
  }

  /**
   * 同步记忆
   * 确保洞见数据库和索引一致
   */
  async sync(): Promise<void> {
    await this.adapter.reindex();
  }
}
```

##### 3. 洞见系统适配器

```typescript
// adapter.ts
import { spawn } from 'child_process';
import * as path from 'path';

export class InsightAdapter {
  private insightSystemPath: string;

  constructor() {
    this.insightSystemPath = '/workspace/projects/extensions/insight-system';
  }

  /**
   * 添加碎片到洞见系统
   */
  async addFragment(content: string, metadata: any): Promise<void> {
    const script = path.join(this.insightSystemPath, 'core/insight_system.py');
    
    await this.runPython(script, 'add_fragment', {
      text: content,
      source: metadata.source,
      tags: metadata.tags,
      timestamp: metadata.timestamp,
    });
  }

  /**
   * 处理碎片，生成洞见
   */
  async processFragments(): Promise<void> {
    const script = path.join(this.insightSystemPath, 'core/insight_system.py');
    await this.runPython(script, 'process');
  }

  /**
   * 搜索洞见
   */
  async searchInsights(query: string, options: any): Promise<any[]> {
    const script = path.join(this.insightSystemPath, 'core/openclaw_api.py');
    
    const results = await this.runPython(script, 'search_memory', {
      query,
      max_results: options.maxResults,
    });

    return results;
  }

  /**
   * 生成每日 Markdown 视图
   */
  async generateDailyMarkdown(date: string): Promise<string> {
    const script = path.join(this.insightSystemPath, 'core/memory_writer.py');
    
    const markdown = await this.runPython(script, 'read_daily', {
      date,
    });

    return markdown;
  }

  /**
   * 重新索引
   */
  async reindex(): Promise<void> {
    const script = path.join(this.insightSystemPath, 'core/openclaw_api.py');
    await this.runPython(script, 'index_memory', { force: true });
  }

  /**
   * 运行 Python 脚本
   */
  private async runPython(script: string, method: string, args: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const process = spawn('python3', [
        script,
        '--method', method,
        '--args', JSON.stringify(args),
      ]);

      let output = '';
      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data}`);
      });

      process.on('close', (code) => {
        if (code === 0) {
          try {
            resolve(JSON.parse(output));
          } catch (e) {
            resolve(output);
          }
        } else {
          reject(new Error(`Python script failed with code ${code}`));
        }
      });
    });
  }
}
```

##### 4. 配置 OpenClaw 使用洞见记忆提供者

```json
// openclaw.json
{
  "memory": {
    "provider": "insight",
    "providers": {
      "insight": {
        "path": "/workspace/projects/extensions/insight-memory-provider",
        "config": {
          "syncToMarkdown": true,
          "autoProcess": true,
          "collisionInterval": 10800
        }
      }
    }
  }
}
```

---

### 方案二：Hook 机制（过渡方案）

如果 OpenClaw 不支持自定义记忆提供者，可以使用 Hook 机制：

#### 实现

```typescript
// extensions/insight-memory-hook/index.ts
import { Hook } from '@openclaw/core';

export default class InsightMemoryHook implements Hook {
  name = 'insight-memory';

  // 拦截记忆写入
  async onMemoryWrite(content: string, metadata: any): Promise<void> {
    // 1. 写入洞见系统
    await this.insight.addFragment(content, metadata);
    
    // 2. 触发洞见生成
    await this.insight.processFragments();
    
    // 3. 阻止默认写入（可选）
    // return { preventDefault: true };
  }

  // 拦截记忆搜索
  async onMemorySearch(query: string): Promise<any[]> {
    // 使用洞见系统的搜索
    return await this.insight.search(query);
  }
}
```

#### 限制
- ⚠️ 只能拦截，不能完全替换
- ⚠️ 性能可能有损耗
- ⚠️ 需要保持 Markdown 文件兼容

---

### 方案三：混合模式（渐进式）

#### 阶段一：双向同步（已实现）
- 洞见系统读取 Markdown 文件
- 洞见系统写入 Markdown 文件
- 保持两个系统并行运行

#### 阶段二：主从模式
- 洞见系统作为主存储
- Markdown 文件作为视图（只读）
- OpenClaw 读取 Markdown，写入洞见系统

#### 阶段三：完全替代
- 洞见系统成为唯一存储
- Markdown 文件完全移除
- 提供完全兼容的 API

---

## 🔄 数据迁移

### 从 Markdown 迁移到洞见系统

#### 迁移脚本

```python
#!/usr/bin/env python3
"""
将 OpenClaw 的 Markdown 记忆迁移到洞见系统
"""

import os
import re
from datetime import datetime
from pathlib import Path

def migrate_memory_to_insight():
    """
    将 memory/*.md 迁移到洞见系统
    """
    workspace = "/workspace/projects/workspace"
    memory_dir = f"{workspace}/memory"
    
    # 初始化洞见系统
    from core.insight_system import NeuronInsight
    insight = NeuronInsight()
    
    # 读取所有记忆文件
    memory_files = sorted(Path(memory_dir).glob("*.md"))
    
    for mf in memory_files:
        print(f"📝 处理 {mf.name}...")
        
        content = mf.read_text()
        
        # 提取日期
        date_match = re.search(r'# (\d{4}-\d{2}-\d{2})', content)
        if date_match:
            date = date_match.group(1)
        
        # 提取段落
        sections = re.split(r'##+', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # 添加到洞见系统
            insight.add_fragment(
                section.strip(),
                source="migrated_memory"
            )
    
    # 处理并保存
    insight.process()
    insight.save_state()
    
    print(f"✅ 迁移完成: {len(memory_files)} 个文件")

if __name__ == "__main__":
    migrate_memory_to_insight()
```

---

## 📋 实施计划

### Phase 1: 准备阶段（1-2 天）

- [x] 分析 OpenClaw 记忆系统架构
- [x] 设计替代方案
- [ ] 检查 OpenClaw 是否支持自定义记忆提供者
  - 查阅文档：`openclaw docs memory provider`
  - 查看源码：OpenClaw 是否暴露 MemoryProvider 接口
- [ ] 确定最佳实现路径

### Phase 2: 实现阶段（3-5 天）

#### 路径 A：支持自定义提供者
- [ ] 创建 `insight-memory-provider` 插件
- [ ] 实现 `MemoryProvider` 接口
- [ ] 编写适配器连接洞见系统
- [ ] 测试记忆读写和搜索
- [ ] 配置 OpenClaw 使用洞见记忆提供者

#### 路径 B：使用 Hook 机制
- [ ] 创建 `insight-memory-hook`
- [ ] 拦截记忆操作
- [ ] 转发到洞见系统
- [ ] 测试兼容性

#### 路径 C：混合模式
- [ ] 完善双向同步
- [ ] 优化性能
- [ ] 逐步迁移数据

### Phase 3: 测试阶段（1-2 天）

- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试
- [ ] 用户测试

### Phase 4: 部署阶段（1 天）

- [ ] 文档更新
- [ ] 迁移指南
- [ ] 发布说明

---

## 🎯 核心优势

### 对比 OpenClaw 原生记忆系统

| 特性 | OpenClaw 原生 | 洞见系统 |
|------|--------------|----------|
| 存储方式 | Markdown 文件 | 向量数据库 + SQLite |
| 洞见生成 | ❌ 无 | ✅ 碰撞、追问、变异 |
| 记忆关联 | ❌ 无 | ✅ 自动发现连接 |
| 动态演化 | ❌ 静态 | ✅ 强化、遗忘、权重 |
| 多模态 | ❌ 仅文本 | ✅ 文本、图片、视频 |
| 语义搜索 | ⚠️ 需配置 | ✅ 内置 |
| 追问引擎 | ❌ 无 | ✅ 主动反思 |
| 变异模式 | ❌ 无 | ✅ 探索可能性 |

---

## 🚨 风险与挑战

### 技术风险

1. **兼容性问题**
   - OpenClaw 可能不支持自定义记忆提供者
   - 需要保持 API 兼容

2. **性能问题**
   - 向量搜索可能比文本搜索慢
   - 需要优化索引和缓存

3. **数据一致性**
   - 双系统同步可能出现冲突
   - 需要设计冲突解决机制

### 解决方案

1. **混合模式过渡**
   - 先使用双向同步
   - 逐步切换到主从模式

2. **性能优化**
   - 使用缓存加速
   - 异步处理洞见生成

3. **数据备份**
   - 定期备份 Markdown 文件
   - 提供回滚机制

---

## 📚 参考资料

- [OpenClaw Memory System](https://docs.openclaw.ai/concepts/memory)
- [OpenClaw Hooks](https://docs.openclaw.ai/automation/hooks)
- [OpenClaw Plugin Development](https://docs.openclaw.ai/tools/plugin)
- [洞见系统设计文档](./README.md)
