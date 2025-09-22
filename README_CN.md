# TG Auto Messenger

基于 Telegram Bot API 的轻量广播系统，可向少量群组/频道/私聊发送模板化通知，支持命令行发送与可视化控制台操作。当前完成“手动广播 + 模板管理 + 可视化”闭环，其余自动调度（Stage 2）规划已沉淀在文档中，便于后续二次开发。

## ✨ 功能亮点
- **模板管理**：版本号自动递增、Markdown/HTML 解析、发送状态与时间记录。
- **手动广播 CLI**：`--dry-run` 预览，便于上线前确认；默认限速配置可扩展。
- **Vue 控制台**：批量勾选模板 + Chat 即刻发送/删除，仪表盘概览统计，动态渐变背景提升视觉体验。
- **SQLite + SQLModel**：轻量级存储，可平滑迁移至 PostgreSQL + Alembic。
- **pytest 套件**：覆盖模板 CRUD 与广播流程，保障迭代质量。

## 📦 目录结构
```text
app/
  bot/            # 广播入口、未来调度占位
  config.py       # 配置读取（支持 .env）
  db/             # SQLModel 数据结构与 Session 辅助
  services/       # 模板业务逻辑
examples/         # 写入数据库的示例脚本
visualize/
  api.py          # FastAPI 后端，提供 /api 接口并托管前端
  frontend/       # Vue 前端控制台
run_backend.py    # 启动后端并自动打开前端页面
解读.md           # 项目背景与经验总结
```

## ⚙️ 环境准备
1. 安装 [Poetry](https://python-poetry.org/docs/#installation)
2. 安装依赖
   ```bash
   poetry install --no-root
   ```
3. 复制并修改环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env，填入真实 BOT_TOKEN / DATABASE_URL / TIMEZONE
   ```

## 🚀 使用说明
### 1. 写入示例模板（可选）
```bash
poetry run python examples/write_pending_message.py
```
脚本自动定位项目根目录，调用 `TemplateService` 写入/更新 `messagetemplate` 表中的记录。

### 2. 手动广播 CLI
```bash
poetry run python -m app.bot.main broadcast \
  --template welcome \
  --chat-id <目标 chat_id> \
  --dry-run
```
- `--dry-run` 用于预览，确认文本无误后去掉即可真实发送。
- `chat_id` 可通过 `https://api.telegram.org/bot<token>/getUpdates` 获取。

### 3. 启动可视化控制台
```bash
poetry run python run_backend.py --reload
```
- 默认监听 `http://127.0.0.1:8000`
- 脚本会自动打开 `http://127.0.0.1:8000/ui/`
- 可在页面中勾选模板与 Chat，批量执行“立即发送/批量删除”，仪表盘统计概览

### 4. 数据库结构自检
新增字段 `was_sent`、`sent_at` 后，如老库缺列，可执行：
```bash
poetry run python data/append_column.py
```
或直接删除 `data/app.db` 让系统重新建表。

## ✅ 测试
```bash
poetry run pytest
```
覆盖以下核心场景：
- 模板创建、更新、删除、批量标记已发送
- 环境变量覆盖与配置缓存
- 广播逻辑（含 dry-run、发送调用）

## 🔄 Stage 2 蓝图（自动调度）
为了实现“外部写库 → 自动筛选 → 自动群发”的闭环，可参考以下方案：

### 数据模型规划
```text
pending_messages (
  id                INTEGER PRIMARY KEY,
  title             TEXT,
  body              TEXT,
  target_template   TEXT NOT NULL,
  max_recipients    INTEGER NULL,
  status            TEXT DEFAULT 'new',    -- new|queued|sent|skipped
  priority          INTEGER DEFAULT 0,
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  available_at      DATETIME NULL,
  metadata_json     TEXT NULL
)

deliveries (
  id                 INTEGER PRIMARY KEY,
  message_id         INTEGER REFERENCES pending_messages(id),
  chat_id            INTEGER NOT NULL,
  status             TEXT NOT NULL,
  error_code         TEXT NULL,
  attempt            INTEGER DEFAULT 1,
  sent_at            DATETIME NULL,
  retry_after        INTEGER NULL,
  note               TEXT NULL
)
```

### 模块分工
| 模块 | 说明 |
| --- | --- |
| 数据写入端 | 外部项目/脚本写入 `pending_messages`，可通过 REST API 封装； |
| 内容调度器 | `SchedulerService` 周期读取 `pending_messages`，筛选优先级、控制节奏； |
| 广播执行器 | 复用 `broadcast.py`，支持 dry-run、失败重试、限速； |
| 发送日志 | `deliveries` 记录成功/失败，可做统计或重试； |
| 前端扩展 | 在控制台加入待发送队列视图、人工审核入口。 |

### 开发清单
1. 新增 SQLModel 模型与数据迁移脚本；
2. 实现 `MessageQueueService`，封装入队/出队/标记逻辑；
3. 在 `SchedulerService` 接入 APScheduler 或 PTB JobQueue；
4. 扩展前端 UI 显示队列、审核状态；
5. 编写单元/集成测试覆盖调度和重试流程。

## 📌 常用命令速查
```bash
poetry run python -m app.db.session      # 初始化 SQLite schema
poetry run python -m app.bot.main --help# 查看广播 CLI 帮助
poetry run python run_backend.py --help  # 查看后端启动参数
```

## 📝 参考
- Telegram Bot API 官方文档
- `解读.md`：项目背景与个人经验总结
- `visualize/frontend/index.html`：扁平化 + 动态渐变的 Vue 控制台实现

> 当前版本完成数据库录入、模板发送与可视化；Stage 2 自动调度功能仍待开发，欢迎在此基础上继续拓展。
