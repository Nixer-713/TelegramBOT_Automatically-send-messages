"""FastAPI 后端：为可视化界面提供模板/广播操作接口。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db.models import Chat
from app.services.templates import TemplateService
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.bot.broadcast import send_manual_broadcast
from app.db.session import get_engine, init_db

init_db()

app = FastAPI(title="TG Auto Messenger Visualize API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount(
        "/ui",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend",
    )


def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    with Session(engine) as session:
        yield session


class TemplateDTO(BaseModel):
    id: int
    name: str
    version: int
    text: str
    parse_mode: str
    was_sent: bool
    sent_at: datetime | None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TemplatesResponse(BaseModel):
    items: list[TemplateDTO]


class SendRequest(BaseModel):
    template_ids: list[int] = Field(default_factory=list)
    chat_ids: list[int] = Field(default_factory=list)


class DeleteRequest(BaseModel):
    template_ids: list[int] = Field(default_factory=list)


@app.get("/", response_class=FileResponse)
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="前端页面缺失")
    return FileResponse(index_path)


@app.get("/api/templates", response_model=TemplatesResponse)
async def list_templates(include_sent: bool = True, session: Session = Depends(get_session)):
    service = TemplateService(session)
    items = service.list_templates(include_sent=include_sent)
    return TemplatesResponse(items=items)


@app.get("/api/chats")
async def list_chats(session: Session = Depends(get_session)):
    chats = session.exec(select(Chat).where(Chat.is_active.is_(True))).all()
    return [
        {
            "chat_id": chat.chat_id,
            "title": chat.title or str(chat.chat_id),
            "type": chat.type,
        }
        for chat in chats
    ]


@app.post("/api/templates/send", response_model=TemplatesResponse)
async def send_templates(payload: SendRequest, session: Session = Depends(get_session)):
    if not payload.template_ids:
        raise HTTPException(status_code=400, detail="template_ids 不能为空")
    if not payload.chat_ids:
        raise HTTPException(status_code=400, detail="chat_ids 不能为空")

    service = TemplateService(session)
    templates = [service.get_template_by_id(template_id) for template_id in payload.template_ids]

    for tpl in templates:
        for chat_id in payload.chat_ids:
            await send_manual_broadcast(
                template_name=tpl.name,
                chat_id=chat_id,
                override_text=None,
                dry_run=False,
            )

    service.mark_templates_sent(payload.template_ids)
    items = service.list_templates()
    return TemplatesResponse(items=items)


@app.post("/api/templates/delete", response_model=TemplatesResponse)
async def delete_templates(payload: DeleteRequest, session: Session = Depends(get_session)):
    service = TemplateService(session)
    if payload.template_ids:
        service.delete_templates(payload.template_ids)
    items = service.list_templates()
    return TemplatesResponse(items=items)
