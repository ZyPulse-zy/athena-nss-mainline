# 证据索引

仓库内可直接核对：

- `evidence/nss33-summary.json`：关键量化结果、试验退出位置、回滚和结论范围。
- `evidence/nss33-admission-timing.json`：66 个已脱敏的时序样本，仅保留相对时间、年龄、原因、候选存在性；不是完整包捕获。
- `evidence/nss34-loop-profile.json`：只读循环的汇总与相对时间分解；不含流元组。
- `evidence/nss34-admission-replay.json`：87 项离线检查，身份/IO 为模拟，真实时间包络 66 条；硬件验收明确为 false。
- `evidence/nss34-classifier-restarts.json`：两次自动重启触发时间、地址查询返回码、随后只读复查；不含原始进程和连接记录。
- `evidence/nss35-address-recovery.json`：136 项分层检查、轻负载指标、独立回滚和常驻部署，明确未证明事项。
- `evidence/nss36-mainline.json`：299 项准备检查、真实 WAN1 失败、44 次拒绝、回滚、407.82 Mbps 软件诊断、目标内存成本分解与限制。
- `evidence/nss36-admission-replay.json`：212 项当前准入检查，108 新旧差分，66 历史包络；不等于硬件验收。
- `evidence/nss36-admission-timing.json`：失败后独立只读窗口的 58 条相对时序；当时所选游戏已不在候选，不能当原失败全过程。
- `evidence/nss37-normalizer.json`：9,113 项新本地检查、16 对目标 RAM 解析测量、三组轻负载观测、两次安装/实际独立回滚/提交和最新控制器绑定；明确没有本轮 fast path 尝试。
- `evidence/current-runtime.json`：最新审核摘要与部署哈希；读取者仍应重新核验现网。
- `source-manifest.json`：每个源码副本的原路径、SHA256、大小；部署源文件必须与当前配置记录的哈希一致。

仅在完整私有工作区：

| 路径 | 用途 |
| --- | --- |
| `outputs/nss32-matched-aba-report.html` | 历史受控低负载完整 A/B/A2 |
| `outputs/nss33-classifier-readiness-report.html` | 上一轮完整报告 |
| `work/nss37/deployment-latest.json` | 当前常驻分类器部署引用 |
| `work/nss35/deployment-latest.json` | 历史地址恢复部署，NSS36 证明仍绑定它 |
| `work/nss35/address-trial-qualified.json` | 试装修复与 180 秒独立到期回滚 |
| `outputs/nss35-address-recovery-report.html` | 上轮分类器恢复报告 |
| `outputs/nss36-admission-timing-report.html` | 历史真实准入失败与时序定位报告 |
| `outputs/nss37-normalizer-report.html` | 本轮等价属性解析、独立回滚与保留报告 |
| `work/nss37/normalizer-trial-qualified.json` | 第一次安装、180 秒独立自动恢复旧解析器/配置的证据 |
| `work/nss37/affinity-qualified.json` | 当前新配置绑定与 66 项清单；未完成真人高负载验收 |
| `work/nss36/real-matched-aba-20261003091409-28454bad/` | 真实 WAN1 尝试、独立回滚、59 份冻结源文件、完整私有证据 |
| `work/nss36/affinity-qualified.json` | 绑定 NSS35 的候选 source manifest；准备通过不代表真人闭环通过 |
| `work/nss33/compact-trial-qualified.json` | 分类发布语义与独立 180 秒回滚 |
| `work/nss33/real-matched-aba-20261003071100-604d4fe1/` | 实际失败与回滚、冻结源码、完整私有原始证据 |
| `work/nss33/admission-rehearsal-20261003071535-private.json` | 66 个准入检查原始样本 |
| `work/nss34/` | 历史只读定位与 GitHub 建仓记录 |
| `work/nss35/` | 历史恢复逻辑、测试与部署完整私有证据 |
| `work/nss37/` | 当前解析优化、测试、部署与完整私有证据；原始连接/配置/检查点不上传 |

旧 NSS35/NSS33/NSS30/NSS29/NSS28 部署别名仍用于历史证明，不能用来覆盖当前常驻分类器状态。
