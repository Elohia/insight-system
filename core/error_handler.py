#!/usr/bin/env python3
"""
容灾处理与重试机制
"""

import traceback
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Any, Optional, TypeVar, Generic
from functools import wraps
from dataclasses import dataclass, field

# 尝试导入 config，避免循环依赖
try:
    from config import get_error_log_file
except ImportError:
    def get_error_log_file() -> str:
        return str(Path.home() / ".openclaw" / "logs" / "errors.log")


T = TypeVar('T')


@dataclass
class ErrorRecord:
    """错误记录"""
    timestamp: str
    error_type: str
    error_message: str
    traceback: str
    context: dict = field(default_factory=dict)
    retry_count: int = 0


class ErrorHandler:
    """容灾处理"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 60):
        """
        初始化错误处理器

        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_log = Path(get_error_log_file())

        # 确保日志目录存在
        self.error_log.parent.mkdir(parents=True, exist_ok=True)

    def log_error(
        self,
        error: Exception,
        context: Optional[dict] = None,
        retry_count: int = 0
    ) -> ErrorRecord:
        """
        记录错误到日志

        Args:
            error: 异常对象
            context: 上下文信息
            retry_count: 重试次数

        Returns:
            错误记录
        """
        record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=traceback.format_exc(),
            context=context or {},
            retry_count=retry_count,
        )

        # 写入日志文件
        with open(self.error_log, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"[{record.timestamp}] {record.error_type}\n")
            f.write(f"消息: {record.error_message}\n")
            if record.context:
                f.write(f"上下文: {json.dumps(record.context, ensure_ascii=False)}\n")
            if retry_count > 0:
                f.write(f"重试次数: {retry_count}\n")
            f.write(f"堆栈:\n{record.traceback}\n")

        return record

    def retry_with_backoff(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        指数退避重试

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            最后一次重试的错误
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e

                if attempt == self.max_retries - 1:
                    # 最后一次尝试，记录错误并抛出
                    self.log_error(e, {"attempt": attempt + 1})
                    raise

                wait_time = self.retry_delay * (2 ** attempt)
                print(f"⚠️ 错误: {e}, {self.max_retries - attempt - 1}秒后重试...")

                # 记录非致命错误
                self.log_error(e, {"attempt": attempt + 1}, retry_count=attempt + 1)

                time.sleep(wait_time)

        # 不应该到达这里
        if last_error:
            raise last_error

    def retry_decorator(self, max_retries: Optional[int] = None, retry_delay: Optional[float] = None):
        """
        重试装饰器

        Args:
            max_retries: 最大重试次数（覆盖实例设置）
            retry_delay: 重试延迟（覆盖实例设置）

        Returns:
            装饰器函数
        """
        _max_retries = max_retries or self.max_retries
        _retry_delay = retry_delay or self.retry_delay

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                last_error = None

                for attempt in range(_max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_error = e

                        if attempt == _max_retries - 1:
                            self.log_error(e, {"function": func.__name__, "attempt": attempt + 1})
                            raise

                        wait_time = _retry_delay * (2 ** attempt)
                        print(f"⚠️ {func.__name__} 错误: {e}, {wait_time:.1f}秒后重试...")

                        time.sleep(wait_time)

                if last_error:
                    raise last_error

            return wrapper
        return decorator

    def health_check(self) -> dict:
        """
        健康检查

        Returns:
            健康检查结果
        """
        results = {
            "status": "healthy",
            "checks": {},
        }

        # 检查日志目录可写
        try:
            test_file = self.error_log.parent / ".health_check"
            test_file.touch()
            test_file.unlink()
            results["checks"]["log_writable"] = True
        except Exception as e:
            results["checks"]["log_writable"] = False
            results["status"] = "unhealthy"

        # 检查依赖
        try:
            import importlib
            for mod in ["anthropic", "chromadb"]:
                try:
                    importlib.import_module(mod)
                    results["checks"][f"module_{mod}"] = True
                except ImportError:
                    results["checks"][f"module_{mod}"] = False
        except Exception as e:
            results["checks"]["dependencies"] = False

        return results

    def get_recent_errors(self, limit: int = 10) -> list:
        """
        获取最近的错误记录

        Args:
            limit: 返回数量限制

        Returns:
            错误记录列表
        """
        if not self.error_log.exists():
            return []

        with open(self.error_log, "r", encoding="utf-8") as f:
            content = f.read()

        # 简单解析：按时间戳分割
        errors = content.split("=" * 60)
        errors = [e.strip() for e in errors if e.strip()]

        return errors[-limit:] if len(errors) > limit else errors


# 全局错误处理器实例
default_handler = ErrorHandler()


def retry(
    max_retries: int = 3,
    retry_delay: float = 60,
    on_error: Optional[Callable[[Exception], None]] = None
):
    """
    简单的重试装饰器

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        on_error: 错误回调

    Returns:
        装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    if attempt == max_retries - 1:
                        if on_error:
                            on_error(e)
                        raise

                    wait_time = retry_delay * (2 ** attempt)
                    print(f"⚠️ {func.__name__}: {e}, {wait_time:.1f}秒后重试...")
                    time.sleep(wait_time)

            if last_error:
                raise last_error

        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试错误处理器
    handler = ErrorHandler()

    print("健康检查:")
    health = handler.health_check()
    print(f"  状态: {health['status']}")
    for check, result in health['checks'].items():
        print(f"  {'✓' if result else '✗'} {check}")

    print("\n最近的错误:")
    errors = handler.get_recent_errors(5)
    print(f"  共 {len(errors)} 条")
