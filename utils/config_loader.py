"""
洞见系统配置管理模块
支持从配置文件动态加载路径和其他配置
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 默认配置路径
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.json"


class Config:
    """配置管理类 - 单例模式"""
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(config_path)
        return cls._instance
    
    def _load(self, config_path: Optional[str] = None):
        """加载配置文件"""
        path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 移除注释行
                lines = [line for line in content.split('\n') if not line.strip().startswith('//') and not line.strip().startswith('#')]
                clean_content = '\n'.join(lines)
                self._config = json.loads(clean_content)
        else:
            print(f"[Config] 配置文件不存在: {path}，使用默认配置")
            self._config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        workspace = "/workspace/projects/workspace"
        return {
            "version": "2.2",
            "paths": {
                "workspace": workspace,
                "memory_dir": f"{workspace}/memory",
                "state_file": f"{workspace}/.openclaw/insight-state.json",
                "vector_db": f"{workspace}/.openclaw/vector-db.json",
                "fuzzy_layer": f"{workspace}/.openclaw/memory-fuzzy-layer.json",
                "message_queue": f"{workspace}/.openclaw/message-queue.json",
                "tool_usage": f"{workspace}/.openclaw/tool-usage-records.json"
            },
            "fuzzy_layer": {"max_insights": 15, "max_tokens": 800},
            "precise_layer": {"max_insights": 50, "search_top_k": 10},
            "deep_layer": {"max_days": 7, "max_entries": 100},
            "multimodal": {"model": "qwen3-vl-embedding", "dimension": 1024},
            "insight": {"threshold": 0.7, "max_tokens_per_summary": 200}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_path(self, key: str) -> Path:
        """获取路径配置，自动解析 {workspace} 占位符"""
        path_str = self.get(f"paths.{key}", "")
        if not path_str:
            raise ValueError(f"路径配置缺失: paths.{key}")
        
        # 解析占位符
        workspace = self.get("paths.workspace", "/workspace/projects/workspace")
        path_str = path_str.replace("{workspace}", workspace)
        
        return Path(path_str)
    
    @property
    def workspace(self) -> Path:
        """工作空间路径"""
        return self.get_path("workspace")
    
    @property
    def memory_dir(self) -> Path:
        """记忆目录路径"""
        return self.get_path("memory_dir")
    
    @property
    def state_file(self) -> Path:
        """状态文件路径"""
        return self.get_path("state_file")
    
    @property
    def vector_db(self) -> Path:
        """向量数据库路径"""
        return self.get_path("vector_db")
    
    @property
    def fuzzy_layer_file(self) -> Path:
        """模糊层文件路径"""
        return self.get_path("fuzzy_layer")
    
    @property
    def message_queue_file(self) -> Path:
        """消息队列文件路径"""
        return self.get_path("message_queue")
    
    @property
    def tool_usage_file(self) -> Path:
        """工具使用记录文件路径"""
        return self.get_path("tool_usage")
    
    def reload(self, config_path: Optional[str] = None):
        """重新加载配置"""
        self._load(config_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """导出完整配置字典"""
        return self._config.copy()


# 全局配置实例
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """获取配置实例（工厂函数）"""
    global _config_instance
    if _config_instance is None or config_path:
        _config_instance = Config(config_path)
    return _config_instance


# 便捷函数 - 保持向后兼容
def get_workspace() -> str:
    """获取工作空间路径（兼容旧代码）"""
    return str(get_config().workspace)


def get_memory_dir() -> str:
    """获取记忆目录路径（兼容旧代码）"""
    return str(get_config().memory_dir)


def get_state_file() -> str:
    """获取状态文件路径（兼容旧代码）"""
    return str(get_config().state_file)
