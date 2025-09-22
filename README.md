# TG Auto Messenger (English Overview)

A lightweight broadcasting system built on the Telegram Bot API. It targets small-scale operations (≤5 chats) and currently delivers manual broadcasts with template management and a modern Vue-based dashboard. Stage 2 work (message queue + scheduler) is outlined but not yet implemented.

## ✨ Highlights
- **Template management** with versioning, Markdown/HTML parse modes, and delivery history (`was_sent`, `sent_at`).
- **Command-line broadcaster** supporting `--dry-run` previews and rate-limit hooks.
- **Vue dashboard** for multi-select send/delete actions, real-time stats, and animated gradient UI.
- **SQLite + SQLModel** for easy local persistence, ready to migrate to PostgreSQL + Alembic.
- **Pytest coverage** for template CRUD and broadcasting logic.

## 🗂 Directory
```text
app/              # Bot runtime, config, database models, services
examples/         # Helper scripts (e.g., insert sample templates)
visualize/        # FastAPI API + Vue frontend
run_backend.py    # Launch FastAPI backend and auto-open dashboard
解读.md           # Chinese project summary (personal notes)
```

## ⚙️ Getting Started
1. Install Poetry
   ```bash
   pip install poetry      # or follow Poetry official guide
   ```
2. Install dependencies
   ```bash
   poetry install --no-root
   ```
3. Configure environment variables
   ```bash
   cp .env.example .env
   # edit .env with real BOT_TOKEN / DATABASE_URL / TIMEZONE
   ```

## 🚀 Usage
### Insert a sample template (optional)
```bash
poetry run python examples/write_pending_message.py
```

### Manual broadcast (CLI)
```bash
poetry run python -m app.bot.main broadcast \
  --template welcome \
  --chat-id <target_chat_id> \
  --dry-run
```
Remove `--dry-run` after confirming the preview. `chat_id` can be obtained via `https://api.telegram.org/bot<token>/getUpdates`.

### Launch dashboard
```bash
poetry run python run_backend.py --reload
```
- FastAPI listens on `http://127.0.0.1:8000`
- Browser auto-opens `http://127.0.0.1:8000/ui/`
- Select templates + chats to send or delete; dashboard tab shows totals

### Database migration tip
If your SQLite file was created prior to `was_sent/sent_at` fields, run:
```bash
poetry run python data/append_column.py
```
or delete `data/app.db` to let SQLModel recreate the schema.

## ✅ Tests
```bash
poetry run pytest
```
Covers template CRUD, bulk updates, and broadcasting logic.

## 🔮 Stage 2 Blueprint (not implemented yet)
- Tables `pending_messages` and `deliveries` for queued content and delivery history
- `SchedulerService` powered by APScheduler / PTB JobQueue for periodic sends
- Dashboard extensions for review queues and send statistics
- Alembic migrations + optional PostgreSQL/Redis integration

## 📌 Helpful Commands
```bash
poetry run python -m app.db.session      # create SQLite schema
poetry run python -m app.bot.main --help # CLI reference
poetry run python run_backend.py --help  # backend launch options
```

The current code base handles template authoring, manual sending, and a modern dashboard experience. Stage 2 automation work (queue + scheduler) remains open for future development.
