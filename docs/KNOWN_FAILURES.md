# 当前 P0：旧 ABI1 引用未释放，完整回退未确认

本次重新启用最大 NSS14 后，五条规则删除回执缺失。精确恢复请求实际得到五个 ENACK4/error5 NO_ENTRY；固件无这五条规则，但旧 gate 只接受 DESTROY ACK，自引用5/ECM CI5仍在。软件队列、WAN模式与保护服务已恢复，NSS0、准入关闭。此前“没有未确认回退P0”仅属历史交付快照。

ABI2 精确删除请求/独立固件不存在状态已实现，134 C mock/目标writer-NFT模型/目标解析/编译通过并保存，未加载；P0不能据此关闭。规则为何先在固件中消失尚无直接通知证据。普通模块卸载不能通过；不强卸载/伪造ACK/修改内核内存，重启需要用户明确授权。P1真人游戏、Wi-Fi station/字节覆盖/长期CPU及开机验收仍未通过。

## 以下为本次启用前的历史记录，不代表当前状态

# v2 当前问题

本批恢复全部确认，没有未确认回退的P0。uint32/errno/full snapshot、qdisc kind/root filter、NFT空表及同CI重新CREATE旧ACK问题已修复并定向验证。物理NSS root无tcf block，用自有clsact完成软件上行标签。96 receipt mock及最终模块加载通过；IGS partial-bind故障仅mock，未现场注入。

P1仍为三类游戏质量、同机Wi-Fi固件队列、符合资格流NSS字节覆盖及混合队列质量；用户延期真人测试。手动procd/持有3条NSS时owner退出恢复已通过，实际开机和长期CPU/softirq未测。現网仍用旧Windows continuous，.207/三槽/LAN4/旧预算仍存在；停用的新候选不等于生产已经替换。

## 以下保留历史，旧范围及“当前”不得覆盖上方事实

# v2 当前未关闭问题

P1：全宿舍有线/Wi-Fi 游戏稳定及下载利用余量尚未验收。旧 NSS 仍固定 .207/Windows/三槽/LAN4，旧 DOWN18/UP60 只是实验预算。新影子流表与软件状态撤销已运行验证，但没有动态 native permit、固件逐流 ACK、无线队列和共同容量控制。旧健康 90 秒/四次限制已取消，不重复修复。

本批 P2 启动环境问题集中修好：缺 nohup 改用 nixio fork/setsid，nixio 权限改为八进制字符串，start 必须确认新心跳，成功停止不发布 error=nil。最初失败输出保留本地；没有进入 NSS、修改队列或网络配置。最终目标运行中的 stop/rollback 及清理通过，无本批未确认恢复。

procd 常驻、自启、独立 native 守护和长期负载未验收；20 项模型与约两分钟影子观察均不能冒充三类真实游戏结果。见 [STATE](STATE.md)。

## 以下为历史记录

# 连续常驻批次：P2已修，体验P1仍未关闭

夹具config.seconds、停止helper及发送器signal.alarm182与360秒寿命不一致，本批集中修复；失败输入和恢复均保留。源码绑定拒绝发生在连接前，独立新目录只读恢复核验通过。最终跨期限集成和主动停止/完整恢复通过，当前没有由本次实测证明的未恢复P0。

用户下载时游戏高丢包仍为未关闭P1；RT-only模拟不证明下载体验修复。常驻不等于所有新流都加速，未知/不支持流保持软件路径，ECM自然撤销仍结束当前epoch。[实现、实测与限制](RESIDENT_CONTINUOUS.md)

## 以下保留历史记录

# 当前问题分级：准入集成已通过，体验P1仍未关闭

新optional native实际RT mask2已90秒/ECM1/30续租，完整恢复通过，独立准入开发批次完成。P2旧模块绑定在fork前拒绝已纠正，原失败/首次checkpoint/恢复保持；16本地守护执行检查覆盖旧错误和错误hash/大小/boot/ECM状态。收尾脚本两种固定frontend状态假设与初始队列快照误用仅本地更正，不制造硬件失败结论或重跑实验。

