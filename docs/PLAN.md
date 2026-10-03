# 下一步：稳定单 WAN 负载，集中完成性能与游戏验收

唯一主线：自动游戏分类 → NSS bulk/RT leaf → 真人 CS2＋Steam 单 WAN。

NSS41 功能路径成立，原控制器失败保留。NSS42 已修正通用 WAN 后处理、恢复审核用途及声明的依赖绑定；不要再重复这三项准备，也不要重跑 NSS41 冻结入口。NSS42 控制器只完成隔离回放和目标只读审核，尚未完成新真人 A/B。

1. **每次先核验现网。** 常驻仍 `work/nss39/deployment-latest.json`，实际入口是新目录 NSS42。先检查当前配置/102 项输入与外部连接源码哈希、worker/guardian、生产队列、受保护配置和 ECM 全零。新变更另建轮次，保持 v1/v2 冻结证明。
2. **先确定可解释的负载。** 当前 gate 固定一条 TCP＋一条 UDP，NSS 子组上限 20 Mbps。NSS41 bulk/RT 仅占 B＋撤销 leaf 计数约 4%，总流量和 WAN1 负载又持续上升。下一次先只读观测同一 WAN、总 LAN4、pps、受控 bulk 活跃性和流量份额，不把 global busy 的小变化当收益。若该子组不足以回答问题，应单独准备并资格核验一个单 WAN 变量；不能在当前 102 项入口中偷偷扩大预算、流数或 TTL。新预算还需考虑该 WAN 的非受控软件流，不能先假定总下行受控。
3. **只集中请求一次真人窗口。** 用户无需常驻游戏或反复下载；没有真人 flow 时可做离线/只读工作，但不能冒充 CS2 验收。新鲜应用 socket、CT ID/zone/双向元组、完整 mark、NAT 与 WAN 匹配，完整审核通过后，才创建本轮 checkpoint 并先确认独立 owner。
4. **运行修正后的完整验收入口。** 默认拒绝、精确放行、learning 前 tag、精确撤销、相同队列预算和观察循环。学习前使用 `prewrite` 模式；关闭 ECM 后使用 `recovery` 模式的原完整审核。初始 <1 秒、预学习 <2 秒、原持锁 <6/<9 秒、调度内 5/外 6 秒、owner 45 秒均不变。调度失败保留当前逐帧年龄和读取阶段，不延长期限碰运气。
5. **判断有效性再判断收益。** 确认加速数 0→2→0、bulk/RT leaf 流量、完整 mark/NAT/WAN affinity 保持，完整控制器成功与独立恢复结果另记。负载未匹配则只记录功能和测量，不能给 CPU 因果结论。重点看 softirq/time_squeeze、pps/吞吐、游戏 jitter/loss/Miss/体感；无客户端指标明确未测，RT leaf 丢弃不是端到端 loss。用路由器 uptime 校准游戏窗口，不错配时间。
6. **闭环全部通过后才扩展。** 第二 WAN、共享预算、Wi-Fi、autorate、五 WAN 继续等待。CAKE 是软件对照与未加速流 fallback，不转回长期 CAKE 优化；host fairness 和 N100 不作为方向。

每次生产写入仍需本次 checkpoint 和独立于控制连接的自动回滚。不得刷机/升级内核/改分区/全清 conntrack/重建全部生产 qdisc，保护认证/PBR/sing-box/Tailscale。无上游提交；旧后处理问题保留在 [校验缺陷记录](ISSUE_ECM_WAN_VALIDATOR.md)。
