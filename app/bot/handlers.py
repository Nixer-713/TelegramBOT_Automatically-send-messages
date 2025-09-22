"""Stage 1 指令处理器占位。"""  # 未来会注册 Telegram Bot 指令
from __future__ import annotations  # 兼容未来注解写法

from typing import Any  # 使用 Any 适配 PTB 的 Application 对象


def register_handlers(application: Any) -> None:  # 后续将把各类处理器挂载到 bot 实例
    """Stage 2 及以后再实现指令注册。"""  # 当前阶段仅声明接口
    raise NotImplementedError("处理器将在下一阶段补全。")  # 显式提醒开发者
