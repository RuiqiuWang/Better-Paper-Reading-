# 追问保存与定位协议

共享助手在本技能目录的 `followup.py`。路径加引号，用当前可用 Python；不要把用户问题拼接为 shell 命令。先将结构化请求写为 UTF-8 JSON 文件，再传递文件路径。

## 选择原会话

读取宿主的 `paper_reading_config.json`，获取 `store_dir` 与可选 `dashboard_url`。按 [会话登记协议](session-registration.md) 验证本机服务。

优先使用显式 `--session ID`，其次是当前任务已经阅读/打开并明确关联的论文 ID，或已获知的阅读工作台 URL 中的 `#session=ID`。读取 `<STORE>/_index.json` 核对标题与文件；不能默认选日期最新的论文。若上下文没有唯一目标，先列出候选并询问用户。`--comment N` 只定位该论文内部的线程。

先检查现有状态：
```text
python FOLLOWUP_PATH STORE --session ID
```
输出原文件路径、`sha256`、可用元素 ID 和完整批注线程。读取实际 HTML（不只检查输出）及相关论文来源后再作答。请求中的 `expected_sha256` 必须是该次检查的值。写入时若文件已变，重新读取并调整，不能直接用新哈希重试旧修改。

## 新建局部批注

请求文件示意（替换为真实信息）：
```json
{
  "action": "comment",
  "expected_sha256": "HASH_FROM_INSPECT",
  "thread": "new",
  "anchor_text": "正文中唯一出现的一句原始文本",
  "label": "这个知识点的简短名称",
  "question": "用户的疑惑",
  "answer": "结合上下文与来源的完整回答，可分段、用 TeX 和来源 URL。"
}
```
`anchor_text` 必须在单个原始文本节点唯一出现；不会匹配脚本、代码、链接、按钮或已有批注。跨标签、公式或实体编码文本使用 `anchor_id` 替代：选择已有唯一的 p/span/li/h2/h3/h4/div/section ID，优先最小的段落，避免给整节画线。无合适 ID 时先用 guarded rewrite 给目标元素增加唯一 ID，重新 inspect 后批注。不要删去格式来方便匹配。

首次编号从 1 开始，后续递增。对已有知识点的追问指定 `"thread": "1"`（省略 anchor 字段）；追加一对问答，不替换旧回答。全局问题使用 `"thread": "global"`，不添加正文下划线。右栏的“全局”是整体问题线程，不是所有批注的汇总。

## 融入原文的改写

```json
{
  "action": "rewrite",
  "expected_sha256": "HASH_FROM_INSPECT",
  "old_html": "精确且唯一的完整旧段落 HTML",
  "new_html": "上下文衔接自然的新段落 HTML"
}
```
只替换唯一精确匹配。不能编辑 `PAPER-READING-FOLLOWUPS` 标记内的运行时与数据；助手自动保留它。改写包含已有批注时，保持其元素 ID、`data-pr-comment` 和 `data-pr-open` 按钮一一对应。检查旧问答在改写后是否仍然适用；有实质更正时在对应线程追加澄清，保留问答历史。

## 保存、验证、交付

```text
python FOLLOWUP_PATH STORE --session ID --request REQUEST_JSON --host HOST --base-url VERIFIED_LOOPBACK_URL
```
助手在库锁内检查哈希，备份到 `<STORE>/.reading-history/<session-hash>/<content-hash>.html`，更新原文件与同一索引项，刷新工作台。编号、问答、运行时都嵌入 HTML，直接打开文件也能阅读；备份目录不由阅读服务器公开。不要注册新的 ID 或改动项目、置顶等元数据。

浏览器检查对应会话：正文原图/公式正常，点击编号展示正确的问题与回答，切换全局/其他编号不会串线；改写后已有批注仍可用。右栏宽屏并排、窄屏可收起。网页输入框生成带会话和线程参数的追问指令（Codex `$read-comment`，Claude Code `/read-comment`）；不能声称网页本身已提交给模型。

按登记协议实际打开并保留浏览器标签、复用本机服务。最终必须给工作台与独立笔记可点击链接；报告改写位置或批注编号。没有完成打开/验证时如实说明，不以工具调用成功替代页面验证。

## Host configuration

Before resolving the note library, run the installed sibling read-main `host_config.py --host codex` in Codex or `--host claude` in Claude Code. Its output is authoritative for the config path, store and language: it honors CODEX_HOME / CLAUDE_CONFIG_DIR and existing preferences. Without a configured store, use D:/claude_paper_reading only on Windows with a D: drive; otherwise use ~/PaperReading. Resolve scripts from the actual skill location, never a hardcoded ~/.claude/skills path. Use the host's available file/shell/browser tools; when no browser tool exists, use build_dashboard.py --open and report the printed links without claiming visual verification.
