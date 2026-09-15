---
name: read-rewrite
description: Resolve a reader's confusion by rewriting the relevant passage of an existing paper HTML note in context. Use for /read_rewrite, /read-rewrite, $read-rewrite, 改写论文讲解, or requests to integrate a follow-up explanation into the original note. Preserve the session, source evidence, surrounding content and existing comment anchors.
---

# 将追问融入原文

用户输入 `/read_rewrite Question` 后，定位当前论文中引起疑惑的地方，把解答自然整合进原有讲解。不要只在聊天里回答或在文末堆积独立问答。菜单名称为 `read-rewrite`，下划线和连字符写法均触发本技能。

1. 读取 [追问保存协议](../read-main/references/followups.md)，确定会话、读取原 HTML 与相关原文。可通过 `--session ID` 指定论文；不创建新的阅读记录。
2. 遵循 [阅读风格](../read/references/reading-style.md)。结合上下文补足疑惑背后的缺失环节：动机、符号、假设、推导、例子或机制的直观解释，按需使用。保留技术严谨性和原文依据，不把实验支持写成证明。
3. 以最小完整的段落或小节为改写范围。替换不清楚的表述、补上过渡和必要推导，让读者顺着原文就能理解；避免重复已经讲清楚的内容。必要时更正前后引用，但不整体重写无关部分。
4. 按协议使用准确的 `old_html`、`new_html` 和最新文件哈希提交改写。已有编号锚点及按钮必须保留在对应知识点；若知识点移位，在同次改写中一起移动。不能删除批注、公式脚本、原图或来源来绕过检查。
5. 助手自动备份、原子替换并刷新原会话。验证改写上下文、公式、已有批注，自动打开原会话，最终给工作台和完整笔记链接，并用一两句说明改了哪里、解除了什么疑惑。
