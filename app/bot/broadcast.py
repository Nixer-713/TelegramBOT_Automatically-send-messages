"""Stage 1 手动广播相关工具。"""  # 提供干/湿运行的手动群发能力
from __future__ import annotations  # 允许在注解中引用后定义的类型

import asyncio  # 用于在同步环境中运行异步协程
from dataclasses import dataclass  # 用 dataclass 表达广播结果

from telegram import Bot  # Telegram 官方 Bot 客户端

from app.config import get_settings  # 读取运行时配置（如 BOT_TOKEN）
from app.db.session import init_db, session_scope  # 初始化数据库并提供会话上下文
from app.services.templates import TemplateNotFoundError, TemplateService  # 使用模板服务读取或校验模板


@dataclass(slots=True)  # 使用 slots 减少开销
class ManualBroadcastResult:
    """保存一次手动广播的关键结果数据。"""  # 对外返回模板名、目标 chat、文本及 dry-run 标记

    template_name: str  # 发送使用的模板名称
    chat_id: int  # 目标 chat 的 ID
    text: str  # 实际发送或预览的文本
    dry_run: bool  # 标记是否仅为预览


async def send_manual_broadcast(*, template_name: str, chat_id: int, override_text: str | None = None, dry_run: bool = False) -> ManualBroadcastResult:  # 执行真正的广播逻辑
    """根据模板向指定 chat 发送消息，可选择仅预览。"""  # 支持 override 文本与 dry-run

    init_db()  # 确保第一次运行时数据库表已创建

    with session_scope() as session:  # 在数据库会话中读取模板
        service = TemplateService(session)  # 实例化模板服务
        template = service.get_template(template_name)  # 获取模板，找不到会抛出 TemplateNotFoundError

    message_text = override_text or template.text  # 优先使用覆盖文本，否则采用模板内容
    parse_mode = template.parse_mode  # 保留模板指定的 parse_mode

    if dry_run:  # 预览模式下不调用 Telegram API
        return ManualBroadcastResult(template_name=template_name, chat_id=chat_id, text=message_text, dry_run=True)  # 返回预览结果

    bot = Bot(token=get_settings().bot_token)  # 根据配置创建 Telegram Bot 客户端
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode=parse_mode)  # 异步调用 Telegram 发送消息

    return ManualBroadcastResult(template_name=template_name, chat_id=chat_id, text=message_text, dry_run=False)  # 返回发送成功的数据


def run_manual_broadcast(*, template_name: str, chat_id: int, override_text: str | None = None, dry_run: bool = False) -> ManualBroadcastResult:  # 提供同步封装，方便 CLI 使用
    """同步封装的手动广播入口，供命令行调用。"""  # 内部调用异步函数

    try:
        return asyncio.run(send_manual_broadcast(template_name=template_name, chat_id=chat_id, override_text=override_text, dry_run=dry_run))  # 通过 asyncio.run 执行协程
    except TemplateNotFoundError as exc:  # pragma: no cover - 防御性分支
        raise SystemExit(f"未找到模板：{exc}") from exc  # 提示用户模板缺失
