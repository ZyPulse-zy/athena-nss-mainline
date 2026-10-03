# 下一步：验证优化后分类数据能及时进入 NSS

唯一主线：自动游戏分类 → NSS RT/bulk leaf → 真人 CS2 + Steam 单 WAN 闭环。NSS37 属性解析优化已保留，独立回滚通过；NSS36 真实失败仍是未解决的高负载验收边界。

1. **核验当前 NSS37。** 读取 `work/nss37/deployment-latest.json`、配置/源码哈希、现网与 ECM 全零。检查当前 producer 和 last-error 的归属；不能把首次试装到期当作当前崩溃，也不能把一次健康当长期稳定。
2. **只读验证代表性负载下的发布时间。** 本轮仅证明解析 CPU 耗时下降，轻负载发布约 0.25–0.29 秒。记录来源序号、query age、publication delay、完整检查耗时与拒绝原因，判断初始 <1 秒窗口是否真正可用。用户没有持续下载时不反复催促，不将合成文本测量写成真实网络压测。
3. **若仍不足，只定位同一发布路径。** 采集、核心分类、同步 fallback 规则维护与审计可能影响周期；先只读/内存量化具体阶段，再决定一个最小变量。不得删字段、缩小源范围、跳过身份、改变 PBR/mark/NAT、延长 TTL 或换时间基准。不要先改进程架构或开启其它 QoS 支线。
4. **更新控制器资格后，集中一次真人测试。** 当前 NSS37 已绑定新配置与 66 项源文件；任何被绑定源码/证明的变更都需新轮次重新核验。自然同 WAN 的 Steam TCP 与 CS2 UDP、完整 mark/NAT/实例/应用归属均核对。准备充分后集中一次配合，无需长期挂着。
5. **先验证加速路径，再评价性能。** checkpoint、独立回滚先于变更；单 WAN、单连接对。证明 tag 在 ECM 学习前就绪、两流分别命中 bulk/RT leaf、出口/ct mark/NAT/WAN affinity 不变、精确撤销有效，再做 software → NSS → software。重点 softirq/time_squeeze/吞吐及真实 CS2 jitter/loss/Miss；busy 仅辅助。现有子组 20 Mbps，不等于整体 300 Mbps 以上均已加速。
6. **闭环通过后再扩展。** 第二 WAN、共享预算、Wi-Fi、autorate、五 WAN 和 bridge B-shaper/ECN/HTB dump 等继续等待。没有客户端数据就明确未取得，不用 ICMP/合成 UDP 替代真实游戏体验。

NSS37 本轮不再要求用户维持游戏或下载。已提交部署仍持续保留安全分类守护，ECM 关闭；不承诺未安排的后台测试。每轮保存假设、变更、负载、ECM/leaf、mark/NAT/WAN、时序、softirq/time_squeeze/吞吐、客户端指标来源与恢复结果。
