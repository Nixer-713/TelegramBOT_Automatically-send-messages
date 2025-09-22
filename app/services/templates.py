"""Stage 1 模板业务服务。"""
from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.db.models import MessageTemplate, touch_template


class TemplateNotFoundError(Exception):
    """请求的模板不存在时抛出。"""


class TemplateService:
    """提供模板的创建、读取、列表与删除能力。"""

    def __init__(self, session: Session):
        self.session = session

    def create_template(self, name: str, text: str, *, parse_mode: str = "MarkdownV2") -> MessageTemplate:
        """当模板不存在时创建，存在则更新内容并递增版本号。"""

        existing = self.session.exec(select(MessageTemplate).where(MessageTemplate.name == name)).one_or_none()
        if existing:
            existing.version += 1
            existing.text = text
            existing.parse_mode = parse_mode
            existing.was_sent = False  # 更新内容后视为未发送
            existing.sent_at = None
            touch_template(existing)
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing

        template = MessageTemplate(name=name, text=text, parse_mode=parse_mode)
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return template

    def mark_templates_sent(self, template_ids: list[int]) -> list[MessageTemplate]:
        """批量标记模板已发送。"""

        if not template_ids:
            return []
        templates = self.session.exec(
            select(MessageTemplate).where(MessageTemplate.id.in_(template_ids))
        ).all()
        now = datetime.utcnow()
        for tpl in templates:
            tpl.was_sent = True
            tpl.sent_at = now
            touch_template(tpl)
            self.session.add(tpl)
        self.session.commit()
        for tpl in templates:
            self.session.refresh(tpl)
        return templates

    def get_template(self, name: str) -> MessageTemplate:
        template = self.session.exec(select(MessageTemplate).where(MessageTemplate.name == name)).one_or_none()
        if template is None:
            raise TemplateNotFoundError(name)
        return template

    def get_template_by_id(self, template_id: int) -> MessageTemplate:
        template = self.session.get(MessageTemplate, template_id)
        if template is None:
            raise TemplateNotFoundError(str(template_id))
        return template

    def list_templates(self, include_sent: bool = True) -> list[MessageTemplate]:
        """返回按更新时间降序的模板列表。"""

        query = select(MessageTemplate).order_by(MessageTemplate.updated_at.desc())
        if not include_sent:
            query = query.where(MessageTemplate.was_sent.is_(False))
        result = self.session.exec(query).all()
        return list(result)

    def delete_templates(self, template_ids: list[int]) -> int:
        if not template_ids:
            return 0
        templates = self.session.exec(
            select(MessageTemplate).where(MessageTemplate.id.in_(template_ids))
        ).all()
        for tpl in templates:
            self.session.delete(tpl)
        self.session.commit()
        return len(templates)

    def delete_template(self, name: str) -> None:
        template = self.session.exec(select(MessageTemplate).where(MessageTemplate.name == name)).one_or_none()
        if template is None:
            raise TemplateNotFoundError(name)
        self.session.delete(template)
        self.session.commit()
