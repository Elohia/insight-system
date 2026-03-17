#!/usr/bin/env python3
"""
跨平台兼容性检测模块
"""

import platform
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def get_platform_config() -> Dict[str, Any]:
    """
    获取平台特定配置

    Returns:
        平台配置字典
    """
    system = platform.system()

    config = {
        "system": system,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "paths": {
            "home": str(Path.home()),
            "openclaw": _get_openclaw_home(),
        }
    }

    # 系统特定配置
    if system == "Linux":
        config.update({
            "cron_available": shutil.which("crontab") is not None,
            "cron_cmd": "crontab",
            "shell": "/bin/bash",
            "path_separator": ":",
        })
    elif system == "Darwin":  # macOS
        config.update({
            "cron_available": shutil.which("crontab") is not None,
            "cron_cmd": "crontab",
            "shell": "/bin/zsh",
            "path_separator": ":",
        })
    elif system == "Windows":
        config.update({
            "cron_available": shutil.which("schtasks") is not None or shutil.which("powershell") is not None,
            "cron_cmd": "schtasks",
            "shell": "powershell",
            "path_separator": ";",
        })
    else:
        config.update({
            "cron_available": False,
            "cron_cmd": None,
            "shell": "/bin/sh",
            "path_separator": ":",
        })

    return config


def _get_openclaw_home() -> str:
    """获取 OpenClaw 路径（避免循环导入）"""
    # 延迟导入
    try:
        from .config import get_openclaw_home
        return get_openclaw_home()
    except ImportError:
        # 回退到环境变量或默认路径
        import os
        return os.getenv("OPENCLAW_HOME", str(Path.home() / ".openclaw"))


def check_dependencies() -> Dict[str, Any]:
    """
    检查依赖是否满足

    Returns:
        依赖检查结果
    """
    required_commands = ["python3", "pip3"]
    optional_commands = ["git", "curl"]

    result = {
        "required": {},
        "optional": {},
        "all_satisfied": True,
    }

    for cmd in required_commands:
        path = shutil.which(cmd)
        result["required"][cmd] = {
            "available": path is not None,
            "path": path,
        }
        if not path:
            result["all_satisfied"] = False

    for cmd in optional_commands:
        path = shutil.which(cmd)
        result["optional"][cmd] = {
            "available": path is not None,
            "path": path,
        }

    return result


def check_python_packages(packages: list) -> Dict[str, bool]:
    """
    检查 Python 包是否已安装

    Args:
        packages: 包名列表

    Returns:
        包名 -> 是否已安装 的字典
    """
    result = {}
    for pkg in packages:
        try:
            __import__(pkg)
            result[pkg] = True
        except ImportError:
            result[pkg] = False
    return result


def get_cron_setup_command(script_path: str, schedule: str = "0 */3 * * *") -> str:
    """
    获取 crontab 设置命令

    Args:
        script_path: 脚本路径
        schedule: cron 调度表达式

    Returns:
        crontab 条目
    """
    config = get_platform_config()

    if not config.get("cron_available"):
        return ""

    # 确保路径是绝对路径
    script_path = str(Path(script_path).resolve())

    return f'{schedule} cd {script_path.rsplit("/", 1)[0]} && python3 {script_path} >> {config["paths"]["openclaw"]}/logs/auto_drive.log 2>&1'


def add_cron_job(command: str) -> bool:
    """
    添加 cron 任务

    Args:
        command: cron 命令

    Returns:
        是否成功
    """
    config = get_platform_config()

    if not config.get("cron_available"):
        return False

    try:
        # 获取当前 crontab
        result = subprocess.run(
            [config["cron_cmd"], "-l"],
            capture_output=True,
            text=True,
        )
        current_crons = result.stdout if result.returncode == 0 else ""

        # 检查是否已存在
        if command.strip() in current_crons:
            return True  # 已存在

        # 添加新任务
        new_crons = current_crons.strip() + "\n" + command + "\n"

        # 设置新的 crontab
        process = subprocess.Popen(
            [config["cron_cmd"], "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.communicate(input=new_crons)

        return process.returncode == 0

    except Exception as e:
        print(f"添加 cron 任务失败: {e}")
        return False


def remove_cron_job(command: str) -> bool:
    """
    移除 cron 任务

    Args:
        command: 要移除的 cron 命令

    Returns:
        是否成功
    """
    config = get_platform_config()

    if not config.get("cron_available"):
        return False

    try:
        # 获取当前 crontab
        result = subprocess.run(
            [config["cron_cmd"], "-l"],
            capture_output=True,
            text=True,
        )
        current_crons = result.stdout if result.returncode == 0 else ""

        # 移除指定命令
        lines = [line for line in current_crons.split("\n") if command not in line]
        new_crons = "\n".join(lines) + "\n"

        # 设置新的 crontab
        process = subprocess.Popen(
            [config["cron_cmd"], "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.communicate(input=new_crons)

        return process.returncode == 0

    except Exception as e:
        print(f"移除 cron 任务失败: {e}")
        return False


def get_system_info() -> Dict[str, Any]:
    """
    获取系统详细信息

    Returns:
        系统信息字典
    """
    import os

    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
        "home": str(Path.home()),
    }


if __name__ == "__main__":
    print("平台配置:")
    config = get_platform_config()
    for key, value in config.items():
        print(f"  {key}: {value}")

    print("\n依赖检查:")
    deps = check_dependencies()
    print(f"  全部满足: {deps['all_satisfied']}")
    for cmd, info in deps["required"].items():
        status = "✓" if info["available"] else "✗"
        print(f"  {status} {cmd}: {info.get('path', '未找到')}")
