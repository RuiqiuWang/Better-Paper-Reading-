# 性能优化 / Research Optimize

`research-optimize` 是正式训练或批量推理前的小预算优化入口，包含通用视频和两阶段2Dto3D参考。它指导agent检查真实工程、适配计时与修改并验证，不是安装后自动启动的benchmark或训练调度器。

```text
准备正式大规模实验，先检查瓶颈，用小预算比较方案并保存可靠配置。
优化这个视频训练的数据供给，同时保持有效batch、增强和评测协议。
按两阶段2Dto3D方案，检查深度、warp、生成和输出的完整推理管线。
```

这些自然语言请求由[自动流程](automatic-workflow.md)衔接，用户无需手动调用。也保留 `$research-optimize`（Claude Code为 `/research-optimize`）作为可选入口；安装profile选 `research` 或 `all`。

## 分类与发现

| 层次 | 权威入口 | 用途 |
|---|---|---|
| 所有领域共用 | [技能入口](../skills/research-optimize/SKILL.md)、[领域诊断](../skills/research-optimize/references/domain-workflow.md) | 工作负载、预算、瓶颈、正确性与正式运行条件 |
| 通用视频训练/推理 | [视频管线](../skills/research-optimize/references/video-pipelines.md) | 解码、时序窗口、缓存、传输、计算、多卡和写出 |
| 两阶段2Dto3D | [任务方案](../skills/research-optimize/references/two-stage-2dto3d.md) | 深度/几何→生成补全、单目与右目辅助区分、实测配置 |
| 保存与复用 | [性能记录](../skills/research-optimize/references/performance-record.md) | 试跑证据、正式配置、有效条件与回退 |

先选择当前瓶颈，少量候选验证后进入正式实验；已有匹配记录可复用。性能选择遵守research-evaluate的质量协议，结果由research-manage登记。无收益就保留基线，避免调优本身变成无期限实验。

案例已验证：两阶段2Dto3D、24个17帧窗口、50步Euler、两张A100交换卡位，组合流水线使平均耗时15.235→13.723秒，减少9.92%。这不代表视频训练、长视频或新模型都有同样收益；详见任务方案与其证据JSON。完整真实资产保留在课题项目，技能仓库只分发去除私有路径的摘要。

新增领域时先在具体课题保存适配记录，证据成熟后再新增有清晰触发条件的reference，并从技能入口链接。只有独立触发与执行流程足够明确时才拆成新技能；不为每个细分领域复制一套通用规则。
