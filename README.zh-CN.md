# PaperReading Skills

<p align="center">
  <em>一套 Claude Code 技能:像一位好导师那样读 arXiv 论文或 GitHub 仓库——先讲直觉,再讲数学,最后讲代码——并能把一个研究方向里所有值得读的论文都找出来。</em>
</p>

<p align="center">
  <img alt="version" src="https://img.shields.io/badge/version-v2.0.0-blue">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="platform" src="https://img.shields.io/badge/platform-Claude%20Code-purple">
  <img alt="status" src="https://img.shields.io/badge/status-stable-brightgreen">
  <a href="./README.md"><img alt="English" src="https://img.shields.io/badge/README-English-blue"></a>
</p>

<p align="center">
  <sub><a href="./README.md">English</a> &nbsp;|&nbsp; <b>中文</b> &nbsp;|&nbsp; <a href="./README.zh-CN.md">简体中文</a></sub>
</p>

---

## 这是什么?

**PaperReading Skills** 是一套(共四个)Claude Code 技能,把「帮我读这篇论文并讲解」和「帮我找这个方向有哪些论文」变成一条命令。

给它一个 arXiv 链接或 GitHub 仓库,它会抓取论文、有重点地阅读,并产出结构化的三层讲解——从大白话的问题直觉,一直到逐步推导的数学公式和参考实现的伪代码。每份讲解都渲染成排版精美的、LaTeX 就绪的 HTML 笔记,可以保存反复看。给它一个研究方向,它则跑一轮多源检索,列出所有相关论文(带 arXiv 链接、代码、一句话摘要)。

它存在的理由是:**把一篇论文讲好是一门可复用的手艺,不是一次性的活。** 同一套理解阶梯——*直觉 → 方法 → 细节*——无论论文讲的是立体视觉、扩散桥还是滚动校验都适用。把这套阶梯固化成技能,你就再也不用每次重新交代「我想怎么读论文」,只需 `/read <url>`。

## 阅读方法:直觉 → 数学 → 代码

每篇论文分三层递进讲解。核心原则:**在读者知道公式是干嘛用的之前,别把他们扔进公式里。**

### 第一层 —— 用大白话讲清问题
这篇论文解决什么问题?为什么难、之前的方法为什么不行、为什么重要?不谈数学、不谈代码。标准:不在该领域的人也能听懂它在干嘛。

### 第二层 —— 直觉上讲方法
作者到底做了什么(不写公式)?关键问题——*为什么有效?* 它抓住了什么洞见?如果有一句话能点破的「啊哈」(比如 rsync 的「让窗口滑动而不是固定块边界」),就在这里明确点出。

### 第三层 —— 细节:数学 + 代码
对每个**核心贡献**(不是每个章节——只聚焦论文真正的创新点):

1. **先直觉** —— 这一步在干什么、为什么需要。
2. **再数学** —— 公式,**每一步推导都配一句「这步在干嘛/为什么」**。光甩公式没用;让读者跟着「这步什么意思」走才有用。符号首次出现时用大白话解释。
3. **再代码** —— 如果论文开源,把参考实现抽象成约 10–30 行带注释的伪代码,对应回论文的步骤。代码和论文不一致的地方(工程简化、trick)明确点出。

## 笔记怎么存

笔记不会消失在对话里。每次阅读都会在你配置的笔记库里生成一个独立 HTML 文件,并自动在浏览器打开。

