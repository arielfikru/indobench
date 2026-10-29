"""FastAPI: menyajikan halaman statis, GET /api/catalog, dan POST /api/submit.

Endpoint POST hanya menerima JSON. Token Hugging Face hanya dipakai di sisi server.
"""

from __future__ import annotations

import collections
import json
import logging
import secrets
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

import catalog
from storage import Storage
from validate import GENERIC_ERROR, build_record, honeypot_filled, validate_submission

log = logging.getLogger("submit.server")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

MAX_BODY_BYTES = 50 * 1024
RATE_LIMIT_PER_HOUR = 20
RATE_WINDOW_SECONDS = 3600

MSG_TOO_LARGE = "Data terlalu besar. Batas 50 KB."
MSG_TOO_MANY = "Kamu sudah mengirim banyak soal dalam satu jam. Coba lagi nanti."
MSG_SAVE_FAILED = "Soal belum bisa disimpan karena gangguan server. Coba lagi beberapa saat lagi."


class RateLimiter:
    """Batas sederhana di memori: `limit` permintaan per `window` detik untuk tiap kunci (IP)."""

    def __init__(self, limit: int, window: float, clock=time.monotonic):
        self.limit = limit
        self.window = window
        self._clock = clock
        self._hits: dict[str, collections.deque] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = self._clock()
        with self._lock:
            hits = self._hits.setdefault(key, collections.deque())
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse({"ok": False, "errors": {"_form": message}}, status_code=status)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        # The HF Spaces proxy appends the real peer address; earlier entries are client-supplied.
        return forwarded.split(",")[-1].strip() or "unknown"
    return request.client.host if request.client else "unknown"


def create_app(storage: Storage | None = None,
               rate_limit: int = RATE_LIMIT_PER_HOUR,
               rate_window: float = RATE_WINDOW_SECONDS) -> FastAPI:
    store = storage if storage is not None else Storage.from_env()
    known_hashes = store.load_hashes()
    limiter = RateLimiter(rate_limit, rate_window)
    save_lock = threading.Lock()

    app = FastAPI(title="Kirim Soal indobench", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/api/catalog")
    def get_catalog():
        return JSONResponse(catalog.public_catalog())

    @app.post("/api/submit")
    async def submit(request: Request):
        declared = request.headers.get("content-length", "")
        if declared.isdigit() and int(declared) > MAX_BODY_BYTES:
            return _error(413, MSG_TOO_LARGE)
        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            return _error(413, MSG_TOO_LARGE)

        if not limiter.allow(_client_ip(request)):
            return _error(429, MSG_TOO_MANY)

        try:
            payload = json.loads(body) if body else None
        except ValueError:
            payload = None
        if not isinstance(payload, dict) or honeypot_filled(payload):
            return _error(400, GENERIC_ERROR)

        def process():
            with save_lock:
                clean, errors = validate_submission(payload, known_hashes)
                if errors:
                    return 400, {"ok": False, "errors": errors}
                sid = "sub-" + secrets.token_hex(5)
                record, contact = build_record(clean, sid)
                try:
                    store.save(record, contact)
                except Exception as exc:  # noqa: BLE001 - hanya tipe error yang dicatat
                    log.error("Gagal menyimpan submission: %s", type(exc).__name__)
                    return 500, {"ok": False, "errors": {"_form": MSG_SAVE_FAILED}}
                known_hashes.add(clean["text_sha256"])
                return 200, {"ok": True, "submission_id": sid}

        status, data = await run_in_threadpool(process)
        return JSONResponse(data, status_code=status)

    return app


app = create_app()
