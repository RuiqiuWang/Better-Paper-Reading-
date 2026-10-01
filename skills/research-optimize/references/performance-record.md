# 性能记录与正式配置

在课题已有性能文档中更新；没有时采用 `research/performance/<id>.md`。链接实际配置和run，不手工复制大量日志。原始计时放个人run目录，轻量摘要随课题Git维护。以下是字段模板，填写真实值；未测项注明未测，不填0。

```yaml
status: planned # planned / running / completed / failed
validation: pending # pending / passed / failed / limited
purpose: throughput # latency / throughput / training_time_to_quality
workload:
  task: task-and-input-contract
  mode: inference # training / inference / validation
  manifest: fixed-sample-file-and-hash
  units: samples-and-effective-frames-or-tokens
  shape_precision_steps: actual-config-reference
  quality_protocol: metric-tolerance-and-seed-reference
environment:
  code_model_versions: version-or-hash-reference
  hardware_software: actual-machine-gpu-uuid-framework-driver
  resource_allocation: gpu-cpu-ram-disk-and-sharing
budget:
  max_wall_seconds: set-before-running
  max_candidates: set-before-running
  max_samples_or_updates: set-before-running
  stop_conditions: numerical-failure-resource-limit-budget-no-gain
comparison:
  baseline_config: original-config-reference
  candidates: changes-and-expected-bottleneck
  repetitions_order: measured-plan
  warmup_and_cache: cold-warm-compile-accounting
  output_contract: required-files-and-writer-drain
results:
  raw_timings: run-path
  correctness: intermediate-output-or-training-check-evidence
  wall_latency_throughput: measured-values-with-units
  stage_times: cpu-wait-device-communication-output-and-overlap
  resource_peaks: ram-pinned-vram-and-disk
decision:
  selected_config: measured-selection-or-baseline
  reason: gain-quality-cost-and-uncertainty
  fallback: original-working-config
  validity: workload-code-environment-resource-conditions
  uncovered: untested-shapes-training-quality-or-long-video
  production_run: authorized-run-reference-or-not-started
```

候选比较表至少包含：配置差异、完成数、完整墙钟/目标吞吐或延迟、峰值资源、质量检查、结论与证据。需要p50/p95时保存足够原始样本；样本太少应注明分位数不稳定。

保存每视频/每batch的阶段记录及其计时类别，注明包含关系；逐步GPU事件可作为诊断，不强制永久高频记录。训练注明microstep与optimizer step、有效batch和验证开销；推理注明真实有效帧及输出策略。多卡吞吐记录整体完成墙钟，不能直接相加各卡FPS冒充端到端吞吐。

正式配置附带适用条件和回退配置。预算耗尽但基线可靠时可记录保留基线；未经正确性验证的候选不放大。新任务已有匹配记录时引用它并做变化项核验，不强制每次重复测速。
