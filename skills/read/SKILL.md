---
name: read
description: Read and explain an arXiv paper or paper-linked GitHub repository. Use for /read URL, $read URL, 精读论文, or requests to understand a paper. Build a technical overview followed by an intuitive overview, then explain the important parts through motivation, source-grounded formal reasoning and an intuitive interpretation as needed. Save an HTML note and automatically open its session in the reading workspace.
---

# 论文阅读 · 整体认识与深入理解

帮助读者先知道论文在解决什么问题、提出了什么方法，再真正理解关键部分。先建立专业与直观的整体认识，深入时结合直观动机、原文的严谨解释和直观回看。段落结构和讲解深度随内容调整。

## 配置与会话

读取当前宿主的 `paper_reading_config.json`：Claude Code 使用 `~/.claude/`，Codex 使用 `~/.codex/`。不存在则用默认值：
- `store_dir`：笔记和缓存目录，默认按下述 Host configuration 解析，下文记作 `<STORE>`。
- `language`：讲解语言，默认 `chinese`，也支持 `english`。下述讲解原则适用于两种语言。
- `dashboard_url`（可选）：本机阅读工作台的 HTTP 地址。按登记协议确认它服务于当前 `<STORE>` 后优先复用；服务未启动时先恢复本机服务，不能返回失效链接。

读取相邻技能的 `../read-main/references/session-registration.md`。先提取可选的 `--session <id>`，再解析论文 URL；没有 ID 就为本次阅读分配一个。项目创建的会话复用其 ID，后续结果才能保留项目归属。普通 `/read` 无需先在网页里创建会话。

准备 `<STORE>/_cache/`。所有路径参数加引号；使用当前平台支持的目录创建与文件打开方式。Windows PowerShell 下显式使用 `curl.exe`，避免被解析为其他命令。

## 第一步 · 获取原始材料

从输入提取 arXiv 链接或 GitHub 仓库链接。

**arXiv**：解析 `arxiv.org/(abs|pdf|html)/<id>`，保留指定版本。已有对应缓存时复用；否则依次尝试：
1. `https://arxiv.org/html/<id>`，保存为 `<STORE>/_cache/<id>.html`。
2. 不可用时尝试 `https://ar5iv.labs.arxiv.org/html/<id>`。
3. 再尝试 `https://arxiv.org/pdf/<id>.pdf`，按所需章节分页阅读。

HTML 便于检查公式和章节；PDF 用于补充公式、图表或排版信息。确认响应是论文而不是错误页面。如果全文拿不到，如实说明材料范围，不能把摘要或搜索片段写成对方法与证明的全文解读。

**GitHub**：先读 README（main 不可用时试 master），查找关联论文，再走论文获取流程。如果没有论文链接，按仓库名称和关键词检索；仍找不到时，明确改为基于 README/代码的解释，不能使用“论文证明了”等措辞。

保存原文 URL 和版本；讲解中用实际读到的章节、公式、图表或代码位置定位依据。

## 第二步 · 建立整篇文章的结构

先读摘要和引言，明确研究任务、已有方法的具体瓶颈和作者的核心主张。然后根据这些主张定向读取：
- 方法与必要背景：组件如何衔接，每一部分解决哪个子问题。
- 定理、证明及被引用的附录：结论成立的条件和关键逻辑，不能仅凭方法章节猜测证明。
- 实验与消融：主张得到了哪些支持，评价设置和适用范围是什么。
- 关键图表：用架构图、示例或结果图帮助对齐专业描述和直观理解。

按理解所需的依赖顺序组织讲解。优先展开核心创新及不可缺少的前置概念；相关工作、常规组件和实验细节的深度以是否帮助理解为准。

## 第三步 · 组织讲解

写作前读取 [references/reading-style.md](references/reading-style.md)，其中定义整体与局部的讲解方式、严谨性的边界和何时简化。

### 先建立整体认识

先从**专业技术角度**介绍问题与方法：任务、关键瓶颈、作者的技术路线，以及它相对已有做法的变化。术语首次出现时给出必要释义，避免一开始陷入局部公式。

再补一个**直观版本**：用具体输入输出、情境或小例子说明发生了什么、作者改变了哪一步。让两种说法指向同一机制，使读者有一幅能带入后文的整体图景。

### 再深入关键部分

