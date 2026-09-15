"""Register an output and refresh the dashboard; legacy positional CLI supported."""
import argparse
from pathlib import Path
import sys
from urllib.parse import quote
from library import TYPES, library_lock, note_path, read_index, save_and_render, stamp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path)
    parser.add_argument("id", help="Unique session id. Reuse only when updating that session.")
    parser.add_argument("title")
    parser.add_argument("type", choices=sorted(TYPES))
    parser.add_argument("path", help="Note path relative to the library")
    parser.add_argument("topics", nargs="?", default="")
    parser.add_argument("topics_count", nargs="?", type=int)
    args = parser.parse_args()
    if not args.id.strip() or not args.title.strip():
        parser.error("Session id and title cannot be empty.")
    store = args.store.expanduser().resolve()
    full = note_path(store, args.path)
    if not full.is_file():
        parser.error("Write the note before registering it: " + str(full))
    with library_lock(store):
        data = read_index(store)
        previous = next((e for e in data["entries"] if e["id"] == args.id), {})
        entry = dict(previous)
        entry.update(id=args.id, title=args.title, type=args.type,
                     path=full.relative_to(store).as_posix(), date=stamp(full),
                     topics=[t.strip() for t in args.topics.split(",") if t.strip()])
        if args.topics_count is not None:
            entry["topics_count"] = args.topics_count
        data["entries"] = [e for e in data["entries"] if e["id"] != args.id] + [entry]
        save_and_render(store, data)
    print((store / "index.html").as_uri() + "#session=" + quote(args.id, safe=""))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print("Registration failed: " + str(error), file=sys.stderr)
        sys.exit(1)