未关闭P1：用户大下载时游戏高丢包，本次模拟不证明体感修复。已知限制：最多2BULK/1RT，直接进程归属IPv4客户端，有限90秒代/20分钟四次；其它mask仅模型与历史核心证据，未硬件逐一验收；未知/代理/IPv6/QUIC保持软件路径。非关键环境取得/报告细节进入backlog，不阻止保留已通过的候选。[实测与限制](../evidence/resident-independent-admission.json)。

## 以下保留历史记录

# 当前blocker与限制：独立准入现场集成待自然负载

P1：新optional-slot native尚未现场集成，用户大下载游戏丢包仍未关闭。已有正常三流/五WAN/CPU证明不重做。P2：固定组合/不同WAN限制、初始probe诊断丢失、旧startup byte-exact断言本批一起修复，集中本地回归通过。dev-g原拒绝确实已有checkpoint/stage，native和NSS尚未放行且最终恢复通过；缺少原详细probe，精确原因未知，不追溯标为“无写入”或“CT退出”。

dev-h准备期失去准入只有在完整证明无NSS＋stage清理＋保护和两物理恢复通过时返回等待；未知错误/已进入NSS错误仍暂停，P0恢复优先。七种组合仅模型资格，实际无候选不当成功。其它非阻塞限制：有限代而非连续永久NSS；最多两BULK/一RT；单PC直接IPv4；其它协议/代理/全网和高阶功能后续。见[本批事实](../evidence/resident-service-dev-h.json)。

## 以下保留历史记录

# 当前接续：dev-g已恢复自动观察，当前RT1／BULK0

2026-10-08 13:32只读快照：CS2 RT1，下载BULK0、组合0；控制器运行，准入未暂停，三次读取成功且来源序列推进，实际ECM关闭全零。使用 work/resident-service-dev-g-20261008/service.ps1 Status / Stop / Start，先核对状态，不重复启动。启动完整健康和两物理原队列全部选项/handle通过。下载保持，不操作游戏或制造流量，heartbeat仍暂停。

13:18完整分类和本机socket匹配已确认CS2 RT在WAN3，约197pps、1.26Mbps。旧RT0仅表示当时未匹配合格候选；早先快照缺记录的精确原因未证明，不能据此认定游戏无UDP或CT退出。dev-f 13:15另一次真实入口在Windows socket查询后source6过期，checkpoint/stage前退出；中间恢复审核拒绝原输出保留，最后完整审核和原物理队列恢复通过。

本批只修P2读取时序对P1准入的影响：首次分类只发现端口，Windows精确归属之后读取最终分类，分别保留source6和OS6，完整计入最终网络耗时；owner变化、query倒退及未查过端口仍拒绝。119入口＋61服务本地检查、实际Lua5.1语法、34 JS／2 PS通过。六份其它数据面Lua保持RC1、classifier.lua保持dev-f，分类/QoS/期限/checkpoint/独立恢复不改。仅切换已有手动任务启动参数，两个其它任务保持。

新候选现场只读来源3.04秒及当前1.23秒通过，完整90秒NSS集成尚未完成，游戏丢包P1仍待闭环。最短路径仅接续已有自然下载＋RT；缺合格组合则等待，不新增fixture、边界、CPU或QoS实验。见[本批事实](../evidence/resident-service-dev-g.json)。

## 以下保留历史记录

# 当前blocker：发布读取持续运行P1，体验P1待闭环

