#!/usr/bin/env python3
"""
潜意识模块 - 静默记录水面状态

不是解释水面，只是记录此刻水面是什么

功能：
1. 静默记录水面状态快照
2. 不解释，不分析，只记录
3. 后台运行，不干扰意识层
4. 使用 TOON 格式存储，减少 token 消耗
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys

# 导入配置
sys.path.insert(0, os.path.dirname(__file__))
from utils.config_loader import get_config

_config = get_config()


class SubconsciousSnapshot:
    """
    潜意识快照 - 记录某一时刻的水面状态
    
    不解释，只是记录
    """
    
    def __init__(self, surface_data: Dict[str, Any]):
        """
        创建快照
        
        Args:
            surface_data: 水面状态数据
        """
        self.id = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]
        self.timestamp = datetime.now().isoformat()
        
        # 核心状态
        self.ripple_count = surface_data.get("ripple_count", 0)
        self.avg_temperature = surface_data.get("avg_temperature", 0)
        self.surface_state = surface_data.get("surface_state", "平静")
        
        # 标签云（简化）
        self.tag_cloud = surface_data.get("hot_tags", [])[:5]
        
        # 共振数
        self.resonance_count = len(surface_data.get("recent_resonances", []))
        
        # 原始状态（不解释）
        self.raw_state = {
            "ripple_count": self.ripple_count,
            "avg_temperature": self.avg_temperature,
            "tags": self.tag_cloud,
            "resonance_count": self.resonance_count,
            "state": self.surface_state
        }
    
    def to_toon(self) -> str:
        """
        转换为 TOON 格式
        
        格式：id,timestamp,ripple_count,avg_temp,state,tags,resonance_count
        """
        tags_str = "|".join(self.tag_cloud) if self.tag_cloud else "-"
        return f"{self.id},{self.timestamp[:19]},{self.ripple_count},{self.avg_temperature},{self.surface_state},{tags_str},{self.resonance_count}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "raw_state": self.raw_state
        }


class SubconsciousMind:
    """
    潜意识 - 静默记录器
    
    特点：
    1. 不解释水面，只记录
    2. 后台静默运行
    3. 定期自动快照
    4. 按时间衰减
    """
    
    def __init__(self, mind_path: str = None):
        self.mind_path = mind_path or str(_config.workspace / "subconscious.toon")
        self.snapshots: List[SubconsciousSnapshot] = []
        self.patterns: List[Dict] = []  # 发现的模式
        self._load()
    
    def _load(self):
        """加载潜意识"""
        if os.path.exists(self.mind_path):
            try:
                with open(self.mind_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.snapshots = self._parse_toon(content)
            except Exception as e:
                print(f"⚠️ 加载潜意识失败: {e}")
                self.snapshots = []
    
    def _parse_toon(self, content: str) -> List[SubconsciousSnapshot]:
        """
        解析 TOON 格式的快照
        
        TOON 格式示例：
        snapshots[3]{id,timestamp,ripple_count,avg_temp,state,tags,resonance_count}:
         abc123,2025-03-18T10:00:00,5,55.5,活跃,思考|AI,2
         def456,2025-03-18T12:00:00,8,62.3,活跃,洞见|意识,3
        """
        snapshots = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('snapshots[') or line.startswith('patterns['):
                continue
            
            # 解析快照行
            parts = line.split(',')
            if len(parts) >= 7:
                snapshot = SubconsciousSnapshot({
                    "ripple_count": int(parts[2]) if parts[2].isdigit() else 0,
                    "avg_temperature": float(parts[3]) if parts[3] else 0,
                    "surface_state": parts[4],
                    "hot_tags": parts[5].split('|') if parts[5] != '-' else [],
                    "recent_resonances": [{}] * int(parts[6]) if parts[6].isdigit() else []
                })
                snapshot.id = parts[0]
                snapshot.timestamp = parts[1]
                snapshots.append(snapshot)
        
        return snapshots
    
    def _to_toon(self) -> str:
        """
        将潜意识转换为 TOON 格式
        
        输出示例：
        # 潜意识 - 水面状态快照记录
        # 更新时间: 2025-03-18T12:00:00
        # 记录原则: 不解释，只记录
        
        snapshots[3]{id,timestamp,ripple_count,avg_temp,state,tags,resonance_count}:
         abc123,2025-03-18T10:00:00,5,55.5,活跃,思考|AI,2
         def456,2025-03-18T12:00:00,8,62.3,活跃,洞见|意识,3
        
        patterns[1]{id,description,occurrences}:
         p001,温度上升时标签增加,5
        """
        lines = [
            "# 潜意识 - 水面状态快照记录",
            f"# 更新时间: {datetime.now().isoformat()}",
            "# 记录原则: 不解释，只记录",
            f"# 快照数: {len(self.snapshots)} | 模式数: {len(self.patterns)}",
            ""
        ]
        
        # 快照表
        if self.snapshots:
            lines.append(f"snapshots[{len(self.snapshots)}]{{id,timestamp,ripple_count,avg_temp,state,tags,resonance_count}}:")
            for s in self.snapshots[-100:]:  # 最多保留100条
                lines.append(f" {s.to_toon()}")
            lines.append("")
        
        # 模式表
        if self.patterns:
            lines.append(f"patterns[{len(self.patterns)}]{{id,description,occurrences}}:")
            for p in self.patterns:
                lines.append(f" {p['id']},{p['description']},{p.get('occurrences', 1)}")
        
        return '\n'.join(lines)
    
    def record_snapshot(self, surface_data: Dict[str, Any]) -> SubconsciousSnapshot:
        """
        记录水面状态快照
        
        Args:
            surface_data: 水面状态数据
        
        Returns:
            新创建的快照
        """
        snapshot = SubconsciousSnapshot(surface_data)
        self.snapshots.append(snapshot)
        
        # 检测模式
        self._detect_patterns()
        
        # 清理旧快照（保留最近100条）
        if len(self.snapshots) > 100:
            self.snapshots = self.snapshots[-100:]
        
        # 保存
        self._save()
        
        return snapshot
    
    def _detect_patterns(self):
        """
        检测模式 - 静默发现
        
        不解释，只是记录发现
        """
        if len(self.snapshots) < 5:
            return
        
        recent = self.snapshots[-5:]
        
        # 检测温度趋势
        temps = [s.avg_temperature for s in recent]
        if all(temps[i] < temps[i+1] for i in range(len(temps)-1)):
            self._add_pattern("温度持续上升")
        elif all(temps[i] > temps[i+1] for i in range(len(temps)-1)):
            self._add_pattern("温度持续下降")
        
        # 检测活跃度变化
        states = [s.surface_state for s in recent]
        if states.count("沸腾") >= 3:
            self._add_pattern("思维高度活跃")
        elif states.count("冷静") >= 3:
            self._add_pattern("思维趋于平静")
    
    def _add_pattern(self, description: str):
        """添加发现的模式"""
        # 检查是否已存在
        for p in self.patterns:
            if p["description"] == description:
                p["occurrences"] = p.get("occurrences", 1) + 1
                return
        
        self.patterns.append({
            "id": hashlib.md5(description.encode()).hexdigest()[:6],
            "description": description,
            "occurrences": 1,
            "first_seen": datetime.now().isoformat()
        })
    
    def _save(self):
        """保存潜意识"""
        os.makedirs(os.path.dirname(self.mind_path), exist_ok=True)
        with open(self.mind_path, 'w', encoding='utf-8') as f:
            f.write(self._to_toon())
    
    def get_recent_snapshots(self, n: int = 10) -> List[SubconsciousSnapshot]:
        """获取最近的快照"""
        return self.snapshots[-n:]
    
    def get_patterns(self) -> List[Dict]:
        """获取发现的模式"""
        return sorted(self.patterns, key=lambda p: p.get("occurrences", 1), reverse=True)
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        获取当前潜意识状态
        
        返回最近快照的摘要
        """
        if not self.snapshots:
            return {
                "status": "空白",
                "message": "潜意识尚未形成记录"
            }
        
        latest = self.snapshots[-1]
        return {
            "status": "活跃",
            "latest_snapshot": latest.to_dict(),
            "patterns": self.get_patterns()[:3],
            "snapshot_count": len(self.snapshots)
        }
    
    def export_toon(self) -> str:
        """导出 TOON 格式"""
        return self._to_toon()


