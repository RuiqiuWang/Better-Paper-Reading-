# Better Research · 更好的科研

**让 AI agent 从理解论文，走向有记录、可比较、可复现的科研工作。**

[English](README.md) · [文档导航](docs/README.md) · [参与维护](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

Better Research 将论文阅读、课题管理和评测设计整合为一套面向 **Codex 与 Claude Code** 的技能。项目由 Better Paper Reading 演进而来，保留原有阅读命令、HTML 笔记库和个人配置，后续科研能力在这个仓库持续维护。

## 一条完整的科研工作流

| 阶段 | 技能 | 产出 |
|---|---|---|
| 找论文、理解方法 | `read-search`、`read` | 相关论文、基于原文的解释和 HTML 笔记 |
| 整理知识与追问 | `read-main`、`read-comment`、`read-rewrite` | 阅读工作台、原文批注与解释改写 |
| 管理课题 | `research-manage` | 路径导航、方法卡、实验记录与本地 Git 历史 |
| 确定评测方案 | `research-evaluate` | 论文依据、指标口径、固定样本及曲线/表格/日志方案 |

另有 `read-store`、`read-language` 设置笔记位置与解释语言。当前共 **9 个技能**，统一登记在 [skill_catalog.json](skill_catalog.json)。

阅读工作台与本地 Git 管理已有可执行工具。评测技能目前提供 agent 工作流、协议模板和任务参考；真实训练器的日志、评分与绘图需在具体课题内接入。安装技能不会自行启动训练或后台监控。

## 快速开始

需要 **Python 3.8+**、可以访问本地文件和运行命令的 agent 宿主；本地版本管理需要 **Git**。检索和获取论文需要网络。

在终端运行：

```sh
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git Better-Research
cd Better-Research
python install.py --target codex --profile all
```

Claude Code 使用 `--target claude`，两个宿主一起安装用 `--target both`。系统命令为 `python3` 时替换上面的 `python`。

| 安装组合 | 内容 |
|---|---|
| `all` | 阅读与科研全部技能，新用户推荐 |
| `reading` | 七个阅读技能；为兼容旧用户，仍是命令行默认值 |
| `research` | 科研管理与评测设计，保留已有阅读设置 |

已有技能更新前会备份。安装位置、PowerShell/Bash 入口和升级步骤见[安装指南](docs/installation.md)。

安装后在 **agent 对话中**输入：

```text
$read-search 单目转双目视频生成
$read <论文链接>
$research-manage 为这个课题建立目录导航、方法卡和本地 Git。
$research-evaluate 调研相关论文，确定该课题的指标、固定样本、曲线、表格和日志。
```

Claude Code 将 `$` 换成 `/`。从课题建立到实验结果维护，见[课题工作流](docs/workflow.md)。

## 科研文件与实验记录

默认服务器布局将代码、共享资产和个人产物分开：

```text
/home/<account>/code/<topic>/        # 代码、课题文档、协议和本地 Git
/data/<topic>/                      # 共享数据集、baseline 资产与模型
/data/<account>/envs/                # 实际环境
/data/<account>/env_specs/           # 环境配方
/data/<account>/projects/<topic>/runs/<run-id>/
                                    # 配置、指标、权重、预测和日志
```

课题文档与方法卡回答“东西在哪里、何时因为什么变化”；实验记录保存具体数值与原始证据。固定样本清单和版本化评测协议用于保持比较口径，已包含 2Dto3D 与深度估计的参考规则。

代码和小型文档按阶段维护本地提交，**只有用户明确要求才推送**。数据、环境、大权重和视频不进入普通 Git。已有科研目录先记录真实位置，迁移另按用户授权执行。

## 文档与后续维护

- [文档导航](docs/README.md)：阅读、管理、评测与安装入口。
- [参与维护](CONTRIBUTING.md)：小步修改、验证和评审约定。
- [开发说明](docs/development.md)：项目结构与验证命令。
- [路线图](docs/roadmap.md)：已完成能力与后续方向。

`main` 是统一集成分支。后续继续在本仓库维护，通常使用 `codex/<topic>` 分支完成一项具体改动。

项目名称统一为 **Better Research**。GitHub 地址保留旧名称以兼容已有 clone 和链接；旧阅读配置名与备份目录继续保留，支持原位升级。

[MIT 许可证](LICENSE)。