dev-e普通Steam／CS2已NSS3／54.07秒／18续租，因stable读取时inode更换中断，完整恢复通过。具体旧失败文件未记录；不推断固件故障、CT退出或游戏丢包根因。dev-f本地复现并给分类发布通道一次50ms内重读，未知IO、owner/config变化及第二次更换仍拒绝，未放宽任何TTL。165本地检查通过，候选真实完整90秒仍待已有流量。用户自报约1%以内且好转，回复在恢复后，P1体验尚未关闭。排序和空候选处理P2同批完成，非新正式版本；其余非阻塞限制保留backlog。见[本批事实](../evidence/resident-service-dev-f.json)。

## 以下保留历史记录

# dev-d：常驻异步路径错误已修复

北京时间2026-10-08 11:59。dev-c在11:49心跳后因连接初始化临时切换工作目录，异步心跳写到外部目录并发生ENOENT退出；当前进程不存在，0新NSS代。原失败、源码和空锁全部留存。路由器ECM停止且连接/加速/待处理计数全零、gate不存在，旧代恢复通过后才接续。

修复同一P2层：服务存储、心跳、锁/停止检查与进程路径固定到模块所属工作区；只读审核子进程显式cwd；启动器刷新并严格返回子进程退出码。48项服务本地回归及11 JavaScript/2 PowerShell语法通过，原异步目录错误本地复现，退出码7实际子进程检查通过。正常入口、七份数据面、分类、QoS、全部准入/期限与独立恢复保持。

当前dev-d控制器已运行并通过启动只读完整审核和两物理队列检查，源序列继续推进，准入未暂停；WAITING_FLOW，下载TCP BULK为0、游戏RT为1、新NSS代0。这是进程恢复，实际NSS仍未加速。用户下载时60–70%丢包仍为未关闭P1，不能宣称体验已修复。继续接续原正常负载，不启动游戏、制造fixture或重复数据面/CPU实验。控制入口为[dev-d service.ps1](../code/work/resident-service-dev-d-20261008/service.ps1)，[本批摘要](../evidence/resident-service-dev-d.json)。

## 以下保留历史记录

# 当前P1体验问题与已修P2

P1：用户实际下载时人物回弹、丢包升至60–70%，下载降速后消失；具有负载关联，原因与NSS改善未证明。P2：11:15 WAN查询Lua管道读空后解析崩溃，checkpoint/stage前拒绝；中间审核失败和随后最终恢复通过都保留。dev-c已替换只读输出接收并保存原始命令结果，65入口/37服务本地检查及三WAN只读查询通过。未知错误仍拒绝，未开放更宽资格或生产重试。见[修复摘要](../evidence/resident-service-dev-c.json)。

## 以下保留历史记录

# 常驻调度 dev-b 已恢复运行；下载时游戏卡顿待核验

2026-10-08：用户报告人物回弹、延迟或丢包升高。首次自然流入口因UDP资格在下一次读取前消失，在checkpoint前退出，无生产写入；原完整恢复及两物理队列全部选项/handle检查通过。当时NSS未进入，不能把卡顿归为NSS转发故障。

修复P1调度问题：只有原入口明确证明无候选、无checkpoint、恢复通过及ECM全零，才返回等待新鲜自然流；未知失败、进入后的错误、绑定变化和P0仍停止后续准入。37项本地回归、10份JavaScript和2份PowerShell语法通过；原每20分钟四次及source6/native120/owner180/client180不变。没有新正式硬件轮次、fixture或CPU benchmark。

同名手动任务只改为dev-b启动路径，其它相关任务及触发/重启/终止设置未变。控制器已恢复运行、准入未暂停。当前控制入口为 work/resident-service-dev-b-20261008/service.ps1；进程运行与实际NSS命中分别核对，不能把等待合格流当作NSS已开启。实际状态快照见[本批记录](../evidence/resident-service-dev-b.json)。

只读18.10秒记录约405Mbps物理WAN下行、CPU忙碌84.17%、softirq62.75%、CPU0 time_squeeze增加729。游戏WAN1优先队列新增丢包0，下行排队峰值0.379ms；这证明存在软件路径处理压力，尚未证明端到端卡顿根因或体感恢复。未改学校认证、PBR、NAT/mark/affinity和十CAKE。

