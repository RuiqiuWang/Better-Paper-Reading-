"""Build/open a static reading workspace, importing pre-existing local notes."""
import argparse
from pathlib import Path
import sys
import webbrowser
from urllib.parse import quote, urlparse
from library import discover, library_lock, note_path, read_index, save_and_render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--session", default="")
    parser.add_argument("--base-url", help="Verified loopback HTTP URL serving this library, for in-app browsers")
    parser.add_argument("--no-discover", action="store_true")
    args = parser.parse_args()
    if args.base_url:
        base = urlparse(args.base_url)
        if base.scheme != "http" or base.hostname not in ("localhost", "127.0.0.1", "::1") or base.username or base.password or base.query or base.fragment:
            parser.error("--base-url must be a loopback HTTP URL without credentials, query or fragment")
    store = args.store.expanduser().resolve()
    with library_lock(store):
        data = read_index(store)
        if not args.no_discover:
            discover(store, data)
        save_and_render(store, data)
    url = args.base_url.rstrip("/") + "/index.html" if args.base_url else (store / "index.html").as_uri()
    if args.session:
        url += "#session=" + quote(args.session, safe="")
    print(url)
    print("[打开阅读工作台](" + url + ")")
    entry = next((e for e in data["entries"] if e["id"] == args.session), None)
    if entry:
        note = note_path(store, entry["path"])
        target = args.base_url.rstrip("/") + "/" + quote(entry["path"].replace("\\", "/"), safe="/") if args.base_url else "/" + note.as_posix() if note.drive else note.as_posix()
        print("[打开完整笔记](<" + target + ">)")
    if args.open:
        if not webbrowser.open(url):
            print("Browser opener did not confirm success. Open and verify the printed link using the host browser tools.", file=sys.stderr)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print("Dashboard build failed: " + str(error), file=sys.stderr)
        sys.exit(1)
