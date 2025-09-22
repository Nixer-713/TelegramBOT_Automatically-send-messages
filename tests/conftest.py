"""Stage 1 通用测试夹具。"""  # 为测试提供统一的环境配置
from __future__ import annotations  # 保持类型注解的前向兼容

import pathlib  # 构建临时数据库文件路径
import tempfile  # 提供临时目录上下文

import pytest  # 引入 pytest 夹具机制

from app import config  # 用于刷新配置缓存
from app.db import session as db_session  # 控制 SQLModel Engine 的创建与销毁


@pytest.fixture()
def temp_env(monkeypatch: pytest.MonkeyPatch) -> None:  # 为每个测试提供隔离环境
    """使用临时目录作为 SQLite 数据库，并注入测试用环境变量。"""

    with tempfile.TemporaryDirectory() as tmpdir:  # 创建自动清理的临时目录
        db_path = pathlib.Path(tmpdir) / "test.db"  # 构造 SQLite 路径
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")  # 指定测试数据库
        monkeypatch.setenv("BOT_TOKEN", "TEST_TOKEN")  # 设置可预测的 token
        monkeypatch.setenv("TIMEZONE", "UTC")  # 固定时区
        config.reload_settings()  # 清空并重建配置缓存
        db_session.reset_engine()  # 重建 SQLModel Engine
        yield  # 交还控制权给测试
        config.reload_settings()  # 测试结束后再次刷新配置
        db_session.reset_engine()  # 释放 Engine，避免文件锁


@pytest.fixture()
def settings(temp_env) -> config.Settings:  # 返回已经应用测试环境变量的配置
    """返回测试环境下的配置实例。"""

    return config.get_settings()  # 获取缓存好的 Settings 对象
