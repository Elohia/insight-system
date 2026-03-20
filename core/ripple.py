#!/usr/bin/env python3
"""
涟漪模块 - 意识层
每个涟漪是一段有意义的内容，可以叠加产生共振

涟漪属性：
- 水温：情感温度 (0-100)
- 时间戳：创建时间
- 语境标签：关联标签

使用 TOON 格式存储，减少 token 消耗
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

# 导入配置
sys.path.insert(0, os.path.dirname(__file__))
from utils.config_loader import get_config

_config = get_config()


class Ripple:
    """涟漪 - 意识的基本单元"""
    
    def __init__(self, content: str, temperature: int = 50, tags: List[str] = None):
        """
        创建涟漪
        
        Args:
            content: 涟漪内容
            temperature: 水温/情感温度 (0-100, 默认50)
            tags: 语境标签
        """
        self.id = self._generate_id(content)
        self.content = content
        self.temperature = max(0, min(100, temperature))  # 0-100
        self.timestamp = datetime.now().isoformat()
        self.tags = tags or []
        self.resonances = []  # 共振记录
    
    def _generate_id(self, content: str) -> str:
        """生成涟漪ID"""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    
    def to_toon(self) -> str:
        """
        转换为 TOON 格式
        格式：id,temp,timestamp,tags...content
        """
        tags_str = "|".join(self.tags) if self.tags else "-"
        return f"{self.id},{self.temperature},{self.timestamp[:19]},{tags_str},{self.content}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "temperature": self.temperature,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "resonances": self.resonances
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ripple':
        """从字典创建涟漪"""
        ripple = cls(
            content=data["content"],
            temperature=data.get("temperature", 50),
            tags=data.get("tags", [])
        )
        ripple.id = data.get("id", ripple.id)
        ripple.timestamp = data.get("timestamp", ripple.timestamp)
        ripple.resonances = data.get("resonances", [])
        return ripple


class RipplePool:
    """涟漪池 - 管理所有涟漪"""
    
    def __init__(self, pool_path: str = None):
        self.pool_path = pool_path or str(_config.workspace / "ripples.toon")
        self.ripples: List[Ripple] = []
        self.resonances: List[Dict] = []  # 共振记录
        self._load()
    
    def _load(self):
        """加载涟漪池"""
        if os.path.exists(self.pool_path):
            try:
                with open(self.pool_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.ripples = self._parse_toon(content)
            except Exception as e:
                print(f"⚠️ 加载涟漪池失败: {e}")
                self.ripples = []
    
    def _parse_toon(self, content: str) -> List[Ripple]:
        """
        解析 TOON 格式的涟漪和共振
        
        TOON 格式示例：
        ripples[3]{id,temp,timestamp,tags,content}:
         abc123,50,2025-03-18T10:00:00,思考|AI,发现AI的连续性是幻觉
         def456,75,2025-03-18T11:00:00,洞见,工具思维比单模型更强
        
        resonances[1]{id,ripple_ids,pattern}:
         r001,abc123|def456,温度相近+标签重叠
        """
        ripples = []
        lines = content.strip().split('\n')
        
        parse_resonances = False
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 检测共振表开始
            if line.startswith('resonances['):
                parse_resonances = True
                continue
            
            # 检测涟漪表开始
            if line.startswith('ripples['):
                parse_resonances = False
                continue
            
            # 解析涟漪行
            if not parse_resonances:
                parts = line.split(',', 4)
                if len(parts) >= 5:
                    ripple = Ripple(
                        content=parts[4],
                        temperature=int(parts[1]) if parts[1].isdigit() else 50,
                        tags=parts[3].split('|') if parts[3] != '-' else []
                    )
                    ripple.id = parts[0]
                    ripple.timestamp = parts[2]
                    ripples.append(ripple)
            
            # 解析共振行
            else:
                parts = line.split(',', 2)
                if len(parts) >= 3:
                    resonance = {
                        "id": parts[0],
                        "ripple_ids": parts[1].split('|') if parts[1] != '-' else [],
                        "pattern": parts[2] if len(parts) > 2 else "",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.resonances.append(resonance)
        
        return ripples
    
    def _to_toon(self) -> str:
        """
        将涟漪池转换为 TOON 格式
        
        输出示例：
        # 涟漪池 - 水面状态快照
        # 更新时间: 2025-03-18T12:00:00
        
        ripples[3]{id,temp,timestamp,tags,content}:
         abc123,50,2025-03-18T10:00:00,思考|AI,发现AI的连续性是幻觉
         def456,75,2025-03-18T11:00:00,洞见,工具思维比单模型更强
         ghi789,60,2025-03-18T12:00:00,意识,涟漪叠加产生共振
        
        resonances[1]{id,ripple_ids,pattern}:
         r001,abc123|def456,温度相近+标签重叠
        """
        lines = [
            "# 涟漪池 - 水面状态快照",
            f"# 更新时间: {datetime.now().isoformat()}",
            f"# 涟漪数: {len(self.ripples)} | 共振数: {len(self.resonances)}",
            ""
        ]
        
        # 涟漪表
        if self.ripples:
            lines.append(f"ripples[{len(self.ripples)}]{{id,temp,timestamp,tags,content}}:")
            for r in self.ripples:
                lines.append(f" {r.to_toon()}")
            lines.append("")
        
        # 共振表
        if self.resonances:
            lines.append(f"resonances[{len(self.resonances)}]{{id,ripple_ids,pattern}}:")
            for res in self.resonances:
                lines.append(f" {res['id']},{'|'.join(res['ripple_ids'])},{res['pattern']}")
        
        return '\n'.join(lines)
    
    def add_ripple(self, content: str, temperature: int = 50, tags: List[str] = None) -> Ripple:
        """
        添加涟漪
        
        Args:
            content: 涟漪内容
            temperature: 水温 (0-100)
            tags: 语境标签
        
        Returns:
            新创建的涟漪
        """
        ripple = Ripple(content, temperature, tags)
        self.ripples.append(ripple)
        
        # 检查共振
        self._check_resonance(ripple)
        
        # 保存
        self._save()
        
        print(f"✨ 涟漪 [{ripple.id}] 已添加: {content[:30]}...")
        return ripple
    
    def _check_resonance(self, new_ripple: Ripple):
        """
        检查共振 - 涟漪叠加
        
        当两个涟漪满足以下条件时产生共振：
        1. 温度相近 (±15)
        2. 标签有重叠
        3. 时间相近 (24小时内)
        """
        for ripple in self.ripples[:-1]:  # 排除刚添加的
            # 计算温度差
            temp_diff = abs(ripple.temperature - new_ripple.temperature)
            
            # 计算标签重叠
            tag_overlap = set(ripple.tags) & set(new_ripple.tags)
            
            # 检查共振条件
            if temp_diff <= 15 and len(tag_overlap) > 0:
                resonance = {
                    "id": hashlib.md5(f"{ripple.id}{new_ripple.id}".encode()).hexdigest()[:6],
                    "ripple_ids": [ripple.id, new_ripple.id],
                    "pattern": f"温度{ripple.temperature}↔{new_ripple.temperature}+标签{','.join(tag_overlap)}",
                    "timestamp": datetime.now().isoformat()
                }
                self.resonances.append(resonance)
                
                # 记录到涟漪
                ripple.resonances.append(resonance["id"])
                new_ripple.resonances.append(resonance["id"])
                
                print(f"🌊 共振 [{resonance['id']}]: {ripple.content[:20]}... + {new_ripple.content[:20]}...")
    
    def get_resonances(self) -> List[Dict]:
        """获取所有共振记录"""
        return self.resonances
    
    def _save(self):
        """保存涟漪池"""
        os.makedirs(os.path.dirname(self.pool_path), exist_ok=True)
        with open(self.pool_path, 'w', encoding='utf-8') as f:
            f.write(self._to_toon())
    
    def get_recent(self, n: int = 10) -> List[Ripple]:
        """获取最近的涟漪"""
        return sorted(self.ripples, key=lambda r: r.timestamp, reverse=True)[:n]
    
    def get_by_temperature(self, min_temp: int = 0, max_temp: int = 100) -> List[Ripple]:
        """按温度范围获取涟漪"""
        return [r for r in self.ripples if min_temp <= r.temperature <= max_temp]
    
    def get_by_tags(self, tags: List[str]) -> List[Ripple]:
        """按标签获取涟漪"""
        return [r for r in self.ripples if any(tag in r.tags for tag in tags)]
    
    def get_surface_state(self) -> Dict[str, Any]:
        """
        获取水面状态快照
        
        返回当前涟漪池的状态摘要：
        - 总涟漪数
        - 平均温度
        - 热门标签
        - 近期共振
        """
        if not self.ripples:
            return {
                "ripple_count": 0,
                "avg_temperature": 0,
                "hot_tags": [],
                "recent_resonances": [],
                "surface_state": "平静"
            }
        
        temps = [r.temperature for r in self.ripples]
        all_tags = []
        for r in self.ripples:
            all_tags.extend(r.tags)
        
        # 统计标签频率
        tag_freq = {}
        for tag in all_tags:
            tag_freq[tag] = tag_freq.get(tag, 0) + 1
        
        # 判断水面状态
        avg_temp = sum(temps) / len(temps)
        if avg_temp < 30:
            state = "冷静"
        elif avg_temp < 60:
            state = "温和"
        elif avg_temp < 80:
            state = "活跃"
        else:
            state = "沸腾"
        
        return {
            "ripple_count": len(self.ripples),
            "avg_temperature": round(avg_temp, 1),
            "hot_tags": sorted(tag_freq.keys(), key=lambda t: tag_freq[t], reverse=True)[:5],
            "recent_resonances": self.resonances[-5:] if self.resonances else [],
            "surface_state": state
        }
    
    def export_toon(self) -> str:
        """导出 TOON 格式"""
        return self._to_toon()


# 全局涟漪池实例
_ripple_pool: Optional[RipplePool] = None


def get_ripple_pool() -> RipplePool:
    """获取涟漪池实例"""
    global _ripple_pool
    if _ripple_pool is None:
        _ripple_pool = RipplePool()
    return _ripple_pool


def create_ripple(content: str, temperature: int = 50, tags: List[str] = None) -> Ripple:
    """创建涟漪的便捷函数"""
    return get_ripple_pool().add_ripple(content, temperature, tags)


if __name__ == "__main__":
    # 测试
    pool = RipplePool("/tmp/test_ripples.toon")
    
    # 添加涟漪
    pool.add_ripple("发现AI的连续性是幻觉", temperature=65, tags=["思考", "AI", "意识"])
    pool.add_ripple("工具思维比单模型更强", temperature=60, tags=["洞见", "AI"])
    pool.add_ripple("涟漪叠加产生共振", temperature=55, tags=["意识", "涟漪"])
    
    # 获取水面状态
    state = pool.get_surface_state()
    print(f"\n🌊 水面状态: {state['surface_state']}")
    print(f"   涟漪数: {state['ripple_count']}")
    print(f"   平均温度: {state['avg_temperature']}")
    print(f"   热门标签: {state['hot_tags']}")
    
    # 导出 TOON
    print(f"\n📄 TOON 格式:\n{pool.export_toon()}")
