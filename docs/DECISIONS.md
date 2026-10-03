# 已确定的方向

- 单一主线：自动分类 → NSS RT leaf → 真人 CS2 + Steam。
- Linux 负责新连接 PBR/ct mark；已有连接的 WAN affinity 保持，不让 NSS 重新负载均衡。
- NSS 目标是主要数据面 QoS；CAKE 只作 fallback/对照。
- host fairness 不再作为必须功能，基本不考虑 N100。
- 不机械复刻 CAKE：可以采用 HTB + 两个显式 FQ-CoDel leaf，但要单独验证拥塞延迟、吞吐与必要优先级。
- 现有原生 gate 要求 TCP/game **完整 mark 相等**。不同低位标记必须拒绝；不通过清位凑成相等。
- 测试负载不足、候选不存在或条件不满足时，停止该现场尝试并记录原因；不靠扩大范围碰运气。
- 不把历史低负载成功、默认队列计数、ICMP 或进程正在运行替代真实游戏验证。
- 单 WAN 闭环通过前，不扩多 WAN、Wi-Fi、ECN/autorate 研究支线。
