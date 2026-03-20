#!/usr/bin/env python3
"""
TOON 格式工具模块
Token-Oriented Object Notation - 为 LLM 优化的数据格式

功能：
1. JSON <-> TOON 互转
2. 数据压缩（减少 token）
3. 结构验证
"""

import json
import re
from typing import Any, Dict, List, Union


def json_to_toon(data: Union[Dict, List], indent_size: int = 2) -> str:
    """
    将 JSON 转换为 TOON 格式
    
    Args:
        data: JSON 数据
        indent_size: 缩进空格数
    
    Returns:
        TOON 格式字符串
    """
    if isinstance(data, list):
        return _array_to_toon(data, indent_size)
    elif isinstance(data, dict):
        return _object_to_toon(data, indent_size)
    else:
        return str(data)


def _object_to_toon(obj: Dict, indent: int = 0) -> str:
    """将对象转换为 TOON"""
    lines = []
    prefix = " " * indent
    
    for key, value in obj.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_object_to_toon(value, indent + 2))
        elif isinstance(value, list):
            if _is_uniform_array(value):
                lines.append(_uniform_array_to_toon(key, value, indent))
            else:
                lines.append(f"{prefix}{key}:")
                lines.append(_array_to_toon(value, indent + 2))
        elif isinstance(value, str):
            if _needs_quote(value):
                lines.append(f'{prefix}{key}: "{value}"')
            else:
                lines.append(f"{prefix}{key}: {value}")
        elif isinstance(value, bool):
            lines.append(f"{prefix}{key}: {str(value).lower()}")
        elif value is None:
            lines.append(f"{prefix}{key}: null")
        else:
            lines.append(f"{prefix}{key}: {value}")
    
    return '\n'.join(lines)


def _array_to_toon(arr: List, indent: int = 0) -> str:
    """将数组转换为 TOON"""
    if not arr:
        return " " * indent + "[]"
    
    prefix = " " * indent
    lines = []
    
    for item in arr:
        if isinstance(item, dict):
            lines.append(f"{prefix}- ")
            for k, v in item.items():
                if isinstance(v, str):
                    lines.append(f"{prefix}  {k}: {v}")
                else:
                    lines.append(f"{prefix}  {k}: {v}")
        elif isinstance(item, str):
            lines.append(f"{prefix}- {item}")
        else:
            lines.append(f"{prefix}- {item}")
    
    return '\n'.join(lines)


def _is_uniform_array(arr: List) -> bool:
    """检查是否为均匀数组（所有元素都是相同结构的对象）"""
    if not arr or not all(isinstance(item, dict) for item in arr):
        return False
    
    # 检查所有对象是否有相同的键
    keys = set(arr[0].keys())
    return all(set(item.keys()) == keys for item in arr)


def _uniform_array_to_toon(key: str, arr: List, indent: int) -> str:
    """将均匀对象数组转换为 TOON 表格格式"""
    if not arr:
        return " " * indent + f"{key}[]:"
    
    prefix = " " * indent
    fields = list(arr[0].keys())
    fields_str = ",".join(fields)
    
    lines = [f"{prefix}{key}[{len(arr)}]{{{fields_str}}}:"]
    
    for item in arr:
        values = []
        for f in fields:
            v = item.get(f, "")
            if isinstance(v, str):
                # 如果包含逗号，需要转义
                if ',' in str(v):
                    v = f'"{v}"'
                values.append(str(v)[:50])  # 限制长度
            elif isinstance(v, bool):
                values.append(str(v).lower())
            elif v is None:
                values.append("")
            else:
                values.append(str(v))
        
        lines.append(f"{prefix} {','.join(values)}")
    
    return '\n'.join(lines)


def _needs_quote(value: str) -> bool:
    """检查字符串是否需要引号"""
    # 包含特殊字符时需要引号
    special_chars = [',', ':', '#', '{', '}', '[', ']', '\n', '\t']
    return any(c in value for c in special_chars)


def toon_to_json(toon_str: str) -> Union[Dict, List]:
    """
    将 TOON 格式转换为 JSON
    
    Args:
        toon_str: TOON 格式字符串
    
    Returns:
        JSON 数据
    """
    lines = toon_str.strip().split('\n')
    result = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 解析表格头：key[N]{fields}:
        table_match = re.match(r'(\w+)\[(\d+)\]\{([^}]+)\}:', line)
        if table_match:
            key = table_match.group(1)
            count = int(table_match.group(2))
            fields = table_match.group(3).split(',')
            result[key] = []
            continue
        
        # 解析表格行
        if line.startswith(' ') and ',' in line and key:
            values = line.strip().split(',')
            if len(values) >= len(fields):
                obj = {}
                for i, f in enumerate(fields):
                    obj[f] = _parse_value(values[i])
                result[key].append(obj)
            continue
        
        # 解析键值对
        if ':' in line:
            k, v = line.split(':', 1)
            k = k.strip()
            v = v.strip()
            result[k] = _parse_value(v)
    
    return result


def _parse_value(v: str) -> Any:
    """解析值"""
    v = v.strip()
    
    if not v:
        return None
    if v.lower() == 'true':
        return True
    if v.lower() == 'false':
        return False
    if v.lower() == 'null':
        return None
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    
    # 尝试解析数字
    try:
        if '.' in v:
            return float(v)
        return int(v)
    except ValueError:
        return v


def estimate_tokens(json_str: str, toon_str: str) -> Dict[str, int]:
    """
    估算 token 节省
    
    Args:
        json_str: JSON 字符串
        toon_str: TOON 字符串
    
    Returns:
        token 统计
    """
    # 简单估算：每 4 个字符约 1 个 token（英文）
    # 中文约 1.7 字符/token
    json_tokens = len(json_str) // 4
    toon_tokens = len(toon_str) // 4
    
    saved = json_tokens - toon_tokens
    percentage = (saved / json_tokens * 100) if json_tokens > 0 else 0
    
    return {
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "saved_tokens": saved,
        "saved_percentage": round(percentage, 1)
    }


if __name__ == "__main__":
    # 测试
    test_data = {
        "ripples": [
            {"id": "r001", "temp": 65, "content": "发现AI的连续性是幻觉"},
            {"id": "r002", "temp": 60, "content": "工具思维比单模型更强"},
            {"id": "r003", "temp": 55, "content": "涟漪叠加产生共振"}
        ],
        "state": {
            "ripple_count": 3,
            "avg_temp": 60.0,
            "surface": "活跃"
        }
    }
    
    # 转换
    json_str = json.dumps(test_data, indent=2, ensure_ascii=False)
    toon_str = json_to_toon(test_data)
    
    print("=== JSON 格式 ===")
    print(json_str)
    print(f"\n长度: {len(json_str)} 字符")
    
    print("\n=== TOON 格式 ===")
    print(toon_str)
    print(f"\n长度: {len(toon_str)} 字符")
    
    # Token 估算
    stats = estimate_tokens(json_str, toon_str)
    print(f"\n=== Token 节省 ===")
    print(f"JSON: {stats['json_tokens']} tokens")
    print(f"TOON: {stats['toon_tokens']} tokens")
    print(f"节省: {stats['saved_tokens']} tokens ({stats['saved_percentage']}%)")
