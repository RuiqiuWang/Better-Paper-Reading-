---
name: read-comment
description: Answer a follow-up question about an existing paper HTML note and save it as a numbered, underlined inline annotation with a right sidebar. Use for /read_comment, /read-comment, $read-comment, 论文批注, or requests to add a question and answer without rewriting the note. Supports global questions and continued numbered comment threads.
---

# 论文批注与追问

保留论文笔记正文，把问题与回答存入同一个 HTML。正文相关知识点带下划线和方形编号；点击编号打开右侧问答栏，可在全局与各编号之间切换。同一问题的连续追问追加到同一线程，不产生新的阅读会话。

1. 读取相邻技能的 [追问保存协议](../read-main/references/followups.md)，按它确定当前论文、读取已有批注、定位知识点并保存。用户输入 `/read_comment` 与 `/read-comment` 均按本技能处理；宿主的技能菜单使用 `read-comment`。
2. 输入为问题，可包含 `--session ID` 和 `--comment global|N`。显式编号表示继续该批注；全局表示整篇论文或不适合锚定具体段落的问题。未指定时，结合当前任务上下文判断是否接续已有问题；独立的局部问题创建新编号。不要因为上次刚写了一个编号就把无关问题追加进去。
3. 阅读该段上下文和与问题相关的论文原文、公式、图表或代码，遵循 [阅读风格](../read/references/reading-style.md)：按需先直观说明，再严谨解释，最后直观回看；简单问题直接解释清楚。原文事实、补充推导和类比要区分。不要根据问题猜出未读到的论文结论。
4. 将用户的问题和完整解答写到请求 JSON；回答用纯文本段落，可包含 TeX 和来源 URL，不能依赖 Markdown/HTML 渲染。内容长度依理解所需，不压缩关键推导。新编号优先锚定首次解释该知识点的句子；需要跨格式/公式定位时选已有段落 ID。
5. 调用协议中的助手保存，验证下划线、编号、右栏切换和当前回答可见。按照会话登记协议自动打开原论文会话，最终回复给工作台和完整笔记链接，并简述新增/续写的编号。网页输入框只复制追问指令；用户在阅读任务发送后才会调用技能并生成回答。
