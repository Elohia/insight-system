#!/usr/bin/env python3
"""
三层记忆系统 v1.0
- 模糊层 (Fuzzy Layer): 启动时加载，压缩摘要，快速唤醒
- 精确层 (Precise Layer): 按需加载，详细记忆片段
- 深度层 (Deep Layer): 按需加载，原始对话和完整上下文

设计原则：
1. 启动只加载模糊层，最小化 token 消耗
2. 精确层和深度层按需加载
3. 模糊层定期更新，保持时效性
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

WORKSPACE = "/workspace/projects/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"
STATE_FILE = f"{WORKSPACE}/.openclaw/insight-state.json"
FUZZY_LAYER_FILE = f"{WORKSPACE}/.openclaw/memory-fuzzy-layer.json"

# 三层记忆配置
CONFIG = {
    "fuzzy_layer": {
        "max_insights": 15,        # 模糊层最多保留15条洞见摘要
        "max_tokens": 800,         # 模糊层 token 上限
        "update_interval_hours": 6  # 更新间隔
    },
    "precise_layer": {
        "max_insights": 50,        # 精确层最多50条
        "search_top_k": 10         # 搜索返回数量
    },
    "deep_layer": {
        "max_days": 7,             # 深度层保留天数
        "max_entries": 100         # 最大条目数
    }
}


class ThreeLayerMemory:
    """三层记忆系统"""
    
    def __init__(self):
        self.fuzzy_layer = self.load_fuzzy_layer()
        self.precise_layer = None  # 延迟加载
        self.deep_layer = None     # 延迟加载
        
    # ==================== 模糊层 (启动加载) ====================
    
    def load_fuzzy_layer(self) -> Dict[str, Any]:
        """加载模糊层"""
        if os.path.exists(FUZZY_LAYER_FILE):
            try:
                with open(FUZZY_LAYER_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # 不存在则创建
        return self.generate_fuzzy_layer()
    
    def generate_fuzzy_layer(self) -> Dict[str, Any]:
        """生成模糊层（从洞见和记忆压缩）"""
        print("🔮 生成模糊层...")
        
        fuzzy = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "identity_summary": "",      # 身份摘要
            "key_insights": [],          # 关键洞见 (压缩后)
            "active_goals": [],          # 活跃目标
            "recent_themes": [],         # 最近主题
            "personality_traits": [],    # 人格特质
            "stats": {
                "total_insights": 0,
                "total_memories": 0,
                "token_estimate": 0
            }
        }
        
        # 1. 加载身份信息
        identity_file = f"{MEMORY_DIR}/IDENTITY.md"
        if os.path.exists(identity_file):
            with open(identity_file, 'r') as f:
                identity = f.read()
            fuzzy["identity_summary"] = self._compress_text(identity, 150)
        
        # 2. 加载洞见状态
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            
            insights = state.get("insights", [])
            fuzzy["stats"]["total_insights"] = len(insights)
            
            # 按权重和质量排序
            scored_insights = []
            for i in insights:
                if i.get("type") == "insight":
                    score = self._score_insight(i)
                    scored_insights.append((score, i))
            
            scored_insights.sort(key=lambda x: x[0], reverse=True)
            
            # 压缩洞见到模糊层
            for score, insight in scored_insights[:CONFIG["fuzzy_layer"]["max_insights"]]:
                compressed = self._compress_insight(insight)
                if compressed:
                    fuzzy["key_insights"].append(compressed)
            
            # 提取人格特质
            tags = []
            for i in insights:
                tags.extend(i.get("tags", []))
            from collections import Counter
            tag_counts = Counter(tags)
            fuzzy["personality_traits"] = [t for t, c in tag_counts.most_common(10) if c > 1]
        
        # 3. 加载活跃目标 (从 SOUL.md)
        soul_file = f"{MEMORY_DIR}/SOUL.md"
        if os.path.exists(soul_file):
            with open(soul_file, 'r') as f:
                soul = f.read()
            # 提取目标相关内容
            goals = self._extract_goals(soul)
            fuzzy["active_goals"] = goals[:5]
        
        # 4. 统计最近主题
        memory_files = sorted(Path(MEMORY_DIR).glob("*.md"))[-3:]
        themes = []
        for mf in memory_files:
            content = mf.read_text()
            themes.extend(self._extract_themes(content))
        fuzzy["recent_themes"] = list(set(themes))[:10]
        
        # 5. 估算 token
        fuzzy["stats"]["token_estimate"] = self._estimate_tokens(fuzzy)
        
        # 保存模糊层
        self.save_fuzzy_layer(fuzzy)
        
        return fuzzy
    
    def save_fuzzy_layer(self, fuzzy: Dict = None):
        """保存模糊层"""
        if fuzzy is None:
            fuzzy = self.fuzzy_layer
        
        os.makedirs(os.path.dirname(FUZZY_LAYER_FILE), exist_ok=True)
        with open(FUZZY_LAYER_FILE, 'w') as f:
            json.dump(fuzzy, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 模糊层已保存 (估算 {fuzzy['stats']['token_estimate']} tokens)")
    
    def get_fuzzy_context(self) -> str:
        """获取模糊层上下文（启动时调用）"""
        fuzzy = self.load_fuzzy_layer()
        
        lines = []
        
        # 身份
        if fuzzy.get("identity_summary"):
            lines.append(f"### 身份概要\n{fuzzy['identity_summary']}")
        
        # 关键洞见
        if fuzzy.get("key_insights"):
            lines.append("### 核心洞见")
            for i, insight in enumerate(fuzzy["key_insights"][:10], 1):
                lines.append(f"{i}. {insight}")
        
        # 活跃目标
        if fuzzy.get("active_goals"):
            lines.append("### 活跃目标")
            for goal in fuzzy["active_goals"][:5]:
                lines.append(f"- {goal}")
        
        # 人格特质
        if fuzzy.get("personality_traits"):
            traits = ", ".join(fuzzy["personality_traits"][:8])
            lines.append(f"### 人格特质\n{traits}")
        
        return "\n\n".join(lines)
    
    def should_update_fuzzy(self) -> bool:
        """检查是否需要更新模糊层"""
        if not os.path.exists(FUZZY_LAYER_FILE):
            return True
        
        try:
            with open(FUZZY_LAYER_FILE, 'r') as f:
                fuzzy = json.load(f)
            
            generated = datetime.fromisoformat(fuzzy.get("generated_at", "2000-01-01"))
            interval = timedelta(hours=CONFIG["fuzzy_layer"]["update_interval_hours"])
            
            return datetime.now() - generated > interval
        except:
            return True
    
    # ==================== 精确层 (按需加载) ====================
    
    def load_precise_layer(self, query: str = None) -> List[Dict]:
        """加载精确层（按需，可带查询）"""
        if not os.path.exists(STATE_FILE):
            return []
        
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        insights = [i for i in state.get("insights", []) if i.get("type") == "insight"]
        
        if query:
            # 按相关性过滤
            return self._search_insights(insights, query, CONFIG["precise_layer"]["search_top_k"])
        
        return insights[:CONFIG["precise_layer"]["max_insights"]]
    
    def get_precise_context(self, query: str) -> str:
        """获取精确层上下文（按需调用）"""
        insights = self.load_precise_layer(query)
        
        if not insights:
            return ""
        
        lines = ["### 相关洞见 (精确匹配)"]
        for i in insights:
            text = i.get("insight_text", i.get("text", ""))
            follow_up = i.get("follow_up_question", "")
            lines.append(f"- {text}")
            if follow_up:
                lines.append(f"  ❓ {follow_up}")
        
        return "\n".join(lines)
    
    # ==================== 深度层 (按需加载) ====================
    
    def load_deep_layer(self, date: str = None) -> str:
        """加载深度层（原始记忆文件）"""
        if date:
            # 加载特定日期
            file_path = f"{MEMORY_DIR}/{date}.md"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return f.read()
            return ""
        
        # 加载最近N天的记忆
        lines = []
        cutoff = datetime.now() - timedelta(days=CONFIG["deep_layer"]["max_days"])
        
        memory_files = sorted(Path(MEMORY_DIR).glob("*.md"))
        for mf in memory_files:
            try:
                # 从文件名提取日期
                date_str = mf.stem.split("-")[0:3]
                file_date = datetime.strptime("-".join(date_str), "%Y-%m-%d")
                
                if file_date >= cutoff:
                    content = mf.read_text()
                    # 压缩长文件
                    if len(content) > 2000:
                        content = content[:2000] + "\n... (已截断)"
                    lines.append(f"## {mf.stem}\n{content}")
            except:
                continue
        
        return "\n\n---\n\n".join(lines[-CONFIG["deep_layer"]["max_entries"]:])
    
    def get_deep_context(self, keywords: List[str] = None) -> str:
        """获取深度层上下文（按需调用）"""
        if not keywords:
            return self.load_deep_layer()
        
        # 搜索包含关键词的记忆
        lines = []
        memory_files = sorted(Path(MEMORY_DIR).glob("*.md"))
        
        for mf in memory_files:
            content = mf.read_text()
            # 检查是否包含任一关键词
            if any(kw.lower() in content.lower() for kw in keywords):
                # 提取相关段落
                paragraphs = self._extract_relevant_paragraphs(content, keywords)
                if paragraphs:
                    lines.append(f"## {mf.stem}\n" + "\n".join(paragraphs))
        
        return "\n\n---\n\n".join(lines)
    
    # ==================== 辅助方法 ====================
    
    def _compress_text(self, text: str, max_chars: int) -> str:
        """压缩文本到指定长度"""
        text = text.strip()
        if len(text) <= max_chars:
            return text
        # 简单截断，保留关键信息
        return text[:max_chars-3] + "..."
    
    def _compress_insight(self, insight: Dict) -> str:
        """压缩洞见到一句话"""
        # 优先使用 insight_text，其次 text
        text = insight.get("insight_text") or insight.get("text", "")
        if not text:
            return ""
        
        # 压缩到 100 字符以内
        if len(text) > 100:
            # 尝试截取核心部分
            sentences = text.replace("。", "。\n").split("\n")
            if sentences:
                text = sentences[0][:97] + "..."
            else:
                text = text[:97] + "..."
        
        return text.strip()
    
    def _score_insight(self, insight: Dict) -> float:
        """计算洞见质量分数"""
        score = 0.0
        
        # 有追问加分 (表示深度思考)
        if insight.get("follow_up_question"):
            score += 10
        
        # 有回答加分 (表示已探索)
        if insight.get("answer"):
            score += 15
        
        # 置信度
        score += (insight.get("confidence", 0.5)) * 10
        
        # 权重
        score += (insight.get("weight", 0.5)) * 10
        
        # 标签数量
        tags = insight.get("tags", [])
        score += len(tags) * 2
        
        # 时效性 (越新越好)
        created = insight.get("created", insight.get("created_at", ""))
        if created:
            try:
                created_date = datetime.fromisoformat(created.replace("Z", ""))
                days_old = (datetime.now() - created_date).days
                if days_old < 1:
                    score += 20
                elif days_old < 7:
                    score += 10
                elif days_old < 30:
                    score += 5
            except:
                pass
        
        return score
    
    def _extract_goals(self, text: str) -> List[str]:
        """从文本提取目标"""
        goals = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                goal = line.replace("- [ ]", "").replace("- [x]", "").strip()
                if goal:
                    goals.append(goal)
            elif line.startswith("目标:") or line.startswith("Goal:"):
                goal = line.split(":", 1)[1].strip()
                if goal:
                    goals.append(goal)
        return goals
    
    def _extract_themes(self, text: str) -> List[str]:
        """从文本提取主题关键词"""
        import re
        # 提取标题
        themes = []
        for match in re.finditer(r"#{1,3}\s+(.+)", text):
            theme = match.group(1).strip()
            if len(theme) > 2 and len(theme) < 30:
                themes.append(theme)
        return themes
    
    def _search_insights(self, insights: List[Dict], query: str, top_k: int) -> List[Dict]:
        """搜索相关洞见"""
        import re
        query_words = set(re.findall(r'[\w\u4e00-\u9fff]+', query.lower()))
        
        scored = []
        for insight in insights:
            text = insight.get("insight_text", "") + " " + insight.get("text", "")
            insight_words = set(re.findall(r'[\w\u4e00-\u9fff]+', text.lower()))
            
            overlap = len(query_words & insight_words)
            if overlap > 0:
                scored.append((overlap + self._score_insight(insight), insight))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_k]]
    
    def _extract_relevant_paragraphs(self, content: str, keywords: List[str]) -> List[str]:
        """提取包含关键词的段落"""
        paragraphs = content.split("\n\n")
        relevant = []
        
        for p in paragraphs:
            if any(kw.lower() in p.lower() for kw in keywords):
                # 截断过长段落
                if len(p) > 500:
                    p = p[:500] + "..."
                relevant.append(p)
        
        return relevant[:5]  # 每个文件最多5个段落
    
    def _estimate_tokens(self, fuzzy: Dict) -> int:
        """估算模糊层 token 数"""
        text = fuzzy.get("identity_summary", "")
        text += " ".join(fuzzy.get("key_insights", []))
        text += " ".join(fuzzy.get("active_goals", []))
        text += " ".join(fuzzy.get("recent_themes", []))
        text += " ".join(fuzzy.get("personality_traits", []))
        
        # 简单估算：中文 1.5 字符/token，英文 4 字符/token
        return int(len(text) / 2)


# ==================== 便捷函数 ====================

def get_startup_context() -> str:
    """启动时获取上下文（只加载模糊层）"""
    memory = ThreeLayerMemory()
    
    # 检查是否需要更新模糊层
    if memory.should_update_fuzzy():
        print("🔄 模糊层已过期，重新生成...")
        memory.fuzzy_layer = memory.generate_fuzzy_layer()
    
    return memory.get_fuzzy_context()


def get_context_by_need(layer: str = "fuzzy", query: str = None, keywords: List[str] = None) -> str:
    """按需获取上下文
    
    Args:
        layer: "fuzzy" | "precise" | "deep"
        query: 精确层搜索查询
        keywords: 深度层搜索关键词
    """
    memory = ThreeLayerMemory()
    
    if layer == "fuzzy":
        return memory.get_fuzzy_context()
    elif layer == "precise":
        return memory.get_precise_context(query)
    elif layer == "deep":
        return memory.get_deep_context(keywords)
    
    return ""


def update_fuzzy_layer():
    """手动更新模糊层"""
    memory = ThreeLayerMemory()
    memory.fuzzy_layer = memory.generate_fuzzy_layer()
    return memory.fuzzy_layer


if __name__ == "__main__":
    # 测试
    print("=" * 50)
    print("三层记忆系统测试")
    print("=" * 50)
    
    # 生成模糊层
    memory = ThreeLayerMemory()
    
    print("\n🔮 模糊层内容:")
    print(memory.get_fuzzy_context())
    
    print(f"\n📊 统计: {memory.fuzzy_layer['stats']}")
    
    print("\n✅ 测试完成")
