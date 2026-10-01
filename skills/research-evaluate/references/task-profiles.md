# 任务参考：2Dto3D 与深度估计

以下是起点，不是所有课题的固定benchmark。新topic仍须查其相关论文与官方实现，记录所选版本。无GT的指标不可伪造，写不适用及可用证据。表中时序/几何检查需要协议明确实现、运动/遮挡处理和额外模型依赖，未确定前不能包装成标准分数。

## 2Dto3D：单目视频生成双目视频

- 有配对目标右目GT时，候选验证曲线为PSNR↑、SSIM↑、LPIPS↓；总loss/各分项与学习率单独记录。先核对左右视角、帧对齐、分辨率、颜色范围、SSIM参数及LPIPS网络/权重和输入归一化。
- 明确是left-only还是right-assisted，使用GT深度/相机/右目作为辅助的结果分表。避免把额外输入带来的优势归因于方法本身。
- 全画面指标与遮挡/补全区域指标可分别报告；mask来源必须一致。SSIM/LPIPS等局部或特征指标不能简单把区域外置零后称为区域评分，需明确有效窗口/裁剪或特征mask实现。
- 固定可视化：输入左目、预测右目、GT右目、误差图、遮挡mask；保存左右并排播放和必要的局部放大。没有GT时省去相应面板并标注。
- 视频除逐帧外需看闪烁、结构跳变与左右对应。时序指标需处理真实运动，不能把原始相邻帧差当全部时序质量；首版可先固定视频人工对照，自动分数按论文协议接入。
- 原始预测帧用于评分；预览MP4用于观看。记录fps、帧段、分辨率、推理种子与采样配置，同一topic固定样本后不因结果不好更换。

可查起点：[StereoCrafter官方仓库](https://github.com/TencentARC/StereoCrafter)（任务与论文入口）；[LPIPS官方实现](https://github.com/richzhang/PerceptualSimilarity)（指标实现）。这些链接不代表已核验任意新课题的完整协议。

## 深度估计：先确定尺度语义

- 有数值深度GT时，常见候选为AbsRel↓、RMSE↓、δ1↑；按目标benchmark补SqRel、RMSE-log、SILog或其他指标。δ1常指max(pred/GT, GT/pred)<1.25的有效像素比例，保存时明确是0–1比例还是百分数。
- PSNR/SSIM不是深度主指标的默认替代品，尤其不能对彩色深度预览评分来声称距离准确。序关系标注等无数值GT任务应采用相应benchmark协议，不能强套RMSE。
- 米制深度记录单位；相对深度记录对齐域（depth/disparity）、scale或scale+shift、拟合范围和按帧/片段/数据集对齐方式。用GT对齐后的指标与不对齐的米制结果分开；按帧对齐可能掩盖视频尺度漂移。
- 固定数据划分、裁剪、有效mask、最小/最大深度、插值以及预测截断顺序；零/负/缺失GT与无效预测处理遵从选定协议，记录剔除数量。
- 固定可视化：RGB、预测深度、GT深度、有效区域误差；对比采用一致的范围和色标。原始深度保留精度与单位（如npy/EXR），不只保存8位伪彩图。视频保存固定片段，用统一色标观察边界和时序/尺度漂移。
- 表格至少按数据集/域、方法、输入与对齐方式分组；逐样本指标保留，避免一个均值掩盖近远景或某个域退化。边界/时序指标仅在研究问题需要且定义可核验时补充。

可查起点：[Depth Anything V2指标实现](https://github.com/DepthAnything/Depth-Anything-V2/blob/main/metric_depth/util/metric.py)、[Monodepth2评测](https://github.com/nianticlabs/monodepth2/blob/master/evaluate_depth.py)。其不同尺度与裁剪协议不可混用；应用时固定实际revision。
