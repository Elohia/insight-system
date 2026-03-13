# OpenClaw 记忆接口集成方案

## 📊 当前集成状态

### ✅ 已支持功能

1. **读取 OpenClaw 记忆文件**
   - `fetch_memory_fragments()` 方法可以读取 `workspace/memory/*.md` 文件
   - 自动提取标题和内容作为记忆碎片

2. **多模态记忆同步**
   - `sync_to_multimodal()` 方法可以将洞见同步到多模态记忆系统
   - 支持文本、图片、视频的记忆存储

3. **独立运行**
   - 洞见系统可以独立运行，不依赖 OpenClaw 主进程

### ❌ 缺少功能

1. **双向同步**
   - 无法将洞见写回 OpenClaw 的 `MEMORY.md` 文件
   - 用户无法在 OpenClaw 中查看洞见结果

2. **API 调用**
   - 没有调用 OpenClaw 的 `memory search` API
   - 无法利用 OpenClaw 的语义搜索功能

3. **标签集成**
   - 洞见标签与 OpenClaw 记忆标签系统独立
   - 无法通过标签关联记忆和洞见

4. **自动触发**
   - 需要手动运行洞见系统
   - 无法在新增记忆时自动生成洞见

---

## 🚀 增强方案

### 1. 双向同步（优先级：高）

#### 目标
将洞见系统生成的洞见自动写入 OpenClaw 的 `MEMORY.md` 文件。

#### 实现方案

##### 1.1 创建 OpenClaw 记忆写入器

在 `core/` 目录下创建 `memory_writer.py`：

```python
#!/usr/bin/env python3
"""
OpenClaw 记忆写入器
将洞见写入 OpenClaw 的 MEMORY.md 文件
"""

import os
from datetime import datetime
from pathlib import Path

class MemoryWriter:
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = workspace
        self.memory_file = f"{workspace}/MEMORY.md"
        self.daily_memory_dir = f"{workspace}/memory"
    
    def write_insight(self, insight, tags=None):
        """
        将洞见写入 MEMORY.md
        
        Args:
            insight: 洞见内容
            tags: 标签列表
        """
        # 确保 memory 目录存在
        Path(self.daily_memory_dir).mkdir(parents=True, exist_ok=True)
        
        # 构建洞见条目
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        tag_str = " ".join([f"#{tag}" for tag in (tags or [])])
        
        entry = f"""
## 💡 洞见 ({timestamp})

{insight}

{tag_str}

---
"""
        
        # 追加到 MEMORY.md
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            # 创建新的 MEMORY.md
            header = "# 🧠 长期记忆\n\n本文档由 OpenClaw 自动维护\n"
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write(header + entry)
        
        print(f"✅ 洞见已写入 {self.memory_file}")
    
    def write_to_daily(self, insight, tags=None):
        """
        将洞见写入今日记忆文件
        
        Args:
            insight: 洞见内容
            tags: 标签列表
        """
        # 确保 memory 目录存在
        Path(self.daily_memory_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成今日文件名
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = f"{self.daily_memory_dir}/{today}.md"
        
        # 构建洞见条目
        timestamp = datetime.now().strftime("%H:%M")
        tag_str = " ".join([f"#{tag}" for tag in (tags or [])])
        
        entry = f"""
### 💡 洞见 ({timestamp})

{insight}

{tag_str}
"""
        
        # 追加或创建文件
        if os.path.exists(daily_file):
            with open(daily_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            header = f"# {today} 记忆\n\n"
            with open(daily_file, 'w', encoding='utf-8') as f:
                f.write(header + entry)
        
        print(f"✅ 洞见已写入 {daily_file}")
```

##### 1.2 修改洞见系统

在 `core/insight_system.py` 中添加写入逻辑：

