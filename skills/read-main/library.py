"""Shared, dependency-free persistence and rendering for the reading library."""
import contextlib
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime

TYPES = {"read", "search", "search_topic"}
ASSETS = Path(__file__).parent / "assets"


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".paper-reading-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
            output.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def library_lock(store):
    store.mkdir(parents=True, exist_ok=True)
    lock = store / "_index.lock"
    deadline = time.monotonic() + 10
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise RuntimeError("Library is busy (_index.lock). If no writer is running, remove the stale lock and retry.")
            time.sleep(0.05)
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def read_index(store):
    path = store / "_index.json"
    if not path.exists():
        return {"entries": []}
    # Fail without modifying anything if a legacy index is malformed.
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError("_index.json must contain an entries list; repair or restore it first.")
    ids = set()
    for entry in data["entries"]:
        if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k] for k in ("id", "title", "path")):
            raise ValueError("Each index entry needs a nonempty id, title and path.")
        if entry["id"] in ids:
            raise ValueError("Duplicate session id in _index.json: " + entry["id"])
        ids.add(entry["id"])
    return data


def note_path(store, relative):
    relative = relative.replace("\\", "/")
    if relative.startswith("/") or ":" in relative or ".." in relative.split("/"):
        raise ValueError("Note path must stay inside the library: " + relative)
    full = (store / relative).resolve()
    try:
        full.relative_to(store.resolve())
    except ValueError:
        raise ValueError("Note path escapes the library: " + relative)
    if full.suffix.lower() not in (".html", ".htm", ".md"):
        raise ValueError("Only HTML and Markdown notes can be registered.")
    if full == store.resolve() / "index.html" or relative.split("/")[0] in ("_cache", "_dashboard"):
        raise ValueError("Dashboard and cache files are not reading sessions.")
    return full


def stamp(path):
    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds")


def script_json(data):
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def discover(store, data):
    """Import old notes once, without scanning downloaded papers in _cache."""
    registered = {e["path"].replace("\\", "/") for e in data["entries"]}
    ids = {e["id"] for e in data["entries"]}
    candidates = list(store.glob("*.html")) + list(store.glob("*.htm"))
    for folder in ("_search", "_topic"):
        if (store / folder).exists():
            candidates.extend(p for p in (store / folder).rglob("*") if p.suffix.lower() in (".html", ".htm", ".md"))
    for path in sorted(candidates):
        relative = path.relative_to(store).as_posix()
        if relative == "index.html" or relative in registered:
            continue
        # Prefer an HTML digest when both formats of the same legacy output exist.
        if path.suffix == ".md" and path.with_suffix(".html").exists():
            continue
        try:
            note_path(store, relative)
        except ValueError:
            continue
        eid = "import-" + hashlib.sha256(relative.encode()).hexdigest()[:20]
        if eid in ids:
            continue
        data["entries"].append({"id": eid, "title": path.stem, "path": relative,
                                "type": "search" if relative.startswith("_search/") else "search_topic" if relative.startswith("_topic/") else "read",
                                "date": stamp(path), "topics": []})
        ids.add(eid)
    return data


def render_dashboard(store, data):
    entries = []
    for raw in data["entries"]:
        entry = dict(raw)
        entry["path"] = entry["path"].replace("\\", "/")
        try:
            full = note_path(store, entry["path"])
            entry["missing"] = not full.is_file()
            if full.suffix.lower() == ".md" and not entry["missing"]:
                # Generate a local page; fetch(file://...) fails in common browsers.
                filename = hashlib.sha256(entry["id"].encode()).hexdigest() + ".html"
                entry["view_path"] = "_dashboard/" + filename
                title = html.escape(entry["title"])
                body = html.escape(full.read_text(encoding="utf-8-sig"))
                atomic_write(store / entry["view_path"], '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                             + '<title>' + title + '</title><style>body{max-width:900px;margin:48px auto;padding:0 32px;color:#292929;font:16px/1.8 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><h1>'
                             + title + '</h1><pre>' + body + '</pre></html>')
        except ValueError:
            entry["missing"] = True
            entry["path"] = ""
        entries.append(entry)
    key = hashlib.sha256(str(store.resolve()).encode()).hexdigest()[:24]
    payload = {"library_id": key, "entries": entries}
    template = (ASSETS / "dashboard.html").read_text(encoding="utf-8")
    template = template.replace("/*__STYLES__*/", (ASSETS / "dashboard.css").read_text(encoding="utf-8"))
    template = template.replace("/*__APP__*/", (ASSETS / "dashboard.js").read_text(encoding="utf-8"))
    template = template.replace("/*__DATA__*/", script_json(payload))
    atomic_write(store / "_index.js", "window.paperReadingUpdate(" + script_json(payload) + ");\n")
    atomic_write(store / "index.html", template)


def save_and_render(store, data):
    # Render before committing the manifest so a missing template cannot corrupt it.
    render_dashboard(store, data)
    atomic_write(store / "_index.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")
