# 当前主线阻塞

## LOCAL-ADDR-001：地址查询失败导致分类器自动重启

状态：已确认两次失败与恢复；阻塞/信号的底层原因未定。未修改现网代码，未提交上游。

- 部署：NSS33 常驻 worker，哈希见 `STATE.md`。
- 现场日志：2026-10-03 15:54:43、16:00:11（北京时间）。
- 命令：`/usr/bin/timeout -k 1 2 /bin/sh -c '/sbin/ip -j -4 address show'`。
- 最新保存的返回码：143。没有当时的内核栈或进程信号记录，因此不能把所有可能原因都排除后宣称是 RTNL/CPU 故障。
- 路径：`code/deployed-classifier/worker.lua` 的 `direct()` 非零状态断言 → `classifier-core.lua` 的地址发现 → 主循环退出 → procd 重启。
- 影响：重新生成 producer 实例，重置分类历史；NSS consumer 必须拒绝旧实例。常驻并最终健康不等于连续稳定。
- 当前：16:03 快照中新 worker 和 guardian 健康；ECM 仍关闭。随后 8 次同命令查询均约 10 ms、RC 0，没有重现阻塞。

下一步最小验证：先在离线 fixture 中注入该返回码与输出边界，验证不使用旧 WAN 地址、不保留有效 NSS 候选、有限恢复和 guardian 协作；弄清超时子进程是否完全退出。任何现场修复须新 checkpoint 和独立回滚，不能直接加长 timeout 或忽略返回码。

## LOCAL-ADMISSION-001：通用超时文案掩盖具体准入原因

状态：87 项离线检查通过，诊断候选已准备，真实失败根因仍未确定。

- 缺少所选 RT 候选、来源过旧，均可能最终报 `Insufficient fresh-classifier margin for complete ABA`。
- 原失败没有逐次拒绝记录。不能从这一句推断 CPU 性能不足。
- 当前候选保留 `initialAlignment.probes`，其中记录每次时间、布尔结果、具体原因。回放已验证这能显示内部候选拒绝。
- 有效期、独立截止和默认拒绝规则均未放宽；没有本轮新的 fast path 验收。
