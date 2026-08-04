# -*- coding: utf-8 -*-
"""
openreview 登录 + 拉取会议录用论文列表的辅助脚本。
被 /read-search skill 调用。凭据从本地凭据文件读(首次运行时交互式写入)。

用法:
  python openreview_fetch.py <venue> <year> [--proxy http://127.0.0.1:7890]
    venue: ICML / ICLR / NeurIPS (OpenReview 类)
  输出 JSON 到 stdout(最后两行是 SUMMARY: ... 和 FILE: <path>)

凭据文件: ~/.claude/openreview_credentials.json  (首次运行时提示输入)
  {"username": "...", "password": "..."}
"""
import os, sys, json, time, getpass

CRED_FILE = os.path.join(os.path.expanduser("~"), ".claude", "openreview_credentials.json")

def load_or_prompt_credentials():
    """读凭据文件;不存在则交互式提示输入并保存。返回 (username, password) 或 None。"""
    if os.path.exists(CRED_FILE):
        try:
            d = json.load(open(CRED_FILE, encoding="utf-8"))
            if d.get("username") and d.get("password"):
                return d["username"], d["password"]
        except Exception:
            pass
    # 首次:提示输入(由调用方/skill 引导,这里只读环境变量兜底)
    # 真正交互由 skill 对话完成;这里只认环境变量,避免脚本卡住
    u = os.environ.get("OPENREVIEW_USERNAME")
    p = os.environ.get("OPENREVIEW_PASSWORD")
    if u and p:
        # 保存到凭据文件
        os.makedirs(os.path.dirname(CRED_FILE), exist_ok=True)
        json.dump({"username": u, "password": p}, open(CRED_FILE, "w", encoding="utf-8"))
        return u, p
    return None

def main():
    if len(sys.argv) < 3:
        print("ERROR: 用法 python openreview_fetch.py <venue> <year> [--proxy URL]"); sys.exit(2)
    venue = sys.argv[1].upper()
    year = sys.argv[2]
    proxy = None
    if "--proxy" in sys.argv:
        proxy = sys.argv[sys.argv.index("--proxy")+1]
        os.environ["HTTP_PROXY"] = proxy; os.environ["HTTPS_PROXY"] = proxy

    creds = load_or_prompt_credentials()
    if not creds:
        print("NO_CREDENTIALS")  # skill 据此提示用户输入
        sys.exit(3)
    username, password = creds

    try:
        import openreview
    except ImportError:
        print("ERROR: openreview-py 未安装,请 pip install openreview-py"); sys.exit(4)

    print(f"==> 登录 OpenReview ({username}) ...", file=sys.stderr)
    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net",
        username=username, password=password,
    )

    venue_id = f"{venue}.cc/{year}/Conference"
    print(f"==> 拉取 {venue_id} ...", file=sys.stderr)

    all_notes = []
    offset = 0; limit = 1000
    while True:
        batch = client.get_notes(content={"venueid": venue_id}, limit=limit, offset=offset)
        if not batch: break
        all_notes.extend(batch)
        print(f"  已获取 {len(all_notes)} 篇 ...", file=sys.stderr)
        if len(batch) < limit: break
        offset += limit
        time.sleep(0.5)

    # 按 venue 字段分类
    by_venue = {}
    for n in all_notes:
        c = n.content
        v = c.get("venue", {})
        v = v.get("value", "") if isinstance(v, dict) else str(v)
        by_venue.setdefault(v, []).append(n)

    out = {"venue": venue, "year": year, "venue_id": venue_id,
           "total": len(all_notes), "by_venue": {k: len(v) for k, v in by_venue.items()},
           "papers": []}
    for vtype, notes in by_venue.items():
        for n in notes:
            c = n.content
            def gv(key, default=""):
                x = c.get(key, default)
                return x.get("value", default) if isinstance(x, dict) else x
            out["papers"].append({
                "venue": vtype,
                "title": gv("title"),
                "authors": gv("authors", []),
                "abstract": gv("abstract", "")[:600],
                "tldr": gv("TLDR", ""),
                "keywords": gv("keywords", []),
                "primary_area": gv("primary_area", ""),
                "url": f"https://openreview.net/forum?id={n.id}",
            })

    cache_dir = os.path.join("D:", os.sep, "claude_paper_reading", "_cache", f"search_{venue.lower()}{year}")
    os.makedirs(cache_dir, exist_ok=True)
    out_path = os.path.join(cache_dir, f"{venue}{year}_openreview.json")
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"==> 保存 {out_path}", file=sys.stderr)
    # stdout 给 skill 读
    print(f"SUMMARY: {venue}{year} total={len(all_notes)} by_venue={out['by_venue']}")
    print(f"FILE: {out_path}")

if __name__ == "__main__":
    main()
