# PaperReading Skills

**在 Codex 和 Claude Code 中阅读论文、整理 HTML 笔记，并把追问留在原文对应位置。**

[English](README.md) · [更新记录](CHANGELOG.md) · [MIT 许可](LICENSE)

## 功能

- **论文精读**：先从技术与直观两个角度建立整体认识，再结合原文深入关键部分。
- **阅读工作台**：左侧保留会话、项目、置顶、搜索和归档；点击条目打开对应 HTML，支持项目内创建阅读草稿。
- **自动打开**：阅读完成后打开本次论文会话，并返回工作台和完整笔记链接；打开失败时明确说明。
- **原文改写追问**：将解答自然融入相关段落，保留上下文、公式、来源和已有批注。
- **编号批注追问**：知识点加下划线及方形编号，点击在右栏查看问答；右栏可切换“全局、1、2……”并在同一编号下连续追问。
- **论文发现**：按主题检索，可限定会议，核实录用状态，扩展相关工作并收集论文和代码链接。

## 安装

需要 **Python 3.8+**，以及能够访问本地文件、运行命令的 Codex 或 Claude Code 环境。工作台和追问脚本只用 Python 标准库；调用 OpenReview 搜索助手时才需要可选依赖 `openreview-py`。获取论文和 MathJax 等外部资源需要网络。

```sh
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git
cd Better-Paper-Reading-
python install.py --target both
```

只安装一个宿主时，使用 `--target codex` 或 `--target claude`。系统命令为 `python3` 时替换上面的 `python`。

```powershell
# Windows PowerShell 入口
.\install.ps1 -Target both
# 自定义 Python 路径：追加 -Python "C:/path/to/python.exe"
```

```sh
# macOS / Linux / Git Bash 入口
bash install.sh --target both
```

预览安装位置而不写入：`python install.py --target both --dry-run`。

| 宿主 | 个人技能目录 | 显式调用 |
|---|---|---|
| Codex | 新安装使用 `~/.agents/skills` | `$read URL` |
| Claude Code | `~/.claude/skills`，支持 `CLAUDE_CONFIG_DIR` | `/read URL` |

如果检测到 PaperReading 已安装在 `~/.codex/skills` 或 `CODEX_HOME/skills`，安装器会原地升级，避免重复安装。可以用 `--target codex --skills-dir PATH` 或 `--target claude --skills-dir PATH` 指定其他目录。已有技能会备份到目标目录上一级的 `paper-reading-backups/`。安装不会复制或重置阅读配置、账号凭据和笔记；技能菜单未刷新时重新加载宿主或开启新任务。

