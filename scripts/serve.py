"""Local dev server for AFM Journey.

    python scripts/serve.py          # http://localhost:8765
    python scripts/serve.py --open   # ...and open it in the default browser

Every page load rebuilds dist/index.html from data/journey-data.js and
src/index.template.html, so edits show up on refresh. Works offline.
On Windows, double-click "Open AFM Journey.bat" instead of using a terminal.
"""
from __future__ import annotations

import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

PORT = 8765
URL = f"http://localhost:{PORT}/"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            try:
                build.main()
            except Exception as exc:  # serve the last good build rather than failing
                print("Build failed, serving the previous dist/index.html:", exc)
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def main() -> None:
    build.main()  # make sure dist/ exists before the first request
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(build.OUT.parent)))
    except OSError:
        print("Already running at", URL)
        if "--open" in sys.argv:
            webbrowser.open(URL)
        return
    print("AFM Journey running at", URL, "(Ctrl+C to stop)")
    if "--open" in sys.argv:
        threading.Timer(0.6, webbrowser.open, args=(URL,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
