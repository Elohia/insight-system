"""
涟漪 - 显意识的基本单位
"""
import time
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Ripple:
    """涟漪：显意识片段"""
    content: str
    temp: float = 50.0
    tags: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    resonances: List[str] = field(default_factory=list)  # 共振链
    
    def to_toon(self) -> str:
        """
        TOON 格式序列化
        格式: temp|timestamp|tags|resonances|content
        """
        tags_str = ','.join(self.tags) if self.tags else ''
        res_str = ','.join(self.resonances) if self.resonances else ''
        ts = f"{self.timestamp:.0f}"
        return f"{self.temp:.0f}|{ts}|{tags_str}|{res_str}|{self.content}"
    
    @classmethod
    def from_toon(cls, line: str) -> Optional['Ripple']:
        """从 TOON 格式解析"""
        if not line or line.startswith('#'):
            return None
        
        parts = line.split('|', 4)
        if len(parts) < 5:
            # 兼容旧格式
            parts = line.split('|', 3)
            if len(parts) < 4:
                return None
            temp, ts, tags_str, content = parts
            res_str = ''
        else:
            temp, ts, tags_str, res_str, content = parts
        
        try:
            tags = [t for t in tags_str.split(',') if t]
            resonances = [r for r in res_str.split(',') if r]
            return cls(
                content=content,
                temp=float(temp),
                tags=tags,
                timestamp=float(ts),
                resonances=resonances
            )
        except (ValueError, IndexError):
            return None
    
    def to_dict(self) -> dict:
        """字典格式"""
        return {
            'content': self.content,
            'temp': self.temp,
            'tags': self.tags,
            'timestamp': self.timestamp,
            'resonances': self.resonances
        }
    
    def can_resonate(self, other: 'Ripple', temp_threshold: float = 15.0, time_threshold: float = 86400.0) -> bool:
        """
        判断是否可以发生共振
        条件: 温度相近(±15) + 标签重叠 + 时间相近(24h)
        """
        # 温度检查
        if abs(self.temp - other.temp) > temp_threshold:
            return False
        
        # 标签重叠
        if self.tags and other.tags:
            if not set(self.tags) & set(other.tags):
                return False
        
        # 时间检查
        if abs(self.timestamp - other.timestamp) > time_threshold:
            return False
        
        return True
