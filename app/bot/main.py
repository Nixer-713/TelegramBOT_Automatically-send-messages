"""Stage 1 提供机器人命令行工具。"""  # 通过命令行执行初始化或手动广播
from __future__ import annotations  # 启用未来注解语法

import argparse  # 解析命令行参数
from typing import Sequence  # 表示 argv 形态的序列类型

from app.bot.broadcast import run_manual_broadcast  # 引入手动广播同步入口
from app.config import get_settings  # 提前加载配置，校验必需变量
from app.db.session import init_db  # 提供数据库初始化能力


def build_parser() -> argparse.ArgumentParser:  # 构建命令行解析器
    """创建命令行参数解析器。"""  # 目前支持 init-db 与 broadcast 两种子命令

    parser = argparse.ArgumentParser(description="TG Auto Messenger 机器人工具集")  # 设置描述信息
    subparsers = parser.add_subparsers(dest="command")  # 创建子命令分组

    subparsers.add_parser("init-db", help="初始化数据库结构")  # 注册 init-db 子命令

    broadcast_parser = subparsers.add_parser("broadcast", help="使用模板执行手动广播")  # 注册 broadcast 子命令
    broadcast_parser.add_argument("--template", required=True, help="要加载的模板名称")  # 必填参数：模板名
    broadcast_parser.add_argument("--chat-id", required=True, type=int, help="目标 chat 的 ID")  # 必填参数：目标 chat
    broadcast_parser.add_argument("--text", help="可选的消息覆盖文本")  # 可选：覆盖模板内容
    broadcast_parser.add_argument("--dry-run", action="store_true", help="仅预览，不真正发送")  # dry-run 开关

    return parser  # 返回组装好的解析器


def main(argv: Sequence[str] | None = None) -> None:  # 主函数供 poetry run 调用
    """命令行入口，处理初始化与广播需求。"""

    get_settings()  # 提前加载配置，若缺少 token 会直接报错
    parser = build_parser()  # 初始化解析器
    args = parser.parse_args(argv)  # 解析外部传入的参数

    if args.command == "init-db":  # 处理 init-db 场景
        init_db()  # 创建数据库表结构
        print("数据库初始化完成。")  # 告知用户
        return  # 任务结束

    if args.command == "broadcast":  # 处理广播指令
        result = run_manual_broadcast(template_name=args.template, chat_id=args.chat_id, override_text=args.text, dry_run=args.dry_run)  # 调用同步封装
        if result.dry_run:  # dry-run 模式
            print(f"[dry-run] 将向 {result.chat_id} 发送模板 '{result.template_name}':\n{result.text}")  # 输出预览
        else:  # 实际发送模式
            print(f"已向 {result.chat_id} 发送模板 '{result.template_name}'。")  # 输出结果
        return  # 广播结束

    parser.print_help()  # 未提供子命令时显示帮助


if __name__ == "__main__":  # pragma: no cover - 供直接运行调试使用
    main()  # 执行命令行入口
