# 证据索引

## 当前NSS82

- [实测汇总](../evidence/nss82-mainline.json)、[五次现场/失败保留](../evidence/nss82-trials.json)、[18Mbps可比对照](../evidence/nss82-matched18.json)、[32Mbps拥塞观察](../evidence/nss82-saturated32.json)。
- [计数偏差与重读](../evidence/nss82-tag-reader.json)、[终态原完整审核](../evidence/nss82-final-audit.json)、[端点独立恢复](../evidence/nss82-endpoint-closure.json)、[新源字节冻结](../evidence/nss82-source-proof.json)。
- [当前运行](../evidence/current-runtime.json)、[旧78 runtime原字节](../evidence/nss78-runtime.json)；本地报告`outputs/nss82-mainline-report.html`。

# 证据索引

## 当前NSS78

- [只读时序诊断](../evidence/nss78-mainline.json)、[终态审核](../evidence/nss78-final-audit.json)、[新增源码](../evidence/nss78-source-proof.json)。
- [当前运行](../evidence/current-runtime.json)、[原77 runtime原字节](../evidence/nss77-runtime.json)。入口保持77；轻载诊断不授予准入。

## 当前NSS77

- [实测轮次](../evidence/nss77-mainline.json)、[终态审核](../evidence/nss77-final-audit.json)、[新源冻结](../evidence/nss77-source-proof.json)。
- [当前运行](../evidence/current-runtime.json)、[NSS68 runtime原字节](../evidence/nss68-runtime.json)。

## 当前：NSS68

- [实际保留与自然恢复记录](../evidence/nss68-mainline.json)、[当前运行](../evidence/current-runtime.json)、[终态原审核](../evidence/nss68-final-audit.json)。
- [257项入口绑定](../evidence/nss68-entry-binding.json)、[23份白名单源码](../evidence/nss68-source-proof.json)、[接续位置](PUBLICATION_ENTRY_HANDOFF.md)。
- [NSS67 runtime原字节](../evidence/nss67-runtime.json)保持。新入口和保留已完成，真实高负载NSS A/B/A2尚未完成。

## 当前主线：NSS63

- [本轮汇总](../evidence/nss63-mainline.json)、[当前运行](../evidence/current-runtime.json)：常驻47、最终ECM关闭全零；5暂存全部撤销。
- [12真实案例](../evidence/nss63-attempts.json)：5 checkpoint/独立45秒恢复，只有56打开ECM；62本地导入失败另记。
- [NSS56实际A+B](../evidence/nss63-partial56.json)、[实际HUD](../evidence/nss63-client56.json)：ECM0→2→0，WAN1/mark/NAT和leaf正确；A2缺失、304/262Mbps不匹配、无真人体验，不称收益。
- [241项最新绑定](../evidence/nss63-entry-binding.json)、[最新源码](../evidence/nss63-source-proof.json)、[离线证据修正](../evidence/nss63-source-proof-v2.json)；全实际输入/配置/截图留私有，源码冻结不授予额外权限。
- [终态审核](../evidence/nss63-final-audit.json)、[终态清理](../evidence/nss63-final-cleanup.json)、[下载完成状态](../evidence/nss63-steam-ended.json)。本地报告`outputs/nss63-mainline-report.html`。
- [NSS53原runtime](../evidence/nss53-runtime.json)原字节保留；[失败定位](ISSUE_NSS63_MAINLINE.md)明确已修和仍未修的边界，没有上游提交。

## NSS53 历史

- [当前汇总](../evidence/nss53-mainline.json)、[运行核验](../evidence/current-runtime.json)：常驻NSS47未变、ECM关闭全零，本轮仅只读。
- [真实下载发现时序](../evidence/nss53-phase-load.json)：两组三次6/6通过，294–366Mbps，原200ms条件保持；CPU/softirq/squeeze含profiler成本，不是NSS A/B。
- [拒绝帧诊断](../evidence/nss53-diagnostics.json)：60本地断言/14原生helper与两次实际只读ready分开；投影缺失未知、严格同源完整帧，不改变权限。
- [159项新入口](../evidence/nss53-entry-binding.json)、[24份源码冻结](../evidence/nss53-source-proof.json)、[Steam负载结束状态](../evidence/nss53-steam-load.json)。当前入口`work/nss53/real-session.mjs`，报告`outputs/nss53-mainline-report.html`。
- [NSS52原runtime](../evidence/nss52-runtime.json)按原字节保留，[历史汇总](../evidence/nss52-mainline.json)与[NSS49原生功能](../evidence/nss49-actual-aba.json)保持原义。
- [进程发现问题](ISSUE_CORE_SLEEP_DISCOVERY.md)、[准入投影诊断问题](ISSUE_ADMISSION_PROJECTION.md)为私有控制器backlog，未提交上游。

