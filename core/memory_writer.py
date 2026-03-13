#!/usr/bin/env python3
"""
OpenClaw 记忆写入器
将洞见写入 OpenClaw 的 MEMORY.md 和每日记忆文件
"""

import os
from datetime import datetime
from pathlib import Path

class MemoryWriter:
    """OpenClaw 记忆文件写入器"""
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = workspace
        self.memory_file = f"{workspace}/MEMORY.md"
        self.daily_memory_dir = f"{workspace}/memory"
    
    def ensure_directories(self):
        """确保记忆目录存在"""
        Path(self.daily_memory_dir).mkdir(parents=True, exist_ok=True)
    
    def write_insight(self, insight, tags=None, source="collision"):
        """
        将洞见写入 MEMORY.md
        
        Args:
            insight: 洞见内容
            tags: 标签列表
            source: 来源类型（collision, reinforce, question, mutation）
        """
        self.ensure_directories()
        
        # 构建洞见条目
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        tag_str = self._format_tags(tags, source)
        
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
    
    def write_to_daily(self, insight, tags=None, source="collision"):
        """
        将洞见写入今日记忆文件
        
        Args:
            insight: 洞见内容
            tags: 标签列表
            source: 来源类型
        """
        self.ensure_directories()
        
        # 生成今日文件名
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = f"{self.daily_memory_dir}/{today}.md"
        
        # 构建洞见条目
        timestamp = datetime.now().strftime("%H:%M")
        tag_str = self._format_tags(tags, source)
        
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
    
    def write_question(self, question, context=None):
        """
        将追问写入今日记忆文件
        
        Args:
            question: 追问内容
            context: 上下文信息
        """
        self.ensure_directories()
        
        # 生成今日文件名
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = f"{self.daily_memory_dir}/{today}.md"
        
        # 构建追问条目
        timestamp = datetime.now().strftime("%H:%M")
        
        entry = f"""
### ❓ 追问 ({timestamp})

{question}

#追问 #需要思考
"""
        
        if context:
            entry += f"\n**上下文**: {context}\n"
        
        # 追加或创建文件
        if os.path.exists(daily_file):
            with open(daily_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            header = f"# {today} 记忆\n\n"
            with open(daily_file, 'w', encoding='utf-8') as f:
                f.write(header + entry)
        
        print(f"✅ 追问已写入 {daily_file}")
    
    def write_collision(self, fragment1, fragment2, insight, tags=None):
        """
        将碰撞结果写入记忆文件
        
        Args:
            fragment1: 碎片1
            fragment2: 碎片2
            insight: 碰撞产生的洞见
            tags: 标签列表
        """
        self.ensure_directories()
        
        # 生成今日文件名
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = f"{self.daily_memory_dir}/{today}.md"
        
        # 构建碰撞条目
        timestamp = datetime.now().strftime("%H:%M")
        tag_str = self._format_tags(tags, "collision")
        
        entry = f"""
### ⚡ 碰撞洞见 ({timestamp})

**碎片 1**: {fragment1[:100]}...

**碎片 2**: {fragment2[:100]}...

**洞见**: {insight}

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
        
        print(f"✅ 碰撞洞见已写入 {daily_file}")
    
    def _format_tags(self, tags, source):
        """
        格式化标签
        
        Args:
            tags: 标签列表
            source: 来源类型
        
        Returns:
            str: 格式化后的标签字符串
        """
        # 基础标签
        base_tags = ["#洞见"]
        
        # 根据来源添加标签
        source_tags = {
            "collision": "#碰撞",
            "reinforce": "#强化",
            "question": "#追问",
            "mutation": "#变异",
            "new": "#新发现"
        }
        
        if source in source_tags:
            base_tags.append(source_tags[source])
        
        # 添加自定义标签
        if tags:
            for tag in tags:
                if not tag.startswith("#"):
                    tag = f"#{tag}"
                base_tags.append(tag)
        
        return " ".join(base_tags)


def main():
    """测试写入器"""
    writer = MemoryWriter()
    
    # 测试写入洞见
    writer.write_insight(
        "这是一个测试洞见，验证写入功能是否正常。",
        tags=["测试", "示例"],
        source="collision"
    )
    
    # 测试写入今日记忆
    writer.write_to_daily(
        "这是另一个测试洞见，写入今日记忆文件。",
        tags=["测试"],
        source="new"
    )
    
    # 测试写入追问
    writer.write_question(
        "这个洞见对你有什么启发？",
        context="测试上下文"
    )
    
    # 测试写入碰撞
    writer.write_collision(
        "碎片1的内容",
        "碎片2的内容",
        "这是碰撞产生的洞见",
        tags=["创新"]
    )


if __name__ == "__main__":
    main()