- **笔记库** —— 用 `/read-store <路径>` 设置一次(默认 `D:/claude_paper_reading/`)。每篇论文变成 `<标题>.html`,积累成你的个人论文笔记集。
- **缓存** —— 抓取的论文(arXiv HTML/PDF、GitHub 源码)存在 `<store>/_cache/`,重读同一篇不会重新下载。
- **渲染** —— HTML 用 [MathJax](https://www.mathjax.org/) 渲染 LaTeX,浅色主题 + 彩色标注框:<span style="color:#0b62c4">蓝 = 直觉/场景</span>、<span style="color:#666">灰 = 含义</span>、<span style="color:#b8791a">橙 = 结论</span>、<span style="color:#c0392b">红 = 坑/不确定</span>、<span style="color:#1a7f45">绿 = 要点</span>。
- **语言** —— 用 `/read-language chinese|english` 切换讲解语言(默认中文)。对话摘要和 HTML 笔记都跟随这个设置。

## 四个命令

| 命令 | 作用 |
|---|---|
| `/read <arxiv-或-github-链接>` | 读一篇论文,产出三层讲解 + HTML 笔记。 |
| `/read-search [会议] <主题>` | 发现某个主题的论文——全面地——可选地限定到某个顶会。 |
| `/read-store <路径>` | 设置笔记和缓存的保存位置(跨会话持久化)。 |
| `/read-language <chinese\|english>` | 切换讲解语言(跨会话持久化)。 |

`/read-store` 和 `/read-language` 写一个小 JSON 配置(`~/.claude/paper_reading_config.json`),`/read` 和 `/read-search` 每次运行都读它,所以你的偏好跨会话保留。

## 用 /read-search 发现论文

`/read` 读单篇论文,`/read-search` 找值得读的论文——全面地。给它一个主题,可选地限定到某个顶会,它会跑一轮独立的多角度检索,免得你只搜到两篇就以为覆盖全了。

```text
/read-search self-evolution like AlphaEvolve
/read-search cvpr2027 stereo video generation
/read-search 2D-to-3D video conversion like StereoCrafter
```

会议部分是**可选的**,且只认重要的会议(CCF-A 加上 ECCV/EMNLP 这类顶级 B):`neurips`、`icml`、`iclr`、`aaai`、`ijcai`、`cvpr`、`iccv`、`eccv`、`acl`、`emnlp`、`naacl`、`siggraph`……可带可不带年份。如果第一个 token 不是已知会议,整个输入就当作主题。

目标是广度。比如「像 StereoCrafter 那样的 2D-to-3D」,期望是种子**加上**它的邻居——StereoPilot、M2SVID、StereoWorld、Elastic3D、Deep3D——而不是只出现 StereoCrafter 两遍。所以这个技能:

- **按会议家族路由** —— 这是 hard filter 的关键:
  - **OpenReview 会议(ICLR / NeurIPS / ICML)**:用官方 `openreview-py` SDK 登录,绕过 OpenReview 的 Cloudflare JS 挑战(匿名 curl/requests 一律 `403 ChallengeRequired`,无论 IP 或 VPN)。凭据存在本地 `~/.claude/openreview_credentials.json`,首次使用时提示输入。然后用 `content.venueid=<会议>.cc/<年份>/Conference` 拉取**核验过的录用列表**,每篇的录用档次(Oral/Spotlight/Poster/regular)直接从 `content.venue` 字段读出。
  - **CVF 会议(CVPR / ICCV / WACV / ECCV)**:直接爬 `openaccess.thecvf.com`(无 Cloudflare)。
  - **ACL / AAAI / SIGGRAPH / ACM**:抓取各自的 proceedings 页。
- **arXiv 走纯 HTTPS** —— `https://export.arxiv.org/api/query` 在国内可直连(无需代理);查询用 `+AND+` 连接或带引号短语构建,避免空格分隔导致的松散 OR 误命中。
- **解析种子** —— 点名的锚点论文(AlphaEvolve、StereoCrafter)*加上* 概念任务(self-evolution、2D-to-3D)——围绕两者都搜。
- **并行多源检索** —— arXiv API、Semantic Scholar、Papers With Code、DBLP(全免费、无需 key),加上 4–8 条带同义词的网页搜索。
- **引用图雪球** —— 对顶级种子,通过 Semantic Scholar 同时拉它的 *references*(前驱)和 *citations*(后继)。这一步是抓到「邻居」的关键,纯关键词搜索抓不到。
- **找真代码仓库** —— 对每个命中(尤其种子),从 arXiv HTML 全文里 grep GitHub/项目链接,再用 GitHub 反查交叉验证;从不编造仓库,找不到就省略。
- **去重 + 分类** —— 按 arXiv id 再按模糊标题去重,然后分组:锚点 / 相关 / 近期-SOTA / 基础前驱。

结果是聊天里的一个**列表**(不是表格)——每项是一句话直觉加 `arXiv`/`forum`/`code`/`page` 链接(没有的行省略)——并保存一份带日期的 digest 到 `<store>/_search/`,和你的阅读笔记放一起。诚实规则同 `/read`:绝不编造论文、arXiv id 或仓库;标记仅片段匹配的;如果某会议的录用列表确实拿不到(且用户不愿提供 OpenReview 凭据),如实说明并改用无会议的预印本搜索——绝不用预印本冒充录用论文。

## 安装

这些是标准 Claude Code 技能。

```bash
# 1. 克隆仓库
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git

# 2. 把技能复制(或软链)到你的 Claude Code 技能目录
cp -r paper-reading-skills/skills/* ~/.claude/skills/
#    Windows (Git Bash) 下是:  C:/Users/<你>/.claude/skills/

# 3. 开一个新的 Claude Code 会话,然后可选地设置笔记库:
#    /read-store D:/my/papers
```

**依赖:**
- [Claude Code](https://claude.com/claude-code)(CLI / 桌面 / IDE 扩展)。
- `curl`,用于抓 arXiv/GitHub(macOS/Linux 自带;Windows 随 Git 安装)。
- Python 3.8+ 且装了 `openreview-py`(给 `/read-search` 用在 OpenReview 会议——ICLR/NeurIPS/ICML)。安装:`pip install openreview-py`(国内:`-i https://pypi.tuna.tsinghua.edu.cn/simple`)。首次用 OpenReview 会议时会提示输入你的 openreview.net 账号(免费注册),凭据存在本地 `~/.claude/openreview_credentials.json`。
- 能访问 `arxiv.org` / `github.com` / `openreview.net`。

然后运行:
```
/read https://arxiv.org/abs/2401.12345
/read-search self-evolution like AlphaEvolve
/read-search icml2026 stereo video generation
```

## 底层怎么工作

几个不那么显然的设计选择,区分了「它吞了 PDF」和「它真懂了这篇论文」:

- **arXiv HTML 优先于 PDF。** PDF 里数学公式是渲染后的字形,文本提取会把下标、矩阵、希腊字母搞乱——这会毁掉第三层。技能优先用 `arxiv.org/html/<id>`(和 `ar5iv` 镜像),那里公式是 MathML,能还原成干净的 LaTeX。PDF 是后备,也是看图的来源。
- **聚焦阅读,不是全文塞进上下文。** 30 页论文全塞进去又贵又分散注意。技能读 abstract+intro 建立问题框架,直接跳到 method 章节拿第三层细节,再扫结果——跳过不服务于理解的部分。
- **GitHub → 论文解析。** 给一个仓库,它读 README、提取 arXiv badge/链接、跟到论文。如果仓库没带论文链接,就退回直接读代码(明确标注)。
- **抓取而非克隆。** 对开源论文,只拉 README 指向的 1–3 个核心源文件(model、训练入口、loss)——不是整个仓库(常带几个 G 的 checkpoint)。讲的是伪代码,不是原始源码。
- **诚实标注。** 论文没讲清的、代码和公式不一致的、技能推断而非读到的,都用红色标注框标出——绝不假装确定。

## 项目结构

```
paper-reading-skills/
├── README.md
├── README.zh-CN.md            # 中文版 README
├── LICENSE
├── install.sh                 # 把技能复制到 ~/.claude/skills/
└── skills/
    ├── read/                  # 主阅读技能
    │   ├── SKILL.md
    │   └── assets/paper_template.html
    ├── read-store/            # 设置笔记库路径
    │   └── SKILL.md
    ├── read-language/         # 切换讲解语言
    │   └── SKILL.md
    └── read-search/           # 发现某个主题的论文
        ├── SKILL.md
        ├── openreview_fetch.py    # 登录并拉取 OpenReview 录用列表
        └── save_credentials.py    # 本地存储 OpenReview 凭据
```

## 自定义 HTML

笔记模板在 `skills/read/assets/paper_template.html`。这是一个自包含文件,所有 CSS 和 MathJax 配置都内联——改配色、字体或标注框样式,以后每篇笔记都会跟着变。渲染时替换两个占位符:`{{TITLE}}`( `<h1>` 和 `<title>`)和 `{{CONTENT}}`(渲染后的讲解正文)。

## License

[MIT](./LICENSE) —— 读论文、存笔记、自由 fork。
