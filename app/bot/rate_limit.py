"""Stage 1 速率限制配置。"""  # 存放速率桶相关默认值
from __future__ import annotations  # 保留未来注解特性

from dataclasses import dataclass  # 使用 dataclass 表达配置结构


@dataclass  # 定义速率限制配置实体
class RateLimitConfig:
    """描述全局与单聊的限速阈值。"""  # 方便在不同模块引用

    global_interval_seconds: float = 5.0  # 全局最短发送间隔（秒）
    chat_interval_seconds: float = 10.0  # 同一 chat 最短发送间隔（秒）


DEFAULT_RATE_LIMITS = RateLimitConfig()  # 提供默认限速实例供运行时引用
