# -*- coding: utf-8 -*-
"""一次性:把 OpenReview 凭据从环境变量写入本地凭据文件。密码不进命令文本。"""
import os, json
u = os.environ.get("OPENREVIEW_USERNAME")
p = os.environ.get("OPENREVIEW_PASSWORD")
if not u or not p:
    print("ERROR: 需设置 OPENREVIEW_USERNAME / OPENREVIEW_PASSWORD 环境变量"); raise SystemExit(1)
path = os.path.join(os.path.expanduser("~"), ".claude", "openreview_credentials.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
json.dump({"username": u, "password": p}, open(path, "w", encoding="utf-8"))
try: os.chmod(path, 0o600)
except Exception: pass
print(f"凭据已存到 {path}")
