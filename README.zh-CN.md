# Better Research

**从论文阅读到科研课题管理，为 Codex 和 Claude Code 提供可组合的技能。**

[English](README.md) · [更新记录](CHANGELOG.md) · [MIT 许可](LICENSE)

由 Better Paper Reading 演进而来。原阅读功能与命令保持兼容，按小步增加科研能力；当前仓库目录和远程地址保持原名称。

## 已实现

| 模块 | 命令 | 功能 |
|---|---|---|
| 论文阅读 | `read`、`read-main`、`read-search` | 精读、工作台、论文发现 |
| 阅读追问与偏好 | `read-rewrite`、`read-comment`、`read-store`、`read-language` | 原文改写、编号批注、存储位置和语言 |
| 科研管理 | `research-manage` | 课题路径、方法卡、变更历史、具体实验结果和本地 Git |

阅读使用 `read-*`，科研使用 `research-<动作>`。目录、环境与结果如何管理，见[科研管理指南](docs/research-management.md)；完整阅读流程见[阅读指南](docs/reading.zh-CN.md)。

## 安装

需要 Python 3.8+；本地版本管理另需 Git。

```sh
git clone https://github.com/RuiqiuWang/Better-Paper-Reading-.git
cd Better-Paper-Reading-
python install.py --target codex --profile all
```

- `--profile reading`：原七个阅读技能，也是省略该参数时的默认值。
- `--profile research`：只安装科研管理，保留现有阅读技能与配置。
- `--profile all`：同时安装；`--target both` 支持两个宿主。
- `--dry-run`：预览安装；已有技能会备份，笔记与个人配置保留。

```powershell
./install.ps1 -Target codex -Profile all
```

```sh
bash install.sh --target both --profile all
```

安装位置、旧版本升级与阅读配置详见[阅读指南](docs/reading.zh-CN.md)。保留旧配置名和备份目录以便原位升级。

## 使用

```text
$read <论文链接>
$research-manage 为课题整理目录、方法说明和实验结果，维护本地 Git。
```

Claude Code 使用 `/read`、`/research-manage`。科研管理默认代码放 `/home`、环境放 `/data`；阶段完成后只提交相关代码与小型文档。**只有用户明确要求时才推送到远端。** 大数据、权重、视频和环境不进入普通 Git。

## 仓库结构

```text
skill_catalog.json       # 阅读/科研技能清单，安装器读取
skills/read*/            # 论文阅读与追问
skills/research-manage/  # 管理指令、文档模板和本地 Git 脚本
docs/                    # 使用指南、开发说明、待讨论方案
tests/                   # 阅读、安装与 Git 行为验证
install.py/.ps1/.sh      # 统一安装入口
```

开发和验证见[开发说明](docs/development.md)。PSNR/SSIM/loss 曲线及固定视频集目前只是[待讨论方案](docs/experiment-logging-proposal.md)，尚未实现。此仓库不自动启动训练、服务器迁移或后台监控。