下一步仅观察用户原有对局和下载下的自动准入及体验；历史数据面、QoS、CPU和恢复证明复用。不启动/操作游戏，不制造新的fixture。

## 以下保留历史记录

# 2026-10-08 10:35 — 手动常驻部署批次

真实进程启动/分类源推进/停止/重启通过，已保留WAITING_FLOW；当前0合格组合/0新NSS代。原入口与数据面不变，18本地检查通过，模型计时和Windows任务属性两处P2原失败留存。只复用历史硬件证据，未新增硬件轮次。见[部署与限制](RESIDENT_SERVICE.md)。

## 以下保留历史记录

# 2026-10-08 08:10 — 正常流常驻控制器批次

正常流入口和四代有界常驻协调通过，实际COMPLETE，恢复通过。57本地检查集中收敛P2，四代协调的实际时长与限制见[正常流控制器](RESIDENT_NORMAL_CONTROLLER.md)。数据面/CPU历史证据复用；不逐bug创建硬件版本。

## 以下保留历史记录

# 当前开发批次：常驻控制器 RC1

北京时间2026-10-08 00:41。P0未观察到，当前已完成90秒集成及完整恢复；较长soak状态为COMPLETE。P1低速整形BULK丢资格已用当前大包/ACK证据保留修复，24项Lua回归及30次实际续租通过。P2部署绑定、inode缓存、最终学习读取竞态与其它入口修复在同一开发批次完成；不为每个软件bug新增正式实验。环境取得拒绝、固件精确计数解释及长期默认常驻移至后续，不当作已证明NSS缺陷。详见[当前范围](RESIDENT_CONTROLLER.md)。

## 以下保留历史失败记录

# 当前主线阻塞与本地修复

## LOCAL-ADDR-001：地址查询失败导致分类器自动重启

状态：NSS35 已安装有界故障恢复修复，独立回滚验收通过；底层阻塞/信号原因未定，未提交上游。

- 历史部署：NSS33，代码保留在 `code/work/nss33/worker.lua`。
- 原现场日志：2026-10-03 15:54:43、16:00:11（北京时间），2 秒 timeout 包裹的 `/sbin/ip -j -4 address show` 最新保存返回码 143、输出为半截 JSON。
- 原处理：`direct()` 非零断言 → 地址发现失败 → watch 退出 → procd 重启，producer 与分类历史变化。
- 原查询随后 8 次只读调用约 10 ms 成功；没有失败当时的内核栈或信号来源，不能断言 RTNL/CPU 是根因。
- 修复：原命令仍限定 2 秒，由既有 group runner 清理整个子进程组；仅确认清理后才发布无候选 degraded、恢复自有软件规则并重采样。未确认清理和未知异常仍终止。Guardian 没有接受携带旧 snapshot、未恢复或过期的 degraded 状态。
- 最小可回放：`tools/replay_classifier_recovery.py` 覆盖返回码、半截 JSON、无候选发布、守护拒绝、未知子进程状态；`code/work/nss35/test-query-native.mjs` 的目标内存 fixture 覆盖真实超时和派生子进程回收，依赖私有连接封装，不能直接作为通用部署脚本运行。
- 修改前后证据：历史两次 respawn；新逻辑 136 项分层检查、两个 35 次健康轻负载窗口、一次真实 180 秒自动回滚与重新部署。并未给生产常驻进程注入地址失败，也未自然重现原始阻塞；不宣称已证明高负载/长期稳定。

这是本工作区分类器的本地恢复问题，尚无证据把它写成 NSS/ECM 上游驱动缺陷。继续保留为研究记录，未经最小复现和归因不提交上游 Issue/PR。

## LOCAL-ADMISSION-001：通用超时文案掩盖具体准入原因

