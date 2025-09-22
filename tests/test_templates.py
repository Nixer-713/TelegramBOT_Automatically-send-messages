"""Stage 1 模板服务单元测试。"""
from __future__ import annotations

from app.db.session import init_db, session_scope
from app.services.templates import TemplateNotFoundError, TemplateService


def test_create_and_list_templates(temp_env) -> None:
    """模板创建后应按名称排序列出。"""

    init_db()
    with session_scope() as session:
        service = TemplateService(session)
        tpl1 = service.create_template(name="welcome", text="Hello")
        tpl2 = service.create_template(name="update", text="Latest news")

        assert tpl1.was_sent is False and tpl1.sent_at is None
        assert tpl2.was_sent is False and tpl2.sent_at is None

        templates = service.list_templates()
        assert [tpl.name for tpl in templates] == ["update", "welcome"]


def test_create_updates_existing_template(temp_env) -> None:
    """重复创建应更新版本并覆盖内容。"""

    init_db()
    with session_scope() as session:
        service = TemplateService(session)
        first = service.create_template(name="welcome", text="Hello")
        initial_version = first.version
        first.was_sent = True
        first.sent_at = None
        session.add(first)
        session.commit()

        second = service.create_template(name="welcome", text="Hi")

        assert second.id == first.id
        assert second.version == initial_version + 1
        assert second.text == "Hi"
        assert second.was_sent is False and second.sent_at is None


def test_mark_templates_sent(temp_env) -> None:
    """批量标记模板已发送。"""

    init_db()
    with session_scope() as session:
        service = TemplateService(session)
        tpl1 = service.create_template(name="a", text="A")
        tpl2 = service.create_template(name="b", text="B")
        updated = service.mark_templates_sent([tpl1.id, tpl2.id])
        assert len(updated) == 2
        for tpl in updated:
            assert tpl.was_sent is True
            assert tpl.sent_at is not None


def test_delete_templates(temp_env) -> None:
    """批量删除模板。"""

    init_db()
    with session_scope() as session:
        service = TemplateService(session)
        tpl1 = service.create_template(name="a", text="A")
        tpl2 = service.create_template(name="b", text="B")
        deleted = service.delete_templates([tpl1.id, tpl2.id])
        assert deleted == 2
        assert service.list_templates() == []


def test_get_missing_template_raises(temp_env) -> None:
    """读取不存在的模板时抛出 TemplateNotFoundError。"""

    init_db()
    with session_scope() as session:
        service = TemplateService(session)
        try:
            service.get_template("absent")
        except TemplateNotFoundError as exc:
            assert str(exc) == "absent"
        else:  # pragma: no cover - 防御逻辑
            raise AssertionError("预期抛出 TemplateNotFoundError")
