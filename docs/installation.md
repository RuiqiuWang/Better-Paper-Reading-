# 安装与升级 / Installation

## 完整安装

需要Python 3.8+；本地Git功能需要Git。安装器及核心辅助脚本使用Python标准库。OpenReview助手需要的 `openreview-py` 是按需依赖，见[阅读指南](reading.zh-CN.md)。开发验证还需要Node.js。

在仓库根目录执行：

```sh
python install.py --target codex --profile all
```

- `--target codex|claude|both` 选择宿主，省略时为both。
- `--profile reading|research|all` 选择技能组合，省略时仍为reading。
- `--dry-run` 预览目标目录，不写入。
- `--skills-dir PATH` 为单个宿主指定安装位置，不能与target=both组合。

其他终端入口：

```powershell
.\install.ps1 -Target codex -Profile all
# 自定义Python：-Python "C:/path/to/python.exe"
```

```sh
bash install.sh --target both --profile all
```

## 安装位置

| 宿主 | 默认位置与兼容行为 |
|---|---|
| Codex | 新安装为 `~/.agents/skills`；已有本项目技能在 `~/.codex/skills` 或 `CODEX_HOME/skills` 时复用现有位置 |
| Claude Code | `~/.claude/skills`，支持 `CLAUDE_CONFIG_DIR` |

两个Codex候选目录都存在本项目技能时，安装器要求显式选择 `--skills-dir`，避免重复安装。旧技能先备份到目标目录上一级的 `paper-reading-backups/<timestamp>/`。笔记、个人阅读设置和凭据不会被重置。技能菜单未刷新时重新加载宿主或开启新任务。

## 升级与兼容

GitHub仓库已从 `RuiqiuWang/Better-Paper-Reading-` 更名为 `RuiqiuWang/Better-Research`。从旧地址clone的用户，在确认origin指向本项目后更新：

```sh
git remote set-url origin https://github.com/RuiqiuWang/Better-Research.git
```

在工作区干净且本地main没有独立分叉时：

```sh
git switch main
git pull --ff-only origin main
python install.py --target codex --profile all
```

有未提交改动或分叉时先检查并处理，不使用reset/clean覆盖工作。查看[更新记录](../CHANGELOG.md)，再选需要的安装组合；仓库更新本身不会自动更新个人技能目录。

Better Paper Reading升级到Better Research无需迁移阅读库。`read-*`命令、阅读配置文件和备份目录保持兼容；research组合增加两个科研技能。新clone目录为Better-Research，旧checkout文件夹无需改名。

如需撤回某次技能升级，可从对应备份恢复所需技能；先保留升级后的个人修改。备份不包含此次新安装、此前不存在的技能；不要将整个技能目录一并覆盖。