状态：NSS36 精确拒绝处理已通过 212 项准入检查；新真实尝试记录 44 次时间余量拒绝。NSS33 历史失败仍不回溯归因为同一原因。

- 缺少所选 RT 候选、来源过旧，均可能最终报 `Insufficient fresh-classifier margin for complete ABA`。
- 原失败没有逐次拒绝记录。不能从这一句推断 CPU 性能不足。
- NSS36 保留 `initialAlignment.probes`，记录时间、结果、原因与 retryable。只有三种精确的本地时间余量失败可以重试；所选身份/类别先核验，其它错误立即结束这次尝试。
- 108 组新旧差分和 66 历史包络保持准入结果相同；完整 212 项回放入口为 `tools/replay_mainline_admission.py`。代码见 `code/work/nss36/classifier.lua` 与 `fast-path.lua`。
- 有效期、独立截止和默认拒绝规则均未放宽；没有本轮新的 fast path 验收。

## LOCAL-PUBLICATION-001：采集/分类发布时间挤占初始准入窗口

状态：仍缺真人高负载闭环验收；NSS37 已安装等价属性解析优化，目标内存证明解析 CPU 成本下降，不属于已证实的上游 NSS 缺陷。

- 最小现场证据：NSS36 真实同 WAN CS2 UDP + Steam TCP，初始约 5.93 秒中 44 次时间拒绝，gate/ECM 均未开启；WAN/队列独立恢复。
- `classifier.lua` 的 pair 学习屏障要求 query age <2 秒，ready 再预留 tag 设置时间而要求 <1 秒。没有改变这些边界。
- 后续独立只读窗口 publication delay 0.77–1.21 秒、完整检查最高 0.26 秒；所选游戏已不在候选，不能把该窗口当原失败完整重放。
- `conntrack-source.lua` 的 normalize 与 `classifier-core.lua` 的行解析是已测到的开销：单次目标 RAM 分解为 0.55 / 0.28 秒，另有真实查询 0.28 秒。样本 455 行，未优化版本，未跟踪生产 worker 的全部阶段。
- worker 同步 fallback 规则维护和审计可能延长采样间隔，但没有阶段计时证明它解释了每次长间隔。结束审计一次来源过旧、随后通过，producer 未变。
- NSS37 的最小代码改动为 `code/work/nss37/conntrack-source.lua / attrs()`，基线在同目录 `original-conntrack-source.lua`。`tools/replay_normalizer.py` 可独立执行 9,085 项合成输入检查；私有真实采集文本另增加 2 项，总 9,087。两版本在本地 Lua 5.1 对相同输入做输出及拒绝比较，不连接路由器。
- 目标机 16 对内存交替测量中，204 行真实文本 CPU 平均 27.043 → 15.470 ms，512 行合成文本 64.393 → 38.408 ms，全部输出相等。180 秒独立回滚验证后重新部署保留；详见 `evidence/nss37-normalizer.json`。
- 这是本地分类器性能优化，只证明该解析函数的成本。NSS36 高负载 0.55 秒与 NSS37 轻负载毫秒值不能直接相减；没有完成相同高负载的全发布路径比较。同步软件维护是否拖长周期仍是待验证假设。
- 下一步只读验证高负载新鲜度与入口余量；不得丢字段、缩小范围、延长 TTL 或改时间基准绕过问题。没有驱动级最小复现，不提交上游 Issue/PR。

## LOCAL-ADAPTER-001：重复完整校验增加准入观察开销

状态：NSS38 本地候选与目标 RAM 微测量通过；未安装、未完成当前控制器完整绑定。

