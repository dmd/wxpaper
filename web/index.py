#!/usr/bin/python3
"""CGI endpoint: server-render the wxpaper panel as self-contained HTML.

This is the DirectoryIndex for ~/3e.org/wxpaper/, so https://3e.org/wxpaper/
returns a complete, data-filled page in one request -- no client-side fetch,
nothing hidden until JS runs. That makes it safe for trmnl, which screenshots
the page after a fixed wait.

The shared logic lives in the home directory (above the web root, never
served): forecast_core.py (data) and webrender.py (HTML), alongside
pirate-secret and wxpaper-event.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("HOME", "/home/edges"))

import forecast_core  # noqa: E402
import webrender  # noqa: E402

body = webrender.render_page(forecast_core.fetch_forecast(), HERE)
print("Content-Type: text/html; charset=utf-8")
print()
print(body, end="")
