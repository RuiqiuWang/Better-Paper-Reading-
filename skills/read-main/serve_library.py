"""Serve reading artifacts on loopback for browsers that do not open local files.

python serve_library.py STORE --port 8898
Keep this process running while its links are in use. It does not open a browser.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


class ReadingHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(404, "Directory listing is disabled")
        return None

    def send_head(self):
        root = Path(self.directory).resolve()
        requested = unquote(urlsplit(self.path).path).lstrip("/") or "index.html"
        full = (root / requested).resolve()
        try:
            full.relative_to(root)
        except ValueError:
            self.send_error(403)
            return None
        if any(part.startswith(".") for part in Path(requested).parts) or full.suffix.lower() not in {".html", ".htm", ".js", ".css", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".woff", ".woff2", ".ttf", ".pdf", ".md"}:
            self.send_error(404)
            return None
        return super().send_head()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path)
    parser.add_argument("--port", type=int, default=8898)
    args = parser.parse_args()
    store = args.store.expanduser().resolve()
    if not (store / "index.html").is_file():
        parser.error("Build index.html before starting the server")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(ReadingHandler, directory=str(store)))
    print("http://127.0.0.1:" + str(server.server_port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