宿主规范参考：[Codex 官方技能文档](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 官方技能文档](https://code.claude.com/docs/en/skills)。

## 七个命令

以下命令输入到助手对话中，不是在终端运行：

| Codex | Claude Code | 功能 |
|---|---|---|
| `$read URL` | `/read URL` | 精读论文或关联论文的 GitHub 仓库 |
| `$read-main` | `/read-main` | 打开阅读工作台 |
| `$read-search [会议] 主题` | `/read-search [会议] 主题` | 发现论文，可限定会议 |
| `$read-rewrite 问题` | `/read-rewrite 问题` | 将解答融入原文对应段落 |
| `$read-comment 问题` | `/read-comment 问题` | 新建或续写编号/全局批注 |
| `$read-store PATH` | `/read-store PATH` | 设置笔记与缓存目录 |
| `$read-language chinese` | `/read-language chinese` | 选择 `chinese` 或 `english` |

追问指令也识别 `/read_rewrite`、`/read_comment` 的自然语言请求；宿主技能菜单使用上表的连字符名称。

### 第一次阅读

1. 用 `$read-store ~/PaperReading` 或 `/read-store ~/PaperReading` 设置笔记库。
2. 输入 `$read https://arxiv.org/abs/2409.07447`，Claude Code 则使用 `/read`。
3. 助手保存并登记笔记，自动打开这篇论文的工作台会话。左栏可以回看、置顶和归入项目。
4. 在同一任务中继续追问；需要指定另一篇已保存论文时，加 `--session ID`。

### 追问示例

```text
# Codex
$read-rewrite 这一步为什么需要这个假设？
$read-comment 这个公式应该怎样理解？
$read-comment --comment 1 能再举一个具体例子吗？
$read-comment --comment global 这些组件如何一起解决最初的问题？

# Claude Code
/read-rewrite 这一步为什么需要这个假设？
/read-comment --comment 1 能再举一个具体例子吗？
```

`rewrite` 修改对应讲解；`comment` 保留正文，通过下划线和编号关联问答。“全局”保存整篇论文层面的问题，与各编号线程独立。回答沿用正文的阅读风格。

右栏可选择 Codex / Claude Code 指令格式。输入框会复制带论文 ID 和批注编号的命令，**回到助手任务发送后才会生成回答**；网页本身不调用模型。追问更新原会话并保留问答历史，每次修改前备份 HTML；文件已变化或定位不唯一时会停止写入，要求重新检查。

## 阅读风格

先整体、后深入。首先从专业技术角度说清任务、瓶颈和作者的方法，再用直观版本描述同一个机制，让读者知道发生了什么。

对重要部分按需展开：

1. **直观动机**：这一部分想解决什么事情，作者准备用什么方法？
2. **原文与严谨解释**：原文如何定义、建模、推导、证明或实现？说明符号、假设和关键逻辑，并定位到原文章节、公式或图表。
3. **直观回看**：看过形式细节后，这一步本质上做了什么，我们怎样理解它？

根据内容调整深度，不要求每节都有三段、证明、类比或代码。区分作者主张、原文证明、实验支持、补充推导和直观例子。最后把组件重新连起来，回应开头的问题。完整原则见 [reading-style.md](skills/read/references/reading-style.md)。

## 存储与配置

| 设置 | Codex | Claude Code |
|---|---|---|
| 阅读配置 | `$CODEX_HOME/paper_reading_config.json`，默认根目录 `~/.codex/` | `$CLAUDE_CONFIG_DIR/paper_reading_config.json`，默认根目录 `~/.claude/` |
| OpenReview 凭据 | 同一配置目录的 `openreview_credentials.json` | 同一配置目录的 `openreview_credentials.json` |

始终保留已设置的 `store_dir`。首次使用时，Windows 有 D 盘则默认 `D:/claude_paper_reading`，其他情况默认 `~/PaperReading`；默认中文讲解。两个宿主分别设置相同目录即可共用笔记，配置和凭据仍各自独立。

- 笔记：`<标题>--<session-id>.html`；原文与图片缓存：`_cache/`。
- 检索结果：`_search/`；笔记登记信息：`_index.json`。
- 工作台：`index.html`，登记结果时自动刷新。兼容旧根目录 HTML、`_search/`、`_topic/` 的结果。仓库不包含可选的 `read-search-topic` 技能，但支持它的 `search_topic` 索引类型。
- 追问备份：`.reading-history/`；编号、问答和批注交互保存在 HTML 内。
- 项目、置顶、别名、归档和草稿：浏览器 localStorage，按笔记库和浏览器来源/配置隔离。更换浏览器或访问地址前，可在左下角导出整理数据，再到新环境导入；该备份不包含笔记文件。
- 可选 `dashboard_url`：经过验证的本机 HTTP 地址。`serve_library.py` 为不支持本地文件的内置浏览器提供服务，只监听 127.0.0.1，不公开配置文件和隐藏备份；访问期间需要保持服务运行。

OpenReview 凭据是可选的。需要时在本地设置 `OPENREVIEW_USERNAME`、`OPENREVIEW_PASSWORD`，运行已安装的 `read-search/save_credentials.py --host codex` 或 `--host claude`。不要把密码写入仓库或笔记。访问失败应明确说明，不能把预印本冒充已录用论文。

## 项目结构

```text
install.py / install.sh / install.ps1   # 共用安装器及命令行入口
skills/
  read/                                # 阅读风格、图片与 HTML 模板
  read-main/                           # 工作台、服务、登记、配置与追问助手
  read-comment/                        # 编号和全局批注
  read-rewrite/                        # 原文对应段落改写
  read-search/                         # 检索与 OpenReview 助手
  read-store/                          # 笔记库设置
  read-language/                       # 语言设置
tests/                                 # 保存、批注及双宿主安装测试
```

## 验证

```sh
python -m unittest discover -s tests -v
node --check skills/read-main/assets/dashboard.js
node --check skills/read-main/assets/comments.js
```

HTML 交互已在 Codex 内置浏览器中人工验证；自动化测试覆盖共用脚本和两个安装目标。这不等于已在所有 Codex、Claude Code 版本完成模型端到端测试。
