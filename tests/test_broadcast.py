"""Tests for manual broadcast helper."""  # Docstring describing focus on broadcast utilities
from __future__ import annotations  # Enable postponed annotation evaluation

import pytest  # Use pytest markers and fixtures for async testing

from app.bot.broadcast import ManualBroadcastResult, send_manual_broadcast  # Import coroutine under test and result dataclass
from app.db.session import init_db, session_scope  # Provide database helpers for fixture setup
from app.services.templates import TemplateService  # Use TemplateService to create templates for broadcast


@pytest.mark.asyncio()  # Mark test as asynchronous to run coroutine directly
async def test_manual_broadcast_dry_run(temp_env) -> None:  # Ensure dry-run returns preview without network call
    """Dry-run should skip Telegram calls and echo content."""  # Docstring clarifying expectation

    init_db()  # Prepare database schema
    with session_scope() as session:  # Obtain session for template creation
        TemplateService(session).create_template(name="welcome", text="Hello ::)")  # Insert template used for broadcast

    result = await send_manual_broadcast(template_name="welcome", chat_id=123, dry_run=True)  # Execute coroutine with dry_run flag and capture result

    assert isinstance(result, ManualBroadcastResult)  # Validate return type matches dataclass
    assert result.dry_run is True  # Confirm dry_run flag preserved
    assert result.text == "Hello ::)"  # Ensure template content returned untouched


@pytest.mark.asyncio()  # Enable event loop for coroutine execution
async def test_manual_broadcast_sends_message(monkeypatch, temp_env) -> None:  # Verify real execution calls Telegram Bot API
    """Real run should call Telegram Bot API with template content."""  # Docstring recording behaviour being tested

    init_db()  # Bootstrap schema before template creation
    with session_scope() as session:  # Create transactional session
        TemplateService(session).create_template(name="welcome", text="Hello ::)")  # Insert template for live send scenario

    calls: list[tuple[int, str, str | None]] = []  # Track Bot.send_message invocations for assertion

    class FakeBot:  # Define lightweight stub replacing python-telegram-bot Bot class
        def __init__(self, token: str) -> None:  # Capture token to mimic real constructor signature
            self.token = token  # Store provided token for optional debugging

        async def send_message(self, chat_id: int, text: str, parse_mode: str | None = None):  # Mimic async send_message behaviour
            calls.append((chat_id, text, parse_mode))  # Record call parameters for later validation

    monkeypatch.setattr("app.bot.broadcast.Bot", FakeBot)  # Patch broadcast module to use FakeBot instead of real API client

    result = await send_manual_broadcast(template_name="welcome", chat_id=456, dry_run=False)  # Execute coroutine performing actual send (now patched)

    assert calls == [(456, "Hello ::)", "MarkdownV2")]  # Verify FakeBot captured expected call and parse mode
    assert result.dry_run is False  # Confirm result indicates live send
