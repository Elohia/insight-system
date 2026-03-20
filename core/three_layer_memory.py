"""
三层记忆架构管理器
模糊层(~250 tokens) + 精确层(按需检索) + 深度层(完整数据)
"""
import os
import json
import time
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from .ripple import Ripple
from .subconscious import SubconsciousEntry


class ThreeLayerMemory:
    """三层记忆管理器"""
    
    FUZZY_BUDGET = 250  # 模糊层预算
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.ripples: List[Ripple] = []
        self.subconscious: List[SubconsciousEntry] = []
        self.tag_index: Dict[str, List[int]] = defaultdict(list)
        self.temp_index: Dict[int, List[int]] = defaultdict(list)  # 按温度区间索引
        
        self._load_data()
    
    def _get_tokenizer(self):
        """获取 tokenizer"""
        if TIKTOKEN_AVAILABLE:
            return tiktoken.get_encoding("cl100k_base")
        return None
    
    def count_tokens(self, text: str) -> int:
        """精确计算 token 数"""
        enc = self._get_tokenizer()
        if enc:
            return len(enc.encode(text))
        # 回退到估算
        chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fa5')
        return int(chinese / 1.7 + (len(text) - chinese) / 4)
    
    # ========== 模糊层 ==========
    
    def get_fuzzy_layer(self) -> str:
        """
        模糊层：极简概要，~250 tokens
        启动时加载，作为系统提示
        """
        lines = ["# 模糊层"]
        
        # 1. 水面状态（潜意识摘要）
        if self.subconscious:
            latest = self.subconscious[-1]
            lines.append(f"\n## 水面状态 ({latest.timestamp[:10]})")
            lines.append(f"涟漪 {latest.ripple_count} | 共振 {latest.resonance_count}")
            lines.append(f"温度 {latest.temp_avg:.0f} | 标签 {', '.join(latest.top_tags[:3])}")
        
        # 2. 热门标签
        if self.tag_index:
            top_tags = sorted(self.tag_index.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            lines.append(f"\n## 热门标签")
            lines.append(' '.join(f"#{t}" for t, _ in top_tags))
        
        # 3. 高温涟漪 TOP 3
        hot_ripples = sorted(self.ripples, key=lambda r: r.temp, reverse=True)[:3]
        if hot_ripples:
            lines.append(f"\n## 热点涟漪")
            for r in hot_ripples:
                lines.append(f"[{r.temp:0.0f}] {r.content[:50]}...")
        
        fuzzy_text = '\n'.join(lines)
        
        # 确保不超过预算
        while self.count_tokens(fuzzy_text) > self.FUZZY_BUDGET and len(lines) > 5:
            lines = lines[:-1]
            fuzzy_text = '\n'.join(lines)
        
        return fuzzy_text
    
    # ========== 精确层 ==========
    
    def query_precise(
        self,
        tags: Optional[List[str]] = None,
        temp_range: Optional[Tuple[int, int]] = None,
        time_range: Optional[Tuple[float, float]] = None,
        keyword: Optional[str] = None,
        limit: int = 10
    ) -> List[Ripple]:
        """
        精确层：按条件检索
        - 标签匹配
        - 温度范围
        - 时间范围
        - 关键词搜索
        """
        candidates = []
        
        # 使用索引加速
        if tags:
            candidate_ids = set()
            for tag in tags:
                if tag in self.tag_index:
                    if not candidate_ids:
                        candidate_ids = set(self.tag_index[tag])
                    else:
                        candidate_ids &= set(self.tag_index[tag])
            candidates = [self.ripples[i] for i in candidate_ids if i < len(self.ripples)]
        else:
            candidates = self.ripples.copy()
        
        # 过滤温度
        if temp_range:
            min_t, max_t = temp_range
            candidates = [r for r in candidates if min_t <= r.temp <= max_t]
        
        # 过滤时间
        if time_range:
            start, end = time_range
            candidates = [r for r in candidates if start <= r.timestamp <= end]
        
        # 关键词搜索
        if keyword:
            candidates = [r for r in candidates if keyword.lower() in r.content.lower()]
        
        return candidates[:limit]
    
    # ========== 深度层 ==========
    
    def export_deep_layer(self, format: str = 'toon') -> str:
        """
        深度层：完整数据导出
        支持格式：toon, json
        """
        if format == 'json':
            return json.dumps({
                'ripples': [r.to_dict() for r in self.ripples],
                'subconscious': [s.to_dict() for s in self.subconscious]
            }, ensure_ascii=False, indent=2)
        
        # TOON 格式
        lines = ["# 深度层导出"]
        lines.append(f"涟漪数: {len(self.ripples)}")
        lines.append(f"潜意识数: {len(self.subconscious)}")
        lines.append("")
        
        for r in self.ripples:
            tags_str = ','.join(r.tags) if r.tags else ''
            lines.append(f"R|{r.temp:.0f}|{r.timestamp}|{tags_str}|{r.content}")
        
        lines.append("")
        
        for s in self.subconscious:
            tags_str = ','.join(s.top_tags) if s.top_tags else ''
            lines.append(f"S|{s.temp_avg:.0f}|{s.timestamp}|{s.ripple_count}|{s.resonance_count}|{tags_str}")
        
        return '\n'.join(lines)
    
    # ========== 索引维护 ==========
    
    def _rebuild_indices(self):
        """重建索引"""
        self.tag_index.clear()
        self.temp_index.clear()
        
        for i, ripple in enumerate(self.ripples):
            # 标签索引
            for tag in ripple.tags:
                self.tag_index[tag].append(i)
            
            # 温度索引（按10度区间）
            temp_bucket = int(ripple.temp // 10)
            self.temp_index[temp_bucket].append(i)
    
    # ========== 持久化 ==========
    
    def _load_data(self):
        """加载数据"""
        ripple_file = os.path.join(self.data_dir, 'ripples.toon')
        sub_file = os.path.join(self.data_dir, 'subconscious.toon')
        
        # 加载涟漪
        if os.path.exists(ripple_file):
            with open(ripple_file, 'r', encoding='utf-8') as f:
                for line in f:
                    ripple = Ripple.from_toon(line.strip())
                    if ripple:
                        self.ripples.append(ripple)
        
        # 加载潜意识
        if os.path.exists(sub_file):
            with open(sub_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = SubconsciousEntry.from_toon(line.strip())
                    if entry:
                        self.subconscious.append(entry)
        
        self._rebuild_indices()
    
    def save(self):
        """保存数据"""
        ripple_file = os.path.join(self.data_dir, 'ripples.toon')
        sub_file = os.path.join(self.data_dir, 'subconscious.toon')
        
        with open(ripple_file, 'w', encoding='utf-8') as f:
            for r in self.ripples:
                f.write(r.to_toon() + '\n')
        
        with open(sub_file, 'w', encoding='utf-8') as f:
            for s in self.subconscious:
                f.write(s.to_toon() + '\n')
