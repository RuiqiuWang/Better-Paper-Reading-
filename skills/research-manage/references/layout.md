# 初版文件布局

以下是新建课题的默认布局，不是自动迁移已有目录的命令。只按需要创建非占位文件；未实际安装的环境不得写成已存在。已有仓库无需强制再嵌套一层。

```text
/home/<account>/code/<topic>/
  .git/                           # 本地版本历史，不自动推送
  .gitignore                      # 排除环境、权重、数据、视频、缓存和凭据
  README.md                       # 课题总入口和当前路径导航
  CHANGELOG.md                    # 何时、为何、做了什么及结果
  ours/                           # 自研方法代码
  baselines/<method>/             # 可编辑 baseline checkout
  research/
    methods/<method>.md           # 自研/baseline 方法卡
    EXPERIMENTS.md                # 做过的实验、具体结果与证据入口
    configs/                      # 可复用参数模板
    manifests/                    # 小型清单
    protocols/                    # 正在维护的协议

/data/<topic>/
  README.md                       # 指向权威课题 README
  datasets/<name>/<version>/      # 共享数据集
  baselines/<method>/<revision>/  # 官方权重、原始配置与来源
  models/                         # 共用基础模型
  manifests/                      # 冻结的数据划分
  protocols/                      # 发布的评测协议

/data/<account>/
  envs/<env-id>/                   # 实际环境；不放 home
  env_specs/<env-id>/              # 依赖配方及重建说明
  cache/                          # 可重建缓存
  projects/<topic>/runs/<run-id>/
    README.md                     # 实验目的、经过、结果和证据
    resolved_config.yaml          # 实际运行参数
    checkpoints/                  # 权重/恢复状态
    metrics/                      # 原始指标记录
    predictions/                  # 预测产物
    figures/                      # 曲线及对比图
    logs/                         # 原始运行日志
```

## 位置与身份

- 环境以可辨认的依赖栈/版本命名；说明已验证的 Python/框架版本和环境配方位置，不承诺复制目录就能跨机器恢复。
- 方法 ID 在课题内唯一，自研和 baseline 都有方法卡。官方资源放共享区，个人修改代码放 home。
- run ID 在课题内唯一，可用日期、方法、实验短名和短后缀组成。一次恢复沿用同 run 并记录恢复事件；改变输入、代码或协议形成新实验时使用新 run，注明父 run。
- 课题文档尽量随 Git 管理。跨服务器路径写成“主机别名 + 绝对路径”，不放密码。数据根的入口链接应让目标读者有权访问；权限不足如实写明，不自行放宽。
- 初始化及阶段性本地提交遵循 [本地 Git 规则](local-git.md)。方法的独立 Git 仓库单独提交，父级仅登记路径与版本。
- `research/manifests` 与共享冻结 manifests 不各自维护矛盾副本。发布后在导航中标明权威版本和位置。
- 不要求为空的 checkpoints/metrics 等目录编造文件；例如纯推理没有训练 checkpoint 时注明不适用。

## 读取顺序

课题 README → 相关方法卡或 EXPERIMENTS 索引 → 指定 run README/原始证据。只有询问历史原因时才展开 CHANGELOG。不要每次加载整个课题的所有日志。
