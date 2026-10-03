# 证据索引

仓库内可直接核对：

- `evidence/nss40-mainline.json`：323 Mbps 真实只读准入、写前拒绝、无生产写入、取证改进及结论边界。
- `evidence/nss40-admission-timing.json`：94 条相对时序、来源序号、年龄与阶段耗时，无连接元组。

- `evidence/nss39-mainline.json`：tc 监督复现/修复、四次安装/三次独立回滚、冷启动拒绝、保留实例、68 项控制器绑定与证据限制。

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
- `evidence/nss38-mainline.json`：真实 WAN2 32 次拒绝与独立恢复、两个独立软件高负载窗口、准入候选/目标内存开销、22:27 队列读取故障与自动恢复；常驻仍 NSS37。
- `evidence/nss38-loop-timing.json`：失败后 105 次只读诊断相对时序；所选类别不再准入，不能当原失败重放。
- `evidence/nss38-adapter-differential.json`、`nss38-admission-replay.json`：带诊断未安装候选的 1,470 决策对照、5 次数约束、230 准入/诊断案例。
- `evidence/nss38-native-syntax.json`：两个候选的目标 Lua 编译，明确未执行/未绑定控制器。
- `evidence/current-runtime.json`：最新审核摘要与部署哈希；读取者仍应重新核验现网。
- `source-manifest.json`：每个源码副本的原路径、SHA256、大小；部署源文件必须与当前配置记录的哈希一致。

仅在完整私有工作区：

| 路径 | 用途 |
| --- | --- |
| `outputs/nss32-matched-aba-report.html` | 历史受控低负载完整 A/B/A2 |
| `outputs/nss33-classifier-readiness-report.html` | 上一轮完整报告 |
| `work/nss39/deployment-latest.json` | 当前常驻分类器部署引用 |
| `work/nss39/affinity-qualified.json` | 当前 68 项绑定；未完成真人闭环 |
| `outputs/nss40-mainline-report.html` | 最新真实只读准入、写前审核拒绝与取证报告 |
| `work/nss40/real-matched-aba-20261003155259-d8910c25/` | 写前失败和 72 份冻结源码/证明，未改生产 |
| `work/nss40/current-audit-diagnostic.mjs` | 全部原断言保留的分段诊断入口，已只读核验 |
| `work/nss40/record-candidates.mjs` | 按次应用 socket/候选证据封存，原始数据不上 Git |
| `outputs/nss39-mainline-report.html` | 常驻修复、回滚和准入资格历史报告 |
| `work/nss37/deployment-latest.json` | 历史 NSS37 解析器部署引用 |
| `work/nss35/deployment-latest.json` | 历史地址恢复部署，NSS36 证明仍绑定它 |
| `work/nss35/address-trial-qualified.json` | 试装修复与 180 秒独立到期回滚 |
| `outputs/nss35-address-recovery-report.html` | 上轮分类器恢复报告 |
| `outputs/nss36-admission-timing-report.html` | 历史真实准入失败与时序定位报告 |
| `outputs/nss37-normalizer-report.html` | 本轮等价属性解析、独立回滚与保留报告 |
| `outputs/nss38-mainline-report.html` | 本轮真人准入、未安装候选、自然重启与结论边界 |
| `work/nss38/real-matched-aba-20261003141133-251d83e6/` | 实际 WAN2 失败、回滚与 70 份冻结源码/证明 |
| `work/nss38/candidate-traced-classifier.lua` | 带时序诊断的未安装准入候选；不能直接视为当前控制器 |
| `work/nss37/normalizer-trial-qualified.json` | 第一次安装、180 秒独立自动恢复旧解析器/配置的证据 |
| `work/nss37/affinity-qualified.json` | 历史 NSS37 配置绑定与 66 项清单；未完成真人高负载验收 |
| `work/nss36/real-matched-aba-20261003091409-28454bad/` | 真实 WAN1 尝试、独立回滚、59 份冻结源文件、完整私有证据 |
| `work/nss36/affinity-qualified.json` | 绑定 NSS35 的候选 source manifest；准备通过不代表真人闭环通过 |
| `work/nss33/compact-trial-qualified.json` | 分类发布语义与独立 180 秒回滚 |
| `work/nss33/real-matched-aba-20261003071100-604d4fe1/` | 实际失败与回滚、冻结源码、完整私有原始证据 |
| `work/nss33/admission-rehearsal-20261003071535-private.json` | 66 个准入检查原始样本 |
| `work/nss34/` | 历史只读定位与 GitHub 建仓记录 |
| `work/nss35/` | 历史恢复逻辑、测试与部署完整私有证据 |
| `work/nss37/` | 历史解析优化、测试、部署与完整私有证据；原始连接/配置/检查点不上传 |
| `work/nss38/` | 本轮源码、候选、日志与完整私有证据；原始连接、配置、检查点和模块不上传 |

旧 NSS35/NSS33/NSS30/NSS29/NSS28 部署别名仍用于历史证明，不能用来覆盖当前常驻分类器状态。
