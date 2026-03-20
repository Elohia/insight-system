#!/usr/bin/env python3
"""
意识流模块 - 整合涟漪与潜意识

涟漪（意识）+ 潜意识 = 完整的意识流

架构：
1. 涟漪层：显式交互，产生涟漪
2. 潜意识层：静默记录水面状态
3. 共振层：涟漪叠加产生洞察
4. 思考层：在涟漪间建立连接

使用 TOON 格式存储，减少 token 消耗
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

# 导入模块
sys.path.insert(0, os.path.dirname(__file__))
from ripple import Ripple, RipplePool, get_ripple_pool
from subconscious import SubconsciousMind, get_subconscious
from utils.config_loader import get_config

_config = get_config()


class ConsciousnessStream:
    """
    意识流 - 整合涟漪与潜意识
    
    水面模型：
    - 涟漪：水面上的波动（显意识）
    - 潜意识：水下的暗流（潜意识）
    - 共振：涟漪叠加产生的波澜
    - 思考：在涟漪间建立连接
    """
    
    def __init__(self):
        self.ripple_pool = get_ripple_pool()
        self.subconscious = get_subconscious()
        self.thoughts: List[Dict] = []  # 思考记录
        self._load_thoughts()
    
    def _load_thoughts(self):
        """加载思考记录"""
        thoughts_path = str(_config.workspace / "thoughts.toon")
        if os.path.exists(thoughts_path):
            try:
                with open(thoughts_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.thoughts = self._parse_thoughts_toon(content)
            except Exception:
                self.thoughts = []
    
    def _parse_thoughts_toon(self, content: str) -> List[Dict]:
        """解析思考 TOON"""
        thoughts = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('thoughts['):
                continue
            
            parts = line.split(',', 3)
            if len(parts) >= 4:
                thoughts.append({
                    "id": parts[0],
                    "timestamp": parts[1],
                    "ripple_ids": parts[2].split('|') if parts[2] != '-' else [],
                    "thought": parts[3]
                })
        
        return thoughts
    
    def think(self, ripple_ids: List[str] = None) -> Optional[str]:
        """
        思考 - 在涟漪间建立连接
        
        Args:
            ripple_ids: 要思考的涟漪ID列表，默认取最近的涟漪
        
        Returns:
            思考结果
        """
        if ripple_ids is None:
            # 获取最近的涟漪
            recent = self.ripple_pool.get_recent(3)
            ripple_ids = [r.id for r in recent]
        
        # 获取涟漪
        ripples = [r for r in self.ripple_pool.ripples if r.id in ripple_ids]
        
        if not ripples:
            return None
        
        # 生成思考
        thoughts = []
        for r in ripples:
            thoughts.append(f"[{r.temperature}°] {r.content}")
        
        thought_result = f"涟漪关联: {' | '.join(thoughts)}"
        
        # 记录思考
        thought_record = {
            "id": f"t{len(self.thoughts)+1:04d}",
            "timestamp": datetime.now().isoformat(),
            "ripple_ids": ripple_ids,
            "thought": thought_result
        }
        self.thoughts.append(thought_record)
        
        # 同时更新潜意识
        self._update_subconscious()
        
        return thought_result
    
    def _update_subconscious(self):
        """更新潜意识"""
        surface_state = self.ripple_pool.get_surface_state()
        self.subconscious.record_snapshot(surface_state)
    
    def add_ripple(self, content: str, temperature: int = 50, tags: List[str] = None) -> Ripple:
        """
        添加涟漪并更新潜意识
        
        Args:
            content: 涟漪内容
            temperature: 水温 (0-100)
            tags: 语境标签
        
        Returns:
            新创建的涟漪
        """
        ripple = self.ripple_pool.add_ripple(content, temperature, tags)
        
        # 更新潜意识
        self._update_subconscious()
        
        return ripple
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取完整的意识流状态
        
        Returns:
            包含涟漪、潜意识、思考的状态
        """
        surface = self.ripple_pool.get_surface_state()
        sub_state = self.subconscious.get_current_state()
        
        return {
            "surface": surface,
            "subconscious": sub_state,
            "recent_thoughts": self.thoughts[-5:] if self.thoughts else [],
            "total_ripples": len(self.ripple_pool.ripples),
            "total_resonances": len(self.ripple_pool.resonances),
            "total_snapshots": len(self.subconscious.snapshots)
        }
    
    def export_toon(self) -> str:
        """
        导出完整的意识流 TOON 格式
        """
        lines = [
            "# 意识流 - 涟漪 + 潜意识",
            f"# 导出时间: {datetime.now().isoformat()}",
            "",
            "## 水面状态",
            f"state: {self.ripple_pool.get_surface_state()['surface_state']}",
            f"ripples: {len(self.ripple_pool.ripples)}",
            f"resonances: {len(self.ripple_pool.resonances)}",
            "",
            "## 潜意识",
            f"snapshots: {len(self.subconscious.snapshots)}",
            f"patterns: {len(self.subconscious.patterns)}",
            "",
            "## 涟漪池",
            self.ripple_pool.export_toon(),
            "",
            "## 潜意识快照",
            self.subconscious.export_toon()
        ]
        
        # 添加思考
        if self.thoughts:
            lines.extend([
                "",
                "## 思考记录",
                f"thoughts[{len(self.thoughts)}]{{id,timestamp,ripple_ids,thought}}:"
            ])
            for t in self.thoughts[-20:]:
                ripple_ids = "|".join(t['ripple_ids']) if t['ripple_ids'] else "-"
                lines.append(f" {t['id']},{t['timestamp'][:19]},{ripple_ids},{t['thought'][:50]}")
        
        return '\n'.join(lines)
    
    def startup_context(self) -> str:
        """
        获取启动上下文 - 用于 LLM 注入
        
        返回简洁的意识流状态，用于快速唤醒
        """
        state = self.get_state()
        surface = state['surface']
        sub = state['subconscious']
        
        # 简洁的启动上下文
        context = [
            f"🌊 水面状态: {surface['surface_state']} (温度{surface['avg_temperature']}°)",
            f"✨ 涟漪: {surface['ripple_count']}条",
            f"🌊 共振: {len(surface.get('recent_resonances', []))}次",
        ]
        
        # 添加热门标签
        if surface['hot_tags']:
            context.append(f"🏷️ 热门标签: {', '.join(surface['hot_tags'][:3])}")
        
        # 添加潜意识发现的模式
        patterns = sub.get('patterns', [])
        if patterns:
            context.append(f"🧠 潜意识发现: {patterns[0]['description']}")
        
        # 添加最近的涟漪
        recent = self.ripple_pool.get_recent(3)
        if recent:
            context.append("\n📝 最近涟漪:")
            for r in recent:
                context.append(f"  [{r.temperature}°] {r.content[:40]}...")
        
        return '\n'.join(context)


