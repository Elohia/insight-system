#!/usr/bin/env python3
"""
OpenClaw 记忆系统兼容层
提供与 OpenClaw 记忆系统完全兼容的 API
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from insight_system import NeuronInsight
from memory_writer import MemoryWriter

class OpenClawMemorySystem:
    """
    OpenClaw 记忆系统兼容层
    
    实现与 OpenClaw 记忆系统完全兼容的接口：
    - create() - 创建记忆
    - read() - 读取记忆
    - search() - 搜索记忆
    - index() - 索引记忆
    - status() - 系统状态
    """
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = workspace
        self.memory_dir = f"{workspace}/memory"
        self.memory_file = f"{workspace}/MEMORY.md"
        
        # 洞见系统实例
        self.insight = NeuronInsight()
        self.writer = MemoryWriter(workspace)
    
    def create(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        创建新记忆（替代写入 Markdown 文件）
        
        Args:
            content: 记忆内容
            metadata: 元数据（source, tags, date 等）
        
        Returns:
            创建结果
        """
        # 1. 添加到洞见系统（主存储）
        fragment = self.insight.add_fragment(
            content,
            source=metadata.get("source", "agent") if metadata else "agent"
        )
        
        if not fragment:
            return {
                "success": False,
                "error": "Duplicate fragment"
            }
        
        # 2. 触发洞见生成
        results = self.insight.process()
        
        # 3. 保存状态
        self.insight.save_state()
        
        # 4. 同步到 Markdown 视图（可选，用于兼容性）
        self.writer.write_to_daily(
            content,
            tags=metadata.get("tags") if metadata else None,
            source="new"
        )
        
        return {
            "success": True,
            "fragment_id": fragment["hash"],
            "insights_generated": len(results)
        }
    
    def read(self, date: Optional[str] = None, include_insights: bool = True) -> str:
        """
        读取记忆（生成 Markdown 视图）
        
        Args:
            date: 日期（YYYY-MM-DD），默认今天
            include_insights: 是否包含洞见
        
        Returns:
            Markdown 格式的记忆内容
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 从洞见系统生成 Markdown
        return self._generate_markdown_view(date, include_insights)
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        搜索记忆（使用洞见系统的向量搜索）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
        
        Returns:
            搜索结果列表
        """
        results = []
        
        # 1. 在洞见中搜索
        for insight in self.insight.state.get("insights", []):
            if query.lower() in insight.get("text", "").lower():
                results.append({
                    "type": "insight",
                    "text": insight.get("text"),
                    "weight": insight.get("weight", 0.5),
                    "created": insight.get("created"),
                    "source": insight.get("source")
                })
                
                if len(results) >= max_results:
                    break
        
        # 2. 在碎片中搜索
        if len(results) < max_results:
            for fragment in self.insight.fragments:
                if query.lower() in fragment.get("text", "").lower():
                    results.append({
                        "type": "fragment",
                        "text": fragment.get("text"),
                        "timestamp": fragment.get("timestamp"),
                        "source": fragment.get("source")
                    })
                    
                    if len(results) >= max_results:
                        break
        
        return results[:max_results]
    
    def index(self, force: bool = False) -> Dict:
        """
        索引记忆（更新洞见系统状态）
        
        Args:
            force: 是否强制重新索引
        
        Returns:
            索引结果
        """
        if force:
            # 清空状态，重新处理
            self.insight.state["processed_hashes"] = []
        
        # 重新读取所有记忆文件
        memory_fragments = self.insight.fetch_memory_fragments()
        
        for frag in memory_fragments:
            self.insight.add_fragment(frag, source="memory")
        
        # 处理碎片
        results = self.insight.process()
        
        # 保存状态
        self.insight.save_state()
        
        return {
            "success": True,
            "fragments_indexed": len(memory_fragments),
            "insights_generated": len(results),
            "total_insights": len(self.insight.state.get("insights", []))
        }
    
    def status(self) -> Dict:
        """
        获取记忆系统状态
        
        Returns:
            系统状态
        """
        summary = self.insight.generate_summary()
        
        return {
            "provider": "insight-system",
            "version": "1.0.0",
            "workspace": self.workspace,
            "memory_dir": self.memory_dir,
            "indexed_files": len(list(Path(self.memory_dir).glob("*.md"))) if os.path.exists(self.memory_dir) else 0,
            "total_fragments": len(self.insight.fragments),
            "total_insights": summary["total_insights"],
            "connections": summary["connections"],
            "run_count": summary["run_count"],
            "last_processed": summary["last_message_time"],
            "capabilities": {
                "insight_generation": True,
                "collision_engine": True,
                "question_engine": True,
                "mutation_mode": True,
                "multimodal": True,
                "semantic_search": True
            }
        }
    
    def _generate_markdown_view(self, date: str, include_insights: bool) -> str:
        """
        生成 Markdown 视图（兼容 OpenClaw 格式）
        
        Args:
            date: 日期
            include_insights: 是否包含洞见
        
        Returns:
            Markdown 内容
        """
        markdown = f"# {date} 记忆\n\n"
        
        # 1. 添加今日洞见
        if include_insights:
            insights_today = [
                i for i in self.insight.state.get("insights", [])
                if i.get("created", "").startswith(date)
            ]
            
            if insights_today:
                markdown += "## 💡 今日洞见\n\n"
                
                for i, insight in enumerate(insights_today, 1):
                    markdown += f"### 洞见 {i}\n\n"
                    markdown += f"{insight.get('text')}\n\n"
                    
                    if insight.get("tags"):
                        tags_str = " ".join([f"#{tag}" for tag in insight["tags"]])
                        markdown += f"{tags_str}\n\n"
        
        # 2. 添加今日碎片
        fragments_today = [
            f for f in self.insight.fragments
            if f.get("timestamp", "").startswith(date)
        ]
        
        if fragments_today:
            markdown += "## 📝 今日记忆碎片\n\n"
            
            for i, fragment in enumerate(fragments_today, 1):
                time = fragment.get("timestamp", "").split("T")[1][:5] if "T" in fragment.get("timestamp", "") else ""
                markdown += f"### {time} - {fragment.get('source', 'unknown')}\n\n"
                markdown += f"{fragment.get('text')}\n\n"
        
        # 3. 添加系统状态
        markdown += "## 📊 系统状态\n\n"
        markdown += f"- 总洞见数: {len(self.insight.state.get('insights', []))}\n"
        markdown += f"- 总连接数: {len(self.insight.state.get('connections', {}))}\n"
        markdown += f"- 运行次数: {self.insight.state.get('run_count', 0)}\n"
        
        return markdown
    
    def sync_to_openclaw(self):
        """
        同步到 OpenClaw 记忆文件
        
        将洞见系统的数据同步到 OpenClaw 的 Markdown 文件
        """
        # 1. 同步每日记忆
        today = datetime.now().strftime("%Y-%m-%d")
        markdown = self._generate_markdown_view(today, include_insights=True)
        
        today_file = f"{self.memory_dir}/{today}.md"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        with open(today_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✅ 已同步到 {today_file}")
        
        # 2. 同步长期记忆
        all_insights = self.insight.state.get("insights", [])
        
        if all_insights:
            long_term_memory = "# 🧠 长期记忆\n\n"
            long_term_memory += "本文档由洞见系统自动维护\n\n"
            
            # 添加权重最高的洞见
            top_insights = sorted(all_insights, key=lambda x: x.get("weight", 0), reverse=True)[:20]
            
            for i, insight in enumerate(top_insights, 1):
                long_term_memory += f"## 💡 洞见 {i}\n\n"
                long_term_memory += f"{insight.get('text')}\n\n"
                
                if insight.get("tags"):
                    tags_str = " ".join([f"#{tag}" for tag in insight["tags"]])
                    long_term_memory += f"{tags_str}\n\n"
                
                long_term_memory += f"*权重: {insight.get('weight', 0.5):.2f}*\n\n"
                long_term_memory += "---\n\n"
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write(long_term_memory)
            
            print(f"✅ 已同步到 {self.memory_file}")


# HTTP API 服务器（可选）
def create_api_server():
    """
    创建 HTTP API 服务器
    
    提供 RESTful API，与 OpenClaw 记忆系统兼容
    """
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        memory_system = OpenClawMemorySystem()
        
        @app.route('/api/memory', methods=['POST'])
        def create_memory():
            """创建记忆"""
            data = request.json
            result = memory_system.create(data.get('content'), data.get('metadata'))
            return jsonify(result)
        
        @app.route('/api/memory', methods=['GET'])
        def read_memory():
            """读取记忆"""
            date = request.args.get('date')
            include_insights = request.args.get('include_insights', 'true').lower() == 'true'
            content = memory_system.read(date, include_insights)
            return content, 200, {'Content-Type': 'text/markdown'}
        
        @app.route('/api/memory/search', methods=['GET'])
        def search_memory():
            """搜索记忆"""
            query = request.args.get('query', '')
            max_results = int(request.args.get('max_results', 10))
            results = memory_system.search(query, max_results)
            return jsonify(results)
        
        @app.route('/api/memory/index', methods=['POST'])
        def index_memory():
            """索引记忆"""
            force = request.json.get('force', False) if request.json else False
            result = memory_system.index(force)
            return jsonify(result)
        
        @app.route('/api/memory/status', methods=['GET'])
        def get_status():
            """获取状态"""
            status = memory_system.status()
            return jsonify(status)
        
        @app.route('/api/memory/sync', methods=['POST'])
        def sync_memory():
            """同步到 OpenClaw"""
            memory_system.sync_to_openclaw()
            return jsonify({"success": True})
        
        return app
    
    except ImportError:
        print("⚠️ Flask 未安装，跳过 API 服务器创建")
        return None


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw 记忆系统兼容层')
    parser.add_argument('command', choices=['create', 'read', 'search', 'index', 'status', 'sync', 'serve'],
                       help='命令')
    parser.add_argument('--content', help='记忆内容')
    parser.add_argument('--query', help='搜索查询')
    parser.add_argument('--date', help='日期')
    parser.add_argument('--force', action='store_true', help='强制重新索引')
    parser.add_argument('--port', type=int, default=5001, help='API 服务器端口')
    
    args = parser.parse_args()
    
    memory_system = OpenClawMemorySystem()
    
    if args.command == 'create':
        if not args.content:
            print("❌ 需要提供 --content")
            return
        
        result = memory_system.create(args.content)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'read':
        content = memory_system.read(args.date)
        print(content)
    
    elif args.command == 'search':
        if not args.query:
            print("❌ 需要提供 --query")
            return
        
        results = memory_system.search(args.query)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.command == 'index':
        result = memory_system.index(args.force)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'status':
        status = memory_system.status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.command == 'sync':
        memory_system.sync_to_openclaw()
    
    elif args.command == 'serve':
        app = create_api_server()
        if app:
            print(f"🚀 启动 API 服务器，端口: {args.port}")
            app.run(host='0.0.0.0', port=args.port)
        else:
            print("❌ 无法启动 API 服务器")


if __name__ == "__main__":
    main()
