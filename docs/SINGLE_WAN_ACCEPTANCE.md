# 一次集中真人验收

准备已完成时才请求一次 CS2 对局＋Steam 下载。用户不用持续挂机，也不必反复下载。NSS43 已完成下载连接的只读负载分析；不再用同样的准备观察占用用户时间。

NSS44 已使用真实连接对运行原入口，但完整发布时延使写前调度拒绝，随后分类器自然退出/首次恢复失败。当前先完成 [发布与恢复问题](ISSUE_CLASSIFIER_PUBLICATION.md) 的资格核验；下面仍是未来验收条件，不能用 NSS44 只读候选直接启动生产，也不要让用户重开游戏反复碰门槛。

NSS45 两项修复的轻载试装和独立自然恢复已通过，软件过期候选仍未安装、尚缺真实 apply 子进程及完整服务故障恢复，见 [恢复问题记录](ISSUE_CLASSIFIER_RECOVERY.md)。这两次试装、114 个本地案例和目标 RAM/7 个 query 子进程案例均不能代替下面的真人验收。准备期间无需开游戏或下载。

## 固定范围

- 常驻仍 NSS39，原 NSS42 102 项入口冻结不变；新的修改须另建轮次并重新绑定/资格核验。20 Mbps、单 WAN、一条 Steam TCP＋一条 CS2 UDP、原学习/持锁/owner 时限保持。
- 原选择策略已经在相同游戏 WAN 内优先较大的 bulk 候选，不把这件事重复算作新优化。不能改已有连接 WAN 或让 NSS 重新负载均衡。
- 不额外放行其它 TCP/UDP，不提高预算，不以任何观察比较条件代替原身份、来源年龄、tag、owner、checkpoint 检查。
- 所有生产变更仍在本次 checkpoint 下载/哈希验证、独立 owner 已运行之后。精确撤销与全部受保护基线恢复必须单独记录。

## 在同一对局和下载中记录

| 阶段 | 流与出口 | 数据面 / 队列 | 负载与客户端 |
|---|---|---|---|
| A 软件 | 新鲜应用 socket；CT ID、zone、完整 mark、双向 tuple/NAT、WAN | ECM 0；原 tag/两 leaf 计数边界 | 总 LAN4 Mbps/pps、选中 WAN RX、单 TCP 活跃速率；jitter/loss/Miss |
| B NSS | 同一连接身份；tag 先于学习，类别变更精确撤销 | ECM 2；bulk/RT 正确 leaf；B 内实际字节/包增量 | 同字段；单 TCP/RT 受控份额；softirq/time_squeeze；体感有则记 |
| A2 软件 | 仍同一 CT 实例；出口与 NAT/完整 mark 不变 | ECM 0；精确撤销、独立恢复与保护审核 | 同字段；记录下载终止、连接重建、游戏退出等混杂因素 |

计数窗须使用原生 uptime，单独报告 B 与撤销区间。不能把 B＋撤销计数视为纯 fast path 份额；CT reply 查询窗和物理接口窗也不能不加说明地混合。NSS43 的 Steam-only 匿名连接不能代替现场所选游戏 WAN 的新鲜身份。

## 分开判断

1. **功能与恢复。** 自动游戏分类持续命中、正确 bulk/RT leaf、0→2→0、完整 PBR/mark/NAT/WAN affinity 与保护恢复均通过，才记作功能闭环。原控制器终态必须通过，不能只看片段日志。
2. **观测是否可比。** 在新实验前声明，A/B/A2 的总 Mbps、pps、选中 WAN RX 各自相对跨度不超过 10%。`load_model.assess_load_comparability()` 仅作只读观察检查；通过仍不证明 offered load 相同，也不会授权 NSS。未通过就不做 CPU 因果结论。
3. **性能。** 重点是 softirq/time_squeeze、实际受控包份额和吞吐，busy 辅助。一 TCP 约 6–8% 的整机参考流量，整机变化可能较小；未下降不反驳已证明的 fast path。加速后的实际需求重新测，不能把 NSS43 固定需求模型当预测。
4. **游戏。** 用真实客户端 jitter/loss/Miss、同期体感；RT leaf drop 0、ICMP 或 UDP echo 不代表端到端 loss 0。缺客户端数据明确未验收。用户没有注意到时保留原反馈，不推断改善。

只有功能、恢复、可解释的性能和游戏闭环通过后，才讨论第二 WAN、共享预算、Wi-Fi、autorate 和五 WAN。若一次窗口缺负载或数据，保存具体原因，不要求用户继续长期挂机。

## 可离线复核

从仓库根目录运行 `python code/work/nss43/test_load_model.py`，20 项纯模型检查，不访问路由器、不读私有证据。实际下载观测见 [NSS43 证据](../evidence/nss43-mainline.json) 与 [采样数据](../evidence/nss43-load-profile.json)。此前 NSS41 的新观测条件评估见 [历史对照](../evidence/nss43-prior-aba-comparability.json)，原始功能证明没有改写。
