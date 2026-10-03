# 当前主线阻塞与本地修复

## LOCAL-ADDR-001：地址查询失败导致分类器自动重启

状态：NSS35 已安装有界故障恢复修复，独立回滚验收通过；底层阻塞/信号原因未定，未提交上游。

- 历史部署：NSS33，代码保留在 `code/work/nss33/worker.lua`。
- 原现场日志：2026-10-03 15:54:43、16:00:11（北京时间），2 秒 timeout 包裹的 `/sbin/ip -j -4 address show` 最新保存返回码 143、输出为半截 JSON。
- 原处理：`direct()` 非零断言 → 地址发现失败 → watch 退出 → procd 重启，producer 与分类历史变化。
- 原查询随后 8 次只读调用约 10 ms 成功；没有失败当时的内核栈或信号来源，不能断言 RTNL/CPU 是根因。
- 修复：原命令仍限定 2 秒，由既有 group runner 清理整个子进程组；仅确认清理后才发布无候选 degraded、恢复自有软件规则并重采样。未确认清理和未知异常仍终止。Guardian 没有接受携带旧 snapshot、未恢复或过期的 degraded 状态。
- 最小可回放：`tools/replay_classifier_recovery.py` 覆盖返回码、半截 JSON、无候选发布、守护拒绝、未知子进程状态；`code/work/nss35/test-query-native.mjs` 的目标内存 fixture 覆盖真实超时和派生子进程回收，依赖私有连接封装，不能直接作为通用部署脚本运行。
- 修改前后证据：历史两次 respawn；新逻辑 136 项分层检查、两个 35 次健康轻负载窗口、一次真实 180 秒自动回滚与重新部署。并未给生产常驻进程注入地址失败，也未自然重现原始阻塞；不宣称已证明高负载/长期稳定。

这是本工作区分类器的本地恢复问题，尚无证据把它写成 NSS/ECM 上游驱动缺陷。继续保留为研究记录，未经最小复现和归因不提交上游 Issue/PR。

## LOCAL-ADMISSION-001：通用超时文案掩盖具体准入原因

状态：NSS36 精确拒绝处理已通过 212 项准入检查；新真实尝试记录 44 次时间余量拒绝。NSS33 历史失败仍不回溯归因为同一原因。

- 缺少所选 RT 候选、来源过旧，均可能最终报 `Insufficient fresh-classifier margin for complete ABA`。
- 原失败没有逐次拒绝记录。不能从这一句推断 CPU 性能不足。
- NSS36 保留 `initialAlignment.probes`，记录时间、结果、原因与 retryable。只有三种精确的本地时间余量失败可以重试；所选身份/类别先核验，其它错误立即结束这次尝试。
- 108 组新旧差分和 66 历史包络保持准入结果相同；完整 212 项回放入口为 `tools/replay_mainline_admission.py`。代码见 `code/work/nss36/classifier.lua` 与 `fast-path.lua`。
- 有效期、独立截止和默认拒绝规则均未放宽；没有本轮新的 fast path 验收。

## LOCAL-PUBLICATION-001：采集/分类发布时间挤占初始准入窗口

状态：仍缺真人高负载闭环验收；NSS37 已安装等价属性解析优化，目标内存证明解析 CPU 成本下降，不属于已证实的上游 NSS 缺陷。

- 最小现场证据：NSS36 真实同 WAN CS2 UDP + Steam TCP，初始约 5.93 秒中 44 次时间拒绝，gate/ECM 均未开启；WAN/队列独立恢复。
- `classifier.lua` 的 pair 学习屏障要求 query age <2 秒，ready 再预留 tag 设置时间而要求 <1 秒。没有改变这些边界。
- 后续独立只读窗口 publication delay 0.77–1.21 秒、完整检查最高 0.26 秒；所选游戏已不在候选，不能把该窗口当原失败完整重放。
- `conntrack-source.lua` 的 normalize 与 `classifier-core.lua` 的行解析是已测到的开销：单次目标 RAM 分解为 0.55 / 0.28 秒，另有真实查询 0.28 秒。样本 455 行，未优化版本，未跟踪生产 worker 的全部阶段。
- worker 同步 fallback 规则维护和审计可能延长采样间隔，但没有阶段计时证明它解释了每次长间隔。结束审计一次来源过旧、随后通过，producer 未变。
- NSS37 的最小代码改动为 `code/work/nss37/conntrack-source.lua / attrs()`，基线在同目录 `original-conntrack-source.lua`。`tools/replay_normalizer.py` 可独立执行 9,085 项合成输入检查；私有真实采集文本另增加 2 项，总 9,087。两版本在本地 Lua 5.1 对相同输入做输出及拒绝比较，不连接路由器。
- 目标机 16 对内存交替测量中，204 行真实文本 CPU 平均 27.043 → 15.470 ms，512 行合成文本 64.393 → 38.408 ms，全部输出相等。180 秒独立回滚验证后重新部署保留；详见 `evidence/nss37-normalizer.json`。
- 这是本地分类器性能优化，只证明该解析函数的成本。NSS36 高负载 0.55 秒与 NSS37 轻负载毫秒值不能直接相减；没有完成相同高负载的全发布路径比较。同步软件维护是否拖长周期仍是待验证假设。
- 下一步只读验证高负载新鲜度与入口余量；不得丢字段、缩小范围、延长 TTL 或改时间基准绕过问题。没有驱动级最小复现，不提交上游 Issue/PR。
