# 通用视频训练与推理

适用于视频生成、深度、识别、跟踪等任务的诊断框架；每种优化都要检查模型、数据和硬件条件。下面的PyTorch术语可映射到其他框架，不意味着所有任务都应开启同一配置。

## 先画真实数据流

```text
读文件/解封装 → 解码 → 取帧/时序窗口/增强 → 可选条件构造
             → 有界输入队列 → H2D → GPU计算
训练：前向 → loss → 反向 → 梯度同步/累积 → optimizer更新
推理：前向或多步采样 → 解码/后处理 → 必要D2H → 评分/编码/保存
```

分别标明运行设备、dtype/layout、是否拷贝、是否持有时序状态。训练的周期生成验证单列，不能将50步采样当作每次训练更新。冻结的深度/编码器与可训练模块分开标识。

## 输入供给与传输

- 按片段批量取帧，避免逐帧打开文件或重复随机seek；保留frame ID/PTS、RGB/BGR、颜色范围、resize/crop和视频边界。时序模型的上下文、重叠窗口和状态不能因并行而截断；实时任务还需保持因果性。
- 从当前worker配置和小范围候选开始，例如0/1/2/4；同时控制每个解码器、OpenCV、OMP/MKL内部线程。按rank累计CPU预算，比较吞吐与数据等待。零worker配置不设置多进程专属预取参数；重复epoch可能适合persistent workers，一次短推理未必获益。
- 队列按实际batch字节和并发数预算，计入解码工作区、pin副本、GPU预取及输出。预取只能吸收波动；供给持续慢于消费时，单纯加深队列不会解决瓶颈。[DataLoader官方参数](https://docs.pytorch.org/docs/main/data.html)。
- 锁页缓冲可配合异步H2D；手工在主线程临时pin也有成本，应测量复用缓冲或后台pin路径。`non_blocking=True`不自动产生计算重叠；候选实现使用独立copy stream和事件建立依赖。缓冲在拷贝完成前不能覆写，跨stream张量需保留正确生命周期（如`record_stream`），CPU读取异步D2H结果前必须等待完成。[传输教程](https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html)、[CUDA语义](https://docs.pytorch.org/docs/main/notes/cuda.html)。
- 模型间可兼容的GPU tensor尽量直接传递，减少D2H/H2D往返；CPU tensor不能凭空成为独立GPU显存。GPU warp、GPU预处理或GPU解码需单独核对数值语义。仅在解码确为瓶颈时评估NVDEC等后端的硬件、编码支持和颜色一致性，不因“GPU解码”名称就默认更快。

## 训练特有的判断

| 候选 | 条件与验收 |
|---|---|
| AMP/精度调整 | 核对算子支持与数值稳定性，按dtype/设备需要使用GradScaler；监测梯度/溢出/验证质量，不直接照搬推理低精度 |
| 增大batch或按长度分桶 | 记录有效batch=每rank batch×rank数×累积步数；保留采样分布、正确padding/mask和loss归一化，不能只报step/s |
| 冻结模块缓存 | 仅缓存不需要梯度、在当前输入与增强条件下稳定的结果；缓存键含输入hash、帧/变换、模型版本、精度/协议；随机增强改变内容须重算或正确派生 |
| 编译/融合/注意力实现 | 对照前向、梯度及短程更新；记录冷启动/重编译成本，短任务可能不划算 |
| 激活重计算 | 用重算换显存，是否提高有效吞吐需测量；不能宣称默认加速 |
| DDP/梯度累积 | 记录各rank数据等待与通信；保持分片不重不漏和各rank一致的更新/集合通信次数。使用no_sync时前向也应置于对应上下文，最终累积步正常同步 |

训练只对无需梯度的边界使用`no_grad`，不要把整个训练包进`inference_mode`。冻结模块输出若被可训练模块反向所需，也应核对tensor语义兼容。参考[AMP示例](https://docs.pytorch.org/docs/main/notes/amp_examples.html)、[DDP设计](https://docs.pytorch.org/docs/main/notes/ddp.html)和[调优指南](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html)，以实际安装版本为准。

训练checkpoint后台保存必须先形成一致的模型/优化器/随机状态快照；不能让writer读取持续被更新的活对象。后台快照本身的复制、内存和时间成本要计入。周期验证、媒体导出与checkpoint的频率分别记录，保留科研协议要求。

## 推理与输出

模型持久加载，使用正确的eval与无梯度模式；先预热代表形状，加载/编译另计。保留原采样器、步数、精度作为基线。少步、量化、小模型等作为质量—性能变体单独验证，不能混进“输出等价加速”。有状态或在线视频不能任意跨视频合batch。

视频k计算时可准备k+1，CPU输出线程处理k-1。输入/输出均有上限与背压，复用缓冲前等待消费者完成。D2H按模型输出需求批量传输；编码/压缩后台执行，但传播writer异常、核对样本ID、最终排空才结束计时。流式任务同时报告首帧延迟及稳定帧率，不能用高吞吐掩盖更长响应时间。

## 计时口径

完整批次墙钟是主证据；视频/s和帧/s注明有效帧、padding、分辨率及片段长度。GPU阶段用CUDA events或profiler，不能仅用Python计时包住异步调用。避免为了每阶段计时频繁全局同步而破坏被测流水线；短profile后复核低开销运行。

分别记录CPU处理、主机等待、设备区间、输出和资源。嵌套阶段与重叠区间不能相加当端到端时间；CUDA事件区间可能含launch空隙，不等于纯kernel活跃时间或PCIe带宽。事件交叠只能证明区间交叠，需kernel级证据时使用profiler时间线。GPU利用率只作辅助，报告质量与输出完整性。