对值得展开的部分，通常按下列顺序讲：
1. **直观动机**：这一部分要解决什么具体问题，作者准备怎么做，为什么整体方法需要它。
2. **原文与严谨解释**：文章实际怎样定义、建模、推导或实现。对齐原文位置，解释符号、假设和关键步骤；有证明时把关键逻辑讲清，必要时补推导并注明来源性质。
3. **直观回看**：看过形式化细节后，这一步本质上做了什么，关键公式或机制应该怎样理解，它与开头的问题怎样对应。用例子、极端情形或图示帮助理解，而不是换词重复前面的动机。

这是可调整的讲解顺序。简单部分可以合并，一句就能解释清楚的不扩写成三个小节；复杂核心部分可以展开多轮。无需每节都写公式、证明、类比或伪代码。小节标题应描述实际内容。

### 收束到整篇论文

把重要部分重新连起来，解释为什么这样的组合能处理开头的问题。结合读到的实验或理论，说明作者实际支持了哪些结论、还留下哪些限制。收束应帮助读者复述论文思路。

## 第四步 · 必要时用代码打通理解

论文有公开实现、且代码能解释重要机制或消除歧义时，查看 README 指向的核心文件，通常只需模型、训练入口或损失函数中的相关部分。无需克隆含大量权重或数据的整库。

将代码安排在对应的方法解释旁：说明关键变量、操作、张量形状或数据流与论文的对应关系。伪代码只保留帮助理解的步骤，长度随实际复杂度变化。工程近似、实现差异与自行推断明确标注；没有代码时不编造实现。

## 第五步 · 输出与自动打开

1. 读取 `assets/paper_template.html`。将转义后的标题替换 `{{TITLE}}`，完整 HTML 正文替换 `{{CONTENT}}`；正文遵循上述阅读风格，按实际内容安排章节。
2. 可用 `.technical` 标注专业概览、`.scene` 表达直观动机、`.formal` 放严谨解释、`.takeaway` 放直观回看、`.source` 标注原文位置。保留原有 `.box`、`.result`、`.warn`、`.ok` 和 `.code` 样式。按需选用，不要求每类都出现。
3. 公式用 `$...$` / `$$...$$`。原文链接和引用位置可点击。使用关键原图时，读取 [references/paper-figures.md](references/paper-figures.md) 保留本地缓存、图注和来源。
4. 写入 `<STORE>/<短标题>--<session-id>.html`。短标题去掉路径及文件名非法字符；独立阅读不覆盖旧会话，明确续读则按登记协议更新该会话文件。
5. 确认正文完整、公式符号可读、证据标注准确，然后按 `session-registration.md` 登记，并**自动打开 `index.html#session=<session-id>`**。首次显示本次论文，左侧栏保留。这个步骤属于 `/read` 的默认收尾，无需用户再执行 `/read-main`。打开失败时如实说明并给工作台和笔记链接。
6. 最终回复开头必须给出可点击的工作台链接和完整笔记链接，不能只给路径或声称已打开。按登记协议验证实际页面，并保留交付用浏览器标签及其本机服务。随后给精炼的专业概览与直观概览，突出最重要的理解和必要限定，附工作台及独立笔记路径。细致推导放入 HTML；用户指定详细对话解释时按其要求展开。

## 内容可信度

区分作者原文、作者的证明、实验支持、补充推导和直观类比。经验性方法不强行赋予数学保证；引用到但未读到的证明不假装已核验。关键依据缺失或解释包含推断时，在对应位置明确说明。

## 阅读中的追问

用户对已有笔记提问并希望修改输出时：`/read_rewrite`、`/read-rewrite` 或 `$read-rewrite` 读取 `../read-rewrite/SKILL.md`，将解答融入原段落；`/read_comment`、`/read-comment` 或 `$read-comment` 读取 `../read-comment/SKILL.md`，保存到编号/全局批注。两者复用当前会话与 HTML，不能再次执行独立 `/read` 创建新记录。普通聊天提问不擅自改写笔记。

## Host configuration

Before resolving the note library, run the installed sibling read-main `host_config.py --host codex` in Codex or `--host claude` in Claude Code. Its output is authoritative for the config path, store and language: it honors CODEX_HOME / CLAUDE_CONFIG_DIR and existing preferences. Without a configured store, use D:/claude_paper_reading only on Windows with a D: drive; otherwise use ~/PaperReading. Resolve scripts from the actual skill location, never a hardcoded ~/.claude/skills path. Use the host's available file/shell/browser tools; when no browser tool exists, use build_dashboard.py --open and report the printed links without claiming visual verification.
