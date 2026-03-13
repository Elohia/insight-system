#!/usr/bin/env python3
"""
OpenClaw API 客户端
调用 OpenClaw 的记忆搜索 API
"""

import subprocess
import json
import sys

class OpenClawAPI:
    """OpenClaw API 客户端"""
    
    def __init__(self):
        self.openclaw_cmd = "openclaw"
    
    def search_memory(self, query, max_results=10):
        """
        搜索 OpenClaw 记忆
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
        
        Returns:
            list: 搜索结果列表
        """
        try:
            cmd = [
                self.openclaw_cmd,
                "memory",
                "search",
                "--query", query,
                "--max-results", str(max_results),
                "--json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # 如果不是 JSON，返回空列表
                    print("⚠️ 无法解析 JSON 响应")
                    return []
            else:
                print(f"⚠️ 搜索失败: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("⚠️ 搜索超时")
            return []
        except FileNotFoundError:
            print("⚠️ openclaw 命令未找到，请确保 OpenClaw 已安装")
            return []
        except Exception as e:
            print(f"⚠️ API 调用失败: {e}")
            return []
    
    def index_memory(self, force=False):
        """
        重新索引记忆文件
        
        Args:
            force: 是否强制重新索引
        
        Returns:
            bool: 是否成功
        """
        try:
            cmd = [self.openclaw_cmd, "memory", "index"]
            if force:
                cmd.append("--force")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ 记忆索引完成")
                return True
            else:
                print(f"⚠️ 索引失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ 索引超时")
            return False
        except FileNotFoundError:
            print("⚠️ openclaw 命令未找到")
            return False
        except Exception as e:
            print(f"⚠️ 索引失败: {e}")
            return False
    
    def get_memory_status(self):
        """
        获取记忆系统状态
        
        Returns:
            dict: 记忆系统状态
        """
        try:
            cmd = [self.openclaw_cmd, "memory", "status", "--json"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    print("⚠️ 无法解析 JSON 响应")
                    return {}
            else:
                print(f"⚠️ 获取状态失败: {result.stderr}")
                return {}
                
        except subprocess.TimeoutExpired:
            print("⚠️ 获取状态超时")
            return {}
        except FileNotFoundError:
            print("⚠️ openclaw 命令未找到")
            return {}
        except Exception as e:
            print(f"⚠️ API 调用失败: {e}")
            return {}
    
    def search_by_tag(self, tag):
        """
        根据标签搜索洞见
        
        Args:
            tag: 标签名称（不需要 # 符号）
        
        Returns:
            list: 匹配的洞见列表
        """
        if not tag.startswith("#"):
            tag = f"#{tag}"
        
        results = self.search_memory(tag, max_results=20)
        
        # 过滤出包含标签的结果
        filtered = []
        for r in results:
            if isinstance(r, dict) and tag in r.get("text", ""):
                filtered.append(r)
            elif isinstance(r, str) and tag in r:
                filtered.append({"text": r})
        
        return filtered


def main():
    """测试 API 客户端"""
    api = OpenClawAPI()
    
    print("📊 测试记忆系统状态...")
    status = api.get_memory_status()
    print(f"状态: {status}")
    
    print("\n🔍 测试记忆搜索...")
    results = api.search_memory("测试", max_results=5)
    print(f"搜索结果: {len(results)} 条")
    
    print("\n🏷️ 测试标签搜索...")
    tag_results = api.search_by_tag("洞见")
    print(f"标签搜索结果: {len(tag_results)} 条")
    
    print("\n📚 测试记忆索引...")
    success = api.index_memory(force=False)
    print(f"索引结果: {'成功' if success else '失败'}")


if __name__ == "__main__":
    main()
