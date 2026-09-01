#!/usr/bin/python3
"""CGI endpoint: server-render the wxpaper panel as self-contained HTML.

This is the DirectoryIndex for ~/3e.org/wxpaper/, so https://3e.org/wxpaper/
returns a complete, data-filled page in one request -- no client-side fetch,
nothing hidden until JS runs. That makes it safe for trmnl, which screenshots
the page after a fixed wait.

The shared logic and private runtime files live in ~/wxpaper, outside the web
root.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(os.environ.get("HOME", "/home/edges"), "wxpaper")
sys.path.insert(0, APP_DIR)
os.environ.setdefault("WX_RUNTIME_DIR", APP_DIR)

import forecast_core  # noqa: E402
import webrender  # noqa: E402

body = webrender.render_page(forecast_core.fetch_forecast(), HERE)
print("Content-Type: text/html; charset=utf-8")
print()
print(body, end="")
