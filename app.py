"""Local demo server. No pip install required. Run: python3 app.py"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from engine import run_research
from qloo_client import QlooError
from agent_reviewer import configured as llm_configured, _safe_endpoint
from public_guard import PUBLIC_BUDGET

ROOT = Path(__file__).resolve().parent
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
ENV_KEY = os.environ.get("QLOO_API_KEY", "").strip()
PUBLIC_DEMO = os.environ.get("ATLAS_PUBLIC_DEMO") == "1"
LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")
FILES = {"/": ("index.html", "text/html; charset=utf-8"),
         "/style.css": ("style.css", "text/css; charset=utf-8"),
         "/app.js": ("app.js", "text/javascript; charset=utf-8")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        # Avoid accidentally logging request content or secrets.
        pass

    def _headers(self, code, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()

    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._headers(code, "application/json; charset=utf-8")
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"ok": True, "server_key_configured": bool(ENV_KEY), "llm_configured": llm_configured(), "public_demo": PUBLIC_DEMO})
        if self.path not in FILES:
            return self._json(404, {"error": "Ruta no encontrada"})
        filename, content_type = FILES[self.path]
        body = (ROOT / filename).read_bytes()
        self._headers(200, content_type)
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/program":
            return self._json(404, {"error": "Ruta no encontrada"})
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            return self._json(415, {"error": "Se requiere application/json"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 16384:
                return self._json(400, {"error": "Solicitud demasiado grande o vacía"})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "Solicitud JSON no válida"})
        artist = str(data.get("artist", "")).strip()
        city = str(data.get("city", "")).strip()
        objective = str(data.get("objective", "")).strip()
        if not (2 <= len(artist) <= 80 and 2 <= len(city) <= 80 and 3 <= len(objective) <= 180):
            return self._json(400, {"error": "Comprueba los campos: artista, ciudad y objetivo"})
        # Browser-supplied keys are allowed ONLY for the locally bound demo.
        # In public deployment, require server-side environment key.
        key = ENV_KEY or (str(data.get("api_key", "")).strip() if not PUBLIC_DEMO and HOST in LOCAL_HOSTS else "")
        if not key:
            return self._json(400, {"error": "Falta la clave Qloo. En modo local, introdúcela en el formulario."})
        admission = PUBLIC_BUDGET.admit() if PUBLIC_DEMO else None
        if admission:
            return self._json(429, {"error": "Demo usage limit reached. Please try later.", "reason": admission})
        try:
            return self._json(200, run_research(key, artist, city, objective))
        except QlooError as exc:
            return self._json(502, {"error": str(exc)})
        except Exception:
            return self._json(500, {"error": "Unexpected research error. Please try again."})
        finally:
            if PUBLIC_DEMO:
                PUBLIC_BUDGET.release()


def validate_public_settings():
    """Fail closed rather than exposing an unprotected local demo to the internet."""
    if HOST not in LOCAL_HOSTS and not PUBLIC_DEMO:
        raise SystemExit("Non-loopback binding requires ATLAS_PUBLIC_DEMO=1")
    if PUBLIC_DEMO:
        if not ENV_KEY:
            raise SystemExit("Public demo requires QLOO_API_KEY in server environment")
        endpoint = os.environ.get("ATLAS_LLM_URL", "").strip()
        if not llm_configured() or not _safe_endpoint(endpoint):
            raise SystemExit("Public demo requires a valid remote LLM URL and model")
        if not endpoint.startswith("https://"):
            raise SystemExit("Public demo requires HTTPS for the remote LLM")
        if not os.environ.get("ATLAS_LLM_API_KEY", "").strip():
            raise SystemExit("Public demo requires a server-side LLM API key")


if __name__ == "__main__":
    validate_public_settings()
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    httpd.daemon_threads = True
    print(f"[OK] Affinity Atlas listening on http://{HOST}:{PORT}", flush=True)
    print("[INFO] No credentials are written to disk. Ctrl+C stops the server.", flush=True)
    httpd.serve_forever()
