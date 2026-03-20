#!/usr/bin/env python3
"""
三层记忆 - 模糊而精准的上下文压缩

层级架构：
1. 模糊层（启动加载）~400 tokens
   - 水面状态概要
   - 热门标签云
   - 最近涟漪索引
   
2. 精确层（按需加载）
   - 相关涟漪详情
   - 共振分析
   
3. 深度层（按需加载）
   - 完整涟漪池
   - 潜意识快照

核心理念：模糊而精准
- 启动时只加载模糊层，极简概要
- 按需加载精确层，精准检索
- 深度层用于复盘和分析
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import sys

# Token 计算
try:
    import tiktoken
    _ENCODING = tiktoken.get_encoding("cl100k_base")  # GPT-4/3.5-turbo 编码
except ImportError:
    _ENCODING = None

def count_tokens(text: str) -> int:
    """准确计算 token 数"""
    if _ENCODING:
        return len(_ENCODING.encode(text))
    # 回退：简单估算
    return len(text) // 4

# 导入模块
sys.path.insert(0, os.path.dirname(__file__))
from ripple import Ripple, RipplePool, get_ripple_pool
from subconscious import SubconsciousMind, get_subconscious
from utils.config_loader import get_config

_config = get_config()


class FuzzyLayer:
    """
    模糊层 - 极简概要
    
    目标：~400 tokens 以内
    内容：水面状态 + 热门标签 + 最近涟漪索引
    """
    
    def __init__(self):
        self.ripple_pool = get_ripple_pool()
        self.subconscious = get_subconscious()
    
    def generate(self) -> str:
        """
        生成模糊层内容
        
        返回极简的启动上下文，用于 LLM 注入
        """
        surface = self.ripple_pool.get_surface_state()
        
        lines = [
            "# 🌊 水面状态",
            f"状态: {surface['surface_state']} | 温度: {surface['avg_temperature']}° | 涟漪: {surface['ripple_count']}",
            ""
        ]
        
        # 热门标签（最多5个）
        if surface['hot_tags']:
            lines.append(f"标签: {', '.join(surface['hot_tags'][:5])}")
            lines.append("")
        
        # 最近涟漪索引（最多5条）
        recent = self.ripple_pool.get_recent(5)
        if recent:
            lines.append("## 最近涟漪")
            for r in recent:
                # 极简格式：[温度] 内容前30字 #标签
                tags_str = f" #{' #'.join(r.tags[:2])}" if r.tags else ""
                content_short = r.content[:30] + "..." if len(r.content) > 30 else r.content
                lines.append(f"[{r.temperature}°] {content_short}{tags_str}")
            lines.append("")
        
        # 潜意识发现的模式（最多2条）
        patterns = self.subconscious.get_patterns()[:2]
        if patterns:
            lines.append("## 模式发现")
            for p in patterns:
                lines.append(f"- {p['description']}")
            lines.append("")
        
        # 反向提示（激发思考）
        lines.append("## 反向提示")
        questions = self._generate_questions(surface, recent)
        for q in questions:
            lines.append(f"? {q}")
        
        return '\n'.join(lines)
    
    def _generate_questions(self, surface: Dict, recent: List[Ripple]) -> List[str]:
        """
        生成反向提示 - 激发思考
        
        基于当前状态提出未回答的问题
        """
        questions = []
        
        # 基于水温
        avg_temp = surface['avg_temperature']
        if avg_temp > 70:
            questions.append("高水温状态是否意味着即将突破？")
        elif avg_temp < 30:
            questions.append("低水温是否需要更多输入刺激？")
        
        # 基于涟漪数量
        ripple_count = surface['ripple_count']
        if ripple_count > 10:
            questions.append("涟漪积累是否已足够产生洞见？")
        elif ripple_count < 3:
            questions.append("涟漪稀少，是否需要更多思考输入？")
        
        # 基于标签
        if len(surface['hot_tags']) > 3:
            questions.append(f"多个主题交织，{surface['hot_tags'][0]} 与 {surface['hot_tags'][1]} 是否存在关联？")
        
        return questions[:3]  # 最多3个问题
    
    def to_toon(self) -> str:
        """
        转换为 TOON 格式
        
        格式：
        fuzzy{state,temp,ripples,tags}:
         活跃,62.5,12,AI|意识|洞见
        
        recent[3]{temp,content,tags}:
         65,发现AI的连续性是幻觉,AI|意识
         60,工具思维比单模型更强,洞见|AI
        """
        surface = self.ripple_pool.get_surface_state()
        recent = self.ripple_pool.get_recent(3)
        
        lines = [
            f"fuzzy{{state,temp,ripples,tags}}:",
            f" {surface['surface_state']},{surface['avg_temperature']},{surface['ripple_count']},{'|'.join(surface['hot_tags'][:5])}",
            ""
        ]
        
        if recent:
            lines.append(f"recent[{len(recent)}]{{temp,content,tags}}:")
            for r in recent:
                content_short = r.content[:20] + "..." if len(r.content) > 20 else r.content
                lines.append(f" {r.temperature},{content_short},{'|'.join(r.tags)}")
        
        return '\n'.join(lines)
    
    def get_token_count(self) -> int:
        """准确计算 token 数"""
        content = self.generate()
        return count_tokens(content)


class PreciseLayer:
    """
    精确层 - 按需检索
    
    功能：
    - 关键词搜索涟漪
    - 按温度范围检索
    - 按标签检索
    - 共振分析
    """
    
    def __init__(self):
        self.ripple_pool = get_ripple_pool()
    
    def search(self, query: str, top_k: int = 5) -> List[Ripple]:
        """
        关键词搜索涟漪
        
        Args:
            query: 搜索关键词
            top_k: 返回数量
        
        Returns:
            匹配的涟漪列表
        """
        results = []
        query_lower = query.lower()
        
        for ripple in self.ripple_pool.ripples:
            score = 0
            
            # 内容匹配
            if query_lower in ripple.content.lower():
                score += 10
            
            # 标签匹配
            if any(query_lower in tag.lower() for tag in ripple.tags):
                score += 5
            
            # 温度权重（高温优先）
            score += ripple.temperature / 20
            
            if score > 0:
                results.append((score, ripple))
        
        # 按分数排序
        results.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in results[:top_k]]
    
    def by_temperature(self, min_temp: int = 0, max_temp: int = 100) -> List[Ripple]:
        """按温度范围检索"""
        return self.ripple_pool.get_by_temperature(min_temp, max_temp)
    
    def by_tags(self, tags: List[str]) -> List[Ripple]:
        """按标签检索"""
        return self.ripple_pool.get_by_tags(tags)
    
    def get_resonances(self) -> List[Dict]:
        """获取所有共振"""
        return self.ripple_pool.get_resonances()
    
    def generate(self, query: str = None, tags: List[str] = None, 
                 min_temp: int = None, max_temp: int = None) -> str:
        """
        生成精确层内容
        
        Args:
            query: 搜索关键词
            tags: 标签过滤
            min_temp: 最低温度
            max_temp: 最高温度
        
        Returns:
            精确层内容
        """
        lines = ["# 精确层 - 相关涟漪"]
        
        # 收集涟漪
        ripples = []
        
        if query:
            ripples = self.search(query)
            lines.append(f"\n## 搜索: {query}")
        elif tags:
            ripples = self.by_tags(tags)
            lines.append(f"\n## 标签: {', '.join(tags)}")
        elif min_temp is not None or max_temp is not None:
            min_t = min_temp or 0
            max_t = max_temp or 100
            ripples = self.by_temperature(min_t, max_t)
            lines.append(f"\n## 温度范围: {min_t}° - {max_t}°")
        else:
            ripples = self.ripple_pool.get_recent(10)
            lines.append("\n## 最近涟漪")
        
        # 输出涟漪详情
        for r in ripples:
            lines.append(f"\n### [{r.temperature}°] {r.content}")
            lines.append(f"时间: {r.timestamp[:19]}")
            lines.append(f"标签: {', '.join(r.tags)}")
            
            # 显示共振
            if r.resonances:
                lines.append(f"共振: {len(r.resonances)} 次")
        
        # 共振分析
        resonances = self.get_resonances()
        if resonances:
            lines.append(f"\n## 共振分析 ({len(resonances)} 组)")
            for res in resonances[:5]:
                lines.append(f"- {res['pattern']}")
        
        return '\n'.join(lines)


class DeepLayer:
    """
    深度层 - 完整数据
    
    功能：
    - 完整涟漪池
    - 潜意识快照
    - 导出分析
    """
    
    def __init__(self):
        self.ripple_pool = get_ripple_pool()
        self.subconscious = get_subconscious()
    
    def get_all_ripples(self) -> List[Ripple]:
        """获取所有涟漪"""
        return self.ripple_pool.ripples
    
    def get_all_resonances(self) -> List[Dict]:
        """获取所有共振"""
        return self.ripple_pool.resonances
    
    def get_all_snapshots(self) -> List[Dict]:
        """获取所有潜意识快照"""
        return [s.to_dict() for s in self.subconscious.snapshots]
    
    def generate(self) -> str:
        """生成深度层内容"""
        lines = [
            "# 深度层 - 完整数据",
            "",
            "## 涟漪池",
            self.ripple_pool.export_toon(),
            "",
            "## 潜意识快照",
            self.subconscious.export_toon()
        ]
        
        return '\n'.join(lines)
    
    def export_toon(self) -> str:
        """导出完整 TOON"""
        return self.generate()
    
    def export_json(self) -> Dict:
        """导出 JSON 格式"""
        return {
            "ripples": [r.to_dict() for r in self.ripple_pool.ripples],
            "resonances": self.ripple_pool.resonances,
            "snapshots": [s.to_dict() for s in self.subconscious.snapshots],
            "patterns": self.subconscious.patterns
        }


class ThreeLayerMemory:
    """
    三层记忆系统 - 模糊而精准
    
    使用方式：
    1. 启动时：memory.get_fuzzy() -> 注入 LLM 上下文
    2. 需要详情：memory.get_precise(query) -> 检索相关涟漪
    3. 深度分析：memory.get_deep() -> 获取完整数据
    """
    
    def __init__(self):
        self.fuzzy = FuzzyLayer()
        self.precise = PreciseLayer()
        self.deep = DeepLayer()
        
        # 缓存
        self._fuzzy_cache: Optional[str] = None
        self._cache_time: Optional[datetime] = None
    
    def get_fuzzy(self, force_refresh: bool = False) -> str:
        """
        获取模糊层 - 启动时加载
        
        Args:
            force_refresh: 强制刷新缓存
        
        Returns:
            模糊层内容（~400 tokens）
        """
        # 缓存策略：5分钟内不刷新
        if not force_refresh and self._fuzzy_cache and self._cache_time:
            if datetime.now() - self._cache_time < timedelta(minutes=5):
                return self._fuzzy_cache
        
        self._fuzzy_cache = self.fuzzy.generate()
        self._cache_time = datetime.now()
        return self._fuzzy_cache
    
    def get_fuzzy_toon(self) -> str:
        """获取 TOON 格式的模糊层"""
        return self.fuzzy.to_toon()
    
    def get_precise(self, query: str = None, tags: List[str] = None,
                    min_temp: int = None, max_temp: int = None) -> str:
        """
        获取精确层 - 按需检索
        
        Args:
            query: 搜索关键词
            tags: 标签过滤
            min_temp: 最低温度
            max_temp: 最高温度
        
        Returns:
            精确层内容
        """
        return self.precise.generate(query, tags, min_temp, max_temp)
    
    def get_deep(self) -> str:
        """获取深度层 - 完整数据"""
        return self.deep.generate()
    
    def search(self, query: str, top_k: int = 5) -> List[Ripple]:
        """搜索涟漪"""
        return self.precise.search(query, top_k)
    
    def get_startup_context(self) -> str:
        """
        获取启动上下文 - 用于 LLM 注入
        
        这是模糊层的核心接口
        """
        return self.get_fuzzy()
    
    def update(self):
        """更新缓存 - 添加新涟漪后调用"""
        self._fuzzy_cache = None
        self._cache_time = None


# 全局实例
_three_layer_memory: Optional[ThreeLayerMemory] = None


def get_three_layer_memory() -> ThreeLayerMemory:
    """获取三层记忆实例"""
    global _three_layer_memory
    if _three_layer_memory is None:
        _three_layer_memory = ThreeLayerMemory()
    return _three_layer_memory


def get_fuzzy_layer() -> str:
    """获取模糊层（便捷函数）"""
    return get_three_layer_memory().get_fuzzy()


def get_precise_layer(query: str = None, tags: List[str] = None,
                      min_temp: int = None, max_temp: int = None) -> str:
    """获取精确层（便捷函数）"""
    return get_three_layer_memory().get_precise(query, tags, min_temp, max_temp)


def get_deep_layer() -> str:
    """获取深度层（便捷函数）"""
    return get_three_layer_memory().get_deep()


if __name__ == "__main__":
    # 测试
    memory = get_three_layer_memory()
    
    print("=== 模糊层 ===")
    fuzzy = memory.get_fuzzy()
    print(fuzzy)
    print(f"\n估算 token: {memory.fuzzy.get_token_estimate()}")
    
    print("\n=== TOON 格式 ===")
    print(memory.get_fuzzy_toon())
    
    print("\n=== 精确层（搜索 AI）===")
    print(memory.get_precise(query="AI"))
    
    print("\n=== 精确层（温度 60-70）===")
    print(memory.get_precise(min_temp=60, max_temp=70))
