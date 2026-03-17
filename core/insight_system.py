#!/usr/bin/env python3
"""
神经元洞见系统 v2.0
洞见提取 + 降噪 + 深度追问
"""

import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# 导入配置加载器
import sys
sys.path.insert(0, os.path.dirname(__file__))
from utils.config_loader import get_config, get_workspace, get_memory_dir, get_state_file

# 导入洞见提取器
try:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from insight_extractor import InsightExtractor
    EXTRACTOR_AVAILABLE = True
except ImportError:
    EXTRACTOR_AVAILABLE = False
    print("⚠️ 洞见提取器未加载")

# 尝试导入多模态记忆系统
try:
    from multimodal_memory import MultimodalMemory
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    print("⚠️ 多模态记忆系统未加载")

# 获取配置
_config = get_config()
WORKSPACE = str(_config.workspace)
MEMORY_DIR = str(_config.memory_dir)
STATE_FILE = str(_config.state_file)
VECTOR_DB = str(_config.vector_db)
CONFIG = {
    "threshold": _config.get("insight.threshold", 0.7),
    "max_tokens_per_summary": _config.get("insight.max_tokens_per_summary", 200),
}


class NeuronInsight:
    def __init__(self):
        self.state = self.load_state()
        self.fragments = []
        self.new_fragments = []
        self.extractor = InsightExtractor() if EXTRACTOR_AVAILABLE else None
        
        # 统计
        self.stats = {
            "insights_created": 0,
            "tasks_filtered": 0,
            "noise_filtered": 0,
            "conversations_filtered": 0
        }
        
        # 追踪本次运行新创建的洞见ID
        self.new_insight_ids = []
    
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
        
        self.sync_to_openclaw_memory()
        
        if MULTIMODAL_AVAILABLE:
            self.sync_to_multimodal()
        
        # 更新模糊层（如果有新洞见）
        if self.new_insight_ids:
            self.update_fuzzy_layer()
    
    def update_fuzzy_layer(self):
        """更新三层记忆的模糊层"""
        try:
            from three_layer_memory import update_fuzzy_layer
            fuzzy = update_fuzzy_layer()
            print(f"🔮 模糊层已更新 ({fuzzy['stats']['token_estimate']} tokens)")
        except ImportError:
            pass  # 三层记忆系统不可用时静默跳过
    
    def sync_to_openclaw_memory(self):
        """将新洞见同步到 OpenClaw 记忆文件（只写入本次新创建的洞见）"""
        if not self.new_insight_ids:
            print("📊 本次无新洞见，跳过同步")
            return
        
        try:
            from memory_writer import MemoryWriter
            writer = MemoryWriter()
            
            # 只同步新创建的洞见
            new_insights = [i for i in self.state.get("insights", []) 
                           if i.get("id") in self.new_insight_ids]
            
            written_count = 0
            for insight in new_insights:
                success = writer.write_to_daily(
                    insight.get("insight_text", ""),
                    tags=insight.get("tags", ["洞见", "新发现"]),
                    source="insight"
                )
                if success:
                    written_count += 1
            
            print(f"📊 已同步 {written_count} 条新洞见到记忆文件")
        except Exception as e:
            print(f"⚠️ 同步失败: {e}")
    
    def sync_to_multimodal(self):
        """同步到多模态记忆（只写入本次新创建的洞见，带去重）"""
        if not self.new_insight_ids:
            return
        
        try:
            memory = MultimodalMemory()
            new_insights = [i for i in self.state.get("insights", []) 
                           if i.get("id") in self.new_insight_ids]
            
            added_count = 0
            skip_count = 0
            for insight in new_insights:
                insight_text = insight.get("insight_text", "") or insight.get("text", "")
                # 确保文本不为空且长度足够
                if insight_text and len(insight_text.strip()) >= 2:
                    # 去重检查已内置在 add_text 中
                    result = memory.add_text(
                        insight_text,
                        {"source": "insight", "tags": insight.get("tags", [])}
                    )
                    if result:
                        added_count += 1
                    else:
                        skip_count += 1
                else:
                    skip_count += 1
            
            stats = memory.get_stats()
            print(f"📊 多模态记忆: {stats['total_memories']} 条 (新增 {added_count}, 跳过 {skip_count})")
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
        memory_files = sorted(Path(MEMORY_DIR).glob("*.md"))
        
        for mf in memory_files[-3:]:
            try:
                content = mf.read_text()
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
    
    def add_fragment(self, text, source="unknown"):
        fragment = {
            "text": text[:500],  # 允许更长，因为需要提取
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
        words1 = set(re.findall(r'[\w\u4e00-\u9fff]+', text1.lower()))
        words2 = set(re.findall(r'[\w\u4e00-\u9fff]+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def check_connections(self, fragment):
        """检查与已有洞见的连接"""
        max_sim = 0.0
        best_match = None
        
        for insight in self.state["insights"]:
            # 比较洞见文本，而不是原始碎片
            insight_text = insight.get("insight_text", insight.get("text", ""))
            sim = self.calculate_similarity(fragment["text"], insight_text)
            if sim > max_sim:
                max_sim = sim
                best_match = insight
        
        return max_sim, best_match
    
    def process(self):
        """处理所有碎片 - v2.0 带洞见提取"""
        insights_generated = []
        
        for fragment in self.fragments:
            # 1. 使用提取器判断类型
            if self.extractor:
                extracted = self.extractor.extract(fragment["text"])
                frag_type = extracted.get("type", "noise")
                insight_text = extracted.get("insight_text")
                follow_up = extracted.get("follow_up_question")
                confidence = extracted.get("confidence", 0.5)
            else:
                # 无提取器时，使用规则判断
                frag_type, insight_text, follow_up, confidence = self.rule_based_classify(fragment["text"])
            
            # 2. 根据类型处理
            if frag_type == "task":
                self.stats["tasks_filtered"] += 1
                # 不存储，但记录处理过
                continue
            
            elif frag_type == "noise":
                self.stats["noise_filtered"] += 1
                continue
            
            elif frag_type == "conversation":
                self.stats["conversations_filtered"] += 1
                continue
            
            elif frag_type == "insight":
                # 3. 检查与已有洞见的连接
                sim, match = self.check_connections(fragment)
                
                if sim >= CONFIG["threshold"] and match:
                    # 强化已有洞见
                    match_id = match.get("id", len(self.state["insights"]))
                    self.state["connections"][str(match_id)] = \
                        self.state["connections"].get(str(match_id), 0.1) + 0.1
                    
                    # 更新洞见权重
                    match["weight"] = match.get("weight", 0.5) + 0.1
                    match["reinforced_at"] = datetime.now().isoformat()
                    
                    insights_generated.append({
                        "type": "reinforce",
                        "insight_text": insight_text,
                        "similar_to": match.get("insight_text", "")[:50],
                        "similarity": round(sim, 2)
                    })
                else:
                    # 4. 创建新洞见
                    new_insight = {
                        "id": len(self.state["insights"]) + 1,
                        "text": fragment["text"][:200],  # 原文
                        "insight_text": insight_text,  # 提取的洞见
                        "follow_up_question": follow_up,
                        "confidence": confidence,
                        "source": fragment["source"],
                        "created": fragment["timestamp"],
                        "weight": 0.5,
                        "type": "insight"
                    }
                    self.state["insights"].append(new_insight)
                    self.new_insight_ids.append(new_insight["id"])  # 记录新洞见ID
                    self.stats["insights_created"] += 1
                    
                    insights_generated.append({
                        "type": "new",
                        "insight_text": insight_text[:50],
                        "follow_up": follow_up
                    })
            
            self.state["processed_hashes"].append(fragment["hash"])
        
        self.forget_old()
        return insights_generated
    
    def rule_based_classify(self, text):
        """规则洞见分类（无LLM时备用）"""
        text = text.strip()
        
        # 任务关键词
        task_keywords = ["查看", "查询", "汇报", "列出", "下载", "上传", "发送", "运行", "执行"]
        if any(kw in text for kw in task_keywords):
            return "task", None, None, 0.8
        
        # 对话关键词
        if any(kw in text for kw in ["怎么", "为什么", "是什么", "如何", "吗？", "呢"]):
            return "conversation", None, None, 0.6
        
        # 洞见关键词
        insight_keywords = ["我发现", "我意识到", "洞见", "本质", "核心", "关键", "其实", "真正的", "意义"]
        if any(kw in text for kw in insight_keywords):
            # 尝试提取洞见文本
            for kw in insight_keywords:
                if kw in text:
                    idx = text.index(kw)
                    insight = text[idx:idx+100]
                    break
            else:
                insight = text[:100]
            
            return "insight", insight, "这为什么重要？", 0.7
        
        # 默认噪音
        return "noise", None, None, 0.5
    
    def forget_old(self):
        """遗忘机制"""
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
            "real_insights": len([i for i in self.state["insights"] if i.get("type") == "insight"]),
            "connections": len(self.state["connections"]),
            "run_count": self.state["run_count"],
            "stats": self.stats
        }


def main():
    print("🧠 神经元洞见系统 v2.0 启动")
    
    insight = NeuronInsight()
    
    # 1. 收集碎片
    queue_fragments = insight.fetch_queue_fragments()
    for frag in queue_fragments:
        insight.add_fragment(frag["text"], source="queue")
    
    memory_fragments = insight.fetch_memory_fragments()
    for frag in memory_fragments:
        insight.add_fragment(frag, source="memory")
    
    # 2. 处理（带提取）
    results = insight.process()
    
    # 3. 输出
    summary = insight.generate_summary()
    print(f"\n📊 状态:")
    print(f"   总碎片: {summary['fragments_processed']}")
    print(f"   真洞见: {summary['real_insights']}")
    print(f"   过滤 - 任务: {summary['stats']['tasks_filtered']}, 噪音: {summary['stats']['noise_filtered']}, 对话: {summary['stats']['conversations_filtered']}")
    
    if results:
        print(f"\n💡 本次产生 {len(results)} 个洞见:")
        for r in results[:5]:
            if r["type"] == "new":
                print(f"   ✨ 新洞见: {r['insight_text']}")
                if r.get("follow_up"):
                    print(f"      ❓ 追问: {r['follow_up']}")
            else:
                print(f"   🔁 强化: {r.get('similar_to', 'N/A')[:30]}")
    
    insight.save_state()
    print("\n✅ 运行完成")


if __name__ == "__main__":
    main()