## NSS49 历史功能

- [实际完整对照](../evidence/nss49-actual-aba.json)：WAN2真实CS2/Steam、0→2→0、leaf/mark/NAT/affinity与精确恢复成功；吞吐不匹配、没有B段HUD，CPU/真人收益未通过。
- [当前汇总](../evidence/nss49-mainline.json) 与 [当前运行](../evidence/current-runtime.json)：常驻NSS47纯地址缓存＋NSS46可靠性修复，当前ECM关闭。
- [新入口](../evidence/nss49-entry-binding.json)、[原失败](../evidence/nss49-failed-attempts.json)、[客户端边界](../evidence/nss49-client-boundaries.json)、[13个原生RAM案例](../evidence/nss49-native-aba-cases.json)。
- [NSS47源码冻结](../evidence/nss47-source-proof.json)、[NSS48冻结](../evidence/nss48-source-proof.json)、[NSS49冻结](../evidence/nss49-source-proof.json)：分别19/37/47份可读源码；实际完整来源/连接/备份留本地。
- 私有工作区当前部署 `work/nss47/deployment-latest.json`，当前入口 `work/nss49/real-session.mjs`，成功目录 `work/nss49/real-matched-aba-20261004065238-cdfa8d7a/`；报告 `outputs/nss49-mainline-report.html`。

以下更旧条目是各轮当时记录，出现“当前/最新”时按该轮日期理解，不替代上述来源。

仓库内可直接核对：

- `evidence/nss46-mainline.json`：三项修复逐项保留、真实 apply/worker crash 恢复、两个独立自然到期恢复、新入口 112 项绑定及最终保护核验。
- `evidence/nss46-fault-timing.json`：真实来源过期时两个发布撤回、intent 清零与同实例接续的相对时序，无流端点。
- `evidence/nss46-entry-binding.json`：新的当前配置来源、原门槛和默认拒绝入口范围；不是本轮真人 fast path 证明。
- `evidence/nss45-runtime.json`：保存原 NSS45 现网快照；`current-runtime.json` 已指向 NSS46，旧历史断言不再错误比较当前源码。

- `evidence/nss45-mainline.json`：两次独立轻载试装/自然到期恢复、114 个独立本地案例、目标 RAM/真实 query 子进程证明与未验证边界。
- `evidence/nss45-trial-timing.json`：两组各 35 帧相对时间和自然轻载指标，不能组成转发 A/B。
- `evidence/nss45-query-cleanup.json`：7 个真实 native 子进程的合成查询输出与实际回收证明，无生产规则变更。
- `evidence/nss45-recovery-benchmark.json`：三对空日志只读恢复测量，写回调拒绝；不证明高负载或整机 CPU 收益。
- `docs/ISSUE_CLASSIFIER_RECOVERY.md`：行数边界、重复初始枚举、未安装软件过期候选及真实应用子进程缺失证明。

- `evidence/nss44-mainline.json`：真实 WAN1 写前拒绝、102 份原入口冻结、自然重启/首次恢复失败、未安装候选与最终保护核验。
- `evidence/nss44-failed-admission-timing.json`：实际失败的 39 帧相对年龄/发布时间，无端点；不是模拟或 NSS 阶段。
- `evidence/nss44-publication-timing.json`：随后独立自然轻载窗口的发布时序；未确认真人连接对，不能作为高负载 A/B。
- `docs/ISSUE_CLASSIFIER_PUBLICATION.md`：本地发布等待/分类器恢复问题，现象与根因证明范围分开，未上游提交。
- `evidence/nss43-mainline.json`、`nss43-load-profile.json`：48 秒 Steam-only 负载与单 TCP 份额，不是真人闭环。

- `evidence/nss41-mainline.json`：真人WAN1功能、原控制器错误、重新校验、三段测量与恢复证据；性能/游戏结论未通过。
- `evidence/nss41-load-publication.json`：有限普通TCP下载的104帧脱敏完整/精简年龄；不是游戏或NSS性能。
- `docs/ISSUE_ECM_WAN_VALIDATOR.md`：本地WAN5写死与依赖绑定缺口，未上游提交。

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
- `evidence/nss42-mainline.json`：通用 WAN 后处理/审核用途/102 项绑定、90 项本地＋4 项目标 RAM 检查、600 秒自然轻载只读观察与功能/性能边界。
- `evidence/nss42-stability-timing.json`：21 次相对采样时序，已去除 producer、原始 flow 与系统转储。
- `evidence/current-runtime.json`：最新 NSS44 最终审核/自然重启摘要与 NSS39 部署哈希；读取者仍应重新核验现网。
- `source-manifest.json`：每个源码副本的原路径、SHA256、大小；部署源文件必须与当前配置记录的哈希一致。

仅在完整私有工作区：

