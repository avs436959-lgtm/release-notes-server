from __future__ import annotations

import json
import mimetypes
import os
import sqlite3
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "release_notes.db"
SEED_PATH = BASE_DIR / "seed_state.json"
INDEX_PATH = BASE_DIR / "index.html"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8765))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_seed_state() -> dict:
    if SEED_PATH.exists():
        return json.loads(SEED_PATH.read_text(encoding="utf-8"))
    return {"releases": [], "settings": {}}


def normalize_state(value: object) -> dict:
    if not isinstance(value, dict):
        value = {}
    releases = value.get("releases", [])
    settings = value.get("settings", {})
    if not isinstance(releases, list):
        releases = []
    if not isinstance(settings, dict):
        settings = {}
    return {"releases": releases, "settings": settings}


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS app_state (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    return conn


def read_state() -> dict:
    with connect_db() as conn:
        row = conn.execute("SELECT data FROM app_state WHERE id = ?", ("main",)).fetchone()
    if row is None:
        return {"_not_found": True, "releases": [], "settings": {}}
    return normalize_state(json.loads(row[0]))


def write_state(state: dict) -> None:
    normalized = normalize_state(state)
    with connect_db() as conn:
        conn.execute("""
            INSERT INTO app_state (id, data, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
        """, ("main", json.dumps(normalized, ensure_ascii=False), utc_now()))


class ReleaseNotesHandler(SimpleHTTPRequestHandler):
    server_version = "ReleaseNotesLocalDB/1.0"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status: HTTPStatus, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Allow", "GET, PUT, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.send_json(HTTPStatus.OK, read_state())
            return
        if parsed.path in ("", "/", "/index.html"):
            self.serve_file(INDEX_PATH)
            return
        self.serve_static(parsed.path)

    def do_PUT(self) -> None:
        self.handle_state_write()

    def do_POST(self) -> None:
        self.handle_state_write()

    def handle_state_write(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/state":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            write_state(payload)
        except Exception as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        self.send_json(HTTPStatus.OK, {"ok": True})

    def serve_static(self, request_path: str) -> None:
        relative = request_path.lstrip("/")
        candidate = (BASE_DIR / relative).resolve()
        if BASE_DIR not in candidate.parents and candidate != BASE_DIR:
            self.send_json(HTTPStatus.FORBIDDEN, {"error": "Forbidden"})
            return
        if not candidate.is_file():
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        self.serve_file(candidate)

    def serve_file(self, path: Path) -> None:
        content = path.read_bytes()
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix.lower() == ".html":
            mime_type = "text/html; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


def find_available_port(start: int) -> int:
    for port in range(start, start + 20):
        try:
            s = ThreadingHTTPServer((HOST, port), ReleaseNotesHandler)
        except OSError:
            continue
        s.server_close()
        return port
    raise RuntimeError("No available local port found.")


def main() -> None:
    with connect_db():
        pass  # tabloyu olustur
    port = find_available_port(DEFAULT_PORT)
    url = f"http://{HOST}:{port}/"
    httpd = ThreadingHTTPServer((HOST, port), ReleaseNotesHandler)
    print(f"\nRelease Notes Platform")
    print(f"Veritabani: {DB_PATH}")
    print(f"Adres:      {url}")
    print("\nBu pencere acik kaldigi surece uygulama calisir.")
    print("Durdurmak icin Ctrl+C\n")
    if os.environ.get("RELEASE_NOTES_NO_BROWSER") != "1":
        threading.Thread(target=lambda: (time.sleep(0.8), webbrowser.open(url)), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer durduruldu.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
