# Athena AX6600 / NSS v2 审查修复与验收记录

**后续状态更新**：用户随后明确要求直接部署。db872e0已在2026-10-10完成单次正常切换并保持运行；当前生产结果与新检出的完整双向标签差异见[部署验收](DORM_V2_DEPLOYMENT_ACCEPTANCE.md)。下文“候选未部署”与待许可计划是当时的审查阶段事实，不能当作现在的部署状态。

2026-10-10，北京时间。代码已在 `codex/dorm-qos-v2` 实现并完成定向验证；这是**待部署候选**。共享网络仍运行此前已安装的 ABI2 本机控制器，PR #1 保持 draft。没有停止控制器、加载候选模块、重启、修改现网 QoS/无线配置或制造流量与故障。

## 基线与版本差异

- 起始远端 head 为 `be469530a891944c5a5ed83e4c149b971517384b`；上一轮审查提交为 `3208540`。两者之间只有交接记录更新，本次涉及的生产源码尚无本轮修复。修改前工作区干净，本次使用独立 checkout；`main` 的旧 Windows 三槽方案不是现场代码。
- 已读当前 `docs/STATE.md`、`code/controller/README.md`、`evidence/dorm-v2-native.json` 最新部署记录并核对现场。此前精确标签修复、有限监督恢复、开机启动和第二轮获准冷启动已经完成，保留这些结果和第一轮失败，不重复实现或验收。
- 2026-10-09 23:43:04 的只读核验：已安装 writer/reader/collector/health/diagnose 五文件与起始分支的 SHA256 一致。路由器安装的是模块，不保存这两个 C 源文件；不能用“C 文件不存在”判定部署漂移。原 ECM、NSS driver、IGS 模块与本次构建输入哈希一致。
- 最新只读复核为 **2026-10-10 00:23:42**：native-running、sourceFresh、IPv4 准入开启、未确认移除 0，五 WAN 正常；相关服务 PID/启动时间、受保护配置和已安装五文件哈希均与起始现场一致。来源累计暂停/恢复仍为 4/4。候选的 `create_seen` 等新状态字段尚未在现场出现，明确未部署。
- 原 `/mnt/data/nss_branch_audit/…md/…zip` 在本 Windows/WSL 环境不可访问；使用已读取的会话审查内容，并从 `3208540` 提取实际源码独立复现。

结构化结果见 [修复证据](../evidence/dorm-v2-audit-remediation.json)。源文件历史修订追加到 `source-manifest.json`，冻结的 `code/work` 未改。

## 优先级 1：满槽等待回执与失败缓存，已修复

### 同一条 RT 不再逐轮撤销不同 BULK