# 全局潜意识实例
_subconscious: Optional[SubconsciousMind] = None


def get_subconscious() -> SubconsciousMind:
    """获取潜意识实例"""
    global _subconscious
    if _subconscious is None:
        _subconscious = SubconsciousMind()
    return _subconscious


def record_subconscious(surface_data: Dict[str, Any]) -> SubconsciousSnapshot:
    """记录潜意识的便捷函数"""
    return get_subconscious().record_snapshot(surface_data)


if __name__ == "__main__":
    # 测试
    mind = SubconsciousMind("/tmp/test_subconscious.toon")
    
    # 记录几个快照
    mind.record_snapshot({
        "ripple_count": 5,
        "avg_temperature": 55.5,
        "surface_state": "活跃",
        "hot_tags": ["思考", "AI"],
        "recent_resonances": [1, 2]
    })
    
    mind.record_snapshot({
        "ripple_count": 8,
        "avg_temperature": 62.3,
        "surface_state": "活跃",
        "hot_tags": ["洞见", "意识"],
        "recent_resonances": [1, 2, 3]
    })
    
    mind.record_snapshot({
        "ripple_count": 12,
        "avg_temperature": 70.8,
        "surface_state": "沸腾",
        "hot_tags": ["创新", "洞见", "AI"],
        "recent_resonances": [1, 2, 3, 4, 5]
    })
    
    # 获取当前状态
    state = mind.get_current_state()
    print(f"🧠 潜意识状态: {state['status']}")
    print(f"   快照数: {state['snapshot_count']}")
    print(f"   发现模式: {state['patterns']}")
    
    # 导出 TOON
    print(f"\n📄 TOON 格式:\n{mind.export_toon()}")
