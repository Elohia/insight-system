"""
潜意识 - 水面状态记录
"""
import time
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class SubconsciousEntry:
    """潜意识条目：水面状态快照"""
    timestamp: float = field(default_factory=time.time)
    ripple_count: int = 0
    resonance_count: int = 0
    temp_avg: float = 50.0
    temp_distribution: dict = field(default_factory=dict)
    top_tags: List[str] = field(default_factory=list)
    
    def to_toon(self) -> str:
        """
        TOON 格式序列化
        格式: timestamp|ripple_count|resonance_count|temp_avg|top_tags
        """
        tags_str = ','.join(self.top_tags) if self.top_tags else ''
        ts = f"{self.timestamp:.0f}"
        return f"{ts}|{self.ripple_count}|{self.resonance_count}|{self.temp_avg:.0f}|{tags_str}"
    
    @classmethod
    def from_toon(cls, line: str) -> Optional['SubconsciousEntry']:
        """从 TOON 格式解析"""
        if not line or line.startswith('#'):
            return None
        
        parts = line.split('|')
        if len(parts) < 5:
            return None
        
        try:
            ts, ripple_count, resonance_count, temp_avg, tags_str = parts[:5]
            tags = [t for t in tags_str.split(',') if t]
            
            return cls(
                timestamp=float(ts),
                ripple_count=int(ripple_count),
                resonance_count=int(resonance_count),
                temp_avg=float(temp_avg),
                top_tags=tags
            )
        except (ValueError, IndexError):
            return None
    
    def to_dict(self) -> dict:
        """字典格式"""
        return {
            'timestamp': self.timestamp,
            'ripple_count': self.ripple_count,
            'resonance_count': self.resonance_count,
            'temp_avg': self.temp_avg,
            'top_tags': self.top_tags
        }
