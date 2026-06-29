#!/usr/bin/env python3
"""Local development server for the wxpaper web display.

Mirrors the CGI deployment on 3e.org: "/" is server-rendered to the same
self-contained HTML web/index.py produces, and /forecast.py still returns the
raw JSON for debugging. Data logic lives in forecast_core and the HTML in
webrender, so the CGI script and this server stay in sync.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

from forecast_core import fetch_forecast
from webrender import render_page

# Re-exported so test_webversion.py (and any caller) can reach the helpers
# through webversion.* as before.
from forecast_core import (  # noqa: F401
    event_countdown,
    compose_allowance,
    round_dollars,
    build_allowance,
    allowance,
    fallback_data,
    read_secret,
)

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.py"):
            self._send(
                render_page(fetch_forecast(), WEB_DIR).encode("utf-8"),
                "text/html; charset=utf-8",
            )
            return
        if path in ("/forecast.py", "/api/forecast"):
            self._send(
                json.dumps(fetch_forecast()).encode("utf-8"),
                "application/json",
            )
            return
        return super().do_GET()

    def _send(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    handler = partial(Handler, directory=str(WEB_DIR))
    server = ThreadingHTTPServer(("", 8000), handler)
    print("Serving on http://localhost:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