证据位置：[writer 的预留与选槽](../code/controller/native/writer.lua#L209)、[实际 writer 回归](../code/controller/native/test-writer-policy.lua)。原代码只查看“有没有空槽”，没有计算已请求撤销的承诺位置；同一条 RT 在每次等待 ACK 的轮询中又挑另一条 BULK。

用原样 `3208540` writer 和当前 writer 执行相同的拒绝真实 I/O 夹具：32 条 BULK 占满，新增一条 RT，故意让模拟固件延迟确认，连续轮询四次。**旧版发出 4 条不同 BULK 的撤销请求，候选仅 1 条**。这是实际生产 Lua 在模型内的行为，不是测得的真实固件回执延迟。

修复记录 `pending[RT key]={slot,binding}`：先占用可安全复用的空位，再承接已在撤销的非 RT 位置，最后才撤销一条现存非 RT。等待位置不会被 BULK 抢占，同一 RT 不再重复撤销；身份/出口变化、RT 离开或成功准入时清理预留。被替换对象按当前 `rateKbps` 较低者优先、槽号打破并列，替代不确定的 `pairs()` 顺序。这个速率只是同口径的软件分类器指标，尚不是逐流硬件收益测量。

同时阻止已请求撤销的槽再次续租。排名变化不驱逐健康 BULK；32 条 RT 已占满时保持软件回退，不驱逐其它 RT。没有增加设备配额、改变 32 槽或 BE 默认范围。

### rejected 缓存有界且可清理

证据位置：[缓存上限和期限](../code/controller/native/writer.lua#L9)、[定向回归](../code/controller/native/test-writer-policy.lua)。每项保存 sequence/时刻/到期时刻，上限 32、TTL 6 秒；离开、失去候选资格、观察序列变化、期限到达或成功准入时删除，达到上限时确定性淘汰最早项。导出 entries/limit/ttlSeconds/pruned。连续身份轮换模型中始终不超过 32，清空来源后归零；没有增加内核/固件缓存。

## 优先级 2：一次选择与单连接恢复，已实现安全候选，固件验收未完成

证据位置：[内核选择器](../code/controller/native/athena_ecm_gate.c#L83)、[回执状态观察](../code/controller/native/athena_ecm_gate.c#L265)、[writer 恢复](../code/controller/native/writer.lua#L170)、[选择器 C 模型](../code/controller/native/test-selection.py)。

原 `LIVE && !e->selected && now_ms()<e->until` **完整保留**。13 项 C 断言直接编译实际选择函数：首次选择 NSS；原槽续租后再次选择仍返回 NOT_YET；失效 CT、停止、到期、错误 tuple/协议族均不授权。未直接取消防重复保护，也没有按“字节暂时不增长”重启 NSS。

候选只在新鲜、完整绑定仍有效，且存在以下明确回执时开始单连接恢复：

1. `selected>0`、确实观察过 CREATE、pending=0、ACK=0，回执仍为 ARMED：已观察的 CREATE 失败。
2. 已观察 DESTROY ACK，或 DESTROY NACK response=4/error=5（明确规则不存在）。

路径为**拒绝旧绑定 → 请求精确撤销 → 等待既有 ACKED/NEVER_CREATED/FIRMWARE_ABSENT 终态并释放引用 → 重新核验当前身份后建立新 generation**。中途不能换另一个槽绕过 tombstone。每个连续有效身份/绑定/分类 epoch 最多两次重试、1/3 秒退避；第三次失败不再续租，原六秒独立租约自然到期，保留原软件路径。重试账本上限 32；账本满时暂停新身份的硬件准入、保留已有健康流和软件分类，避免丢失重试历史后无界循环。该状态单独展示为 `recovery.newIdentityAdmissionPaused`。

回执缺失、CREATE 仍 pending、旧模块没有 `create_seen`、QoS 标签不符、空闲连接没有字节增长，都不据此撤销。UNCONFIRMED 仍触发既有失败保护，不能把时间经过当成移除成功。

**尚未证明**：真实 ECM 在重新准入后是否对每一种历史失败原因重新调用选择器并成功创建规则；丢失 CREATE 回调、TX_FAILED、固件静默清空且没有观察到回执的恢复；已观察规则提前消失的根因。候选没有新增强制 ECM regeneration API，也没有把新 lease/add 当成真实恢复成功。以上需要自然失败事件或单独获准的隔离验证。

## 优先级 3：轻量核验分层，已实现

证据位置：[标签/字节判断](../code/controller/native/health.lua#L15)、[只读采集](../code/controller/native/diagnose.lua#L21)、[新观察 API](../code/controller/native/receipts.h)。默认诊断不发硬件 tc 队列查询；`--queues` 仍需显式选择，未读到队列不能记为零 drop。

| 证据层 | 候选展示及解释 |
|---|---|
| 分类 | 所有候选 RT/BULK、WAN、出口、有线/无线、来源新鲜度；RT 不等于已确认游戏 |
| 准入 | 完整 CT/mark/NAT/原回 tuple、binding token、serial/generation 一致及剩余 lease |
| CREATE | 仅当前 ARMED 回执、有效身份/租约、ACK=1/pending=0 算已创建；历史 DESTROY 后的 CREATE ACK 不算当前规则 |
| 双向标签 | 观察真实发往 NSS 的 CREATE payload，检查 QoS/IGS valid flags；按观测 CREATE tuple 与 CT original 的正/反向关系解释 up/down，逐项对比预期标签。无法解析方向时明确 unverified |
| 硬件进展 | 单独读取 NSS IPv4 **special** `ipv4_rx_bytes`/`ipv4_tx_bytes`，分别给出全局增量、缺读断窗和计数重置；不冒充该 CT 的字节 |
| 覆盖率 | 只有同 cohort、同窗口、同方向、同字节口径且 numerator≤denominator 才能算比例；实际默认 `measured=false` |

“标签 verified”的证据基础是 **CREATE payload + 固件 ACK**，强于软件写入意图，但仍不是固件实际队列独立 readback，更不是逐包空口投递证明。发现 mismatch 只记录，不主动改变准入或队列。

receipt 旧结构布局保持不变，另加 `athena_receipt_read_observation` 新导出；新 gate 要求新 provider，混用旧 provider 会缺符号而拒绝加载。部署时仍须成套安装两模块与匹配 build-result，不能把 ABI2 数字相同当作可任意混装。

输出最多 80 条当前流证据、256 个匿名流别名、128 条事件；原始 CT/MAC/IP/凭据留在私有 scratch，未进 Git 或公开报告。

## 优先级 4：采集、预算读取与六秒租约，已做小范围修复，历史暂停仍待查

证据位置：[采集失败与超时](../code/controller/collector.lua#L11)、[core 的来源完整性](../code/controller/core.lua#L76)、[预算耗时](../code/controller/native/writer.lua#L109)。

采集命令使用一秒 TERM / 再一秒 KILL 的限时执行，记录每项退出码、耗时和是否成功；成功的空集合与失败、截断、错误 JSON 区分。关键邻居/FDB/WAN 查询失败，或 AP 两种既有查询均失败时标为 topology incomplete：暂停准入和续租，不使用旧邻居证明、延长 lease 或误判 CT 消失。hostapd 失败但原 iw fallback 成功仍可用，并保留失败信息；旧 fallback 的授权语义未扩大。

一次隔离目录中的真实只读调用发现**新候选兼容错误并现场修正**：目标 BusyBox timeout 执行裸 `ip` 时选择自己的 applet，JSON 查询 exit=1；直接 `ip -j` 和绝对 `/sbin/ip`（iproute2 6.18.0）均成功。候选已改用绝对路径并加入回归。修正后同样调用完成六项只读查询：**complete=true、failures=0、约 0.05 秒**，三 AP 使用 hostapd，模型目录清理通过。未安装该采集器或改变运行进程。

writer 在来源缺失时不拿缺失 WAN 地址当真实 NAT 变化，不进行预算读写；真正新鲜的 WAN/NAT 变化仍拒绝。记录 writerTickSeconds、十个 CAKE 查询耗时和读前/读后**已实际续租**的最小租约余量，保留三秒预算周期、只批量更新变化类别、续租先于预算更新。

未把原十个 CAKE 查询的最坏耗时当成已经解决：原共享分类器 tc 子进程清理失败/4.17 秒、历史 recover/6.23 秒及来源累计 4/4 仍是开放问题。现网 71.60 秒短窗没有新增来源暂停，并不否定此前间歇故障。没有扩大六秒租约、重跑 CPU/softirq 压力或多轮故障注入。

## 优先级 5：Wi-Fi、有线 FDB、同设备混合流量与覆盖率

### 本次现场只读实测

2026-10-10 **00:00:49–00:02:01**，八个自然流量样本、71.60 秒：native-running/sourceFresh 全部成立，来源暂停/恢复增量 0/0，实际 NSS 0..4，保护哈希不变。全局 NSS IPv4 special RX 字节增 **3,334,551**，TX 增 **3,396,389**；两方向分开，未用相加值除 WAN 字节构造覆盖率。原 reader topology 耗时最高 0.04 秒；一次完整 SSH 读取最多 229 ms，包含状态、FDB、哈希和传输，不能当作游戏延迟或单独采集器开销。

出现两个匿名设备、八个匿名候选流；四个样本中**同一个 Wi-Fi 设备同时有 RT 与 BULK**。无线候选出口为 phy0-ap0；RT 和 BULK 都有当前 CREATE 回执样本。有线 lan4 出现短暂 RT，含一个当前 CREATE 样本。这证明分类和部分规则可以在两种接入上出现，不能证明它们都是游戏，或同设备游戏+下载体验已经合格。

无线 FDB age 0.01..0.48 秒；有线短样本 0.02..0.03 秒。没有持续超过 60 秒的已加速有线连接证据，因此**无法排除 NSS 快转不刷新 FDB 导致 60 秒身份门槛退出**。仍保留原门槛，未凭推测放宽、静态钉 MAC 或改交换机/无线参数。

现场存在 ath11k peer/HTT 调试入口，本次仅列出路径；未写 stats_config/reset/type，也未读取可能主动发出固件请求的 HTT 统计。是否已启用逐 TID 统计未确认。

### 源码结论与实测边界

软件 RT 低位 6 与普通 0 已写入真实 CREATE 观测值，但旧 gate 不提供方向/IGS validity。部分旧回执的 return_qos 为 0，不能悄悄当作双向标签合格；新诊断会分别给出不符或未知，再定向查 ECM/IGS 路径。

通用 802.11 映射中，UP 6/7 属 AC_VO，0/3 属 AC_BE；Linux 通用分类同时涉及特殊 skb priority、VLAN/DSCP/QoS map。这些规则不能证明当前 NSS→ath11k 快路最终采用同样的 TID。客户端上行先争用无线空口，路由器 WAN 优先级只能保护其后的队列，不能自动修复客户端已发生的空口竞争。[RFC 8325](https://www.rfc-editor.org/rfc/rfc8325.html)、[Linux 6.18 通用无线分类源码](https://github.com/torvalds/linux/blob/v6.18/net/wireless/util.c)。

本次没有同 cohort 的逐 CT 硬件字节，分类投影也排除了普通 BE，因此既不能宣称 32 槽覆盖率很高，也不能据连接条数判断“BE 值得全部加入”。当前只修必要 RT 置换，不周期性追逐流量排名，不新增配额或盲目扩大 BE/缓存。后续按方向/窗口/同字节口径计算 `H/T`，并单列 RT、BULK、BE；只有确认持续软件占比和硬件收益后再评估带滞回/冷却的替换策略。

## 测试与构建结果

| 验证 | 结果 | 证据边界 |
|---|---|---|
| 真实 writer 的旧/新差异夹具 | 4 次轮询撤销 4 条 → 1 条 | 模拟延迟 ACK，无硬件 hook |
| writer 定向回归 | 198 断言通过 | pending/free/多 RT/离开/缓存/有限恢复/预算满/未确认保护 |
| health/core/collector | 35 / 25 / 86 断言通过 | 双向标签、缺读/计数重置、失败与空集合、原 lease 到期 |
| 路由器原 Lua/库执行上述四组 | 344 断言通过；27 文件语法通过 | 独立 RAM 目录，拒绝真实 native/tc/nft I/O，清理成功；不把与本地重复的断言再计一次 |
| 其它已有小模型 | 标签 20、生命周期 25、guard 26、efficiency 通过 | 原策略保护，非压力或故障实测 |
| 实际回执 C 源码 / 实际选择函数 | 137 / 13 断言通过，warnings-as-errors | NSS transport 与 CT/clock 被替换，非固件回执实测 |
| ARM64 Linux 6.18.44 交叉构建 | 两候选模块成功 | 原 ECM/IGS 代码段一致、输入模块匹配现场；kernel 配置/符号表未改，routerConnected=false/binaryLoaded=false |
| 真实候选采集器只读执行 | 六查询成功、0.05 秒 | 用户自然现场、无配置/hook/服务变化；未知最坏尾延迟 |

候选 gate SHA256 `ad11698c01c8121fe196aec03190bcaf0dab03880c41ea8c8f0ecab0fda3e47c`，receipt provider `fd7d4bd1556e10b283b120f4212c4f87388f7261526947189519f37cb4b45411`。模块及私有回退资料仅本地保存；公开证据保存 build-result 与源哈希，不包含二进制。

## 可执行的后续验收与许可边界

下面涉及共享网络的切换步骤**尚未执行，必须另获用户明确许可**；本次代码推送授权不等于维护窗口授权。

1. **单次维护窗口部署**：先 status，核对仍运行的 owner/模块/配置哈希并备份已安装入口、Lua、build-result 与模块；保持既有独立 guardian 和历史回退备份。使用既有 stop，并等待本事务完整恢复确认（不是命令退出即算成功）；原五 WAN/认证/PBR/NAT/软件 CAKE/autorate/代理/Tailscale 和管理可用后，再成套安装候选 receipt/gate、已校验 ECM/IGS 包及 Lua，使用现有服务 start。无需刷机或路由器重启。任何 UNCONFIRMED 不强卸载、不伪造 ACK，保留现有阻止恢复机制。
2. **自然流量验收**：只运行一次默认轻量 `diagnose 60`，确认模块新导出/状态字段及源哈希，逐项查看分类→身份/lease→当前 CREATE→两方向标签→全局字节；检查 pendingRt/rejectedCache/recovery、六秒租约余量及受保护服务。没有自然满槽/失败事件就记未验证，不能用无压力短窗宣布固件恢复已通过。
3. **满槽与恢复**：如自然出现满槽，核对每个等待 RT 最多一个撤销位置；若自然 CREATE 失败/DESTROY 事件出现，记录一次精确代际的撤销终态、1/3 秒退避、至多两次再创建，以及当前 CREATE/标签后续结果。回执丢失/TX_FAILED 或 ECM 不再次选择，作为失败保留；主动故障只在另获许可的隔离环境验证。
4. **Wi-Fi 同设备游戏+下载**：自然负载下按已识别游戏端口与同客户端下载区分 CT，关联端到端延迟/丢包和现有 station/TID/AC、队列统计。需要启用调试统计或用其它适配器监听时先确认具体方法；不把生产 AP 改 monitor、不改 WMM/无线参数。上行还需看客户端 WMM/DSCP 与 airtime，避免用路由器标记替代该证据。
5. **有线 FDB**：至少一条自然持续 70 秒以上、当前 CREATE 有效的有线流，将 FDB age、CT 软件字节、可归因硬件进展与撤销原因对齐；逐 LAN 口在自然流量可得时补齐。若证明 NSS 快转导致超过 60 秒而软件误撤销，再设计保留移动/身份失效保护的最小修复。
6. **覆盖与开销**：先补可比较的同 CT cohort 硬件字节入口，明确 RX/TX 对应方向、窗口和二层/三层口径；BE 必须有全体基线，不能拿 candidate projection 作分母。合并一次自然样本观察 collector commands、reader publication/encoding、CAKE 十查询和实际 lease 余量，与来源暂停时刻对齐；若足够定位就不追加多轮 CPU/故障测试，不扩大租约或增加缓冲。

未解决项目按优先级保留在 [KNOWN_FAILURES](KNOWN_FAILURES.md)；PR 保持草稿，不合并。
