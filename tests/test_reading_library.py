"""Run with python -m unittest discover -s tests -v."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import io
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

MAIN = Path(__file__).resolve().parents[1] / "skills" / "read-main"
spec = importlib.util.spec_from_file_location("library", MAIN / "library.py")
library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.store = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def note(self, path="paper.html", body="<h1>Example note</h1>"):
        target = self.store / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def register(self, eid, title="Example", path="paper.html", check=True):
        return subprocess.run([sys.executable, str(MAIN / "append_index.py"), str(self.store), eid, title, "read", path], capture_output=True, text=True, check=check)

    def test_new_sessions_and_idempotent_retry(self):
        self.note("paper--one.html", "version one")
        self.note("paper--two.html", "version two")
        self.register("one", path="paper--one.html")
        self.register("two", path="paper--two.html")
        self.register("one", "Updated", "paper--one.html")
        entries = library.read_index(self.store)["entries"]
        self.assertEqual(len(entries), 2)
        self.assertEqual(next(e for e in entries if e["id"] == "one")["title"], "Updated")
        self.assertEqual((self.store / "paper--two.html").read_text(), "version two")

    def test_concurrent_registration_does_not_drop_notes(self):
        self.note()
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda i: self.register("session-" + str(i)), range(12)))
        self.assertEqual(len(library.read_index(self.store)["entries"]), 12)

    def test_corrupt_manifest_is_not_reset(self):
        self.note()
        original = '{"entries": [BROKEN'
        (self.store / "_index.json").write_text(original)
        result = self.register("new", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.store / "_index.json").read_text(), original)

    def test_external_paths_and_missing_files_are_rejected(self):
        for path in ("../outside.html", "C:/outside.html", "https://example.org/file.html", "_cache/paper.html", "index.html"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                library.note_path(self.store, path)
        self.assertNotEqual(self.register("missing", check=False).returncode, 0)
        self.assertFalse((self.store / "_index.json").exists())

    def test_discovery_preserves_legacy_ids_and_skips_cache_and_companions(self):
        self.note("paper.html")
        self.note("_cache/download.html")
        self.note("_search/result.md", "# result")
        self.note("_search/result.html")
        self.note("_topic/map.html")
        original = {"entries": [{"id": "legacy-id", "title": "Original", "path": "paper.html", "type": "read", "date": "2026-08-01"}], "custom": True}
        data = library.discover(self.store, original)
        library.discover(self.store, data)
        self.assertEqual(len(data["entries"]), 3)
        self.assertEqual(data["entries"][0]["id"], "legacy-id")
        self.assertTrue(data["custom"])

    def test_markdown_is_readable_without_fetch_and_escaped(self):
        self.note("_search/test.md", '# 中文 "quotes"\n<script>alert(1)</script>\n**read me**')
        self.register("digest", "中文 digest", "_search/test.md")
        wrappers = list((self.store / "_dashboard").glob("*.html"))
        self.assertEqual(len(wrappers), 1)
        source = wrappers[0].read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", source)
        self.assertIn("中文", source)
        self.assertIn("view_path", (self.store / "_index.js").read_text(encoding="utf-8"))

    def test_title_cannot_break_out_of_script(self):
        self.note()
        title = "中文 O'Reilly </script><script>alert(1)</script> & \"quote\""
        self.register("quoted", title)
        page = (self.store / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("</script><script>alert(1)</script>", page)
        self.assertIn("\\u003c/script\\u003e", page)
        self.assertEqual(library.read_index(self.store)["entries"][0]["title"], title)

    def test_removed_note_has_visible_recovery_state(self):
        path = self.note()
        self.register("existing")
        path.unlink()
        library.render_dashboard(self.store, library.read_index(self.store))
        feed = (self.store / "_index.js").read_text(encoding="utf-8")
        payload = json.loads(feed[len("window.paperReadingUpdate("):-3])
        self.assertTrue(payload["entries"][0]["missing"])

    def test_open_targets_requested_session_after_build(self):
        self.note()
        self.register("older-session")
        self.register("current-session")
        builder_spec = importlib.util.spec_from_file_location("build_dashboard", MAIN / "build_dashboard.py")
        builder = importlib.util.module_from_spec(builder_spec)
        with mock.patch.dict(sys.modules, {"library": library}):
            builder_spec.loader.exec_module(builder)
        observed = []

        def open_browser(url):
            # The complete output and refreshed index must exist before opening.
            self.assertTrue((self.store / "index.html").is_file())
            self.assertIn("current-session", (self.store / "_index.js").read_text(encoding="utf-8"))
            observed.append(url)

        argv = ["build_dashboard.py", str(self.store), "--no-discover", "--session", "current-session", "--open"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(builder.webbrowser, "open", side_effect=open_browser), redirect_stdout(io.StringIO()):
            builder.main()
        # Windows runners may expose TEMP through an 8.3 alias (RUNNER~1).
        # Compare the resolved path, as the dashboard builder does.
        self.assertEqual(observed, [(self.store.resolve() / "index.html").as_uri() + "#session=current-session"])

    def test_http_delivery_prints_both_encoded_links(self):
        self.note("folder/paper name.html")
        self.register("selected", path="folder/paper name.html")
        result = subprocess.run([sys.executable, "-X", "utf8", str(MAIN / "build_dashboard.py"), str(self.store), "--no-discover", "--session", "selected", "--base-url", "http://127.0.0.1:8898"], capture_output=True, encoding="utf-8", check=True)
        self.assertIn("[打开阅读工作台](http://127.0.0.1:8898/index.html#session=selected)", result.stdout)
        self.assertIn("[打开完整笔记](<http://127.0.0.1:8898/folder/paper%20name.html>)", result.stdout)

    def test_reader_server_serves_notes_but_not_settings(self):
        from functools import partial
        from http.server import ThreadingHTTPServer
        from threading import Thread
        from urllib.request import urlopen
        from urllib.error import HTTPError
        spec = importlib.util.spec_from_file_location("serve_library", MAIN / "serve_library.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.note()
        (self.store / "settings.json").write_text('{"private": true}')
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(module.ReadingHandler, directory=str(self.store)))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = "http://127.0.0.1:" + str(server.server_port)
        try:
            with urlopen(base + "/paper.html") as response:
                self.assertIn(b"Example note", response.read())
            with self.assertRaises(HTTPError) as caught:
                urlopen(base + "/settings.json")
            self.assertEqual(caught.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