```python
def save_state(self):
    self.state["last_processed"] = datetime.now().isoformat()
    self.state["run_count"] += 1
    
    with open(STATE_FILE, 'w') as f:
        json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    # 同步到 OpenClaw 记忆
    self.sync_to_openclaw_memory()
    
    # 多模态记忆：同步洞见到向量数据库
    if MULTIMODAL_AVAILABLE:
        self.sync_to_multimodal()

def sync_to_openclaw_memory(self):
    """将洞见同步到 OpenClaw 记忆文件"""
    try:
        from memory_writer import MemoryWriter
        
        writer = MemoryWriter()
        
        # 同步最新的洞见
        for insight in self.state.get("insights", [])[-5:]:  # 最近5条
            writer.write_to_daily(
                insight.get("text", ""),
                tags=insight.get("tags", [])
            )
        
        print("📊 已同步洞见到 OpenClaw 记忆文件")
    except Exception as e:
        print(f"⚠️ 同步失败: {e}")
```

---

### 2. API 调用（优先级：中）

#### 目标
调用 OpenClaw 的 `memory search` API 进行语义搜索。

#### 实现方案

##### 2.1 创建 OpenClaw API 客户端

在 `core/` 目录下创建 `openclaw_api.py`：

```python
#!/usr/bin/env python3
"""
OpenClaw API 客户端
调用 OpenClaw 的记忆搜索 API
"""

import subprocess
import json

class OpenClawAPI:
    def __init__(self):
        self.openclaw_cmd = "openclaw"
    
    def search_memory(self, query, max_results=10):
        """
        搜索 OpenClaw 记忆
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
        
        Returns:
            list: 搜索结果列表
        """
        try:
            cmd = [
                self.openclaw_cmd,
                "memory",
                "search",
                "--query", query,
                "--max-results", str(max_results),
                "--json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"⚠️ 搜索失败: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"⚠️ API 调用失败: {e}")
            return []
    
    def index_memory(self, force=False):
        """
        重新索引记忆文件
        
        Args:
            force: 是否强制重新索引
        """
        try:
            cmd = [self.openclaw_cmd, "memory", "index"]
            if force:
                cmd.append("--force")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ 记忆索引完成")
                return True
            else:
                print(f"⚠️ 索引失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️ 索引失败: {e}")
            return False
    
    def get_memory_status(self):
        """
        获取记忆系统状态
        
        Returns:
            dict: 记忆系统状态
        """
        try:
            cmd = [self.openclaw_cmd, "memory", "status", "--json"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"⚠️ 获取状态失败: {result.stderr}")
                return {}
                
        except Exception as e:
            print(f"⚠️ API 调用失败: {e}")
            return {}
```

##### 2.2 增强碰撞引擎

在 `collider/collider.py` 中添加语义搜索功能：

```python
def fetch_related_memories(self, fragment_text):
    """
    使用 OpenClaw 语义搜索获取相关记忆
    
    Args:
        fragment_text: 碎片文本
    
    Returns:
        list: 相关记忆列表
    """
    try:
        from core.openclaw_api import OpenClawAPI
        
        api = OpenClawAPI()
        results = api.search_memory(fragment_text, max_results=5)
        
        if results:
            print(f"🔍 找到 {len(results)} 条相关记忆")
            return results
        else:
            return []
            
    except Exception as e:
        print(f"⚠️ 语义搜索失败: {e}")
        return []

def collide_with_memory_search(self, fragment1, fragment2):
    """
    结合语义搜索的碰撞
    
    Args:
        fragment1: 碎片1
        fragment2: 碎片2
    
    Returns:
        str: 碰撞结果
    """
    # 获取相关记忆
    memories1 = self.fetch_related_memories(fragment1)
    memories2 = self.fetch_related_memories(fragment2)
    
    # 构建上下文
    context = f"""
## 碎片 1
{fragment1}

## 相关记忆
{chr(10).join([f"- {m.get('text', '')}" for m in memories1])}

## 碎片 2
{fragment2}

## 相关记忆
{chr(10).join([f"- {m.get('text', '')}" for m in memories2])}
"""
    
    # 使用 AI 生成洞见
    return self.generate_insight_with_context(context)
```

---

### 3. 标签集成（优先级：中）

#### 目标
将洞见标签与 OpenClaw 记忆标签系统集成。

#### 实现方案

##### 3.1 统一标签格式

使用 OpenClaw 的标准标签格式：

