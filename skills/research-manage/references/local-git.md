# 本地 Git 维护

目标：每个课题在自己的代码/文档目录内有可回看的本地提交。没有用户明确的推送指令，不添加远程、不 push，也不把“整理仓库”解释成发布授权。已有 remote 保留，不访问它。

## 仓库边界

新课题根 `/home/<account>/code/<topic>` 建本地仓库；已有仓库直接沿用。先检查仓库根，不能意外把上级多个课题一起纳入。若处于上级仓库，使用明确选定的既有根与文件范围，或说明需要独立边界；不自动制造嵌套仓库。

baseline 的独立仓库不打包进课题父仓库。父仓库的方法卡记录它的路径、upstream commit 和本地 commit；修改 baseline 时在其已有仓库内另做提交。没有初始化 submodule 的需求就不自动转换成 submodule。

## 跟踪与提交

- 跟踪代码、课题 README、方法卡、CHANGELOG、EXPERIMENTS、配置模板、小型清单及必要环境配方。
- 大数据、环境目录、模型权重、预测视频、缓存和详细日志继续留 `/data`。Git 中保留位置/版本/校验信息与具体实验数值；不要只记录“结果见日志”。可按需保存小型指标摘要或实际配置快照，链接原始证据。
- `/data` 下 run README 的修改本身不受课题 Git 跟踪，所以同步更新 `research/EXPERIMENTS.md` 的数值、范围、验证状态及 CHANGELOG 后再提交。无需把整个 runs 搬进 Git。
- 新建课题/方法、完成一项代码功能、更新实验结果、迁移路径或更正记录后，自动做一次有意义的本地提交。先审查 diff，只提交当前任务相关的明确文件；无变化不做空提交。不按每个训练 step 提交。
- 保留用户已有未提交/已暂存工作。不要使用 `git add .`、`git add -A` 全库暂存、reset/clean/stash/rebase/amend 来让提交变得方便。已有暂存内容归属不明时保留并报告，不替用户提交。
- Git 作者身份缺失时保留文件并说明不能提交，不捏造姓名/邮箱或更改全局配置。用户可以提供项目级身份后继续。

## 工具

脚本路径相对本技能目录，选择实际 Python 可执行文件；中文 Windows 环境建议 `python -X utf8`：

```sh
python <skill-dir>/scripts/local_git.py init --root <topic-root>
python <skill-dir>/scripts/local_git.py status --root <topic-root>
python <skill-dir>/scripts/local_git.py checkpoint --root <topic-root> \
  --message "Record experiment <run-id> results" \
  --files README.md CHANGELOG.md research/EXPERIMENTS.md
```

`init` 保留原 ignore 并补充基础排除项，不自动提交所有旧文件。`checkpoint` 只接收明确文件，拒绝目录、越界、链接、嵌套仓库、常见大资产/私密文件、超过5MiB或含NUL的内容；支持已跟踪文件的删除。它保留 hooks、身份、分支与远程配置，不包含 push 操作。超过脚本边界但确需跟踪的资产应单独评估，不使用强制 add 绕过。

这些检查不是完整秘密扫描；提交前仍检查配置/日志是否含 token。`.gitignore` 对已经跟踪的文件不会生效，发现历史跟踪的大文件/秘密时单独报告，不自动重写历史。helper 锁只协调使用同一 helper 的任务；其他 Git 客户端仍可能并发修改，提交后核对文件范围和状态。

提交失败时记录原因，不谎称已保存；脚本不会清除暂存区，保留失败现场供检查。每次回复可简短给出 commit 短号，明确只在本地。此自动维护由当前活跃任务执行，不是后台守护进程。
