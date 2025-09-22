"""Stage 1 配置读取与缓存工具。"""  # 对外提供环境变量读取能力
from __future__ import annotations  # 支持前向引用的类型注解

import os  # 访问系统环境变量
from dataclasses import dataclass, field  # 使用 dataclass 定义结构化配置对象
from functools import lru_cache  # 通过缓存避免重复解析
from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)  # 使用 slots 限制属性
class Settings:  # 封装所有运行时配置项
    """从环境变量构建的轻量配置对象。"""

    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", "CHANGE_ME"))  # 默认占位 token，可被外部覆盖
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/app.db"))  # 默认指向本地 SQLite
    timezone: str = field(default_factory=lambda: os.getenv("TIMEZONE", "UTC"))  # 默认时区


@lru_cache(maxsize=1)  # 缓存配置实例
def _settings_cache() -> Settings:
    """返回缓存的配置对象。"""

    return Settings()  # 每次调用都会重新读取环境变量


def get_settings() -> Settings:
    """获取当前缓存的运行配置。"""

    return _settings_cache()


def reload_settings() -> Settings:
    """清除缓存并重新构建配置实例。"""

    _settings_cache.cache_clear()  # 清空缓存
    return get_settings()  # 返回新的配置对象
