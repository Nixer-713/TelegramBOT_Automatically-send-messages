#!/usr/bin/env python3
"""命令行入口：启动 FastAPI 后端并自动打开前端页面。"""
from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

try:
    import uvicorn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("未安装 uvicorn，请先运行 poetry add uvicorn 或 pip install uvicorn.\n") from exc

ROOT_DIR = Path(__file__).resolve().parent


def open_browser_later(url: str, delay: float = 1.5) -> None:
    def _open() -> None:
        time.sleep(delay)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()


def main() -> None:
    parser = argparse.ArgumentParser(description="运行可视化后端")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8000, help="监听端口，默认 8000")
    parser.add_argument("--reload", action="store_true", help="启用自动重载（开发环境）")
    args = parser.parse_args()

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    url = f"http://{args.host}:{args.port}/ui/"
    open_browser_later(url)

    uvicorn.run(
        "visualize.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
