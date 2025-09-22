"""Stage 1 SQLModel 数据模型定义。"""  # 集中声明模板与聊天表
from __future__ import annotations  # 支持前向引用的类型注解

from datetime import datetime

from sqlmodel import Field, SQLModel


class MessageTemplate(SQLModel, table=True):
    """保存群发模板及版本信息。"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=1, max_length=100)
    version: int = Field(default=1, ge=1)
    text: str
    parse_mode: str = Field(default="MarkdownV2")
    was_sent: bool = Field(default=False, nullable=False)  # 新增：是否已经成功发送过
    sent_at: datetime | None = Field(default=None, nullable=True)  # 新增：最近一次发送时间
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Chat(SQLModel, table=True):
    """维护目标 chat 的基本信息。"""

    chat_id: int = Field(primary_key=True)
    type: str = Field(default="group", min_length=1, max_length=32)
    title: str | None = None
    is_active: bool = Field(default=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    notes: str | None = Field(default=None, max_length=255)


def touch_template(template: MessageTemplate) -> None:
    """在模板被修改时刷新 updated_at 字段。"""

    template.updated_at = datetime.utcnow()


def init_models() -> None:
    """保留模型初始化钩子，当前未使用。"""

    return None
