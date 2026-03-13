#!/usr/bin/env python3
"""
神经元洞见系统 v1.0
全功能 + Token 优化 + 闭环自动化
支持多数据源：飞书消息、任务记录、文件变化
多模态支持：文本 + 图片 + 视频 向量化
"""

import os
import re
import json
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 尝试导入多模态记忆系统
try:
    import sys
    sys.path.insert(0, f"{os.path.dirname(__file__)}")
    from multimodal_memory import MultimodalMemory
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    print("⚠️ 多模态记忆系统未加载")

# 配置
WORKSPACE = "/workspace/projects/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"
STATE_FILE = f"{WORKSPACE}/.openclaw/insight-state.json"
VECTOR_DB = f"{WORKSPACE}/.openclaw/vector-db.json"
CONFIG = {
    "threshold": 0.7,
    "max_tokens_per_summary": 200,
    "forget_days": 30,
    "cache_size": 50,
}

class NeuronInsight:
    def __init__(self):
        self.state = self.load_state()
        self.fragments = []
        self.new_fragments = []  # 新增碎片
    
    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "last_processed": None,
            "processed_hashes": [],
            "insights": [],
            "connections": {},
            "run_count": 0,
            "last_message_time": None
        }
    
    def save_state(self):
        self.state["last_processed"] = datetime.now().isoformat()
        self.state["run_count"] += 1
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
        
        # 同步到 OpenClaw 记忆文件
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
                    tags=insight.get("tags", []),
                    source="reinforce" if insight.get("weight", 0.5) > 0.5 else "new"
                )
            
            print("📊 已同步洞见到 OpenClaw 记忆文件")
        except Exception as e:
            print(f"⚠️ OpenClaw 记忆同步失败: {e}")
    
    def sync_to_multimodal(self):
        """将洞见同步到多模态记忆系统"""
        try:
            memory = MultimodalMemory()
            
            # 同步最新的洞见
            for insight in self.state.get("insights", [])[-5:]:  # 最近5条
                # 检查是否已存在
                existing = [v for v in memory.db.get("vectors", []) 
                          if v.get("type") == "text" and insight.get("text", "").startswith(v.get("content", "")[:50])]
                if not existing:
                    memory.add_text(
                        insight.get("text", ""),
                        {"source": "insight", "tags": insight.get("tags", [])}
                    )
            
            # 统计
            stats = memory.get_stats()
            print(f"📊 多模态记忆: {stats['total_memories']} 条记忆")
        except Exception as e:
            print(f"⚠️ 多模态同步失败: {e}")
    
    def fetch_queue_fragments(self):
        """从消息队列获取碎片"""
        print("📥 读取消息队列...")
        queue_file = f"{WORKSPACE}/.openclaw/message-queue.json"
        
        if not os.path.exists(queue_file):
            return []
        
        try:
            with open(queue_file, 'r') as f:
                queue = json.load(f)
            
            fragments = []
            for q in queue:
                fragments.append({
                    "text": q["text"],
                    "source": q.get("source", "queue"),
                    "timestamp": q.get("timestamp", datetime.now().isoformat())
                })
            
            print(f"   读取到 {len(fragments)} 条消息")
            return fragments
            
        except Exception as e:
            print(f"⚠️ 读取队列失败: {e}")
            return []
    
    def fetch_memory_fragments(self):
        """从 memory 文件中提取碎片"""
        print("📥 读取记忆碎片...")
        
        fragments = []
        
        # 读取最近的 memory 文件
        memory_files = sorted(Path(MEMORY_DIR).glob("*.md"))
        
        for mf in memory_files[-3:]:  # 最近3个文件
            try:
                content = mf.read_text()
                
                # 提取标题下内容作为碎片
                lines = content.split('\n')
                current_section = ""
                
                for line in lines:
                    if line.startswith('## '):
                        if current_section:
                            fragments.append(current_section.strip())
                        current_section = line
                    elif line.startswith('### '):
                        if current_section:
                            fragments.append(current_section.strip())
                        current_section = line
                    else:
                        current_section += " " + line.strip()
                
                if current_section:
                    fragments.append(current_section.strip())
                    
            except Exception as e:
                print(f"⚠️ 读取 {mf} 失败: {e}")
        
        return fragments
    
    def fetch_task_fragments(self):
        """从飞书任务获取碎片"""
        # 简化处理
        return []
    
    def add_fragment(self, text, source="unknown"):
        fragment = {
            "text": text[:200],  # 限制长度
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.md5(text.encode()).hexdigest()
        }
        
        if fragment["hash"] in self.state["processed_hashes"]:
            return None
        
        self.fragments.append(fragment)
        if source == "new":
            self.new_fragments.append(fragment)
        return fragment
    
    def calculate_similarity(self, text1, text2):
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def check_connections(self, fragment):
        max_sim = 0.0
        best_match = None
        
        for insight in self.state["insights"]:
            sim = self.calculate_similarity(fragment["text"], insight["text"])
            if sim > max_sim:
                max_sim = sim
                best_match = insight
        
        return max_sim, best_match
    
    def process(self):
        """处理所有碎片"""
        insights_generated = []
        
        for fragment in self.fragments:
            sim, match = self.check_connections(fragment)
            
            if sim >= CONFIG["threshold"] and match:
                # 强化
                self.state["connections"][match["id"]] = \
                    self.state["connections"].get(match["id"], 0.1) + 0.1
                insights_generated.append({
                    "type": "reinforce",
                    "fragment": fragment,
                    "similar_to": match["text"][:50],
                    "similarity": round(sim, 2)
                })
            else:
                # 积累
                if sim < 0.3:
                    new_insight = {
                        "id": len(self.state["insights"]) + 1,
                        "text": fragment["text"][:100],
                        "source": fragment["source"],
                        "created": fragment["timestamp"],
                        "weight": 0.5
                    }
                    self.state["insights"].append(new_insight)
            
            self.state["processed_hashes"].append(fragment["hash"])
        
        self.forget_old()
        return insights_generated
    
    def forget_old(self):
        if len(self.state["connections"]) > CONFIG["cache_size"]:
            sorted_conn = sorted(
                self.state["connections"].items(),
                key=lambda x: x[1]
            )
            to_remove = sorted_conn[:len(sorted_conn) - CONFIG["cache_size"]]
            for k, _ in to_remove:
                del self.state["connections"][k]
    
    def generate_summary(self):
        return {
            "run_time": datetime.now().isoformat(),
            "fragments_processed": len(self.fragments),
            "new_fragments": len(self.new_fragments),
            "total_insights": len(self.state["insights"]),
            "connections": len(self.state["connections"]),
            "run_count": self.state["run_count"]
        }


def main():
    print("🧠 神经元洞见系统 v1.0 启动")
    
    insight = NeuronInsight()
    
    # 1. 收集碎片
    # 消息队列（主会话手动加入的）
    queue_fragments = insight.fetch_queue_fragments()
    for frag in queue_fragments:
        insight.add_fragment(frag["text"], source="queue")
    
    # 从记忆文件提取
    memory_fragments = insight.fetch_memory_fragments()
    for frag in memory_fragments:
        insight.add_fragment(frag, source="memory")
    
    # 3. 处理
    results = insight.process()
    
    # 4. 输出
    summary = insight.generate_summary()
    print(f"📊 状态: {summary}")
    
    if results:
        print(f"💡 产生 {len(results)} 个洞见/强化")
        for r in results[:3]:
            print(f"   - {r['type']}: {r.get('similar_to', r['fragment']['text'][:30])}")
    
    insight.save_state()
    print("✅ 运行完成")


if __name__ == "__main__":
    main()
