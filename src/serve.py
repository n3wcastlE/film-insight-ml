"""Serve the results panel on this computer only. No external dependencies."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
root=Path(__file__).resolve().parents[1]
print('Film Insight: http://localhost:8765/dashboard.html (Ctrl+C aby zakończyć)')
ThreadingHTTPServer(('127.0.0.1',8765),partial(SimpleHTTPRequestHandler,directory=str(root))).serve_forever()
