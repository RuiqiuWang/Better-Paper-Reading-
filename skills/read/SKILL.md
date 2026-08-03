---
name: read
description: 读论文并做三段式讲解 / Read a paper and explain it in three escalating layers. Use when the user gives an arXiv link or GitHub link and wants the paper read and explained — especially when the user types /read <url>. Fetches the full paper, explains it from intuition → method → details (intuition + math + pseudocode), then renders a LaTeX-ready HTML note into the configured library and opens it. Trigger whenever the user mentions reading a paper, 精读 paper, 看懂这篇 arxiv, or gives a paper link to explain, even without explicitly asking for a skill.
version: 1.0.0
---

# 论文阅读 · 三段式讲解 (Paper Reading · Three-Layer Explanation)

把"怎么看一篇论文"固化成稳定流程。核心是三层递进讲解 + 一个可积累的 HTML 笔记库。按第一步到第五步执行。

## 配置 (Config)

开始前读配置文件 `~/.claude/paper_reading_config.json`（没有就用默认值）：
- `store_dir`：笔记和缓存目录，默认 `D:/claude_paper_reading`
- `language`：讲解语言，默认 `chinese`（可选 `english`）

下文把 `store_dir` 记作 `<STORE>`。语言由 `language` 决定——`chinese` 用中文讲，`english` 用英文讲。用户可用 `/read-store` 改路径、`/read-language` 改语言，二者都写这个配置文件。

确保目录存在：`mkdir -p "<STORE>/_cache"`。Write 工具 file_path 用正斜杠绝对路径；给 Windows 原生命令（explorer/cmd）传路径时用反斜杠。

## 输入解析 (Parse input)

从 args 或用户消息提取一个 URL：
- **arxiv**：匹配 `arxiv.org/(abs|pdf|html)/<id>`，提取 id（如 `2401.12345`，版本号可带可不带）。
- **github**：匹配 `github.com/<owner>/<repo>`，走"从 repo 反查论文"流程。

## 第一步 · 拿到论文全文（公式优先用 HTML 源）

为什么关键：arxiv PDF 里数学公式是渲染后的字形，文本提取还原成 LaTeX 质量很差（下标、矩阵、希腊字母常错），会毁掉第三层。arxiv HTML 版公式是 MathML，能准确还原。所以 **HTML 源优先，PDF 只在没 HTML 或要看图时用**。

**arxiv 流程**（按序尝试，成功即停）：
1. `curl -sL "https://arxiv.org/html/<id>" -o "<STORE>/_cache/<id>.html"`，Read 这个本地 HTML（当文本读，拿带 MathML 的全文）。
2. 空或 404 → 试 ar5iv：`curl -sL "https://ar5iv.labs.arxiv.org/html/<id>" -o "<STORE>/_cache/<id>.html"`。
3. 仍失败 → 下 PDF：`curl -sL "https://arxiv.org/pdf/<id>.pdf" -o "<STORE>/_cache/<id>.pdf"`，用 Read 的 `pages` 分页读（每次≤20页）。
4. 都失败 → 告诉用户：可能网络受限（国内访问 arxiv/ar5iv 常需代理），或请用户手动把 PDF 放进 `<STORE>/_cache/` 再继续。

**github 流程**（反查论文）：
1. WebFetch `https://raw.githubusercontent.com/<owner>/<repo>/main/README.md`（main 失败试 master）。
2. 从 README 找 arxiv 链接（正则 `arxiv\.org/(abs|pdf|html)/[0-9]{4}\.[0-9]{4,5}`，常在 paper badge 里）。找到 → 回 arxiv 流程。
3. 没找到 → 用 repo 名 + 关键词 WebSearch 搜 arxiv；仍无 → 告诉用户"README 里没找到论文链接"，改为只读 repo 代码（第三层基于 README/代码推断，用 `.warn` 标注"未读到原论文"）。

**缓存**：同一 `<id>` 若 `<STORE>/_cache/` 已有对应文件，直接复用，别重下。

## 第二步 · 分块定向阅读（聚焦核心方法，别无脑全读）

为什么：30 页论文全文塞进上下文又贵又易超 token，相关工作、详细实验对"看懂方法"非必需。