- 对应本地仓库的 `code/work/nss37/classifier.lua`：`current()` 先 inspect，`ready()` 的 pair / `candidates()` 又 inspect 同帧。
- 最小回放：`tools/replay_adapter_candidate.py`，固定时间、模拟文件系统/身份，1,470 决策对照、5 调用次数检查、230 准入/诊断案例。不连接路由器。
- 核心候选 `code/work/nss38/candidate-classifier.lua` 仅消除 ready/observe 的第一次重复 inspect；sample/续租/精确撤销保持原合同。更宽的首次修改改变撤销错误形态，已弃用。
- 目标 Lua/jsonc 同输入交替 12 对：32/64 候选检查 CPU 减少 26.4%/27.1%。真实失败后的密集诊断自身 CPU 8.434 秒/12 秒；不同负载与时间，不能由此证明重复校验是原失败的唯一原因。
- 带诊断候选另外记录序号/来源年龄/发布与检查用时，历史四字段探针格式不变。诊断字段从不授权，来源无效仍原样拒绝。尚无候选现场 NSS 成功证据。
- 这是自有控制器代码，不是 NSS/ECM 驱动缺陷，无上游 Issue/PR。

## LOCAL-QDISC-READ-001：规则维护的队列读取失败导致 worker 重启

状态：NSS38 现场一次观测，未定位原始阻塞或信号源，尚无修复/上游提交。

- 现场：2026-10-03 22:27:08，2 秒 timeout 包裹的 `/sbin/tc -j qdisc show dev rpwan1` 返回 143，日志含 `Terminated`。
- 对应文件：`code/deployed-classifier/worker.lua` 的 `direct()` / `queue()` / `withMutation()`；`backend.lua` 的 `freshKnown()` / `reconcile()`。堆栈位于维护前的队列查询。没有写批次失败证据，不能概括为 CAKE 规则损坏。
- 原始结果：apply 子进程失败、worker 退出；日志确认 exactRecovery，procd 自动恢复，guardian 原进程持续存在。最终自有规则与现网审核通过，ECM 一直关闭。
- 随后同一查询 8 次约 10 ms、RC 0，未复现原失败。没有失败期间栈/信号来源，不能判定 RTNL、CPU、NSS 驱动或解析器为根因。
- 最小复现目前只到日志触发链；下一步须离线覆盖读取超时、半截输出、外层取消以及可能已部分变更的维护阶段。未经清理和精确恢复证明不能原地继续，不能复用旧快照或延长期限掩盖问题。
- NSS35 仅处理地址发现的已知有界故障，这次队列读取不在该恢复范围；现有未知错误退出行为仍符合默认拒绝原则。最终健康不等于完整生命周期通过。


## LOCAL-TC-002：超时监视进程与外层回收

NSS39 已保留局部监督修复，保持原截止及失败终止。详见 [复现与证据](ISSUE_TC_SUPERVISION.md)。不能把本地复现提升为 NSS38 自然阻塞的完整根因，也不能宣称高负载长期稳定。冷启动旧 producer 的观测会被就绪门槛拒绝，不能只检查 status=running。


## LOCAL-AUDIT-003：高负载写前完整快照审核过期

NSS40 实际入口在 operational-audit.lua:32 拒绝，尚未 checkpoint/生产变更。此前约 323 Mbps 下，compact 初始只读准入 4/94 次通过；不能推导 full snapshot 稍后也新鲜。原拒绝没有记录具体年龄、阶段耗时，完整根因未知，不归因于 NSS 驱动。

代码顺序确认 compact 先发布、同步软件维护/审核完成后才发布 full snapshot，外部审核也持同一事务锁。该顺序是可能的时序因素，不是现场完整因果证明。新只读审核诊断保留原全部断言和固定截止，记录阶段/年龄；轻载 0.29 秒通过只证明新诊断可运行。下一轮先整合诊断，不持锁等待新发布、不放宽有效期、不吞错。

NSS40 原始应用 latest 被后续刷新；已新增按次封存工具并验证，历史缺失明确保留。NSS38 精简 adapter 在 NSS39 已绑定（68 项），其历史“未安装”状态只适用于 NSS38 当时；仍无真人高负载闭环验收。
