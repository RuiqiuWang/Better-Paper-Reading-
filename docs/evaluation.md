# 实验评测与记录 / Research Evaluate

状态：已实现 `research-evaluate` 的 agent 工作流和协议模板，包含2Dto3D与深度估计参考。没有内置训练器、自动评分/绘图服务，也未改变真实课题或启动实验。

```text
$research-evaluate 为当前topic核验代表论文和benchmark，确定需要保存的曲线、表格与日志。
```

Claude Code用 `/research-evaluate`；`--profile research` 或 `all` 安装，reading默认不变。

新topic先定义任务与可比条件，再查论文评测章节/官方代码，输出“论文依据表 → 指标契约 → 产物清单”。指标注明来源、方向、单位、预处理、聚合与频率。访问不到的来源明确未核验；与目标条件不符的论文说明排除理由。

| 共用记录 | 任务适配 |
|---|---|
| loss分项、学习率、step与耗时原始数据 | 无训练时不伪造loss曲线 |
| 固定数值验证集和可视化子集 | 固定实际ID/帧段/预处理/种子；最终测试独立 |
| 汇总与逐样本指标、配置/版本、恢复状态 | 主指标来自任务论文和benchmark |
| 运行事件、吞吐/显存/数据等待 | 按成本采样，不以worker越多越好 |

2Dto3D参考包含配对右目PSNR/SSIM/LPIPS及遮挡、时序对照；深度参考包含AbsRel/RMSE/δ1、尺度对齐与原始深度保存。每50个optimizer steps的小验证是可调整起点，完整验证、媒体导出和checkpoint另定周期。

正式大规模运行前衔接[性能优化](optimization.md)：固定本协议的质量与输入条件，先小预算诊断与验证，再选正式配置；已有适用性能记录可复用。

权威内容：[技能入口](../skills/research-evaluate/SKILL.md)、[协议与产物模板](../skills/research-evaluate/references/protocol.md)、[任务参考](../skills/research-evaluate/references/task-profiles.md)。协议纳入课题Git；运行产物进入/data，由research-manage维护实验摘要与历史。具体协议在实际topic内制定和版本化，不因安装技能而自动冻结。
