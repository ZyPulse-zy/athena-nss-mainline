# 本地缺陷：ECM 状态后处理写死 WAN5

这是本工作区的报告后处理缺陷，不是已证明的 NSS/ECM 上游缺陷；没有提交上游。

- 旧文件：[parse-ecm.mjs](../code/work/nss25/parse-ecm.mjs)。`validateAcceleratedState()` 的接口校验写死 `rpwan5`，输出 `wanAffinity:5`。
- 触发：真实选择 WAN1，native 三段完成、加速数 2，但最终主机后处理抛 `WAN affinity absent`。原失败与完整私有状态保留。
- 最小复现：以 NSS41 冻结的实际 WAN1 TCP/UDP 状态与所选身份调用旧解析器。没有重新发流量或变更生产。
- 修改：[parse-ecm-any-wan.mjs](../code/work/nss41/parse-ecm-any-wan.mjs)，两处改为选中 flow 的 `f.wan`，其它方向、mark、NAT、tag、模式和接口层级检查保持。
- 验证：实际 29,061 B / 两条连接状态通过；错误 WAN、完整 mark、NAT 端口、接口层级、RT tag、加速模式的 6 个变异仍拒绝。[结构化证据](../evidence/nss41-mainline.json) 中保留原/新哈希与实际状态哈希。
- 限制：这是冻结硬件数据的后处理检查，不等于新一次实验或性能验收。原控制器未改，终态 false 保留。
- 绑定缺口：旧解析器未在该入口 83 项清单，已单独冻结本次校验来源。下一轮应纳入后处理依赖，重新审查清单闭包，再接到新入口。

恢复后错误地套用学习前 full publication age <2 秒调度是本地流程问题；本次之后恢复原 <6/<9 秒完整审核通过。固定截止未延长；要在新轮次纠正调用场景及失败逐帧诊断，避免继续修改冻结代码。
