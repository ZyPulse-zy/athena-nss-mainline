# 下一步：同一 WAN 的性能与游戏验收

唯一主线：自动游戏分类 → NSS bulk/RT leaf → 真人 CS2＋Steam 单 WAN。

NSS41 已证明真人功能路径，尚未证明固定高负载收益或低延迟游戏体验。原控制器失败保留；不要重跑冻结入口或把重新校验冒充原控制器通过。

1. **先核验现网。** 常驻引用仍是 `work/nss39/deployment-latest.json`。读取 worker/guardian、配置、旧错误归属、生产队列、ECM 全零与实验清理。新目录接续，保持 NSS40/NSS41 冻结证明。
2. **修正本地验收入口并绑定。** 用 NSS41 的通用 WAN 解析器按选中 flow 的 WAN 校验，加入后处理及其依赖哈希，审计整个实际入口的依赖清单。实际 WAN1 冻结数据与 mark/NAT/tag/模式错误副本已检查，不需要为这个修复反复游戏。已冻结的 NSS41 `real-session.mjs` 仍引用旧 WAN5 后处理，不能原样再用。
3. **恢复审核使用原完整断言。** 学习前的锁外调度仍需严格新序列及原 TTL；恢复已关闭 ECM 后使用原 <6/<9 秒完整审核，不再把学习前 source age <2 秒条件套到闭合验收。保留 fixed deadlines，未知读取/恢复拒绝。锁外等待失败应封存每次观察年龄与序号，本次该失败只有错误与总时间，不能伪装成完整逐帧原因。
4. **设计单 WAN 的有效对照。** 当前只加速 1 TCP＋1 UDP、20 Mbps 子组，整机其余 300+ Mbps 不受控。先确定稳定下载负载和受控流量份额，选一个主要变量；不要凭 global busy 微小变化推算收益。仍保持新连接 Linux PBR、完整 ct mark、NAT 与原 WAN；没有理由要求用户常驻游戏或反复下载。
5. **集中真人对照。** 新鲜应用 socket/CT 实例/完整元组/mark/NAT 匹配、全审核通过，才新建 checkpoint 并先验证独立恢复。保持默认拒绝、精准放行、learning 前 tag、精确撤销、相同 QoS 预算与观察循环。记录 bulk/RT leaf、软中断、time_squeeze、pps 和吞吐；客户端 jitter/loss/Miss 或体感没有取得就明确未测。观察时间从路由器 uptime 校准，不能错配窗口。
6. **全部验收后才扩展。** 第二 WAN、共享预算、Wi-Fi、autorate、五 WAN 与其它 qdisc 支线继续等待。CAKE 保留软件基线/fallback，不转回长期优化主线。

所有新的生产写入都需要本次 checkpoint 和独立于控制连接的超时恢复。NSS41 提前恢复完成，不冒充再次触发到期。不得刷机/升级内核/改分区/全清 conntrack/重建全部生产 qdisc，保护认证/PBR/sing-box/Tailscale。无上游提交；本地后处理问题见 [校验缺陷记录](ISSUE_ECM_WAN_VALIDATOR.md)。