顺序：
1. **abstract + introduction**——建立"问题是什么、贡献是什么"。喂第一层、第二层。
2. **定位 method/approach 章节，精读**——第三层细节的唯一来源。HTML 按章节标题定位；PDF 读对应页。
3. **扫 experiments 结果表 + conclusion**——抓关键数字（提升多少、哪个 benchmark），不必逐实验细读。
4. **要看架构图/流程图时**，读 PDF 对应页（Read 能把 PDF 页当图像看）。

## 第三步 · 三段式讲解（对话里先给精炼版）

严格按三层递进，每层先直觉后形式。对话给**精炼版**（每层几段 + 关键公式），完整版进 HTML。语言按 config 的 `language`。

### 第一层 · 直觉讲清问题
- 这篇解决什么问题？大白话，**不**深入数学和代码。
- 为什么难 / 之前方法为什么不行 / 为什么重要。
- 标准：不在该领域的人能听懂"它在干嘛"。

### 第二层 · 方法直觉 + 为什么有效
- 作者从直觉和逻辑上做了什么？还不深入公式。
- 直觉上为什么 work？抓住了什么关键？
- 有"核心洞见"（一句话点破的，如 rsync 的"滑动窗口绕过固定边界"）就在这里点出。

### 第三层 · 细节（直觉 → 数学 → 伪代码）
对**核心方法**逐个走（按"聚焦核心方法"约定，只覆盖论文真正的贡献，不覆盖所有方法）：
1. **先直觉**：这一步在干什么、为什么需要。
2. **再数学**：写公式，**每一步推导配一句"这步在干什么/为什么"**。不甩公式。LaTeX，符号首次出现配中文/英文含义。
3. **若有 github 开源**：fetch 核心代码，用**伪代码**讲清实现（见第四步）。

为什么每步配含义：孤立公式堆砌没用；让读者跟着"这步在干嘛"走才真懂。

## 第四步 · github 代码（若开源，只 fetch 核心文件）

为什么：clone 整库又慢又占地方，大 repo 带 checkpoints/数据集动辄几个 G。看懂"方法怎么实现"只需 README 指向的核心脚本。

流程：
1. 看目录结构：WebFetch `https://api.github.com/repos/<owner>/<repo>/contents/`，或抓 github 页面。识别核心文件（通常 `model.py`/`network.py`、`train.py`、损失函数、README 提到的入口）。
2. 只 fetch 那 1–3 个核心文件（WebFetch `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`）。
3. 用**伪代码**讲清实现：核心逻辑抽象成 10–30 行伪代码，配注释说明对应论文哪一步。**不贴原码**（噪音大）。
4. 代码和论文公式有出入（工程简化、trick）就点出来——这对理解"论文 vs 实际"很有价值。

## 第五步 · 渲染 HTML（完整版笔记）

为什么：对话公式渲染有限、长讲解终端不好读。HTML + MathJax 排版好，且积累成笔记库。

流程：
1. 读模板 `assets/paper_template.html`（本 skill 目录下）。含完整 CSS（浅色窄栏 + 彩色 callout）和 MathJax 配置。
2. `{{TITLE}}` → 论文标题，`{{CONTENT}}` → 完整三段式 HTML。用模板 callout 类组织：
   - `.scene`（蓝）= 直觉/场景 · `.box`（灰）= 含义 · `.result`（橙）= 结论 · `.warn`（红）= 坑/不确定 · `.ok`（绿）= 要点
   - 公式 `$...$` / `$$...$$`，代码 `<pre class="code">`（可用 `.cm`/`.kw`/`.st` span 着色）
3. 文件名：论文英文短标题（空格换 `-`，去掉 `: / \ * ? " < > |`），或直接用 arxiv id。Write 到 `<STORE>/<文件名>.html`。
4. 自动打开：`explorer.exe "<STORE反斜杠>\<文件名>.html"`；无效则 `cmd.exe /c start "" "<STORE反斜杠>\<文件名>.html"`。
5. 对话告知 HTML 路径 + 给精炼版讲解。

## 通用约定

- 讲解语言按 config `language`（默认中文）。
- **诚实**：论文没讲清、代码与论文不一致、自己推断的部分用 `.warn` 标出，别假装确定。
- 对话精炼版 + HTML 完整版分工，不重复堆砌。
