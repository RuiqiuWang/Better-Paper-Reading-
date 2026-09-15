# Register a reading session

Use this protocol for each successful reading/search output. Resolve `<MAIN>` to the installed sibling `read-main` directory; resolve `<STORE>` from the active host's reading config. Quote all filesystem arguments.

1. **Allocate the session before naming output files.** Extract an optional trailing `--session <id>` from the user's input, and remove it before parsing the paper URL, venue or topic. Accept only 1–100 ASCII letters, digits, `_` or `-` (a dashboard-generated UUID qualifies). Reject an invalid option with a clear correction. If absent, generate a new UUID:

   ```text
   python -c "import uuid; print(uuid.uuid4())"
   ```

   A fresh invocation gets a fresh session even when the same paper/topic was read before. Reuse an ID only for that session's explicit continuation or a command created by the workspace.

   Ordinary `/read` does not require creating a draft in the browser. The workspace's draft creation is available only through a project's menu.

2. **Use a distinct output path** such as `<short-title>--<session-id>.html` for papers, or `_search/<date>_<topic>--<session-id>.md` for searches. Preserve the existing directory depth so relative images still load. Include the session ID in both Markdown and HTML companion names. Do not overwrite another session's note. An explicit continuation should update that session's existing path from `_index.json`.

3. **Register only after writing and checking the output.**

   ```text
   python "<MAIN>/append_index.py" "<STORE>" "<session-id>" "<display-title>" read "<relative-note-path>.html" "<topic1,topic2>"
   ```

   Use `search` for a search digest (HTML or Markdown), or `search_topic` for a topic map. Optional final positional argument: topic count. Same ID updates one entry; distinct IDs preserve separate sessions. The helper validates file paths, serializes concurrent writes, saves the index and refreshes the dashboard automatically. Retrying a failed registration with the same ID is safe. Do not silently replace a damaged manifest with an empty one.

4. **Automatically open the workspace at this result after generation**, keeping the sidebar visible. This is the default completion of `/read`; do not wait for the user to invoke `/read-main`:

   ```text
   python "<MAIN>/build_dashboard.py" "<STORE>" --no-discover --session "<session-id>" --open
   ```

   The `--session` argument must be this invocation's ID. Opening `index.html` alone can restore an older selection, so keep the session anchor. Open after the note and refreshed index exist, so the initial content is the completed paper rather than an empty draft. If the host can reuse an existing workspace tab, navigate it to this session; otherwise use the browser opener above. Tell the user the workspace path and the standalone note path. If opening is unavailable, provide both links and report that limitation. The standalone file is still useful for export/sharing.

If the sibling read-main is unavailable, keep the generated note, report that automatic registration is unavailable, and explain that the suite's installer includes read-main. Do not claim the sidebar updated if the command failed.


## Deliver the result in Codex

A successful file write, registration, or queued file-panel open is not evidence that a rendered browser page is visible. Before finishing:

1. Read the optional `dashboard_url` from the active host's reading config. Prefer a verified existing loopback URL for the same library: after rebuilding, compare its `_index.js` with the local `_index.js` (or their hashes). If the configured server is unavailable, restart the loopback reader on that port; if another service occupies it, choose a free port and record the verified replacement URL in config, preserving other fields. If a local HTTP view is needed, run `python "<MAIN>/serve_library.py" "<STORE>" --port <available-port>` bound to loopback. Keep the service alive for the delivered page; on Windows a detached `Start-Process -WindowStyle Hidden` with redirected logs avoids ending it with a verification shell. Do not reuse a server until its library is verified. Follow host browser restrictions; do not try to bypass a denied navigation.
2. Build links with `python "<MAIN>/build_dashboard.py" "<STORE>" --no-discover --session "<id>" --base-url "http://127.0.0.1:<port>"`. Open that exact workspace URL with the host's browser tools. For browser automation, omit `--open` and use the allowed browser tool instead of launching a browser from a shell.
3. Verify that the selected paper title/content is visible. With the Codex browser tool, mark the result tab as a deliverable (`tab.markDeliverable()`) and leave it open. Close only disposable verification tabs. Do not terminate the server backing the delivered link.
4. Put clickable **workspace and complete-note links at the start of the final reply**, even if an automatic open succeeded. Use the verified HTTP links when available. For Windows local-file fallbacks use the host's absolute-file Markdown convention (e.g. `[完整笔记](</D:/papers/Note.html>)`), not a bare path. Copy generated links rather than guessing a port or filename. If browser opening failed, say so while still returning the valid local artifact link.

The browser check and final links are part of completion. If only the local repository copy of a skill was changed, explicitly distinguish it from the installed skill; do not claim subsequent `/read` invocations use it until installation has been verified.