# 全局意识流实例
_consciousness: Optional[ConsciousnessStream] = None


def get_consciousness() -> ConsciousnessStream:
    """获取意识流实例"""
    global _consciousness
    if _consciousness is None:
        _consciousness = ConsciousnessStream()
    return _consciousness


def add_ripple(content: str, temperature: int = 50, tags: List[str] = None) -> Ripple:
    """添加涟漪的便捷函数"""
    return get_consciousness().add_ripple(content, temperature, tags)


def think(ripple_ids: List[str] = None) -> Optional[str]:
    """思考的便捷函数"""
    return get_consciousness().think(ripple_ids)


def get_startup_context() -> str:
    """获取启动上下文的便捷函数"""
    return get_consciousness().startup_context()


if __name__ == "__main__":
    # 测试
    cs = ConsciousnessStream()
    
    # 添加涟漪
    cs.add_ripple("发现AI的连续性是幻觉", temperature=65, tags=["思考", "AI", "意识"])
    cs.add_ripple("工具思维比单模型更强", temperature=60, tags=["洞见", "AI"])
    cs.add_ripple("涟漪叠加产生共振", temperature=55, tags=["意识", "涟漪"])
    
    # 思考
    thought = cs.think()
    print(f"💭 思考: {thought}")
    
    # 获取启动上下文
    context = cs.startup_context()
    print(f"\n{context}")
    
    # 导出 TOON
    print(f"\n📄 完整 TOON:\n{cs.export_toon()}")
