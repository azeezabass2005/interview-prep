"""Serves the API over HTTP for the web app (python server.py, then cd web && npm run dev)."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from edge.http import Request
from edge.wiring import build_production_app

APP = build_production_app(os.environ.get("DB_PATH", "edge.db"))


class Handler(BaseHTTPRequestHandler):
    def _serve(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        request = Request.build(self.command, self.path, dict(self.headers.items()), body, self.client_address[0])
        response = APP.handle(request)
        payload = response.encode()
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        for name, value in response.headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_PATCH = do_DELETE = do_PUT = _serve

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"API on http://localhost:{port}")
    ThreadingHTTPServer(("", port), Handler).serve_forever()
