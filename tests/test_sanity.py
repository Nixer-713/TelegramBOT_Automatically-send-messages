"""Stage 1 烟雾测试。"""  # 快速验证配置与限流默认值
from __future__ import annotations  # 兼容未来注解

from app.bot.rate_limit import DEFAULT_RATE_LIMITS  # 导入速率限制默认值


def test_settings_fixture(settings) -> None:  # 检查 settings 夹具效果
    """确认环境变量覆盖成功。"""
    assert settings.bot_token == "TEST_TOKEN"  # BOT_TOKEN 应被覆盖成测试值
    assert settings.database_url.startswith("sqlite:///")  # 数据库应指向临时 SQLite


def test_rate_limit_defaults() -> None:  # 检查限速默认值是否符合需求
    """校验速率限制默认配置。"""
    assert DEFAULT_RATE_LIMITS.global_interval_seconds == 5.0  # 全局间隔为 5 秒
    assert DEFAULT_RATE_LIMITS.chat_interval_seconds == 10.0  # 单聊间隔为 10 秒
