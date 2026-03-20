"""
TOON (Token-Oriented Object Notation) 工具
相比 JSON 减少 ~67% token
"""
from typing import Any, Dict, List


def toon_encode(obj: Any) -> str:
    """
    将对象编码为 TOON 格式
    - 省略键名引号
    - 使用 | 分隔
    - 压缩空白
    """
    if isinstance(obj, dict):
        return '|'.join(f"{k},{toon_encode(v)}" for k, v in obj.items())
    elif isinstance(obj, list):
        return '|'.join(toon_encode(item) for item in obj)
    elif isinstance(obj, str):
        return obj.replace('|', '\\|')
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif obj is None:
        return ''
    else:
        return str(obj)


def toon_decode(line: str) -> Any:
    """从 TOON 格式解码"""
    if not line:
        return None
    
    # 简单解析
    parts = line.split('|')
    if len(parts) == 1:
        return _parse_value(parts[0])
    
    # 尝试解析为字典
    result = {}
    for part in parts:
        if ',' in part:
            k, v = part.split(',', 1)
            result[k] = _parse_value(v)
        else:
            # 列表模式
            if not result:
                return [_parse_value(p) for p in parts]
            break
    
    return result if result else [_parse_value(p) for p in parts]


def _parse_value(s: str) -> Any:
    """解析单个值"""
    if not s:
        return None
    
    # 尝试数字
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        pass
    
    # 布尔
    if s.lower() in ('true', 'yes'):
        return True
    if s.lower() in ('false', 'no'):
        return False
    
    return s


def token_savings(json_str: str, toon_str: str) -> float:
    """计算 token 节省比例"""
    if not json_str:
        return 0.0
    return 1.0 - (len(toon_str) / len(json_str))
