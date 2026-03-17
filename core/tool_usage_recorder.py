#!/usr/bin/env python3
"""
工具使用记录器
记录成功的工具使用案例，让工具思维自然沉淀
"""

import os
import json
from datetime import datetime
from pathlib import Path
import sys

# 导入配置加载器
sys.path.insert(0, os.path.dirname(__file__))
from utils.config_loader import get_config

# 获取配置
_config = get_config()
TOOL_USAGE_FILE = str(_config.tool_usage_file)


class ToolUsageRecorder:
    """工具使用记录器"""
    
    def __init__(self):
        self.records = self.load_records()
    
    def load_records(self) -> dict:
        """加载记录"""
        if os.path.exists(TOOL_USAGE_FILE):
            with open(TOOL_USAGE_FILE, 'r') as f:
                return json.load(f)
        return {
            "records": [],
            "stats": {}
        }
    
    def save_records(self):
        """保存记录"""
        os.makedirs(os.path.dirname(TOOL_USAGE_FILE), exist_ok=True)
        with open(TOOL_USAGE_FILE, 'w') as f:
            json.dump(self.records, f, indent=2, ensure_ascii=False)
    
    def record(self, scene: str, tools: list, result: str, success: bool = True):
        """记录一次工具使用
        
        Args:
            scene: 场景描述（问题类型）
            tools: 使用的工具列表
            result: 结果描述
            success: 是否成功
        """
        record = {
            "scene": scene[:50],  # 限制长度
            "tools": tools[:5],   # 最多5个工具
            "result": result[:100],
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.records["records"].append(record)
        
        # 更新统计
        for tool in tools:
            if tool not in self.records["stats"]:
                self.records["stats"][tool] = {"success": 0, "fail": 0}
            self.records["stats"][tool]["success" if success else "fail"] += 1
        
        # 保留最近200条
        if len(self.records["records"]) > 200:
            self.records["records"] = self.records["records"][-200:]
        
        self.save_records()
    
    def get_tool_index(self) -> dict:
        """从记录中生成工具索引：场景 → 推荐工具"""
        # 统计每个场景最成功的工具组合
        scene_tools = {}
        
        for record in self.records["records"]:
            if not record["success"]:
                continue
            
            scene = record["scene"]
            tools = record["tools"]
            
            if scene not in scene_tools:
                scene_tools[scene] = {}
            
            tool_key = " → ".join(tools[:3])  # 最多显示3个工具
            scene_tools[scene][tool_key] = scene_tools[scene].get(tool_key, 0) + 1
        
        # 取每个场景最常用的工具组合
        tool_index = {}
        for scene, tools in scene_tools.items():
            if tools:
                best_tool = max(tools.items(), key=lambda x: x[1])[0]
                tool_index[scene] = best_tool
        
        return tool_index
    
    def get_success_patterns(self) -> list:
        """获取成功的工具使用模式"""
        patterns = []
        
        # 从成功案例中提取模式
        for record in self.records["records"][-50:]:  # 最近50条
            if record["success"] and len(record["tools"]) > 1:
                pattern = f"{record['scene']} → {' → '.join(record['tools'][:3])}"
                if pattern not in patterns:
                    patterns.append(pattern)
        
        return patterns[:10]


# 全局记录器
_recorder = None

def get_recorder():
    global _recorder
    if _recorder is None:
        _recorder = ToolUsageRecorder()
    return _recorder


def record_tool_usage(scene: str, tools: list, result: str, success: bool = True):
    """便捷函数：记录工具使用"""
    recorder = get_recorder()
    recorder.record(scene, tools, result, success)


# 示例用法
if __name__ == "__main__":
    # 记录一次成功的工具使用
    record_tool_usage(
        scene="配置问题排查",
        tools=["openclaw doctor", "检查日志"],
        result="发现配置错误并修复",
        success=True
    )
    
    # 获取工具索引
    recorder = get_recorder()
    print("工具索引:", recorder.get_tool_index())
    print("成功模式:", recorder.get_success_patterns())
