# Athena NSS Development Mode：有界常驻控制器 soak 通过

北京时间2026-10-08 00:41。当前交付目标是可复用、逐步常驻的 Multi-WAN controller。使用同一 RC1 批量修复并本地回归，没有新增正式实验版本；五 WAN NSS、QoS、NAT/mark/affinity 与 CPU 历史证据继续复用。

当前 P0 未观察到；原 P1 是低速整形后的已知 TCP BULK 被重新归为 BE。候选只在近期 BULK 记忆仍有效且当前存在大下行包和小反向 ACK 时保持 BULK；冷流、未知、空闲、身份变化、计数重置或过期仍拒绝。24项实际Lua回归复现旧故障，90.01秒/181采样/ECM3/30续租与完整恢复通过。

同批清理 P2：整数 timeout、唯一命名空间、当前部署绑定、publication读取缓存、checkpoint后最终选择，以及预检查与最终读取跨截止的等待竞态。最后一项以单次严格最终读取替代两次检查；仅三种既有时间余量拒绝可在原20秒窗口等待，3/3.25秒学习余量及source6不变。16项实际Lua回归和完整打包通过。

soak预定为控制器至少480秒、最多720秒，两代各90秒；新代只在上一代完整恢复后启动，各有新checkpoint/SHA/gzip及独立恢复。实际状态：**COMPLETE**，通过：**true**。每一代的NSS时长、续租和恢复见[聚合结果](../evidence/resident-controller-rc1.json)。此范围包含代间软件恢复，不声称连续长期NSS或默认永久部署。

默认常驻仍关闭。保留现有硬截止，先交付这一可撤销的有界控制器；后续长期默认运行单列为下一milestone，不主动增加边界、故障注入、CPU、Wi-Fi、autorate或ECN实验。

## 使用

在原工作区运行 `node work/resident-dev-20261007/controller.mjs inspect|status|run|stop`。默认inspect没有流量或路由器写入；run只执行预定两代，失败不自动重试；stop请求本代结束并保持独立恢复。单次入口为 `entry.mjs inspect|status|run|stop`。源码见[controller](../code/work/resident-dev-20261007/controller.mjs)和[入口](../code/work/resident-dev-20261007/entry.mjs)。凭据、实际部署配置、CT、nonce、checkpoint和模块仍仅在原工作区，公开源码不能代替这些写前输入。

## 已知限制与后续

- 当前候选为两条TCP BULK和一条模拟UDP RT，跨自然选择的WAN；五WAN同时ECM5和高级QoS沿用历史v42/v54数据面证明。
- 偶发SSH首包、自然WAN未齐和UDP回显拒绝属于取得条件；没有NSS缺陷证据时不升级blocker，不无限重试或扩大防火墙。
- 固件计数变化的精确原因尚未证明，不继续增加tap。BULK保留必须有当前流量证据，真实暂停/改类仍安全退出。
- 下一阶段才考虑更长正常使用 soak、默认resident部署；不以本次有限运行声称全网、长期或重启恢复。

旧v58及更早状态保留为历史，以本段为当前状态。[代码与恢复摘要](../evidence/resident-controller-rc1.json)、[源码清单](../evidence/resident-controller-source-proof.json)。
