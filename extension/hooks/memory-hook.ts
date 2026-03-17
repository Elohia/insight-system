#!/usr/bin/env python3
"""
OpenClaw 记忆 Hook
拦截 OpenClaw 的记忆操作，转发到洞见系统
"""

import os
import sys
import json
from pathlib import Path

# 动态获取洞见系统路径
# 优先使用环境变量，其次使用相对于当前文件的路径
INSIGHT_SYSTEM_PATH = os.getenv(
    "INSIGHT_SYSTEM_PATH",
    str(Path(__file__).parent.parent.parent.parent)
)
sys.path.insert(0, f"{INSIGHT_SYSTEM_PATH}/core")

from memory_server import OpenClawMemorySystem


class MemoryHook:
    """
    OpenClaw 记忆 Hook
    
    拦截 OpenClaw 的记忆操作：
    - on_memory_write: 写入记忆时触发
    - on_memory_read: 读取记忆时触发
    - on_memory_search: 搜索记忆时触发
    """
    
    def __init__(self):
        self.memory_system = OpenClawMemorySystem()
        self.hook_name = "insight-memory"
    
    def on_memory_write(self, content: str, metadata: dict = None) -> dict:
        """
        记忆写入 Hook
        
        在 OpenClaw 写入记忆时触发
        
        Args:
            content: 记忆内容
            metadata: 元数据
        
        Returns:
            处理结果
        """
        print(f"[Hook] 拦截记忆写入: {content[:50]}...")
        
        # 1. 写入洞见系统
        result = self.memory_system.create(content, metadata)
        
        # 2. 返回结果
        return {
            "success": True,
            "hook": self.hook_name,
            "action": "memory_write",
            "insight_result": result
        }
    
    def on_memory_read(self, date: str = None) -> str:
        """
        记忆读取 Hook
        
        在 OpenClaw 读取记忆时触发
        
        Args:
            date: 日期
        
        Returns:
            记忆内容（Markdown 格式）
        """
        print(f"[Hook] 拦截记忆读取: {date or 'today'}")
        
        # 从洞见系统读取
        content = self.memory_system.read(date)
        
        return content
    
    def on_memory_search(self, query: str, max_results: int = 10) -> list:
        """
        记忆搜索 Hook
        
        在 OpenClaw 搜索记忆时触发
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
        
        Returns:
            搜索结果
        """
        print(f"[Hook] 拦截记忆搜索: {query}")
        
        # 使用洞见系统搜索
        results = self.memory_system.search(query, max_results)
        
        return results


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw 记忆 Hook')
    parser.add_argument('event', choices=['write', 'read', 'search'],
                       help='事件类型')
    parser.add_argument('--content', help='记忆内容')
    parser.add_argument('--date', help='日期')
    parser.add_argument('--query', help='搜索查询')
    parser.add_argument('--max-results', type=int, default=10, help='最大结果数')
    parser.add_argument('--metadata', help='元数据（JSON 格式）')
    
    args = parser.parse_args()
    
    hook = MemoryHook()
    
    if args.event == 'write':
        if not args.content:
            print("❌ 需要提供 --content")
            return
        
        metadata = json.loads(args.metadata) if args.metadata else None
        result = hook.on_memory_write(args.content, metadata)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.event == 'read':
        content = hook.on_memory_read(args.date)
        print(content)
    
    elif args.event == 'search':
        if not args.query:
            print("❌ 需要提供 --query")
            return
        
        results = hook.on_memory_search(args.query, args.max_results)
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