| 路径 | 用途 |
| --- | --- |
| `outputs/nss32-matched-aba-report.html` | 历史受控低负载完整 A/B/A2 |
| `outputs/nss33-classifier-readiness-report.html` | 上一轮完整报告 |
| `work/nss39/deployment-latest.json` | 当前常驻分类器部署引用 |
| `outputs/nss45-mainline-report.html` | 最新分类器恢复、两项轻载试装、独立到期回滚、未安装软件过期候选与结论边界 |
| `work/nss45/source-frozen/` | 53 份源码冻结；不是 NSS 生产入口资格 |
| `work/nss45/backend-trial/`、`row-trial/` | 两次短时试装及 checkpoint/180 秒独立到期恢复私有证据；两者均未长期保留 |
| `outputs/nss44-mainline-report.html` | 最新真人写前拒绝、自然重启、只读候选和结论边界报告 |
| `work/nss42/real-matched-aba-20261004023857-0c4f4549/` | NSS44 实际失败、102 份原入口冻结与完整私有应用归属证据；没有生产写入 |
| `work/nss44/readonly-frozen/` | 16 份只读/未安装候选源码冻结；不是新的生产准入资格 |
| `work/nss39/affinity-qualified.json` | 当前 68 项绑定；未完成真人闭环 |
| `outputs/nss42-mainline-report.html` | 最新验收入口修复、声明依赖绑定、自然轻载观察与下一步报告 |
| `work/nss42/entry-qualified.json` | 最新 v2 的 102 项输入、五份本地检查证明和外部连接源码哈希；不是完整运行环境保证 |
| `work/nss42/v1-frozen/`、`v2-frozen/` | 99/102 项输入分别冻结，私有状态和连接封装不导出 |
| `outputs/nss41-mainline-report.html` | 历史真人 WAN1 bulk/RT 功能、三段测量、原错误和恢复报告 |
| `work/nss41/real-matched-aba-20261003165708-9086b676/` | 真实实验、83项冻结与后处理校验冻结，完整私有证据 |
| `outputs/nss40-mainline-report.html` | 历史真实只读准入、写前审核拒绝与取证报告 |
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

## NSS64

- [本轮只读/候选](../evidence/nss64-mainline.json)、[完整编码](../evidence/nss64-encoding.json)、[编码规模](../evidence/nss64-scale.json)、[被动发布链路](../evidence/nss64-pipeline.json)。
- [原NSS63拒绝拆分](../evidence/nss64-latency.json)、[精确编译](../evidence/nss64-compile.json)、[最终原审核](../evidence/nss64-final-audit.json)、[20份冻结源](../evidence/nss64-source-proof.json)。
- [publication候选worker](../code/work/nss64/candidate-worker.lua)，未安装/未授予准入；[潜在Issue](ISSUE_JSON_PUBLICATION_COST.md) 未提交。
- 本地 `outputs/nss64-mainline-report.html` / `work/nss64/` 保存报告与完整私有证据；原始连接、配置和截图不上传。

## NSS65：现场publication试装与独立自然恢复

- [主线结果](../evidence/nss65-mainline.json)、[自然窗口](../evidence/nss65-pipeline.json)、[恢复后审核](../evidence/nss65-final-audit.json)、[8份白名单源](../evidence/nss65-source-proof.json)。
- [单项试装](../code/work/nss65/publication-trial.mjs)、[独立自然恢复核验](../code/work/nss65/verify-rollback.mjs)。候选没有留驻，也没有新NSS入口绑定或高负载/游戏收益。
- 本地 `outputs/nss65-mainline-report.html` / `work/nss65/` 保留报告与完整私有checkpoint/config/owner/实际输入；未上传。

## NSS66–67：真实下载发布、独立精确恢复和入口接续

- [NSS66实测](../evidence/nss66-mainline.json)、[NSS67实测](../evidence/nss67-mainline.json)、[300Mbps以上窗口](../evidence/nss67-pipeline.json)、[最终审核](../evidence/nss67-final-audit.json)。
- [10份NSS66源码](../evidence/nss66-source-proof.json)、[12份NSS67源码](../evidence/nss67-source-proof.json)、[保留的NSS65 runtime](../evidence/nss65-runtime.json)、[NSS66 runtime](../evidence/nss66-runtime.json)。
- [单项试装](../code/work/nss67/publication-trial.mjs)、[精确独立恢复](../code/work/nss67/verify-rollback.mjs)、[入口接续的三个来源位置](PUBLICATION_ENTRY_HANDOFF.md)。
- 本地 `outputs/nss67-mainline-report.html` 与 `work/nss66/`、`work/nss67/` 保存完整私有资料；配置/checkpoint/owner/CT/socket/截图未上传。本轮没有新NSS入口资格或真人/CPU验收。
