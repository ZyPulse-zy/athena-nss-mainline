# 当前状态

更新：2026-10-04，北京时间。NSS40 延续至 00:00，最新审核和应用观测见 [当前运行记录](../evidence/current-runtime.json)。

**真实 CS2＋Steam 约 323 Mbps 时，初始只读准入 4/94 次通过；随后的写前审核因完整快照过期拒绝。没有开启 NSS，没有进入 A/B/A2。** 见 [NSS40 证据](../evidence/nss40-mainline.json) 与 [94 次时序](../evidence/nss40-admission-timing.json)。

## 当前运行

- 常驻引用仍是 `work/nss39/deployment-latest.json`；配置 `17aaa0797d654938b654d06eaf575ba0766c845aae2a16f8e229998c5992af60`。本轮未改常驻源码、策略或有效期。
- NSS39 保留的 worker 未换实例，守护健康；last-error 仍属于此前试装到期。最终 35/35 次轻载观测健康，配置、规则所有权、认证/PBR/服务审核通过。
- ECM IPv4/IPv6 关闭且连接/加速/待处理全零，无实验 gate/qdisc、暂存、状态节点或事务。没有本轮生产写入，回滚不适用，不能记为一次回滚通过。
- NSS39 的 68 项资格仍有效；NSS40 只重定位本地证据目录/入口，运行时路由器 payload 未变。失败后保存 72 份未变绑定文件。历史证明未覆盖。

## 本轮实测

23:52 的真实只读窗口 9.27 秒：LAN4 322.80 Mbps / 26,712 pps，busy 85.15%、softirq 51.33%、time_squeeze +0。观察程序自身消耗 6.247 CPU 秒；以上包含密集检查成本，不是无干扰基线，也不是 NSS 收益。

应用 socket 归属确认后，所选 CS2 RT UDP 与 Steam bulk TCP 自然位于 WAN5，完整 mark 均为 0x50000、zone 0、同 NAT；adapter 校验了完整实例与双向元组。94 次完整 readiness/phase 检查中，4 次通过（来自 2 个新序列），59 次预学习余量不足、31 次 tag 设置余量不足。最小来源年龄 0.81 秒，最大 adapter/phase 0.20/0.28 秒。初始 <1 秒、预学习 <2 秒未改。

23:52:59 实际入口在 `operational-audit.lua:32` 的完整快照新鲜度断言失败：发布年龄 <9 秒且来源年龄 <6 秒。尚未进入 checkpoint、独立事务或任何 NSS/WAN/队列变更。旧审核器未保存失败时具体年龄与阶段计时；保存 selected pair 的步骤也尚未执行。此前 rehearsal 的元组不能冒充失败瞬间的完整身份记录。

## 补充诊断与未知原因

- 新的 `work/nss40/current-audit-diagnostic.mjs` 保存审核分段时间和拒绝时年龄，所有原断言与固定截止保留；目标机只读集成核验通过。
- `work/nss40/record-candidates.mjs` 按次保存 socket、候选、原始响应和哈希，避免覆盖 latest；已在无游戏时验证。此前尝试的原始应用 latest 后来已刷新，没有把缺失伪装成完整封存。
- 首次带诊断的轻载审核用 0.29 秒通过，来源年龄 2.67 秒；不能用轻载通过解释高负载失败。
- 源码确认 compact classification 先发布，随后同步等待软件维护/审核，最后发布 full snapshot。此顺序使两种发布阶段不同，但**没有证明本次失败由发布、锁等待还是审核耗时造成**。

## 下一步

先把诊断和按次应用封存接入新一轮实际入口并重新绑定。保持所有期限，定位完整快照在高负载审核中的年龄变化，再集中一次单 WAN A/B/A2。无需继续挂机或下载，不扩第二 WAN、共享预算、Wi-Fi 或 autorate。

本轮没有加速后的 bulk/RT leaf、mark/NAT/WAN 或客户端 CS2 jitter/loss/Miss 数据；高负载 NSS CPU 收益与真人闭环仍未通过。[NSS39 修复与部署资格](../evidence/nss39-mainline.json)、[历史已知问题](KNOWN_FAILURES.md) 保留。
