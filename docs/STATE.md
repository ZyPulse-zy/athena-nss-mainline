# 当前状态

更新：2026-10-04，北京时间。最新现场核验见 [当前运行记录](../evidence/current-runtime.json)。

**真实 WAN1 自动分类→ECM fast path→NSS bulk/RT leaf 已由 NSS41 证明；CPU 和游戏体验验收仍未通过。NSS43 已量清 Steam 的单连接受控份额，现网仍是 NSS39，NSS42 102 项验收入口不变。**

## 当前运行与 NSS43

见 [本轮证据](../evidence/nss43-mainline.json)、[相对采样与脱敏连接速率](../evidence/nss43-load-profile.json)。

- 常驻引用仍 `work/nss39/deployment-latest.json`，配置 `17aaa0797d654938b654d06eaf575ba0766c845aae2a16f8e229998c5992af60`。起止原完整保护审核通过，同一 worker/guardian 健康；旧错误属于此前安装到期。结束 12 个 selector 由常驻分类器自主管理。
- NSS43 工具只读，没有生产配置写入、checkpoint、回滚试验或 NSS 准入。ECM 九项关闭/零计数检查每帧通过，结束无事务、实验模块、暂存或状态节点残留。
- 用户仅开启 Steam，未开 CS2。北京时间 10:11:02 起约 48.02 秒，13/13 次新鲜 socket 与 CT 归属观测成功；每帧 bulk 13–16 条，全窗 23 个 CT 实例，存在退出/重建。WAN5 没有贯穿全窗的单条连接。
- LAN4 277.73 Mbps / 22,985 pps，4 秒窗 262.32–287.97 Mbps，变异系数 2.36%；busy 71.17%、softirq 49.24%、time_squeeze +49、softnet dropped +0，包含观察开销。不是 NSS A/B，未达到全窗 300 Mbps。
- WAN1–5 RX 约 35.46/62.26/46.58/87.71/51.53 Mbps；相应最大全窗 CT reply 单 TCP 为 21.80/17.49/22.99/16.40/未取得 Mbps。CT 查询起始估计窗与物理接口窗略不同，不能作为 Steam 载荷或精确加速份额。
- 固定这些软件路径速率的离线模型：20→30 Mbps，WAN1 整机参考份额 7.20%→7.85%，WAN3 7.20%→8.28%，WAN2/4 无增加。加速后 TCP 需求可能变，这不是实际 NSS 预测。当前不扩预算、连接数或 TTL。
- 20 项离线检查通过；13 份只读源码快照保留，它不构成新的生产入口资格。NSS42 102 项清单只复核、未修改。10% 相对跨度是预先声明的 A/B/A2 观测比较条件，不授权加速，也不证明 offered load 相同；[历史 NSS41 对照](../evidence/nss43-prior-aba-comparability.json) 不满足。
- 第一次采样因本地 JavaScript 语法错误 13 次退出，发生在路由器连接前，原失败保留；修正后重新取得有效窗口。分开读取的 autorate 数值不同，相邻 JSON/文本/JSON 5/5 单位核对通过；采样后的 70–90 Mbps 不能回填为整窗固定预算。

下一步按 [单次真人验收记录](SINGLE_WAN_ACCEPTANCE.md) 集中完成自动分类→bulk/RT leaf→CS2＋Steam。当前不需要用户继续挂机。

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
