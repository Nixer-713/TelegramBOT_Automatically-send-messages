"""示例脚本：演示调用 TemplateService 写入模板。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import init_db, session_scope
from app.services.templates import TemplateService


def main() -> None:
    init_db()
    with session_scope() as session:
        service = TemplateService(session)
        tpl = service.create_template(
            name="test_from_script",
            text="这是从 examples/write_pending_message.py 写入或更新的内容",
            parse_mode="HTML",
        )
        print("模板信息：", tpl)


if __name__ == "__main__":
    main()
