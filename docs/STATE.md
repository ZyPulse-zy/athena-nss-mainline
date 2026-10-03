# 当前状态

更新：2026-10-04，北京时间。最新现场核验见 [当前运行记录](../evidence/current-runtime.json)。

**真实 WAN1 自动分类→ECM fast path→NSS bulk/RT leaf 已由 NSS41 证明；CPU 和游戏体验验收仍未通过。NSS42 已修复本地验收入口、补齐声明的依赖绑定并完成只读核验，现网仍是 NSS39。**

## 当前运行

- 常驻引用 `work/nss39/deployment-latest.json`，配置 `17aaa0797d654938b654d06eaf575ba0766c845aae2a16f8e229998c5992af60`。worker/guardian 与 NSS41 是同一实例，健康；旧错误属于此前安装到期。
- NSS42 没有生产配置写入、checkpoint、回滚试验或 NSS 准入。原完整保护审核通过，ECM 关闭且相关计数全零，无事务、实验模块、暂存或状态节点残留。
- 02:01:48–02:11:48 的 600 秒只读窗，30 秒一次，21/21 次成功，worker/guardian 样本健康、来源序号递增。完整/compact 来源年龄 2.35–2.56 秒。稀疏轻载采样不能证明全部时间和高负载稳定性。
- 自然软件转发约 1.98 Mbps / 187 pps，busy 14.18%、softirq 3.10%、time_squeeze +0，包含观察开销；不是 NSS A/B 或游戏数据。
- 没有检测到真人 CS2＋Steam 下载配对，没有要求休息中的用户开游戏。

## NSS42 验收入口

见 [本轮证据](../evidence/nss42-mainline.json) 和 [相对采样记录](../evidence/nss42-stability-timing.json)。

- 通用 WAN 后处理按选中 flow 的 WAN 验证 mark/NAT/tag/方向/层级，修正历史写死 WAN5。43 项：一份冻结的真实 WAN1 重验、20 个合成方向/WAN 组合、22 个拒绝样本。
- 学习前审核与恢复审核分开。学习前仍锁外等待严格更新、新鲜的完整发布，再执行原审核；恢复直接执行原完整审核，不能授权 NSS。没有放宽任何 TTL 或独立 owner 期限。
- 调度失败保存已观察行和读取阶段。23 项本地时序/诊断检查，目标 Lua/jsonc 4 项隔离 RAM 序列化检查通过；未对生产分类器注入故障。
- 实际控制器 8 项隔离回放、静态依赖解析 7 项、绑定变化拒绝 9 项，总计 90 项本地检查。外部连接、上传、生产写入与部分历史资格 IO 在这些回放中被替换，不能计为新硬件实验。
- 当前 `work/nss42/entry-qualified.json` v2 绑定 102 项输入，包括历史 68 项 runtime、后处理及检查源码。静态图 40 个文件/69 条关系，模块不链接、不执行。声明的动态 payload 另行绑定，外部既有连接实现只记录源码哈希。OS/运行时和所有可能动态依赖不在全面保证内；连接封装、凭据和私有清单不导出。
- v1 冻结 99 项输入；v2 冻结 102 项输入及五份本地检查证明。两种审核用途在目标路由器上通过；修正后的完整控制器尚未执行新真人 A/B。

## NSS41 保持的真人证明与限制

[NSS41 证据](../evidence/nss41-mainline.json) 保持，原控制器终态 false 没有覆盖。真实 WAN1 一条 Steam bulk TCP＋一条 CS2 RT UDP，zone 0、完整 mark 0x10000、同 NAT，tag 先于 ECM 学习。B 5.17 秒，11/11 帧加速数 2，完成一次新序列续租；A/A2 均加速数 0。冻结硬件状态确认 private rpwan1/物理 wan 与 LAN4/br-lan 层级、双向 NAT 和 bulk/RT tag 正确。

原错误分别是旧后处理写死 WAN5，以及恢复审核误套用学习前调度。后处理重新校验和原完整恢复审核已通过；native owner 提前撤销，保护配置与基线恢复，独立 45 秒回滚已布置但本次没有触发到期。历史实际到期证明保持。

总 LAN4 347.72→379.98→391.11 Mbps、WAN1 35.62→68.88→79.19 Mbps，负载不相同。仅受控一条 TCP＋一条 UDP，子组上限仍 20 Mbps。B＋撤销计数窗 bulk/RT +6,688 包 / 9,803,650 B，占全部 leaf 4.37% 包 / 4.11% 字节；该窗包含撤销，不能当精确 fast path 占比。

不能据此宣称 CPU 或吞吐收益。RT leaf 丢弃增量 0 不等于游戏 loss/Miss 为零；用户反馈“没注意到，无法比较”，没有客户端 jitter/loss/Miss。真实功能路径通过，不等于性能和游戏闭环通过。

下一步稳定同 WAN 的实际负载并明确受控份额，再集中真人对照。第二 WAN、共享预算、Wi-Fi、autorate 继续等待。[NSS40](../evidence/nss40-mainline.json) 的 72 份历史拒绝证据与 [NSS39](../evidence/nss39-mainline.json) 的独立到期证明保留。
