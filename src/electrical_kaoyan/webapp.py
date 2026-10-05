from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import ValidationError

from .hotspots import HotspotSnapshot, HotspotTarget, collect_hotspots


def _default_web_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "web"


class HotspotApplication:
    def __init__(self, *, web_dir: Path, state_path: Path) -> None:
        self.web_dir = web_dir.resolve()
        self.state_path = state_path.resolve()

    def read_state(self) -> dict:
        if not self.state_path.exists():
            return {"status": "idle", "events": [], "attempts": [], "metrics": {}}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def refresh(self, payload: dict) -> dict:
        target = HotspotTarget.model_validate(payload)
        previous = None
        if self.state_path.exists():
            try:
                previous = HotspotSnapshot.model_validate(self.read_state())
            except ValidationError:
                previous = None
        snapshot = collect_hotspots(target, previous=previous)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
        return snapshot.model_dump(mode="json")

    def static_path(self, request_path: str) -> Path | None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        candidate = (self.web_dir / relative).resolve()
        if candidate != self.web_dir and self.web_dir not in candidate.parents:
            return None
        return candidate if candidate.is_file() else None


def make_handler(application: HotspotApplication) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ElectricalHotspot/0.1"

        def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/api/health":
                self._json({"status": "ok"})
                return
            if path == "/api/state":
                self._json(application.read_state())
                return
            static = application.static_path(path)
            if static is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            body = static.read_bytes()
            content_type = mimetypes.guess_type(static.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            if urlsplit(self.path).path != "/api/refresh":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                self._json(application.refresh(payload))
            except (json.JSONDecodeError, ValidationError) as exc:
                self._json({"error": "invalid_request", "detail": str(exc)}, HTTPStatus.BAD_REQUEST)
            except OSError as exc:
                self._json({"error": "collection_failed", "detail": str(exc)[:500]}, HTTPStatus.BAD_GATEWAY)

        def log_message(self, format: str, *args: object) -> None:
            print(f"[web] {self.address_string()} {format % args}")

    return Handler


def serve(*, host: str = "127.0.0.1", port: int = 8787,
          web_dir: Path | None = None, state_path: Path | None = None) -> None:
    application = HotspotApplication(
        web_dir=web_dir or _default_web_dir(),
        state_path=state_path or Path("runs/hotspot-web/latest.json"),
    )
    server = ThreadingHTTPServer((host, port), make_handler(application))
    print(f"电研热榜已启动：http://{host}:{port}")
    server.serve_forever()

