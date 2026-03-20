"""
配置加载器 - 统一使用环境变量
"""
import os
from typing import Optional


class Config:
    """配置管理"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.data_dir = os.environ.get(
            'INSIGHT_SYSTEM_PATH',
            '/workspace/projects/extensions/insight-system'
        )
        
        self.fuzzy_budget = int(os.environ.get('FUZZY_BUDGET', '250'))
        self.auto_collect_min_temp = int(os.environ.get('AUTO_COLLECT_MIN_TEMP', '60'))
        
        # 共振参数
        self.resonance_temp_threshold = int(os.environ.get('RESONANCE_TEMP_THRESHOLD', '15'))
        self.resonance_time_threshold = float(os.environ.get('RESONANCE_TIME_THRESHOLD', '86400'))
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置"""
        return os.environ.get(key.upper(), default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置"""
        try:
            return int(os.environ.get(key.upper(), str(default)))
        except ValueError:
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置"""
        try:
            return float(os.environ.get(key.upper(), str(default)))
        except ValueError:
            return default