```python
# OpenClaw 标签格式：#tag
# 示例：#工作 #项目 #重要 #洞见

INSIGHT_TAGS = {
    "reinforce": "#洞见 #强化",
    "new": "#洞见 #新发现",
    "collision": "#洞见 #碰撞",
    "question": "#洞见 #追问",
    "mutation": "#洞见 #变异"
}

def format_tags(tag_type, custom_tags=None):
    """
    格式化标签
    
    Args:
        tag_type: 标签类型
        custom_tags: 自定义标签
    
    Returns:
        str: 格式化后的标签字符串
    """
    base_tag = INSIGHT_TAGS.get(tag_type, "#洞见")
    
    if custom_tags:
        custom_tags_str = " ".join([f"#{tag}" for tag in custom_tags])
        return f"{base_tag} {custom_tags_str}"
    
    return base_tag
```

##### 3.2 标签搜索

添加基于标签的搜索功能：

```python
def search_by_tag(self, tag):
    """
    根据标签搜索洞见
    
    Args:
        tag: 标签名称
    
    Returns:
        list: 匹配的洞见列表
    """
    try:
        from core.openclaw_api import OpenClawAPI
        
        api = OpenClawAPI()
        results = api.search_memory(f"#{tag}")
        
        return [r for r in results if f"#{tag}" in r.get("text", "")]
        
    except Exception as e:
        print(f"⚠️ 标签搜索失败: {e}")
        return []
```

---

### 4. 自动触发（优先级：低）

#### 目标
在新增记忆时自动触发洞见生成。

#### 实现方案

##### 4.1 使用 OpenClaw Hooks

创建 OpenClaw Hook 脚本：

```bash
#!/bin/bash
# ~/.openclaw/hooks/post-memory-save.sh

# 触发洞见系统
cd /workspace/projects/extensions/insight-system
python3 core/insight_system.py
```

##### 4.2 使用文件监控

使用 Python 的 `watchdog` 库监控记忆文件变化：

```python
#!/usr/bin/env python3
"""
记忆文件监控器
自动触发洞见生成
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class MemoryFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            print(f"📝 检测到记忆文件变化: {event.src_path}")
            self.trigger_insight_generation()
    
    def trigger_insight_generation(self):
        """触发洞见生成"""
        import subprocess
        subprocess.run([
            "python3",
            "/workspace/projects/extensions/insight-system/core/insight_system.py"
        ])

def main():
    path = "/workspace/projects/workspace/memory"
    event_handler = MemoryFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    print(f"🔍 监控记忆目录: {path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
```

---

## 📋 实施优先级

| 功能 | 优先级 | 难度 | 预计时间 |
|------|--------|------|----------|
| 双向同步 | 高 | 低 | 2小时 |
| API 调用 | 中 | 中 | 3小时 |
| 标签集成 | 中 | 低 | 1小时 |
| 自动触发 | 低 | 中 | 4小时 |

**建议实施顺序：**
1. 双向同步（立即实施）
2. API 调用（下一步）
3. 标签集成（与 API 调用同时）
4. 自动触发（可选功能）

---

## 🧪 测试计划

### 1. 双向同步测试

```bash
# 1. 运行洞见系统
python3 core/insight_system.py

# 2. 检查 MEMORY.md 是否更新
cat /workspace/projects/workspace/MEMORY.md

# 3. 检查今日记忆文件
cat /workspace/projects/workspace/memory/$(date +%Y-%m-%d).md
```

### 2. API 调用测试

```bash
# 1. 测试语义搜索
python3 -c "from core.openclaw_api import OpenClawAPI; api = OpenClawAPI(); print(api.search_memory('测试查询'))"

# 2. 测试记忆索引
openclaw memory index --force
```

### 3. 标签集成测试

```bash
# 1. 搜索带标签的洞见
openclaw memory search "#洞见"

# 2. 搜索特定类型的洞见
openclaw memory search "#碰撞"
```

---

## 📚 相关文档

- [OpenClaw Memory CLI](https://docs.openclaw.ai/cli/memory)
- [OpenClaw Memory System](https://docs.openclaw.ai/concepts/memory)
- [OpenClaw Hooks](https://docs.openclaw.ai/cli/hooks)
