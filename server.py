"""
Meme Radar — pintu server lokal.

Logika ada di serverlib.py (dipakai bersama oleh server ini dan api/*.py di Vercel).
Cara jalankan:  python server.py   lalu buka  http://127.0.0.1:8765
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import serverlib as lib

PORT = 8765
ROOT = Path(__file__).resolve().parent


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # sunyi biar terminal bersih

    def _send(self, code, body, ctype):
        payload = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, obj, code=200):
        self._send(code, obj, "application/json; charset=utf-8")

    def _file(self, name):
        path = ROOT / name
        try:
            self._send(200, path.read_bytes(), "text/html; charset=utf-8")
        except FileNotFoundError:
            self._send(404, b"file tidak ditemukan", "text/plain; charset=utf-8")

    def do_GET(self):
        import urllib.parse

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        try:
            if path in ("/", "/index.html"):
                self._file("index.html")
            elif path == "/api/search":
                self._json(lib.api_search(qs))
            elif path == "/api/social":
                self._json(lib.social_cached())
            elif path == "/api/potential":
                self._json(lib.api_potential())
            elif path == "/api/trending":
                self._json(lib.api_trending())
            elif path == "/api/safety":
                self._json(lib.api_safety(qs))
            elif path == "/api/safety_batch":
                self._json(lib.api_safety_batch(qs))
            elif path == "/api/verify":
                self._json(lib.api_verify(qs))
            elif path == "/api/dev":
                self._json(lib.api_dev(qs))
            else:
                self._json({"error": "tidak ada route itu"}, 404)
        except Exception as e:
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Meme Radar jalan di http://127.0.0.1:{PORT}  (Ctrl+C untuk stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstop.")


if __name__ == "__main__":
    main()