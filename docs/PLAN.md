# 下一步：稳定分类器，再完成单 WAN NSS 闭环

唯一主线：自动游戏分类 → NSS RT/bulk leaf → 真人 CS2 + Steam。NSS38 真实 WAN2 尝试止于初始时间门槛；常驻 worker 后来又因队列读取返回 143 自动重启。两项均未解决，当前恢复健康不等于长期通过。

1. **先读当前状态。** 常驻引用仍为 `work/nss37/deployment-latest.json`。新轮次目录核验哈希、worker/guardian、last-error、认证/PBR/服务、ECM 全零与上次清理。历史 70 份 NSS38 试验快照保持冻结。
2. **定位队列读取失败与安全恢复。** 日志已确定 `/sbin/tc -j qdisc show dev rpwan1` 的 2 秒 wrapper 返回 143，发生于 apply 中的只读队列检查；尚无阻塞栈或信号来源。后续 8 次查询正常。先设计可离线复现的超时/半截输出及外层子进程取消模型，区分只读阶段与已有写入阶段；只有能证明整个子进程清理、撤回候选、精确恢复自有规则后才考虑原地重采样。未知状态继续终止，禁止吞错、复用旧状态或直接增加超时。这里是分类器生命周期修复，不扩展 CAKE 策略优化。
3. **资格核验 NSS38 未安装候选。** `candidate-classifier.lua` 已证明重复检查可减少；带诊断版本为 `candidate-traced-classifier.lua` 与 `candidate-traced-fast-path.lua`。本地决策/时序检查与目标语法通过，但全套当前部署绑定、tag policy roundtrip 和相关目标 RAM 生命周期尚未完成。新轮次构建，不改 NSS37 或冻结试验的源码/证明。
4. **只读验收完整准入循环。** 记录每次来源序号、query/publication age、phase 与 adapter 用时、完整拒绝原因及观察程序开销。只读阶段通过与实际准备后通过不能混为一谈。保留 <1 秒初始窗口、<2 秒学习余量及原独立截止，不以放宽有效期获得通过。没有自然流量时先完成资格，不反复要求用户下载。
5. **再集中一次真人同 WAN 尝试。** 重新核对 Steam TCP 与 CS2 UDP 的当前应用归属、CT ID/zone/双向 tuple、完整 mark、NAT/WAN。先 checkpoint、独立超时恢复，再单 WAN/单连接对。证明预学习 tag、bulk/RT leaf、accelerated_count、WAN affinity、精确撤销；通过后才解释 software → NSS → software 性能。现有 20 Mbps 子组不代表全部 300 Mbps 以上下载均加速。
6. **通过主线后才扩展。** 第二 WAN、共享预算、Wi-Fi、autorate、五 WAN 与其它 qdisc 支线等待。没有客户端指标就标记 CS2 jitter/loss/Miss 未测，不用 ICMP 或合成 UDP 代替。

目前不需要用户持续挂游戏或下载。不承诺未安排的后台运行。每轮保留假设、唯一主变量、负载、ECM/leaf、mark/NAT/WAN、时序与观察成本、softirq/time_squeeze/吞吐、客户端数据来源以及恢复结果。
