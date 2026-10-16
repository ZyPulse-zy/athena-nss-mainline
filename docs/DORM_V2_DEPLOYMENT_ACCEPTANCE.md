# Athena NSS v2 审查修复：获准部署与验收

2026-10-10，北京时间。用户在完成候选交付后明确要求“直接进行，现在没有人用”；本次已执行单次正常控制器切换，**db872e0 的生产源码和匹配模块已经安装并运行**。PR #1 继续保持 draft，未合并。

## 部署结果

| 项目 | 实际结果 |
|---|---|
| 部署前 | 原 native-running、来源新鲜、NSS7；原 ECM/driver/IGS 输入与构建哈希一致，已安装源码与审查基线一致 |
| 回退备份 | 原安装、init、受保护配置及事务状态私有归档 328,653 字节；下载哈希、gzip 和路由器持久副本均校验，旧备份保留 |
| 原控制器正常退出 | 00:46:40 确认，命令及独立完整回退约 3.254 秒；phase=restored、rollbackConfirmed、锁/两候选模块消失、IPv4/IPv6加速0且准入关闭、原guard字节恢复 |
| 成套安装 | 00:47:42，6个Lua、两新候选模块、两已验证ECM/IGS副本、build-result共11文件；各项哈希一致，原磁盘ECM/driver/IGS未替换 |
| 新会话启动 | 00:47:58 确认 native-running/sourceFresh，约3.905秒，NSS7、新观察字段可见、未确认0、监督器自动重试0 |
| 最终运行核验 | **00:55:06**：native-running/sourceFresh/NSS8/未确认0；新会话来源暂停/恢复0/0、自动重试0；11文件持久安装及运行RAM副本都匹配db872e0候选 |
| 软件路径 | 十个rpwan/rpifb CAKE根的kind/handle及除autorate动态bandwidth外所有选项与已核对哈希的原配置完全一致，diffserv4保留；原分类器配置哈希未改 |
| 其它路径 | 五WAN地址/接口身份、受保护network/firewall/wireless/分类器配置及运行guard哈希一致；认证、分类器、autorate、代理、Tailscale PID/启动时间保持；原开机启用状态保留 |
| 临时资源 | 00:56:25 私有持久回退副本校验完成，本次自有RAM安装目录的枚举文件已清理；运行目录和历史备份保留 |

既有退出/启动过程会重载其拥有的核心guard循环，以恢复原字节或安装已有条件hook。该guard PID按预期变化，已核验运行及最终字节一致，不能笼统宣称所有服务PID都没变。没有重启路由器、刷机、改无线、改变设备配额、调整原CAKE/autorate配置或制造拥塞/故障。

启动前专用 classifier_recovery inspect 带有“无native gate/锁”的保护。运行期一次调用被该前置条件拒绝、没有进行队列查询或修改；没有取消保护或为此再停止NSS。最终使用独立只读软件队列查询，按已核对哈希的原配置核对十个根，验证通过。

结构化事实见 [本次部署证据](../evidence/dorm-v2-audit-deployment.json)。代码修改、旧/新4→1撤销复现、344 Lua/150 C模型及交叉构建见 [前一阶段审查修复](DORM_V2_AUDIT_REMEDIATION.md)。这些离线测试没有重复成多轮现场压力或故障夹具。

## 一次轻量自然流量验收

新默认 `diagnose 60` 成功，21个样本、样本窗口60秒、完整命令约60.47秒；没有 `--queues` 硬件tc查询或主动流量。观测：

- 实际NSS **6..9**；来源新增暂停/恢复 **0/0**；单次只读采集最长 **0.04秒**。
- 全局NSS IPv4 special RX字节增 **4,156,949**，TX增 **4,270,237**，20个有效比较间隔、计数重置0。它们是全局方向独立计数，不是该游戏/CT的字节或覆盖率。
- 末次拓扑六项查询全部exit=0，complete=true，topology约0.04秒、publication约0.01秒；三AP使用hostapd，fallback0。
- 原CAKE十查询最近一次约0.06秒；末次writer记录已续租最小余量约2.15秒。读前/后记录相同表示该轮没有到三秒预算读取周期，不是查询零耗时。六秒lease没有扩大。
- rejected entries0/limit32/TTL6；pendingRt0；单连接恢复tracked0/withdrawals0/exhausted0，未触发新身份准入暂停。自然窗没有满32槽或明确CREATE失败事件，**满槽修复和真实单连接恢复仍只有模型验证，不能说现场故障验收已通过**。

## 新实测问题：双向完整QoS标签并非全部合格

新观察功能实际检出 **6个verified、116个mismatch流样本**。这是随时间重复的流证据计数，不是116条独立连接，更不是丢包率或CREATE失败率。

末次五条无线RT有当前精确身份、正lease、当前CREATE ACK；它们的RT低位6、IGS上行0和下行WAN对应7a标签正确，但CREATE payload中的下行 `return_qos` 高位仍等于上行7e标签。例如匿名WAN1 RT：预期up=`0x7e160006`、down=`0x7a160006`、igsDown=`0x7a16`；实际up/down均`0x7e160006`，igsDown仍`0x7a16`。完整双向核验因此诚实报告mismatch。

维护nft生成器分别设置原向up与回向down（[标签规则](../code/controller/native/tag_rules.lua#L51)）；已有NSS前端源片段直接复制分类结果pr的flow/return QoS。已证明规则意图和实际CREATE观测不同，但尚未定位到ECM分类器初始双向标签、后续覆盖或其它路径。不能通过修改“预期”来让报告变绿，也不能直接把该高位差异说成下行IGS未优先或游戏已经丢包。仍保留正向/IGS/低位结果，下一步应逐流关联software packet priority、ECM分类状态和CREATE时刻。

本次QoS mismatch只读记录，没有据此撤销健康连接或触发共享NSS重启。现有RT/BULK准入、32成本槽、软件分类、CAKE/autorate和无线配置保留。

## 保留的验收范围

1. 双向完整标签差异及独立固件队列readback是当前高优先级待查项；本次部署成功不等于这项合格。
2. 真实ECM再次选择/重新CREATE和精确移除后的有限重试，需要自然失败事件或另行明确的隔离验证；此次恢复计数0，无该事件。
3. Wi-Fi逐station/TID/AC、同设备已识别游戏+下载、客户端上行airtime以及端到端Loss/Miss未测。低位6和IGS标签正确不能替代空口证据。
4. 持续有线NSS快转超过60秒的FDB刷新、包含BE的同cohort/同方向/窗口/字节口径覆盖仍未取得；不扩大BE或放宽FDB/lease。
5. 历史分类器tc清理/来源4/4暂停原因仍未闭环；新会话短窗0/0不能抹去这些事实。后续出现事件时使用已增加的查询耗时、完整性和实际lease余量定位，避免泛化多轮压力测试。

当前服务保持运行。部署授权已在本轮执行完成；没有新建自动监控、合并PR或继续改无线/刷机/制造故障。
