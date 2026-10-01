# 科研管理 / Research management

已实现技能：`research-manage`。面向代码和文档的本地管理；不是服务器后台运维平台。

```sh
python install.py --target codex --profile research
# 两个宿主：--target both；加上阅读技能：--profile all
```

调用示例：

```text
$research-manage 为课题建立目录导航和方法说明，并初始化本地 Git。
$research-manage 根据这次实验的指标文件更新具体结果、失败记录及本地提交。
```

Claude Code 使用 `/research-manage`。

- 代码 `/home/<account>/code/<topic>`；环境 `/data/<account>/envs`。
- 课题 README 指路，方法卡解释代码/环境/资产，CHANGELOG 记录原因。
- EXPERIMENTS 索引和 run README 记录具体结果、样本范围、原始证据和验证状态。
- 初始化本地 Git；有意义的更新自动提交相关文件；只有用户明确要求时才推送。
- 大数据、权重、视频和环境不进普通 Git；实验索引内的数值及小型配置/清单可跟踪。

维护规则和模板的权威来源在技能中：[入口](../skills/research-manage/SKILL.md)、[目录](../skills/research-manage/references/layout.md)、[文档](../skills/research-manage/references/documents.md)、[本地 Git](../skills/research-manage/references/local-git.md)。

Git helper 用 Python 标准库调用已安装的 Git，无远程操作命令。自动维护发生在 agent 当前执行的任务内；不创建后台服务。身份缺失、已暂存工作归属不明等情况会保留现场并报告。

Full paper-reading workflows remain available separately. This module adds local topic documentation, evidence-linked experiment records, and explicit-file Git checkpoints without automatic remote publication.
