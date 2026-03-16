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
        """生成模糊层（工具思维导向）
        
        核心理念：弱模型 + 强工具链 + 工具思维 > 单一大模型
        关键不是"知道多少"，而是"知道该用什么"
        """
        print("🔮 生成模糊层（工具思维模式）...")
        
        fuzzy = {
            "version": "2.0",  # 升级版本，工具思维导向
            "generated_at": datetime.now().isoformat(),
            
            # === 工具思维核心 ===
            "tool_index": {},           # 工具索引：场景 -> 推荐工具
            "decision_patterns": [],    # 决策模式：问题类型 -> 解决策略
            "action_strategies": [],    # 行动策略：目标 -> 执行路径
            
            # === 降维后的知识 ===
            "key_insights": [],         # 关键洞见（精简）
            "personality_traits": [],   # 人格特质（影响决策风格）
            
            # === 统计 ===
            "stats": {
                "total_insights": 0,
                "total_memories": 0,
                "token_estimate": 0,
                "tool_usage": {}        # 工具使用统计
            }
        }
        
        # 1. 加载洞见状态，提取工具思维
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
            
            # === 提取工具索引 ===
            fuzzy["tool_index"] = self._extract_tool_index(scored_insights)
            
            # === 提取决策模式 ===
            fuzzy["decision_patterns"] = self._extract_decision_patterns(scored_insights)
            
            # === 提取行动策略 ===
            fuzzy["action_strategies"] = self._extract_action_strategies(scored_insights)
            
            # 压缩洞见（只保留最关键的）
            for score, insight in scored_insights[:CONFIG["fuzzy_layer"]["max_insights"]]:
                compressed = self._compress_insight(insight)
                if compressed:
                    fuzzy["key_insights"].append(compressed)
            
            # 提取人格特质（影响决策风格）
            tags = []
            for i in insights:
                tags.extend(i.get("tags", []))
            from collections import Counter
            tag_counts = Counter(tags)
            fuzzy["personality_traits"] = [t for t, c in tag_counts.most_common(10) if c > 1]
        
        # 2. 加载 SOUL.md 提取决策偏好
        soul_file = f"{MEMORY_DIR}/SOUL.md"
        if os.path.exists(soul_file):
            with open(soul_file, 'r') as f:
                soul = f.read()
            # 提取行动策略
            strategies = self._extract_strategies_from_soul(soul)
            fuzzy["action_strategies"].extend(strategies[:3])
        
        # 3. 统计工具使用
        fuzzy["stats"]["tool_usage"] = self._count_tool_usage(scored_insights if 'scored_insights' in dir() else [])
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
        """获取模糊层上下文（工具思维导向）
        
        输出：我知道该用什么，而不是我知道什么
        """
        fuzzy = self.load_fuzzy_layer()
        
        lines = []
        
        # === 核心理念 ===
        lines.append("### 🛠️ 工具思维")
        lines.append("> 弱模型 + 强工具链 + 工具思维 > 单一大模型")
        lines.append("> 关键不是'知道多少'，而是'知道该用什么'\n")
        
        # === 工具索引 ===
        if fuzzy.get("tool_index"):
            lines.append("### 📋 场景-工具索引")
            for scene, tools in list(fuzzy["tool_index"].items())[:8]:
                lines.append(f"- **{scene}** → {tools}")
        
        # === 决策模式 ===
        if fuzzy.get("decision_patterns"):
            lines.append("\n### 🎯 决策模式")
            for pattern in fuzzy["decision_patterns"][:5]:
                lines.append(f"- {pattern}")
        
        # === 行动策略 ===
        if fuzzy.get("action_strategies"):
            lines.append("\n### ⚡ 行动策略")
            for strategy in fuzzy["action_strategies"][:5]:
                lines.append(f"- {strategy}")
        
        # === 人格特质（影响决策风格）===
        if fuzzy.get("personality_traits"):
            traits = ", ".join(fuzzy["personality_traits"][:6])
            lines.append(f"\n### 🎭 决策风格\n{traits}")
        
        return "\n".join(lines)
    
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
        text = ""
        # 工具索引
        for scene, tools in fuzzy.get("tool_index", {}).items():
            text += scene + str(tools)
        # 决策模式
        text += " ".join(fuzzy.get("decision_patterns", []))
        # 行动策略
        text += " ".join(fuzzy.get("action_strategies", []))
        # 关键洞见
        text += " ".join(fuzzy.get("key_insights", []))
        # 人格特质
        text += " ".join(fuzzy.get("personality_traits", []))
        
        # 简单估算：中文 1.5 字符/token
        return int(len(text) / 1.5)
    
    # ==================== 工具思维提取方法 ====================
    
    def _extract_tool_index(self, scored_insights: List[tuple]) -> Dict[str, str]:
        """从洞见和工具使用记录中提取工具索引
        
        来源：
        1. 工具使用记录（实际成功的案例）
        2. 高质量洞见中的工具思维
        """
        tool_index = {}
        
        # 1. 从工具使用记录提取（优先，因为已验证）
        try:
            from tool_usage_recorder import get_recorder
            recorder = get_recorder()
            recorded_index = recorder.get_tool_index()
            tool_index.update(recorded_index)
        except ImportError:
            pass
        
        # 2. 从洞见中提取已验证的工具映射
        for score, insight in scored_insights:
            text = insight.get("insight_text", "") or insight.get("text", "")
            
            # 只从高质量洞见中提取
            if score < 15:
                continue
            
            # 检测场景-工具模式："X问题 → 用Y"
            if "→" in text or "->" in text:
                parts = text.replace("->", "→").split("→")
                if len(parts) >= 2:
                    scene = parts[0].strip()[:25]
                    tool = "→".join(p.strip() for p in parts[1:])[:40]
                    if scene and tool and scene not in tool_index:
                        tool_index[scene] = tool
        
        return tool_index
    
    def _extract_decision_patterns(self, scored_insights: List[tuple]) -> List[str]:
        """提取决策模式：只从已验证的高质量洞见中提取
        
        条件：有追问或回答（表示深度思考过）
        """
        patterns = []
        
        for score, insight in scored_insights:
            # 只从深度思考过的洞见提取
            if not (insight.get("follow_up_question") or insight.get("answer")):
                continue
            
            text = insight.get("insight_text", "") or insight.get("text", "")
            
            # 检测决策模式关键词
            if any(kw in text for kw in ["应该", "需要先", "策略", "原则", "关键是"]):
                if len(text) < 70:
                    patterns.append(text)
        
        return patterns[:6]
    
    def _extract_action_strategies(self, scored_insights: List[tuple]) -> List[str]:
        """提取行动策略：从实践验证的洞见和工具记录中提取"""
        strategies = []
        
        # 从工具使用记录获取成功模式
        try:
            from tool_usage_recorder import get_recorder
            recorder = get_recorder()
            strategies.extend(recorder.get_success_patterns()[:3])
        except ImportError:
            pass
        
        # 从洞见中补充
        for score, insight in scored_insights:
            if score < 20:
                continue
            
            text = insight.get("insight_text", "") or insight.get("text", "")
            
            if any(kw in text for kw in ["启动", "加载", "触发", "运行"]):
                if len(text) < 50:
                    strategies.append(text)
        
        return list(set(strategies))[:6]
    
    def _extract_strategies_from_soul(self, soul_text: str) -> List[str]:
        """从 SOUL.md 提取策略（用户的原始设定）"""
        strategies = []
        lines = soul_text.split("\n")
        
        for line in lines:
            line = line.strip()
            # 提取核心原则
            if line.startswith("- **") and "**:" in line:
                principle = line.replace("- **", "").split("**:")[0]
                desc = line.split("**:")[-1].strip() if "**:" in line else ""
                if desc and len(desc) < 50:
                    strategies.append(f"{principle}: {desc}")
        
        return strategies[:3]  # 限制数量
    
    def _count_tool_usage(self, scored_insights: List[tuple]) -> Dict[str, int]:
        """统计工具使用频率：从实际洞见中统计"""
        from collections import Counter
        
        usage = Counter()
        for score, insight in scored_insights:
            text = (insight.get("insight_text", "") or insight.get("text", "")).lower()
            
            # 只统计实际提到过的工具
            tools = ["搜索", "文档", "调试", "配置", "记忆", "洞见",
                     "文件", "图片", "网络", "压缩", "去重", "web_search",
                     "read_file", "edit_file", "exec_shell"]
            
            for tool in tools:
                if tool.lower() in text:
                    usage[tool] += 1
        
        return dict(usage.most_common(10))


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
