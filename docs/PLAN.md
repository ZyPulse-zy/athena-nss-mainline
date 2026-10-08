# 当前最短路径：dev-f正常负载一次有界集成

当前milestone是可复用常驻Multi-WAN controller。局部发布读取P1已本地修复，165检查／启动审核通过；原dev-e实际NSS3及完整恢复已成立。只接续现有下载和游戏RT做一次90秒候选集成，先确认完整撤销／审核再允许下一代；未知错误仍暂停并定位，P0优先恢复。12:28暂无合格RT，常驻等待不制造流量。用户要求保持下载，不操作CS2／Steam。体感好转尚非稳定验收；通过后结束本开发批次，不新增边界、CPU或QoS证明。见[状态](STATE.md)。

## 以下保留历史记录

# 当前最短路径：原正常负载的实际NSS准入

P2异步路径退出已修并恢复dev-d；当前RT1/BULK0，真实NSS未进入。下一步只接续用户原下载/RT，核对实际命中和体验；游戏丢包P1仍未关闭。原数据面和期限保持，不增加正式实验、fixture、游戏操作或CPU证明。见[STATE](STATE.md)。

## 以下保留历史记录

# 当前最短路径：正常下载 + RT 的自动准入与体验闭环

前置读取P2已修复并保留运行dev-c；原数据面/CPU/恢复证明复用。当前下载已降到0Mbps，RT1/BULK0，等待自然负载，不重开fixture或游戏。仍未完成P1：普通下载负载下60–70%游戏丢包的消除；只有实际NSS命中、用户体验和恢复记录支持时才能关闭。源码及事实见[当前状态](STATE.md)。

## 以下保留历史记录

# 常驻调度 dev-b 已恢复运行；下载时游戏卡顿待核验

2026-10-08：用户报告人物回弹、延迟或丢包升高。首次自然流入口因UDP资格在下一次读取前消失，在checkpoint前退出，无生产写入；原完整恢复及两物理队列全部选项/handle检查通过。当时NSS未进入，不能把卡顿归为NSS转发故障。

修复P1调度问题：只有原入口明确证明无候选、无checkpoint、恢复通过及ECM全零，才返回等待新鲜自然流；未知失败、进入后的错误、绑定变化和P0仍停止后续准入。37项本地回归、10份JavaScript和2份PowerShell语法通过；原每20分钟四次及source6/native120/owner180/client180不变。没有新正式硬件轮次、fixture或CPU benchmark。

同名手动任务只改为dev-b启动路径，其它相关任务及触发/重启/终止设置未变。控制器已恢复运行、准入未暂停。当前控制入口为 work/resident-service-dev-b-20261008/service.ps1；进程运行与实际NSS命中分别核对，不能把等待合格流当作NSS已开启。实际状态快照见[本批记录](../evidence/resident-service-dev-b.json)。

只读18.10秒记录约405Mbps物理WAN下行、CPU忙碌84.17%、softirq62.75%、CPU0 time_squeeze增加729。游戏WAN1优先队列新增丢包0，下行排队峰值0.379ms；这证明存在软件路径处理压力，尚未证明端到端卡顿根因或体感恢复。未改学校认证、PBR、NAT/mark/affinity和十CAKE。

下一步仅观察用户原有对局和下载下的自动准入及体验；历史数据面、QoS、CPU和恢复证明复用。不启动/操作游戏，不制造新的fixture。

## 以下保留历史记录

# 手动常驻试用进程已部署

北京时间2026-10-08 10:35，常驻进程已保留运行，当前为WAITING_FLOW。18项本地回归、8份JavaScript和2份PowerShell语法通过；真实启动、分类源推进、正常停止/锁解除、重新启动通过。四个已有相关任务的XML指纹未变，新任务无登录触发、无故障自动重启，使用普通用户权限。

进程每30秒观察已有流量，合格时调用原正常入口，每代90秒；每20分钟最多开始四代，每代新checkpoint下载/SHA/gzip和控制连接外独立恢复，恢复审核通过后才进入下一代。source6/native120/owner180/client180与全部原字节限制保持。原四代900秒控制器/360秒累计NSS、五WAN/QoS/CPU证明复用，不重跑数据面。

当前实际合格组合0、新NSS代0。两次启动前完整只读审核及两物理队列选项/handle通过，ECM关闭全零、五WAN健康、保护配置不变。这次证明的是常驻进程和正常停止/重启；真实普通负载的首次自动准入与更长soak尚待自然出现，不声称连续永久NSS或默认开机常驻。实际[部署结果](../evidence/resident-service-runtime.json)。


详见[使用及限制](RESIDENT_SERVICE.md)。

## 以下保留历史状态

# 正常流入口和四代有界常驻协调通过

北京时间2026-10-08 08:10。沿用 RC1 已证明的数据面，接入正常本机进程/socket归属和当前自动分类；controller自身不启动游戏、下载或测试流。只有两条不同自然WAN的TCP BULK和一条已准入UDP RT可进入原三槽NSS，其它/未知/归属不明确流保持软件路径。

本批57项本地回归及15份源码语法检查通过，集中修复清理重入和部分启动目录登记等P2。七份数据面Lua逐字节复用RC1，没有重复五WAN、QoS或CPU实验。

预定四代各90秒、controller900–1200秒。实际状态 **COMPLETE**；控制器运行 **900.14秒**，完成 **4代**，NSS累计 **360.02秒**。每代独立下载/SHA/gzip checkpoint及写前恢复守护，完整撤销后才进入下一代。终态ECM关闭全零、五WAN健康、保护配置及两物理原队列全部选项/handle一致，端点规则和自有客户端残留0。实测明细见[结果](../evidence/resident-normal-controller.json)。

该集成由独立自有模拟器提供正常socket和连接轮换，未操作CS2/Steam；这是正常入口集成与有界协调证明，不声称第三方应用全面覆盖、连续15分钟NSS或默认永久常驻。


详见[正常流控制器](RESIDENT_NORMAL_CONTROLLER.md)。

## 以下保留历史状态

# Athena NSS Development Mode：有界常驻控制器 soak 通过

北京时间2026-10-08 00:41。当前交付目标是可复用、逐步常驻的 Multi-WAN controller。使用同一 RC1 批量修复并本地回归，没有新增正式实验版本；五 WAN NSS、QoS、NAT/mark/affinity 与 CPU 历史证据继续复用。

当前 P0 未观察到；原 P1 是低速整形后的已知 TCP BULK 被重新归为 BE。候选只在近期 BULK 记忆仍有效且当前存在大下行包和小反向 ACK 时保持 BULK；冷流、未知、空闲、身份变化、计数重置或过期仍拒绝。24项实际Lua回归复现旧故障，90.01秒/181采样/ECM3/30续租与完整恢复通过。

同批清理 P2：整数 timeout、唯一命名空间、当前部署绑定、publication读取缓存、checkpoint后最终选择，以及预检查与最终读取跨截止的等待竞态。最后一项以单次严格最终读取替代两次检查；仅三种既有时间余量拒绝可在原20秒窗口等待，3/3.25秒学习余量及source6不变。16项实际Lua回归和完整打包通过。

soak预定为控制器至少480秒、最多720秒，两代各90秒；新代只在上一代完整恢复后启动，各有新checkpoint/SHA/gzip及独立恢复。实际状态：**COMPLETE**，通过：**true**。每一代的NSS时长、续租和恢复见[聚合结果](../evidence/resident-controller-rc1.json)。此范围包含代间软件恢复，不声称连续长期NSS或默认永久部署。

默认常驻仍关闭。保留现有硬截止，先交付这一可撤销的有界控制器；后续长期默认运行单列为下一milestone，不主动增加边界、故障注入、CPU、Wi-Fi、autorate或ECN实验。


详见[控制器使用与已知限制](RESIDENT_CONTROLLER.md)。

## 以下为原样保留的历史状态

# 最新状态：五 WAN 入口闭环完成；常驻候选已修复程序错误，资格不足退出并恢复

更新：北京时间2026-10-07 21:47。v54真实可复用入口3421绑定，四TCP BULK WAN1／2／4／5＋UDP RT WAN3，NSS B60.01秒／121采样／ECM5／20续租与完整恢复通过。旧入口未通过的记录为历史，当前入口闭环已完成。

仅自有SSH紧凑offer／控制短启动传输、写前启动意图和精确清理、提前实际CT自然WAN取得与整数timeout已接续修复。v58修正版9模型／3424绑定、11归属模型／9RAM／完整Lua语法通过；现网NSS68分类器不改。认证／PBR／mark／NAT／学校策略、source6／owner180／client180与全部原字节上限保持。

90秒常驻候选只改fast固定窗口与native原最大120秒，六份其它Lua／native／分类／QoS不变。v55自然配对未齐、v57timeout类型拒绝、v58实际五WAN连接已齐但仅3BULK＋1RT，均在NSS checkpoint／stage前退出；90秒常驻硬件尚未通过，没有永久／长期NSS。缺失投影不当真实改类或CT退出，不能硬放行；不无条件重开fixture。

原失败与v55 UNCONFIRMED结果保持，后续精确端点只读证明已补齐。最后完整source1.76／selectors12，五WAN健康／ECM关闭全零／保护配置不变，两物理原队列全部选项与handle、端点基线与自有进程0通过，RESTORED／无锁。无CS2／Steam、新CPU或新增下载；heartbeat仍暂停。用户常驻授权持续有效，后续只修有完整同query证据支持的问题，再完成常驻控制器的有界试用。

详情：[本次接续](ENTRY_REPAIR_RESIDENT_2026-10-07.md)。

## 以下为保留的历史状态

# 最新状态：载荷取得拒绝再次出现，现网完整恢复

更新时间：北京时间2026-10-07 19:25。有界只读定位得到原失败窗20行sshd-session日志；认证前关闭／重置与客户端未收首包同时出现，精确归属及根因未证明，未发现可证明限额／penalty因果的记录。原sshd标签0行与同窗口unit查找均保留。

一次同字节v45入口沿用24模型／3406绑定，初始四路payload约2.92秒齐备，保留TCP WAN1／3／4；tcp3第4候选原8秒首包超时，客户端30.36秒结束，13次匹配读／五WAN pair0，NSS checkpoint／stage／ECM前拒绝。没有放宽期限／重试，不继续重开fixture，完整入口仍未通过。

原FW180秒自然到期、端点关闭／规则0／基线、自有进程0与最终审核通过：source1.36／selectors4，五WAN健康／配置不变／ECM关闭全零，两物理原mq＋四fq_codel全部选项／handle一致，RESTORED／无锁。v42五WAN与高级QoS已验收范围保持，NSS68分类器不变，无CS2／Steam／新CPU，heartbeat暂停。

入口完成后尝试常驻NSS的用户授权保留；当前尚未达到该前置条件。SSH载荷取得限制保留，不升级为已证明的NSS／固件故障。详情：[本次记录](V47_TCP_ACQUISITION_2026-10-07.md)。

## 以下为已保留的授权与历史状态

# 当前推进顺序：入口闭环 → 常驻 NSS 试用

北京时间2026-10-07 18:46，用户明确授权入口完成后尝试常驻 NSS。接续工作按以下顺序推进，无需再次询问同一授权。

1. 收敛 TCP 候选首包取得问题。先使用 v46 已冻结的失败、socket／进程与时间线证据定位有依据的改动；保持原自然 WAN 取得方式、30秒窗口、8秒首包、重试及字节上限，不为配齐 WAN 盲重开 fixture。
2. 完成可复用入口的准入、进入 NSS、退出及完整恢复闭环。复用 v42 已验收的五 WAN／高级 QoS 核心与历史 CPU 证据，只验证当前入口改动直接影响的范围；继续使用自有 TCP＋模拟 UDP，不启动 CS2／Steam。
3. 入口闭环通过后，实施可撤销的常驻 NSS 试用。写前仍需新 checkpoint 下载/SHA/gzip、控制连接外独立恢复，保留分类失效退出与明确回到软件路径的方法；根据实际运行结果决定是否保留部署。方案和现场结果分别记录，现有实验期限不在本次授权记录中修改。

常驻试用沿用已验收的多 WAN／QoS 范围，保护 PBR、完整 CT mark/NAT/WAN affinity、MiniEAP/DHCP、singbox/Tailscale 与十 CAKE。Wi-Fi／autorate／ECN、重复 CPU 门槛与故障注入仍不属于本次工作。当前尚未启用常驻 NSS 加速，heartbeat 继续暂停。

## 以下为已封存的实际状态

# 同字节v45入口接续：并发启动实测通过，候选首包超时，已恢复

更新：北京时间2026-10-07 18:38。原v45提交`07001d7d60670094c684ab029332ef58b8411a4f`已push/archive通过4910源SHA/5577文件/1480链接。端点只读恢复连接后，只复用24模型/3406绑定的原v45源码接续一次，未重跑核心准备。四初始PID约0.087秒齐备、四路第一次同时payload约10.71秒；并发启动已实测。

自然WAN去重替换tcp3/tcp4后，tcp3第3候选8秒无首包触发原上限，客户端24.57秒退出；完整五WAN pair0，最后分类读随退出拒绝。没有NSS checkpoint/owner/stage/ECM，完整最新版入口整合仍未通过；根因未知，不归因NSS，不放宽PBR/期限/重试或盲重开fixture。全fixture UDP1040/1025非NSS证据，边界未返不当NSS丢包。

原FW180秒自然到期后端点规则0/canonical基线/精确单位关闭通过，客户端与独立210秒guard退出、自有进程0。最终source0.98/selectors2、五WAN健康/保护配置不变/ECM关闭全零，两物理原mq＋四fq_codel全部选项/handle一致，RESTORED/锁解除。旧v45失败/源码/报告原字节保持，常驻NSS68不变，heartbeat暂停，无CS2/Steam/新CPU/永久NSS。

v42五WAN高级QoS核心硬件验收保持。下一问题仅为候选首包取得条件，不自动重开fixture或重复NSS核心；自然取得限制、SSH超时、v41差异和普通应用factory未验保持。详情：[本次接续](V46_ENTRY_CONTINUATION_2026-10-07.md)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下保留原历史记录，旧“最新”按当时解读

# v45提前取得候选通过，端点SSH写前拒绝；完整恢复

更新：北京时间2026-10-07 18:04。原v44发布`f3a4287094633477487682ff137465c9b1fcbc66`已实际archive读回4757源SHA/5419文件/1462链接。v45同样四条TCP同时启动、四个唯一PID发布后提前核对，24模型/默认inspect/3406绑定通过；最终首包、CIM/socket/CT、4BULK＋1RT、五WAN及全部原期限/恢复条件保持，七Lua原字节。

唯一入口尝试在端点控制SSH连接超时处退出，第一条只读端点checkpoint未返回，无端点/FW/client、fixture/NSS checkpoint/owner/stage/ECM。原失败保留；一次失败相关只读诊断恢复连接，端口/本次单位/自有fixture进程0；不能据此宣称SSH已修复。没有盲重开fixture，新启动时序尚未现场验证，完整可复用入口验收仍未通过。

本次最终审核直接通过：source1.34/selectors0，五WAN健康/保护配置不变/ECM关闭全零，两物理原mq＋四fq_codel所有选项/handle一致，RESTORED/锁解除。常驻NSS68不变，无CS2/Steam、新CPU或永久部署，heartbeat保持暂停。

更正v44旧字段标注：原TCP WAN1/1/2/4是native数组顺序，冻结socket映射的真实槽顺序为4/2/1/1、UDP3；原失败/证据/报告不改，五WAN未齐与写前拒绝结论保持。v42五WAN60.01秒/ECM5/20续租/2373RT全回的核心硬件证明继续成立。

本轮封存，不自动新增实验。新的显式整合需新可执行条件；SSH连接超时、自然取得限制、v41计数差异和普通应用未验仍记录为已知限制。详情：[本次记录](V45_EARLY_ACQUISITION_2026-10-07.md)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下保留历史记录；旧“最新”仅代表当时

# v44入口准入前退出，已完整恢复；五WAN硬件验收保持

更新：北京时间2026-10-07 17:36。执行权限恢复后，原v43提交`b0a3c47965ba7d0113b592f4049a2893005ee946`已推送并实际archive读回，4553源SHA/5209文件/1442链接。v43首次恢复尝试因本地路径替换漏尾部分隔符，在连接/fixture前拒绝；新v44分隔符修复15模型通过，旧失败不改。

唯一一次v44自有四TCP＋模拟UDP实际31.96秒，分类4BULK/1RT，TCP WAN1/1/2/4、UDP WAN3。原30秒自然取得窗口结束，未配齐五WAN，在NSS checkpoint/owner/stage/ECM前退出；客户端错误0，没有NSS B或新硬件验收，不放宽PBR/期限、不盲重试。

端点规则0/FW基线与客户端退出通过。最终audit固定label与先前只读记录冲突EEXIST，原失败保留；只在新目录补一次失败只读步骤，source1.22/selectors6、五WAN健康/配置不变/ECM关闭全零、两物理原mq＋四fq_codel选项/handle和自有进程0通过。可变ledger RESTORED，原RESTORATION_UNCONFIRMED结果原字节保留。

新`work/v44-unique-label-entry`以完整新runtime隔离最终输出，17模型/默认inspect通过，没有新流量；完整可复用入口现场验收仍未通过。v42五WAN60.01秒/ECM5/20续租/2373UDP全回与高级QoS功能验收保持；v41差异仍known limitation。常驻NSS68未改，无CS2/Steam、新CPU或永久部署，heartbeat仍暂停。

本轮封存，不自动开启新实验。自然取得未配齐是有界前提限制；最新入口候选待有新可执行条件时的一次整合，不强行重试。详情：[入口整合报告](BOUNDED_ENTRY_INTEGRATION_2026-10-07.md)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下为原历史记录，旧“未推送”和“权限不可用”只对应当时状态

# v43 发布接续：本地已提交，远端未发布

更新时间：北京时间2026-10-07 16:50。可复用入口的13模型、默认inspect、4553源SHA与暂存检查通过；本地候选提交`854e28b440ffbabc656c32e6d9c98956096e1ef8`保留。实际启动在Windows CIM身份检查处写前拒绝，没有新硬件会话。

CLI推送的凭据子进程因当前执行环境权限失败；GitHub写入接口随后要求批准，但当前批准策略为`never`，在执行写入前被阻止。远端最后确认仍为v42提交`c2319000d8963996edf3e3270efdf412c4204979`。**本次尚未推送，也未通过远端提交匹配的归档读回。** 原报错和发布输入留本地，不修改凭据、Git配置或批准策略。

下一步从这些本地提交接续：在允许GitHub写入的执行条件下完成发布与实际archive，再于能读取原Windows进程身份的条件下补一次新入口整合；不重跑v42核心证明，不操作CS2/Steam，不新开fixture碰运气。heartbeat保持暂停。

## 以下保留已有入口验证记录

# 多 WAN 可复用入口已接入；现场启动写前拒绝

更新：北京时间2026-10-07 16:36。v43新增默认inspect/status/run/stop入口，复用v42五WAN已验收数据面。13模型和默认inspect通过，模型3405绑定=原3354+51；七Lua原字节、分类/QoS/lease/恢复与字节上限保持。新命名空间/独占锁/同session停止支持显式一次运行，不自动连续新代或常驻。

实际run因当前Windows CIM进程身份不可读返回1，在独占锁、记录、负载、SSH/router/checkpoint/stage之前拒绝，状态IDLE；没有新硬件验收或现网写入。原首版9模型及其中不足以证明cutoff的错误用例已保存，修订13项用合法命名空间验证。失败与原输出本地保留，没有为了检查重开fixture。

v42五WAN60.01秒/ECM5/20续租/2373UDP全返回与完整恢复保持；v41计数差异仍known limitation，不重做CPU或旧核心证明。下一步只在能读取原进程身份的执行条件下补一次新入口整合，继续模拟UDP，不启动CS2/Steam；长期、永久、全网、WiFi/autorate/ECN留后续。heartbeat仍暂停。

详情：[可复用入口](BOUNDED_MULTIWAN_ENTRY.md)。

## 以下保留历史记录

# 五 WAN 模拟功能验收完成，完整恢复

更新：北京时间2026-10-07 14:52。v42自有四TCP BULK＋模拟UDP RT自然走TCP WAN2/3/4/5＋UDP WAN1，实际NSS五流60.01秒/121采样ECM5/20续租、双向十tag/leaf/完整ct mark/NAT/affinity通过。共享DOWN18附近四bulk合计16.70Mbps，UP60每WAN12硬上限/RT prio0/FQ-CoDel保持；内部57.06秒2373 UDP全部回包、RT上下leaf零drop，RTT中位/P95/P99约196.47/198.68/200.36ms。不是CS2/HUD/真人、新CPU或长期常驻证明。

v41原BE/cooldown退出和全部旧证据不改。对齐后PC交付与分类计数有差异，但SSH缓冲/计时限制使精确同步根因仍未知；本次没有修改分类、没有复现该退出，最多一次终止计数读取分支未执行。该问题保留known limitation/follow-up，不妨碍本次有界功能验收，不称已修复。

3354实际绑定、fresh checkpoint SHA/gzip和原独立恢复写前通过，bundle73138/exec8799/record634752在原上限内。NSS正常完整恢复后，端点关闭SSH超时导致监督器退出1，原失败保留；原独立期限后一次仅只读新目录重查确认精确服务/端口关闭、规则0/FW基线一致。最后完整audit source1.12/selectors6，五WAN健康、保护配置/epoch/ECM关闭全零；两物理原mq＋四fq_codel全选项/handle、自有进程全部退出。常驻NSS68原config、heartbeat暂停，无CS2/Steam操作。

**五WAN五流60秒与高级QoS受控功能验收完成，本轮停止新增实验。** 已知v41进入窗计数差异/偶发SSH取得超时/普通应用factory未验收留后续；不将本次等同全网、永久或长期部署。详情：[本次报告](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。

## 以下保留历史记录

# 五 WAN 首次同时 NSS 命中；60 秒维持未通过，完整恢复

更新：北京时间2026-10-07 14:15。v41使用自有四TCP＋模拟UDP，原自动分类自然取得TCP WAN2/4/5/3＋UDP WAN1；新checkpoint下载SHA/gzip与独立守护写前通过，五条实际NSS/ECM5、双向十tag/leaf/ct mark/NAT/affinity已取得。B仅3.90秒/6采样/0续租，不能标60秒验收。

同query完整帧证明四TCP仍同CT/mark/NAT/WAN，但类变BE/cooldown、约1506–1689Kbps；UDP仍RT。附近leaf四bulk合计17.00Mbps但计数窗不同，统计反馈精确根因未证实。控制器按原改类规则停止新学习并结束旧代；失败/完整帧/3303实际绑定原字节保留，不强续租或改tag，不把投影缺失当CT退出。

最终audit source1.16、五WAN健康/保护配置/epoch保持/ECM关闭全零；两物理原mq＋四fq_codel全选项/handle，独立端点FW基线与client/controller/guard/sender零残留通过。常驻NSS68原config、heartbeat暂停；没有CS2/Steam操作或新CPU/长期声明。

**已有v38两WAN60秒和v20高级QoS保持；五WAN60秒维持仍未通过。** 下一步只处理已观测的五流BULK分类维持边界，先核对计数窗再决定修正；不盲重试、不放宽阈值/期限、不中途强制改类。详情：[本次报告](FIVE_WAN_INITIAL_HIT_2026-10-07.md)。

## 以下保留历史记录

# 五 WAN 模拟前提有界拒绝，控制命令修正已封存

更新：北京时间2026-10-07 13:51。按用户“继续”推进五 WAN 同时 NSS，使用自有四 TCP＋模拟 UDP，不操作 CS2 / Steam。v39已完成轮换命令在30秒后被重复检查导致客户端退出；v40新目录仅修正旧命令无操作，四 TCP健康、错误0，但实际分类 WAN2/3/3/4＋UDP WAN2未满足五个不同 WAN，准入前拒绝。两轮均无checkpoint/stage/模块/ECM放行，不归因NSS/固件，不再盲重试或改PBR/门槛/期限。

3206/3254实际绑定冻结，五槽编译/63控制/68CT/14RAM旧证据复用；两次资格失败的原输出与源码保存。最后只读原audit source1.15、五WAN健康/保护配置/epoch保持/ECM关闭全零；两物理原mq＋四fq_codel全部选项/handle、两个端点FW基线与原客户端独立退出/零残留完整通过。

**v38两WAN模拟功能验收及v20高级QoS已通过的范围保持；五WAN同时fast path尚未通过。** 常驻仍NSS68原config，无永久NSS；heartbeat保持暂停。后续仍用模拟包，不以CS2作为测试前提。详情：[本次报告](FIVE_WAN_SIMULATION_2026-10-07.md)。

## 以下保留历史记录

# 模拟实时流跨 WAN NSS 验收通过，完整恢复

更新：北京时间2026-10-07 12:59。用户已停止 CS2 测试，后续使用自有脚本模拟游戏包。v38 实际 TCP BULK/UDP RT/TCP BULK走 WAN3/WAN3/WAN5；原自动分类、60秒 NSS / ECM3 / 20续租、双向六tag与bulk/RT leaf / mark / NAT / affinity通过。DOWN18共享借用保持，附近两个bulk约6.82/8.40Mbps；内部约57.17秒发出2443 UDP，全部回包，RT上下leaf零drop，RTT中位/P95/P99约199.92/200.79/202.51ms。是自有海外回包测量，非CS2 HUD/真人或新CPU证明。

新checkpoint下载SHA/gzip、原独立恢复写前通过；最终source2.03/selectors4审核、五WAN健康/保护配置/epoch保持，ECM关闭全零，两物理原mq＋四fq_codel所有选项/handle、端点FW基线、客户端/guard/sender完整恢复。Steam原下载暂停/临时限速关闭，CS2为0。常驻仍NSS68原config；没有永久NSS。

v35已做10本地/7RAM选择与失败帧修正但普通程序factory未执行；v36第二自有SSH首包超时在NSS前退出，v37本地转义目录拒绝在连接前结束，原失败不改。v38只有8秒/最多3次/前30秒未准入自有TCP取得；成功轮均attempt1，超时根因未知。2979实际绑定冻结，重查一次本机只读退出检查的父进程误报；未重做网络/NSS/CPU/gap或五流。

**受控模拟实时流的两WAN功能验收已完成。** 既有v1/v20与CPU证据复用；以后直接用脚本推进，CS2不再是必需条件。本轮封存、heartbeat仍暂停，不主动开启新轮次；五WAN同时fast path/长期常驻/多流公平/WiFi/autorate/ECN保留后续范围。

详情：[本次报告](SIMULATED_MULTIWAN_2026-10-07.md)、[硬件](../evidence/v38-simulated-hardware.json)、[终态](../evidence/v38-simulated-restoration.json)。

## 以下保留历史记录

# checkpoint 后三流选择通过；owner 最终准入拒绝，已完整恢复

更新：北京时间2026-10-07 11:56。v34实际Cache死斗＋已有Hades临时32Mbps，自动分类1CS2 RT/11Steam BULK/1跨WAN三流。准备native后才冻结TCP/WAN，新checkpoint下载SHA/gzip及后续BULK/RT/BULK选择通过；独立owner/暂存/物理QoS实际执行，但首次owner准入报`Selected class is not admitted`。gate模块未加载、ECM未放行、NSS B段和正常程序factory未验收。

13新顺序模型/2762绑定/61依赖通过，18＋14历史模型和v20数据面保持。最后PC帧是checkpoint后选择，不是失败时owner分类；owner完整失败帧缺失，具体slot/改类原因未知，不能推成CT退出或固件故障。原失败、checkpoint/守护/来源按字节保存，旧v33及全部历史code/evidence不改。

11:51完整audit source1.22/selectors2、五WAN健康/保护配置/epoch保持、ECM关闭全零；两物理原mq＋四fq_codel全部选项/handle恢复、stage/state/模块及实验进程零残留。原180客户端guard自然退出；Steam后来手动恢复，下载48%暂停0bps、原限速OFF/数字清空。重开又自动续传，累计严格180秒/720MB不成立。

软件HUD可见ping15/loss上下0、绿色网络图；数值jitter/Miss/真人体感未知。v20三流多WAN、高级QoS及历史CPU证据复用；下一步只解决已证实的正常下载选择到owner准入边界，并封住恢复启动的下载窗口。当前不放宽准入、不盲重试/扩五流，heartbeat保持暂停。

详情：[本轮报告](NORMAL_ADMISSION_2026-10-07.md)、[准入拒绝](../evidence/v34-admission-refusal.json)、[终态](../evidence/v34-normal-restoration.json)、[源码](../evidence/v34-normal-source-proof.json)。

## 以下保留原正常入口及历史记录

# 正常程序已识别三流；NSS 写前拒绝，恢复通过

更新：北京时间2026-10-07 11:12。v33实际Mirage死斗＋已有Hades约32Mbps，自动分类1CS2 RT/9Steam BULK/1跨WAN三流，完整控制器已调用。准备期间两条选中TCP不再合格，checkpoint/stage/模块/ECM前拒绝，普通应用NSS factory验收仍未完成。

失败帧保留：原UDP仍合格，两条TCP socket仍由Steam持有；原WAN槽合格替代0组，其它WAN槽1组。缺失合格候选不当CT退出或NSS故障，不能用新WAN替换已冻结参数。2723绑定/57依赖通过，18＋14模型复用未重跑；数据面与选择合同不变，旧v32/v31截止/源码/失败保持。

11:01原完整audit source1.24/native selectors2、五WAN健康/保护配置/epoch保持、ECM关闭全零；11:02两物理原mq＋四fq_codel全部选项/handle一致。原180秒客户端守护自然退出，CS2/controller/guard0；11:06手动恢复Steam原限速OFF/空数字、下载30%暂停0bps。初次启动和恢复重开曾自动续传，累计下载期限未测，不宣称严格180秒总量/时长。

软件HUD见ping15/loss上下0，数值jitter/Miss/真人体感未知，没有NSS B段。v20三流多WAN及高级QoS硬件和历史CPU继续复用；当前正常入口TCP在准备期间失去资格是具体未验边界，不放宽准入、不盲重试或扩五流。本轮停止新增生产实验，后续只修有证据支持的正常入口准备顺序，heartbeat保持暂停。

详情：[本轮报告](NORMAL_ATTEMPT_2026-10-07.md)、[实际拒绝](../evidence/v33-normal-refusal.json)、[终态](../evidence/v33-normal-restoration.json)、[源码](../evidence/v33-normal-source-proof.json)。

## 以下保留原正常入口与夜间记录

# Steam 已恢复；普通应用 NSS 验收尚未完成

更新：北京时间2026-10-07 10:12。v32承接用户继续推进及一次Hades家庭库限时下载许可，实际约32Mbps；死斗首次被remote host关闭，原180秒守护内只再匹配一次，最终连接/HUD和负载中的程序分类未取得。完整NSS factory、checkpoint/stage/ECM均未启动，不能标硬件/真人验收通过。

新入口2687绑定、57相对依赖/语法通过，数据面及v31的pre-stage TCP选择不变，18＋14模型复用未重跑。旧v31截止/源码/失败保持。本次原180秒客户端守护自然退出，CS2/controller/guard零残留；Steam重开恢复设置时自动续传，随后UI暂停至0bps，显示540.5MB/5%。原限速关闭、空数字、bit/s/游戏中下载/地区保持已视觉核实；累计下载秒数未测，不宣称严格180秒总下载证明。

10:09最后只读原完整audit source1.60/native selectors4、五WAN健康/保护配置/epoch保持、ECM关闭全零；两物理原mq＋四fq_codel全部选项/handle一致。当前Steam可用、下载暂停；v31当时UI未恢复证据单独保留。

v20三流多WAN与五WAN队列/共享借用/RT优先级硬件结果继续复用，普通应用factory仍待一次实际会话。先确认死斗已连接，再开始新的明确下载许可窗口；原180秒期限不重置，续传许可尚待回答。没有新增五WAN同时fast path、长期常驻、CPU或真人体验声明。heartbeat继续暂停。

详情：[本轮报告](NORMAL_WINDOW_2026-10-07.md)、[实际窗口](../evidence/v32-client-window.json)、[终态](../evidence/v32-normal-restoration.json)、[源码](../evidence/v32-normal-source-proof.json)。

## 以下保留原正常入口与夜间记录

# 正常应用写前拒绝已定位并修正；factory验收仍待完成

更新：北京时间2026-10-07 09:14。v30实际CS2＋已有Steam更新识别1RT/24BULK，完整审核后原第一TCP不在合格应用候选中，原UDP和第二TCP保持；checkpoint/stage/ECM前拒绝。2615实际输入和冻结源码逐字节保持，缺失候选不当CT退出证据。

v31只把TCP最终选择移到checkpoint下载/SHA/gzip后、detached stage前，固定原CS2及每TCP槽WAN/fullmark/zone/NAT地址；native/Lua/QoS/分类阈值与原immutable candidate policy不变。实际拒绝帧14模型、2651绑定/61相对依赖/语法通过；完整factory未在模型或硬件执行。Mirage死斗＋已有PUBG更新只读1RT/0BULK，客户端剩余时间不足，未调用完整控制器，不重置期限。

原完整恢复audit source3.94、保护配置/epoch/五WAN健康/ECM关闭全零；随后无router配置写入。09:09新两物理原mq＋四fq_codel全选项/handle一致。两180秒客户端守护自然退出、CS2/测试进程0；下载暂停和原限速关闭在到期前视觉确认。**Steam重开未形成稳定窗口，原UI恢复未确认，不能标完整客户端验收。** 原失败保留、未操作登录。没有新NSS/CPU/主观真人验收声明。

v20三流多WAN、五WAN队列与共享DOWN18/UP60每WAN12硬上限/RT优先级0的硬件结论保持。正常factory仍待一次自然配齐真实三流的有限会话；v31冻结截止不改，下一正常窗口用新目录/新绑定，先恢复SteamUI。本轮停止新增硬件实验，heartbeat继续暂停，不重放CPU/旧准备或新游戏下载。

详情：[正常入口报告](NORMAL_ENTRY_2026-10-07.md)、[拒绝](../evidence/v30-normal-refusal.json)、[14模型](../evidence/v31-last-selection-models.json)、[终态](../evidence/v31-normal-restoration.json)、[源码](../evidence/v31-normal-source-proof.json)。

## 以下保留原传输与夜间记录

# TCP协议源地址假设已修正；单TCP认证短测与恢复通过

更新：北京时间2026-10-07 08:28。用户在08:00晨间封存后要求继续；本轮没有新NSS或router配置写入。v28只读实际TCP走WAN1、UDP走WAN5，公网源地址不同且上游改写TCP源端口；TCP metadata只作时间关联。v29分别取协议公网地址，原两个单IPv4规则/180秒独立FW撤销与原认证server保持，1.391秒首payload、25.007秒22960476字节、客户端无错误。旧v27具体失败连接的精确根因仍未追认。

08:25完整终态通过：原audit source1.55秒、五WAN健康/保护配置及epoch保持/ECM关闭全零；两物理原mq+四fq_codel全部选项/handle一致；FW自然到期规则0/canonical原基线一致、端点和客户端0。首次过早清理读取拒绝的原输出/源码保留，确认到期后一次只读重查通过。

**这只证明单TCP传输前提，未新增五WAN同时fast path、正常Steam/CS2整合factory、CPU或长期验收。** v20三流多WAN和高级QoS硬件结论保持。五流必须逐TCP取实际公网归属，原精确FW政策容纳不了就写前拒绝，不复制UDP地址或盲重试。下一正常应用窗口用新版本和新绑定接v26有界会话；旧v26截止/源码不改。夜间heartbeat继续暂停。

详情：[传输定位报告](PEER_DIAGNOSIS_2026-10-07.md)、[短测](../evidence/v29-peer-proof.json)、[终态](../evidence/v29-peer-restoration.json)、[源码保存](../evidence/v29-peer-source-proof.json)。

## 以下保留晨间与夜间原记录

# 夜间多 WAN / 高级 QoS 受控原型完成；晨间恢复核验通过

更新：北京时间2026-10-07 07:44。07:41最后只读核验全部通过：原完整audit来源1.29秒、五WAN健康/保护配置保持/ECM关闭全零；两物理原mq＋四fq_codel所有选项和handle一致；17个自有端点退出、FW原基线一致/临时规则0/端口关闭；16个本机fixture namespace测试进程零残留。本次无生产实验或远端写入，原冻结源码/失败/证据保持。

本夜交付的受控范围：两TCP BULK＋一UDP RT跨两个或三个WAN，60秒/ECM3/20续租、六双向tag/leaf及ct mark/NAT/affinity正确；五WAN队列映射、DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel在硬件成立。**五WAN同时fast path、v26正常应用整合factory和长期常驻仍未验。** 当前NSS关闭、常驻分类器NSS68/config581b5d46…c791d7与软件fallback保持。

v27 raw TCP首包超时发生在checkpoint/stage/ECM前，原失败保留、根因未知，不盲重试或扩FW/学校策略。下一次正常使用只做一次v26有限应用会话，不要求挂机；五流前提问题和长期连续代进入后续。本夜结束新增实验，检查/提交/推送/实际archive后暂停heartbeat，08:00后不自动实验。

详情：[晨间交付报告](NIGHT_REPORT_2026-10-07.md)、[实际终态](../evidence/morning-final.json)、[源码保存](../evidence/morning-final-source-proof.json)。

## 以下保留原始夜间记录

# 夜间受控多WAN已封存；晨间最后审核待执行

更新：北京时间2026-10-07 05:32。v20的三流跨WAN、五WAN队列/下行共享借用/RT优先级已在硬件证明；当前没有五WAN同时加速、正常程序新factory或长期常驻声明。v27首TCP超时发生在NSS前，端点/FW/客户端与05:19原完整路由器审核/两物理默认队列均恢复通过，e90c4a6已推送并实际archive验证。额外只读input规则顺序没有发现无条件末尾drop，不能借此确定TCP超时根因。

07:40晨间只读收尾入口已准备：[run.mjs](../code/work/morning-20261007/run.mjs)。依次原完整路由器审核、原两物理默认qdisc选项/handle对照、自有端点和canonical防火墙/端口、Windows自有客户端/发送器/守护/控制器核查；17个已知端点单元来自本地记录，05:31本地客户端库存为0。源码语法和默认inspect通过；**最后晨间现场审核尚未执行**。每次新目录保留失败，不重开生产实验。完成真实晨间结果、报告、检查/提交/推送/实际archive后暂停heartbeat，08:00前结束本轮授权。

当前无活跃实验或fixture，必要准备已完成；到07:40前若无新可执行条件，保持安静，不制造轮次或重复报告。无桌面/Steam/CS2/新下载；不盲重试五流或放宽源过滤/期限/认证。正常流入口v26仍只读0流、数据面复用v20，留下一次正常使用中验证，不要求挂机。

证据：[晨间准备，未执行](../evidence/morning-preparation.json)、[输入规则只读](../evidence/night-input-rule-order.json)、[追加源码](../evidence/morning-preparation-source-proof.json)。

## 保留的实测与失败

# 多 WAN高级QoS受控通过；五流新负载在NSS前拒绝

更新：2026-10-07北京时间05:20。v20三流跨WAN和五WAN队列/共享借用硬件结论保持；v26正常Steam/CS2入口已发布并实际archive校验4975bcc。正常整合factory仍仅只读0流，五WAN同时加速和长期常驻未验。

v27唯一改动为四条自有SSH bulk数据连接改成nonce认证raw TCP，固定小UDP/总32Mbps/合64KiB credit/client180及独立210退出保持；五槽native、数据面Lua、PBR/tag/队列/180秒owner与独立恢复均不变。实际sender本地socket10检查、33协议模型、2761绑定通过。现场首TCP约8.008秒首包超时、payload0，NSS stage/checkpoint/模块/放行均未开始；不能归因NSS/固件。旧SSH失败、首次只读诊断语法错误和实际失败保留。

只读端点核查服务就绪、无未处理异常，精确TCP放行规则packet0、UDP规则packet1；控制SSH也曾超时后恢复。不能区分TCP路径与外部源地址差异，根因未定。独立防火墙到期后原canonical基线一致、规则0、精确端点关闭；客户端原实例独立退出通过。05:19完整终态audit source1.00、五WAN健康/保护配置不变/ECM关闭全零、两物理原mq＋四fq_codel、无实验gate。

不盲重试五流或放宽源过滤/期限/认证。睡眠期间无桌面、游戏下载或认证操作。已成立的多WAN原型是两TCP BULK＋一UDP RT、DOWN18共享借用和UP60每WAN12硬上限、RT优先级0/FQ-CoDel；新的普通程序入口一次正常会话和长期连续代列为未验。剩余夜间整理报告并保持安静，07:40做最后完整健康/恢复/端点/客户端核验，07:50不新开实验，08:00前保存推送并暂停heartbeat。

证据：[原生TCP前提与恢复](../evidence/v27-raw-prerequisite.json)、[资格](../evidence/v27-entry-qualification.json)、[本地实际sender与模型](../evidence/v27-raw-models.json)、[源码](../evidence/v27-source-proof.json)。[负载说明](../code/work/v27-raw/README.md)。

## 保留的正常入口与历史硬件证明

# 多 WAN 高级 QoS：受控硬件通过，正常流入口只读就绪

更新：2026-10-07北京时间05:08。已通过的范围仍以v20真实硬件为准：两TCP BULK＋一UDP RT跨两个或三个WAN、60秒/121帧/ECM3/20续租；上下行五WAN各18class、11leaf，DOWN18共享借用、UP60每WAN12硬上限，RT优先级0/FQ-CoDel。完整tag、ct mark、NAT、WAN affinity和恢复通过。该范围是受控有界原型，尚未长期常驻或覆盖所有正常连接。

新的正常流入口`v26-normal`直接接已有Steam、CS2 socket归属和自动分类，选择两个不同WAN的Steam BULK TCP＋一个已准入CS2 RT UDP；无造流、无启动游戏或下载。18选择/拒绝模型与46相对依赖检查通过，2586绑定；native/Lua/tag builder/QoS沿用v20确切字节。现场inspect为0游戏/0下载/0准入，无NSS写入。正常程序整合factory尚未硬件执行，不能用历史数据面替它宣布新入口或真人验收。

五槽native候选同内核编译、63控制/68CT模型、20运行节/675重定位逐项比对及14目标RAM检查通过，55872字节runtime SHA574ffbec…ceb7d4；尚未加载硬件。五流尝试共五次均在NSS前结束：首次自然配齐五WAN但客户端恢复余量不足；一次本地旧目录拒绝；三次自有SSH建连/轮换失败。v24最初四次依次握手成功，后续轮换仍超时，原因未定；不得归因NSS/固件、放宽准入或修改SSH/学校策略。所有端点/FW恢复，四个原客户端独立退出证明通过。

复制换行、错误复制qualifier、缺失本地依赖与sanitizer编码错误原始失败保留，分别更正后才继续。五槽初始78220/81331字节bundle超限原失败保持；现模型72868、guard8763、NFT46750，原9000/65536/73728/49152/1MiB、source6/kernel90最大120/owner180/client180均未放宽。压缩仅JSON数据，无损重构及完整guard分发等价已在目标RAM验证。

04:55完整终态audit source0.95：保护配置不变、五WAN健康、ECM关闭全零；无实验gate，两物理原mq＋四fq_codel。常驻分类器NSS68/config581b5d46…c791d7保持。没有新增CPU因果、300Mbps/长期或真人体验声明。历史CPU证据继续复用；五WAN同时加速不算已通过。

本轮剩余：封存/推送/实际Git archive读回，07:40最后只读终态核验和晨间报告，08:00前暂停heartbeat。无新的五流实验，除非有明确的新可执行前提；不重新开Steam/CS2或下载。下一正常使用时只需一次新整合入口会话，检查实际体验；长期连续新代、五流fixture和扩大加速池进入后续。

证据：[进度和失败](../evidence/v26-progress.json)、[独立客户端和尺寸](../evidence/v26-restoration-limits.json)、[正常入口资格](../evidence/v26-normal-entry-qualification.json)、[五槽源码模型](../evidence/v26-five-native-source-models.json)、[目标RAM](../evidence/v26-five-target-ram.json)、[源码](../evidence/v26-source-proof.json)。[入口说明](../code/work/v26-normal/README.md)。

## 保留的五WAN队列硬件证明

# 五 WAN NSS 队列映射与共享借用通过

更新：2026-10-07北京时间03:50。上下行各18个HTB class、11个FQ-CoDel leaf已实际建立和完整读取，涵盖WAN1..5的BULK/RT以及default950。共同DOWN18：每WAN保障3、ceiling18可借用；共同UP60：每WAN12硬上限。原三槽native gate和常驻自动分类器保持，只放行两TCP BULK＋一UDP RT；实际自然WAN4／5，不声称五WAN同时fast path。

60.00秒／121帧、ECM3、20续租，六tag、完整ct mark、NAT和WAN affinity正确。2533绑定，record844813字节在1MiB内；附近异步窗bulk6.72／8.28Mbps、合14.99，超过3Mbps保障并在共享18内，空闲份额借用继续成立。RT双向leaf drop0；保守B内部57.24秒UDP2434发／2434返，RTT中位197.68ms、p95 198.74ms、p99 200.14ms，仅自有echo，不代替CS2或真人体验。未活跃WAN/类别leaf保持零包。

原完整audit、模块、private WAN、两物理原mq＋四fq_codel、端点/FW/客户端恢复通过。没有新CPU因果、长期或永久NSS声明；历史v18真实改类与失败不覆盖。下一步评估五条精确CT的同时准入，保持同一五WAN QoS政策、默认拒绝和独立撤销；实际前必须确认原传输/记录预算可容纳。07:40收尾、07:50不新开生产、08:00前暂停。

证据：[五WAN映射/借用/RT与恢复](../evidence/v20-five-hardware.json)、[入口](../evidence/v20-five-qualification.json)、[新增映射RAM模型](../evidence/v20-five-native-qualification.json)、[源码](../evidence/v20-five-source-proof.json)。入口：[控制器](../code/work/v20-five/pilot-supervisor.mjs)。

## 三流跨WAN借用与更早历史

# 多 WAN NSS 共享预算借用实测通过

更新：2026-10-07北京时间03:45。保持v18的DOWN18借用／UP60硬上限政策与v16三槽gate，唯一负载变化28＋4→24＋8Mbps，总32和64KiB credit不变。实际WAN1／4／5三条TCP BULK、TCP BULK、UDP RT完成60.01秒／121帧，ECM持续3、20次续租；六tag、完整ct mark、NAT和WAN affinity正确。2497实际绑定，record808129字节在原1MiB内。

附近异步队列窗两路bulk约7.05／8.26Mbps、合15.31；各WAN保障6Mbps，两个bulk均超过保障，且合计在共同18Mbps预算内，证明空闲份额借用已生效。RT上下行FQ-CoDel leaf drop0；保守B内部57.15秒的自有UDP2470发／2470返，RTT中位203.89ms、p95 204.93ms、p99 205.92ms。该echo不代表CS2 jitter/loss/Miss或真人体验；本轮不新增CPU因果、长期限速精度或常驻结论。

原完整audit与模块、private WAN、两物理mq＋四fq_codel、端点、精确FW和客户端恢复全部通过。v18低速TCP真实改类失败保留；没有修改分类阈值或伪造BULK。下一步只扩QoS映射为五WAN的bulk/RT leaf，保留三条精确加速连接和未知默认拒绝；这是五WAN队列覆盖，不能称五WAN同时fast path。07:40收尾、07:50不新开生产、08:00前暂停。

证据：[真实借用/RT与恢复](../evidence/v19-borrow-hardware.json)、[入口](../evidence/v19-borrow-qualification.json)、[复用RAM证明](../evidence/v19-borrow-native-qualification.json)、[源码](../evidence/v19-borrow-source-proof.json)。入口：[控制器](../code/work/v19-borrow/pilot-supervisor.mjs)。

## 保留的改类失败与更早历史

# 共享预算借用配置已建立；低速 TCP 改类后精确结束旧代

更新：2026-10-07北京时间03:35。三条自然WAN1／4／5流进入ECM3，DOWN18共同父预算下按WAN和leaf可借用空闲份额、UP60按WAN硬上限保持，初始tag/ct mark/NAT/affinity正确。但B仅3.09秒，不能宣称60秒或借用吞吐验收通过；原控制器failed结果保持。

同query完整来源显示仅tcp2由BULK转成BE/cooldown：窗口速率1639.42Kbps，低于常驻2000Kbps的bulk门槛。TCP仍在、CT/完整mark/NAT/WAN均相同；另一TCP仍BULK、UDP仍RT。不是将投影缺失当退出。控制器停止新学习、精确关闭这三条旧代CI、ECM3→0，撤销tag并完整恢复模块、private WAN、两物理原mq＋四fq_codel；原完整audit和端点/FW/客户端关闭通过。没有改分类门槛或给BE流硬贴bulk标签。

负载为自有TCP28＋4Mbps、总32Mbps与64KiB credit，UDP50pps。该失败是测试负载未保持BULK类别，不能据此归咎NSS/固件或取消已成立的v16/v17证明。下一轮只将发送器改成24＋8Mbps，总量仍32，借用政策、三槽gate与所有恢复限制保持；先以实际自动分类决定是否准入。BE流仍走软件fallback，当前有限控制器会结束耦合旧代，这项限制进入后续部署backlog。

2461绑定；源6/native90(最大120)/owner180/client180以及9000/65536/73728/1MiB不放宽。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间无桌面、Steam/CS2、新下载或认证操作。

证据：[真实改类与恢复](../evidence/v18-borrow-retirement.json)、[入口](../evidence/v18-borrow-qualification.json)、[预算RAM模型](../evidence/v18-borrow-native-qualification.json)、[源码](../evidence/v18-borrow-source-proof.json)。入口：[控制器](../code/work/v18-borrow/pilot-supervisor.mjs)。

## 已完成的预算响应与更早历史

# 多 WAN NSS 下行预算响应与 RT 共存通过

更新：2026-10-07北京时间03:20。唯一数据面改动为共享DOWN30→18Mbps，UP60保留；三槽native gate、分类器/标签/精确CT pin及其它Lua均复用v16字节。TCP BULK自然WAN3／WAN2、UDP RT在WAN3；60.00秒/121个B帧、ECM3、20次续租、六tag/完整ct mark/NAT/affinity正确，结束ECM0并完整恢复。2425绑定，实际guardian8831／bundle72637／record747019都在原上限内。

两路bulk约6.54／6.70Mbps、合计13.24Mbps，RT双向leaf drop0、squeeze/drop0。相比先前DOWN30的22.16Mbps，流量描述性比例约0.597，与预算18/30的0.6接近；WAN/CT已不同，不能称同流因果A/B。未跑到各WAN9Mbps的90%，不宣称精确跑满或长期限速精度。bulk AQM有drop，TCP利用率和WAN/远端RTT影响列为后续描述，未自动升级blocker。

直接复用既有PC时间、来源uptime和receipt时间戳，偏移不确定度0.85秒并排除边缘；NSS B内部可确定的57.15秒，UDP2365发／2365返、RTT中位199.62ms、p95 200.59ms、p99 201.71ms。是自有Dallas echo，不是CS2 jitter/loss/Miss或真人验收。没有新增tap/故障注入或CPU门槛。

模块、private WAN、两物理原mq＋四fq_codel、精确端点FW和客户端全部恢复，原完整audit通过，常驻NSS68分类器未修改。下一步验证共享预算借用：保持总DOWN18和RT保障，让繁忙WAN在共同父预算下借用空闲份额；使用明确不对称但总量仍32Mbps的自有bulk负载。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间不操作桌面/Steam/CS2或新下载。

证据：[真实硬件/队列/RT窗口与恢复](../evidence/v17-cap-hardware.json)、[入口](../evidence/v17-cap-qualification.json)、[新增预算RAM模型](../evidence/v17-cap-native-qualification.json)、[源码](../evidence/v17-cap-source-proof.json)。入口：[控制器](../code/work/v17-cap/pilot-supervisor.mjs)。

## 三流跨WAN及更早历史

# 三流跨 WAN NSS 与独立 QoS leaf 实测通过

更新：2026-10-07北京时间03:05。两条自有 TCP BULK 自然走WAN1／WAN2，小UDP RT走WAN2。新三槽gate实际运行60.01秒、121个B帧，ECM全程3、20次续租，结束后0。六个上下行按WAN/类别派生的tag、完整ct mark、NAT、LAN/bridge入口和WAN affinity全部正确。实际2389绑定，常驻自动分类器未修改。

真实两路bulk分别进入8f15／8f25下行和8e15／8e25上行FQ-CoDel；RT进入WAN2的8f26／8e26。附近异步队列快照下行bulk约10.54／11.62Mbps，RT双向队列drop0，错误WAN类别leaf零包。DOWN共享30、UP共享60，每WAN15／30Mbps，RT保障1Mbps。已证明跨WAN两路bulk＋RT实际共存；总负载未跑满预算，尚不宣称饱和限速精度。

新gate使用同内核/ECM，不升级固件；CT/predicate/control模型、实际二进制关联和三CI硬件运行成立。三个精确CT对象及zone0/fullmark/NAT约束、未知默认拒绝、全代租约保留。独立守护的连接身份放到原有SHA-pinned bundle中，owner/模块/恢复信息与硬截止仍独立。实际guardian8831、bundle72637、record925671字节都在原9000／73728／1MiB内；source6、kernel90(最大120)、owner180、client180未放宽。三流改类时结束旧代，不直接换tag；没有声称新增选择性改类分支通过。

路由器模块、两个private WAN、两物理原mq＋四fq_codel完整恢复，原完整audit通过；自有端点、精确FW和客户端全部关闭。全fixture UDP5469发／5458返，11未返中9在停止前1秒内；RTT中位200.71ms、p95 201.26ms，仅自有Dallas echo描述，不能归为NSS特定丢包或CS2指标。B-only softirq4.37%、busy16.71%、squeeze/drop0是描述，不新增CPU因果或300Mbps/真人/长期部署结论。

下一步只改变DOWN共享预算到16Mbps，让现有两路受控bulk压住各WAN8Mbps上限，观察限速与RT共存；UP60及其它主要变量保留。07:40晨间收尾、07:50不新开生产、08:00前暂停。睡眠期间不操作桌面/Steam/CS2、不新下载或主动认证。

证据：[硬件与恢复](../evidence/v16-three-hardware.json)、[入口绑定](../evidence/v16-three-qualification.json)、[RAM模型](../evidence/v16-three-native-qualification.json)、[gate构建](../evidence/v16-three-gate-build.json)、[UDP描述](../evidence/v16-three-udp-descriptive.json)、[失败](../evidence/v16-three-failures.json)、[源码](../evidence/v16-three-source-proof.json)。入口：[控制器](../code/work/v16-three/pilot-supervisor.mjs)。

## 双WAN两槽及更早历史

# 双 WAN 独立类别 tag 与 NSS QoS 预算实测通过

更新：2026-10-07北京时间02:35。受控TCP BULK自然走WAN3、UDP RT走WAN2。60.01秒、121帧全程ECM2，20次续租；四个按WAN/方向/类别派生的tag、完整ct mark、NAT及连接粘性正确。NSS gate与常驻自动分类器未变，实际2335绑定。测试结束ECM0，模块、两private WAN、两物理原mq＋四fq_codel、端点FW和客户端完整恢复；原完整审核通过。

两物理NSS HTB上分别设置共享DOWN30／UP60预算，选中两WAN各15／30Mbps；各WAN有BULK与RT FQ-CoDel leaf，RT保障1Mbps、bulk使用余量。下行WAN3 bulk和WAN2 RT、上行对应leaf实际有包；其它选中WAN类别leaf零包。附近60.46秒异步快照bulk下行约10.78Mbps、drop98，RT双向drop0。配置命令和真实leaf生效已证明；没有跑满15Mbps，不能宣称限速精度或两路bulk竞争已经通过。RT队列drop0不代表端到端零丢包。

现有NSS HTB class dump将parent打印成root，实际层级依据本机源码和成功的parent attach命令判断，不用错误dump做层级证明。FQ-CoDel原参数保持；不新增ECN、Wi-Fi、autorate或完整CAKE语义结论。B-only busy13.71%、softirq0.90%、squeeze/drop0仅描述，不重跑CPU门槛或外推300Mbps/真人/常驻。

source6／kernel90(最大120)／独立owner180／client180保持；record767123字节小于1MiB，payload72446小于73728。初次尺寸模型不等价、端点SSH超时均保留；修正后才继续，所有写前新checkpoint下载SHA/gzip与控制连接外自动恢复照常核验。

下一步：两条受控TCP下载同时跨WAN加速，加一条UDP RT，验证共享与每WAN预算实际竞争。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间无桌面/Steam/CS2、新游戏下载或认证操作。

证据：[实际硬件与恢复](../evidence/v15-qos-hardware.json)、[新增准入](../evidence/v15-qos-qualification.json)、[目标RAM模型](../evidence/v15-qos-native-qualification.json)、[保留失败](../evidence/v15-qos-failures.json)、[源码](../evidence/v15-qos-source-proof.json)。入口：[控制器](../code/work/v15-qos/pilot-supervisor.mjs)。

## 双WAN60秒及更早历史

# 双 WAN 60 秒 NSS 运行与完整恢复通过

更新：2026-10-07北京时间02:15。真实受控 TCP BULK 自然走WAN4、小UDP RT走WAN3，Linux PBR仍决定出口。NSS B段60.01秒、121帧全程ECM2、20次续租，四tag/完整ct mark/NAT/WAN affinity正确；结束后ECM0、模块/两WAN/两物理原mq＋四fq_codel/端点FW/客户端全部恢复，原完整审核通过。

上下行四个FQ-CoDel leaf均有实际流量。64.19秒附近异步队列快照下行bulk112566包/drop25，RT上下行2754/2621包/drop0；RT队列零drop不代表端到端零丢包。B仅描述性CPU busy14.16%、softirq0.96%、time_squeeze/softnet drop0，没有重新做CPU因果对照，不外推300Mbps、真人或长期部署。

原two-slot gate二进制未变，仍只一TCP＋一UDP、两个自然健康WAN，未知流默认拒绝。source6秒；本次kernel90秒/最大120，独立owner180秒，client180/其它硬截止保留。2300实际绑定，完整紧凑record623180字节小于1MiB；每次生产写前新checkpoint下载SHA/gzip及控制连接外独立恢复已核验。原v13及所有失败证据保留。

下一步只实现按WAN与类别映射可控NSS预算，再扩大受控bulk准入；保留Linux PBR连接粘性与CAKE fallback。07:40收尾、07:50不新开生产、08:00前暂停。睡眠期间无桌面/Steam/CS2操作或新游戏下载。

证据：[硬件与恢复](../evidence/v14-duration-hardware.json)、[准入范围](../evidence/v14-duration-qualification.json)、[源码](../evidence/v14-duration-source-proof.json)。入口：[60秒双WAN控制器](../code/work/v14-duration/pilot-supervisor.mjs)。

## 双WAN20秒及更早历史

# 双 WAN NSS 硬件闭环通过

用户最新授权：自主推进到2026-10-07北京时间08:00，目标扩展为多 WAN 与高级 QoS。旧 v1 冻结及停止扩展的计划属于历史；其技术证据继续复用，真人体感未验仍保留。

**一条真实受控 TCP BULK 与一条 UDP RT 在两个自然 WAN 完成约20秒 NSS 与恢复。** 实际生产范围仍只两条精确连接：一 TCP BULK＋一 UDP RT，自然分属两个健康 WAN；Linux 继续决定新连接 PBR，NSS 不重做负载均衡。完整 ct mark、NAT、WAN affinity 与 kernel CT pin 保留，未知流默认拒绝。

已完成：新 gate 在原 Linux6.18.44 SDK 编译，15个实际 C 准入条件检查通过；独立两 WAN 模式 helper 的正常及第二步失败恢复模型通过。实际 `ip` 只返回 `link:wan`，已按真实格式核验接口 index/MAC/父接口名；历史 WAN4 排除与旧 import 失败保留。原生 OpenSSH 32Mbps 下载已实际收包，负载专用短保活已关闭，180/185/210秒硬截止保留。模型不能代替硬件。

当前会话沿用20秒 B／27秒 kernel／100秒独立回滚／6秒分类来源，源与实际输入共2272项绑定。每次生产写前新 checkpoint 下载 SHA/gzip 与控制连接外独立恢复核验，保护五路认证/PBR/sing-box/Tailscale和十 CAKE fallback。没有桌面/Steam/CS2操作、购买或新游戏下载，没有认证请求、固件/内核/分区修改。

QoS 当前是两物理口上的共享 bulk/RT HTB＋四 FQ-CoDel leaf，UP60（59/1）／DOWN30（29/1），未准入流 fallback950。还不能称为各 WAN 独立预算、五路同时加速或常驻服务。下一步顺序：双 WAN 实测 → 延长有界会话 → 可实现的共享／每 WAN预算和高级分类，不重复旧 CPU 门槛或 NSS159 gap。

07:40最终恢复/审核/报告，07:50不新开生产，08:00前暂停 heartbeat。失败原证据保留；新源码与脱敏证据按白名单发布，完整 CT/nonce/凭据/config/checkpoint/二进制只本地。

证据：[当前主线](../evidence/v13-night-mainline.json)、[硬件结果](../evidence/v13-night-hardware.json)、[资格范围](../evidence/v13-night-qualification.json)、[保留失败](../evidence/v13-night-failures.json)、[源校验](../evidence/v13-night-source-proof.json)。入口：[双 WAN 有界控制器](../code/work/v13-two/pilot-supervisor-v6.mjs)。

## v1.1及更早历史

# v1.1 单 WAN 有界启停入口已交付

更新：2026-10-07 00:04，北京时间。用户要求一次推进交付，复用 v1 历史证据，不新增 NSS161 实验编号或重新打开 gap/CPU/故障注入支线。

本次将后台启用、状态、停止、真实程序 socket/自动分类、单 WAN bulk/RT 映射、独立 checkpoint/回滚和原完整恢复审核集中接入 `work/v11/`。一启用最多等正常流十分钟，只执行一段约20秒 NSS 后恢复退出；等待阶段只读，不启动桌面/游戏或制造下载。没有改新的路由器 Lua、gate 二进制或常驻分类器。

**现场后台启动→无实际游戏/下载流而只读等待→拒绝重复启动→停止退出通过。NSS 未开启、没有生产实验写入。** 11个新增 host 调度案例通过；真实历史应用帧 payload73325字节与原 single-B builder 完全相等，复用2137历史绑定、总2151。这些是 host/历史整合检查，**不是新入口整段NSS硬件验收**；旧单段生命周期硬件证据保留。

新的原完整只读审核source5.03秒通过，五WAN健康，NSS68/31767/17139/config581b5d46…c791d7不变；ECM关闭全零，无事务/stage/state/实验模块。后台停止后零实验会话、本地准入锁已撤销。没有重新验证已有 checkpoint/rollback 故障路径；未来每次实际会话仍由既有入口创建新 checkpoint 并确认独立回滚。

实际限制：内核 session 最长30秒，当前控制器27秒/有效段约20秒。因此这是有界启停入口，**不是常驻 NSS 或全电脑加速**。停止禁止新准入，已有独立会话按原期限恢复，不强杀守护；未核验恢复时保留本地准入锁。新入口首次整段硬件执行留到正常使用，之后只推进单WAN可持续试用，不再复刻 v1 验收。

源码：[入口说明](../code/work/v11/README.md)、[后台控制](../code/work/v11/service.mjs)、[单段会话](../code/work/v11/session.mjs)。证据：[交付](../evidence/v11-entry-delivery.json)、[新增校验](../evidence/v11-package-qualification.json)、[实际启停](../evidence/v11-live-start-stop.json)、[现网健康](../evidence/v11-current-health.json)。v1原 `current-runtime.json` 是冻结快照，保持原字节；本次状态以本段和新交付证据为准。

## 已冻结 v1 与更早历史

# Athena NSS v1 技术闭环完成并冻结；真人体感未验

更新：2026-10-06 22:53，北京时间。NSS159为起点，本次为最终有界收尾，停止新增自动实验。

**自动分类→单WAN NSS bulk/RT→真实CS2官方死斗＋现有Steam更新，完整20秒software→NSS→software已通过，ECM0→2→0。技术主线冻结；用户明确选择“目前无法接手，仅记录HUD”，因此不写`v1 functional acceptance complete`，严格的真人体感项保留未验。** 不再为这一项自动启动游戏、制造新负载或重复实验。

WAN5一条真实Steam TCP BULK与一条CS2 UDP RT，程序socket归属、同query实际分类、双向四tag、完整ct mark `0x50000`、NAT和WAN affinity正确，六次续租通过。四个NSS FQ-CoDel leaf均有真实包，RT上下行drop0；bulk下行drop15。RT队列零drop不能证明端到端零丢包。UP60（bulk59/RT1）/DOWN30（bulk29/RT1），其余fallback950；没有把整台电脑或五WAN一起加速。

| 最后真实负载窗口 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 秒数 / 帧数 | 20.05 / 41 | 20.05 / 41 | 20.03 / 41 |
| ECM accelerated_count | 0 | 2 | 0 |
| LAN4下行接口Mbps | 107.25 | 106.57 | 104.57 |
| softirq % | 29.33 | 26.96 | 25.90 |
| CPU busy % | 49.26 | 47.00 | 48.76 |
| time_squeeze / softnet drop | 25 / 0 | 19 / 0 | 12 / 0 |

本轮不宣称新CPU因果收益：B softirq并未低于A2。复用NSS128原七项可比条件已通过的约30Mbps上传证据：softirq10.034→5.246→10.393%，相对软件均值下降48.64%。不重复CPU门槛；该结论范围是历史单WAN受控短窗，不外推300Mbps或长期运行。

| 实际CS2 HUD稀疏截图 | ping ms | 下行jitter ms | 下行Loss % | 下行Miss % |
|---|---:|---:|---:|---:|
| software A | 11 | 1 | 2.2 | 2.7 |
| NSS B | 10 | 0 | 2.5 | 1.6 |
| 恢复后 | 11 | 0 | 0 | 0 |

截图在对应窗口内，时钟仅约2秒精度；A2 HUD缺失，无连续HUD遥测。软件路径更早出现15.2%下行Loss尖峰。NSS截图未显示明显额外恶化，未观察到断线或控制器异常；不能写零丢包、实际玩家无卡顿或完整真人验收通过。

**NSS159连续36个UDP echo缺口：known limitation，当前无已证实v1 blocker，未修复、未定位。** 唯一有界定位中的source6.31写前拒绝、端点SSH启动超时与自然WAN不匹配全部保留；最后自有夹具仅software运行53.94秒，UDP2442/2527，尾部待返回不能当稳定丢包。这不是新的NSS复现实验，不能解释原WAN3的连续缺口。没有证据建立NSS/firmware/gate/lease系统性中断或控制器损坏；按照用户收敛标准停止gap支线，不再增加tap或故障模型。若以后出现稳定复现或真实游戏受损的明确证据，才重开blocker。

内核gate、NSS158 native/QoS与实际二进制不变；只修复最终入口的有界程序socket读取及被误替换的历史NSS49字面路径，2137实际输入及冻结副本逐项SHA核验。checkpoint下载SHA/gzip、控制连接外PPID1独立回滚已在写前核验，payload73422/guardian8947满足原73728/9000上限，6/27/100/180秒与1MiB记录不放宽。原失败及早期客户端超时均保留。

实验及最终原完整审核通过，source1.67秒，常驻NSS68/31767/17139、config581b5d46…c791d7不变，五路健康；ECM关闭全零，无事务/stage/state/实验模块。两物理原mq＋四fq_codel及保护配置恢复；自有端点/防火墙恢复。现有Forza更新完成、Steam0bps，临时100Mbps设置已恢复为原不限速/空值，精确客户端守护在恢复后撤销；CS2已断开测试服并目视回主菜单。未购买、重装或新增游戏下载，未永久启用NSS控制器。

v1已知限制和v1.1/v2事项集中到BACKLOG。现有CAKE仅未加速流fallback/对照，不作为继续优化方向。**从现在起保持冻结，不开启NSS161+或重复准备；剩余真人体感仅等用户正常使用时确认，本次不要求继续挂机。**

证据：[主线](../evidence/nss160-mainline.json)、[真实指标](../evidence/nss160-functional-metrics.json)、[缺口判断](../evidence/nss160-gap-decision.json)、[历史CPU](../evidence/nss160-historical-cpu-reuse.json)、[恢复](../evidence/nss160-final-audit.json)、[客户端](../evidence/nss160-client-restore.json)、[失败](../evidence/nss160-failures.json)

## NSS159及更早历史（不作为当前待办）

# 真实下行功能闭环通过，实时质量仍有明确缺口

更新：2026-10-06 19:48，北京时间。NSS159；本日20:00授权的晚间收尾。后台自有下载＋小UDP，没有操作桌面/Steam/CS2。

**新整合控制器已在WAN3完成三段各20秒software→NSS→software，ECM0→2→0。实际下载数据进入bulk leaf，小UDP进入RT leaf；TCP/UDP双向四tag、PBR/完整ct mark/NAT/WAN affinity、七次续租和完整独立恢复通过。** 复用NSS158 native/payload/stage原字节，只换有界下载夹具和精确输入命名空间。

| 指标 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 客户端实际收到下载 Mbps | 25.676 | 26.856 | 25.672 |
| softirq % | 14.289 | 6.245 | 12.962 |
| CPU busy % | 28.832 | 20.035 | 28.273 |
| UDP收/发 | 856/856 | 848/884 | 850/850 |
| UDP echo RTT p95 ms | 194.847 | 194.836 | 194.843 |
| time_squeeze / softnet drop | 0/0 | 0/0 | 0/0 |

**实时质量未通过：NSS B有连续36个echo未返回，位于B第10.976–11.840秒，约4.07%；两个软件段完整返回。** bulk下行FQ-CoDel异步计数drop370，RT上下行drop0；这证明bulk队列实际工作，但RT drop0不能证明端到端交付。第11.01秒有一次成功续租，时间重叠不是因果。已核对与实际二进制绑定的gate源码：成功续租短暂admit=false、更新期限再true，没有显式firmware drain；.5秒计数全程ECM2仍不能排除更短事件。没有端点逐包TX与PC线级捕获，不把未返回定位到NSS或上游，也不贸然修改lease/gate。

**CPU可比性仍5/7，降幅null。** 其它WAN背景0.933/1.640/2.340Mbps违反原上限与波动条件；保持原条件。观察到softirq下降，不能把本轮写成新的因果收益。UDP echo不是CS2 jitter/loss/Miss，没有300Mbps、真人、长期或永久NSS部署验收。NSS158上传与真实改类精确CI撤销/新代重学证明按原字节保存。

夹具仅一自有SSH sender32Mbps/64KiB credit，严格接收旧sender STOP/退出0才启动下一条自己的TCP，最多8端口；UDP固定，Linux自然PBR，没有强制WAN。两次实际夹具均独立FW180秒/OS250秒、PC180秒与210秒guard、SSH185秒timeout并恢复。当前2086绑定/实际冻结输入逐项SHA核验，checkpoint下载SHA/gzip、写前PPID1恢复，payload73428/guardian8947满足73728/9000；原source6/native27/owner100/client180与1MiB记录不放宽。

旧目录regex、继承NSS49依赖误替换和旧端点unit regex三个真实入口/恢复检查失败均保留。前两次router checkpoint/NSS stage前拒绝；首个endpoint helper在连接前拒绝，独立到期后正确精确helper确认恢复。补充实际静态literal依赖检查，旧不完整资格声明保留并明确失效范围；没有覆盖失败或修改冻结证据。

晚间原完整审核source2.48秒，NSS68/31657/17139健康、配置不变；ECM关闭全零，无事务/stage/state/实验模块。两物理原mq+四fq_codel，48历史/新端点与自有接收/发送器、PC客户端/guard均退出，所有FW基线一致。WAN4自然恢复：原控制器十步恢复权重和全部300桶精确重现，五路各60桶；仅恢复三条由实际DHCP租约派生的WAN4规则。旧四路断言拒绝及首个DHCP模型错误均保留，未主动认证或修改路由。常驻分类器与CAKE fallback保留，本轮未长期启用NSS。

下一步只定位这次受控下行UDP缺口：自有端点与PC同步逐包观测，关联firmware CI与续租；定位后再集中真人CS2验证。先不扩第二WAN/共享预算/WiFi/autorate，不重复CPU门槛，不为等待负载下载新游戏。本日到此封存，完成检查/推送/实际archive后暂停heartbeat。

证据：[主线](../evidence/nss159-mainline.json)、[下行数据](../evidence/nss159-download-metrics.json)、[可比性](../evidence/nss159-download-comparison.json)、[UDP缺口](../evidence/nss159-udp-gap.json)、[续租源码核查](../evidence/nss159-renewal-source-inspection.json)、[恢复](../evidence/nss159-flow-rollback.json)、[失败](../evidence/nss159-failures.json)、[晚间审核](../evidence/nss159-evening-final-audit.json)、[端点](../evidence/nss159-evening-endpoint-client-closure.json)

## NSS158及更早历史

# 改类撤销与重学整合通过，完整三段对照已完成

更新：2026-10-06 18:33，北京时间。最新NSS158，合并封存NSS157真实生命周期。未操作桌面、Steam或CS2。

**自动分类→双向NSS bulk/RT leaf已在新整合版本完成真实20秒software→NSS→software。另一次实际暂停自有TCP发送造成BULK→BE/cooldown，完整同query仅TCP受影响；精确撤销TCP CI，ECM2→1且原UDP CI/tag保持，再结束旧代0。原TCP socket/CT与UDP继续，新query/checkpoint/owner/kernel pin和不同两个CI重学20.01秒2→0。**

改类后WAN3上传30.384Mbps，softirq5.396%、UDP771/771、四leaf drop0与squeeze/drop0；没有软件对照，不宣称CPU收益。NSS158同WAN5三段各20.00/20.01/20.01秒：

| 指标 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 服务器确认上传 Mbps | 30.767 | 30.101 | 30.426 |
| softirq % | 10.242 | 1.283 | 7.122 |
| CPU busy % | 26.422 | 17.053 | 23.548 |
| UDP收/发 | 855/855 | 861/861 | 824/824 |
| UDP echo RTT p95 ms | 181.700 | 181.718 | 181.736 |
| time_squeeze / softnet drop | 0/0 | 0/0 | 0/0 |

**功能闭环通过，CPU可比性未通过。** 原七项条件保留，仅五项通过：其它WAN背景1.956/1.648/1.981Mbps超原0.5Mbps上限且波动0.333Mbps超0.25Mbps。相对CPU收益null，不放宽条件或重试追门槛。物理WAN RX drop A/A2各1、B0也保留；UDP echo不是CS2 jitter/loss/Miss。本轮约30Mbps受控上传，下行主要ACK和小UDP，没有300Mbps下载、真人、长期稳定或拥塞AQM验收。

定位两项兼容问题后只改实验入口：常驻classification投影比完整snapshot同query先400–550ms；完整证据最多等.65秒/15次且保留旧lease .5秒余量，最后一份完整query独立比较，不混旧事实、不延长source6秒。实际jsonc重复引用同对象导致class记录null，原run11精确native撤销通过但host整体失败保留；新版本只存一次完整对象并用字段名引用，9项实际改动函数RAM模型及随后真实完整pilot通过。14项完整读取RAM检查属于局部模型，整套factory模型未运行。

新整合close四次整体失败：两次在真实ECM2关闭TCP并恢复旧pair成功，后继四软件TCP未匹配固定UDP WAN，没有新stage；另外两次初始不匹配、没有stage。最后TCP走WAN2/2/5/5、UDP留WAN1；只证明准入不匹配，未证明PBR故障，不盲重试、强制换WAN或扩大端口。NSS156旧版本新TCP重学成功仍保留，不能代替新整合版本后继通过。

所有八个实际stage的完整绑定/冻结输入核验、checkpoint下载SHA/gzip、写前PPID1独立超时恢复与精确恢复通过。分类pilot2020、ABA2042绑定；source6/native27/owner100/client180、9000/65536/73728/1MiB不变；一健康WAN仅一TCP BULK＋一UDP RT，软件准备共享32Mbps/64KiB、最多8端口。PBR/完整ct mark/NAT/affinity和NSS68常驻配置未改。

终态source3.62秒，NSS68/31657/17139健康，ECM关闭全零，无事务/stage/state/模块；两物理原mq+四fq_codel恢复，46历史端点/客户端/自有接收器全关闭。WAN4自然exec-minieap仍down、四路failover保持，未主动认证。

下一步只完善新整合控制器的可部署生命周期和最后集中真人验证；不把有限pilot称为永久NSS部署，不扩第二WAN/共享预算/WiFi/autorate。继续本日授权到20:00；19:40最终只读收尾，19:50不新开生产实验，完成推送/archive后暂停heartbeat。凭据/完整CT/nonce/配置/checkpoint/二进制仅本地，仓库按用户新偏好保持public。

证据：[主线](../evidence/nss158-mainline.json)、[改类实测](../evidence/nss158-class-lifecycle.json)、[三段数据](../evidence/nss158-aba-metrics.json)、[可比性](../evidence/nss158-aba-comparison.json)、[失败](../evidence/nss158-failures.json)、[入口](../evidence/nss158-qualification.json)、[完整恢复](../evidence/nss158-final-audit.json)、[端点](../evidence/nss158-endpoint-client-closure.json)

首次暂存whitespace检查在提交前拒绝，提交/推送链已停止；保留原失败，只给四个固定冻结源码加路径专属blank-at-eof/blank-at-eol属性，原源码SHA不变。见 [格式检查证据](../evidence/nss158-publication-whitespace-check.json)。

## NSS156及更早历史

# 真实TCP退出、新TCP与原UDP重学通过

更新：2026-10-06 16:38，北京时间。最新NSS156。后台自有流量，未操作桌面/Steam/CS2。

**WAN3真实ECM0→2→0→2→0。ECM2时关闭自有TCP；旧双流代停止新学习、撤销并完整恢复，原UDP应用继续。旧固件/标签/队列恢复后才创建新TCP；新分类query、checkpoint、owner、kernel pin及两个新CI完成第二代20.01秒并恢复。UDP的socket/CT/完整mark/NAT/WAN保持，TCP为新socket/CT，旧gate未重开。**

后继服务器确认上传30.009Mbps，busy14.361%、softirq0.883%，time_squeeze/drop均0；UDP 696/696，四个NSS bulk/RT双向FQ-CoDel leaf均有包、drop0。UDP echo RTT中位201.13ms、p95 201.97ms。没有同负载软件对照，CPU降幅null；echo不是CS2 jitter/loss/Miss，当前下行主要ACK与小UDP，不是300Mbps、真人或长期验收。

匹配准备改为四条自有软件TCP共享同一个32Mbps/64KiB credit pacer；按真实分类/mark/NAT选择后关闭其它socket，只一TCP BULK＋一UDP RT进入NSS。四个额外端口留给旧代恢复后的新TCP，共8个候选，不改PBR/mark/NAT/affinity或扩大NSS允许范围。每代1909实际绑定和冻结输入核验、新checkpoint下载SHA/gzip、写前PPID1独立恢复；source6/native27/owner100/client180及9000/65536/73728/1MiB保持。

最初raw TCP连接超时或用尽候选；第三轮仅最后候选匹配而拒绝；旧目录白名单生成错误在写前拒绝并修正。SSH仅此测试进程取消2秒保活，硬截止不变；一次80秒软件上传无该错误但未找到同WAN对，未证明保活是根因。全部六次失败保留且未开启router checkpoint/NSS stage。后处理时校时工具旧目录白名单在连接前拒绝，保留原源后只修正路径再分析。首版封存程序引用两个证明文件时漏了JSON后缀，在Git内容变更与提交前拒绝；修复生成器默认GBK读取也在改动前拒绝；原源保留后使用明确UTF8修正路径。未扩大FW来源/端口，没有系统SSH配置改动。

终态原完整审核source3.39秒，NSS68/31657/17139配置不变，ECM关闭全零、无事务/stage/state/模块；两物理原mq+四fq_codel恢复，34个历史端点/客户端及自有SSH接收器关闭。WAN4既有down/四路failover保持。

下一步把151已证明的精确BULK→BE CI撤销接回155 whole-pair终态，再做有限单WAN pilot。当前生产native仍是155 whole-pair分支；不把未整合的离线候选写成部署完成。仍按授权推进至20:00，19:40收尾、19:50不新开生产实验；凭据/CT/nonce/配置/checkpoint/二进制仅本地，仓库按用户明确偏好保持public。

证据：[主线](../evidence/nss156-mainline.json)、[两代实测](../evidence/nss156-trials.json)、[入口](../evidence/nss156-qualification.json)、[失败](../evidence/nss156-failures.json)、[软件准备](../evidence/nss156-software-preparation.json)、[终态](../evidence/nss156-final-audit.json)、[端点](../evidence/nss156-endpoint-client-closure.json)

首轮仓库checker把实际字段nssScopeOneTcpBulkOneUdpRt漏写Rt，提交链当即停止；仅修正checker字段名，原冻结源码/硬件证据保留。

## NSS155及更早历史

# 真实流退出通过，新TCP后继仍待验证

更新：2026-10-06 15:39，北京时间。最新NSS155。两次在真实ECM2时关闭自有TCP上传socket，旧双流代停止新学习、精确范围内撤销整个pair并完整恢复；原UDP应用继续收发。WAN5与WAN2分别验证，每次只有一个健康WAN。

**退出与恢复已证明；新TCP后继没有通过。** 首次SSH保活超时发生在router checkpoint/stage前；第二次退出成功但8个候选端口用尽，未开启新代；第三次先保留候选，退出成功后新SSH上传再次保活超时。失败原样保留，不把原代恢复写成后继重学通过。

1831与1836项实际绑定/冻结副本对应两次退出。每次新checkpoint下载SHA/gzip、写前PPID1独立恢复、source6/native27/owner100/client180秒和9000/65536/73728/1MiB保持；端口仍8个。常驻分类器、kernel gate和QoS计划不变；本实验只给native fast/guardian加whole-pair terminal分支，未声称149完整factory不变。投影缺失不推断CT退出，本轮不声称仅TCP CI撤销；先前151精确BULK→BE证据仍按原字节保留，部署整合时必须接回该分支。

纯软件两条连续SSH连接在约2.62Mbps及32Mbps分别短测成功，未复现保活超时，根因仍未证明。下一步使用现有自有端点的nonce认证raw TCP上传＋UDP，替代SSH上传fixture，继续新TCP重学；不改学校策略/PBR/NAT/affinity，不扩大WAN/预算/期限，不新增游戏下载。

本轮没有20秒后继、同负载CPU对照、300Mbps或真人CS2验收，CPU降幅null。终态完整原审核source1.18秒、NSS68/31657/17139配置不变，ECM关闭全零，无事务/stage/state/模块；两物理原mq+四fq_codel恢复，27个历史端点/客户端和自有SSH接收器关闭，WAN4既有down/四路failover保持。两份postcheck旧输出路径触发EEXIST，独占创建阻止覆盖，原错误源码保存；只修正路径后检查通过再发布。

继续至20:00；19:40收尾，19:50不新开生产实验。凭据/完整CT/nonce/配置/checkpoint/二进制只在本地。旧154及更早runtime和证据原Git字节保存，仓库按用户明确偏好保持public。

证据：[主线](../evidence/nss155-mainline.json)、[退出实测](../evidence/nss155-trials.json)、[入口](../evidence/nss155-qualification.json)、[失败](../evidence/nss155-failures.json)、[软件传输诊断](../evidence/nss155-software-transport-diagnostics.json)、[终态](../evidence/nss155-final-audit.json)、[端点](../evidence/nss155-endpoint-client-closure.json)

发布流程更正：首次暂存whitespace检查拒绝后编排仍提交并推送627f8c4，是本轮流程错误。该提交、原错误和冻结源码保留；只增加该源码路径的blank-at-eol属性例外。后续检查逐步核验退出码后才允许提交/推送，实际archive结果另存收据。

## NSS154及更早历史

# 监督器自身重启后从磁盘接管通过

更新：2026-10-06 15:02，北京时间。最新NSS154；后台自有32Mbps上传＋小UDP，一健康WAN，未操作桌面/Steam/CS2。

**在ECM＝2时实际终止负责整个两代运行的监督器本身。路由器独立守护完成原20秒与恢复；新监督器从磁盘journal验证旧PID实例缺失和旧代完整恢复，再以新query/checkpoint/owner/kernel pin及两个新CI，在同socket/CT/完整mark/NAT/WAN完成下一代20秒。ECM0→2→0→2→0。**

| 代 | WAN | NSS秒 | 服务器确认上传Mbps | softirq % | UDP收/发 | 续租 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 20.00 | 30.273 | 6.612 | 785/786 | 7 |
| 2 | 1 | 20.00 | 29.972 | 0.981 | 786/786 | 6 |

NSS153只杀控制子进程且父监督器存活；本轮杀直接执行epoch的监督器，没有单独的host epoch子控制器。外层测试harness只维持有界负载、触发精确终止和启动replacement，未代替恢复策略。新进程先验证checkpoint/receipt/journal哈希、原进程实例缺失、原CI/双向tag和独立恢复，再进入正常新代；原gate不重开、不强续。未测试路由器重启，未永久安装NSS服务。

1795个实际绑定及冻结副本匹配，native149 factory、常驻68分类器和内核gate不变；每代新checkpoint下载SHA/gzip和写前PPID1独立恢复，6/27/100/client180秒和9000/65536/73728/1MiB字节不变。2个journal schema接受模型与15个损坏记录拒绝是离线检查，未声称整套factory模型。首次popen读取nil、随后版本生成误改历史依赖均在checkpoint/stage前拒绝，原失败和源码保留；读取根因未证明，独立只读复查通过；第三版本修复确切依赖并补literal/relative存在性检查。

本轮没有同负载CPU对照，降幅null，UDP echo不作CS2 jitter/loss/Miss，也不是300Mbps或长期验收。终态原完整审核source1.69秒，常驻68/31657/17139配置不变，ECM关闭全零、无事务/stage/state/模块，两物理原mq+四fq_codel精确恢复；24个有限端点/客户端及SSH负载进程关闭。WAN4既有down和四路failover保持。仓库按用户已明确的公开偏好保持public，153及旧runtime原Git字节保存。

按用户最新授权继续至今天北京时间20:00，heartbeat已启用；19:40收尾、19:50不新开生产实验。下一步真实自有TCP flow退出与自动收敛，然后单WAN可部署有界pilot；不扩WAN/共享预算/Wi-Fi/autorate，不用游戏下载维持准备。

证据：[主线](../evidence/nss154-mainline.json)、[两代实测](../evidence/nss154-trials.json)、[入口](../evidence/nss154-qualification.json)、[失败](../evidence/nss154-failures.json)、[终态](../evidence/nss154-final-audit.json)、[队列](../evidence/nss154-physical-final.json)、[端点](../evidence/nss154-endpoint-client-closure.json)

## NSS153及更早历史

# 控制子进程中断后自动新代重学通过

更新：2026-10-06 14:29，北京时间。最新 NSS153。用户不用电脑，直接以后台自有32Mbps上传＋小UDP完成单WAN测试；没有桌面、Steam、CS2操作。

**WAN3同一TCP BULK＋UDP RT：ECM=2时实际终止精确自有PC控制子进程，路由器独立守护继续20秒并恢复；仍在运行的父监督器自动取得新分类query/checkpoint/owner/kernel pin和两个新CI，同socket/CT/完整mark/NAT/WAN完成第二代20秒并恢复。ECM0→2→0→2→0。**

| 代 | WAN | NSS秒 | 服务器确认上传Mbps | softirq % | UDP收/发 | native续租 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 3 | 20.02 | 30.392 | 5.126 | 820/821 | 7 |
| 2 | 3 | 20.02 | 30.794 | 0.517 | 840/841 | 7 |

这是有限两代控制子进程中断接管证明。父监督器未被杀，未测试路由器重启；未长期安装NSS服务，未验收300Mbps或真人CS2。没有本轮software/NSS/software CPU因果对照，降幅null；UDP echo不是CS2 jitter/loss/Miss。CAKE仅作为未加速流fallback/对照，NSS主数据面QoS方向保持。

1752个实际入口绑定及冻结副本匹配；每代都有新checkpoint下载SHA/gzip与写前PPID1独立恢复，原149factory/常驻分类器/内核gate不变。6/27/100/client180秒、9000/65536/73728/1MiB字节不变。控制终止同时记录null退出码和SIGTERM信号；缺显式信号的历史记录在新政策中拒绝。14个新增拒绝检查与模型终止字段上的历史native记录重放只是离线政策检查，不是整个factory模型或新硬件证据。四项本地生成/政策/依赖拒绝原样保留。

终态原完整审核source1.42秒，常驻NSS68/config581b5d46…c791d7、31657/17139；ECM关闭全零，无事务/stage/state/模块，wan与lan4原mq+四fq_codel精确恢复。全部21个有限端点/客户端及自有SSH负载进程关闭。WAN4既有认证down和四路failover保持，heartbeat仍暂停。

仓库设置纠正：用户在2026-10-05另一聊天已明确要求此仓库公开；NSS152按旧“私有仓库”说明改回private是误操作。本轮核验owner/admin后只恢复public，其它检查设置不变。旧NSS152实际操作收据保留，以本纠正为当前意图和状态。凭据、完整CT/nonce/配置/checkpoint/二进制仍不加入Git。

下一步把有限监督器收敛为单WAN可部署pilot，先处理监督器自身restart和受控流退出，再决定有界较长运行；不扩第二WAN/共享预算/Wi-Fi/autorate，不重复下载和真人准备。

证据：[主线](../evidence/nss153-mainline.json)、[两代实测](../evidence/nss153-trials.json)、[入口](../evidence/nss153-qualification.json)、[失败](../evidence/nss153-failures.json)、[终态](../evidence/nss153-final-audit.json)、[队列](../evidence/nss153-physical-final.json)、[端点](../evidence/nss153-endpoint-client-closure.json)、[仓库设置纠正](../evidence/nss153-repository-visibility-correction.json)

## NSS152及更早历史

# 自动改类重学与控制进程中断恢复已实测

更新：2026-10-06 13:30，北京时间。最新 NSS152，包含 NSS151 自动改类闭环。仅后台自有有界 TCP 上传＋小 UDP，没有桌面、Steam、CS2 操作。

**真实 BULK→BE 只撤销 TCP CI，ECM2→1，原 UDP CI/RT双向tag保持；旧代完整恢复后，同socket/CT自动取得新query/checkpoint/owner/pin和两个新CI并运行20秒。另一次在ECM2时实际终止精确自有PC控制进程，路由器独立守护仍完成20秒、续租、精确撤销与完整恢复。**

| 测试 | WAN | NSS观测秒 | 服务器确认上传Mbps | softirq % | UDP收/发 | 续租 |
|---|---:|---:|---:|---:|---:|---:|
| automatic-successor | 5 | 20.00 | 30.261 | 1.446 | 801/801 | 6 |
| controller-crash-independent-recovery | 1 | 20.01 | 29.693 | 2.886 | 827/829 | 6 |

这些是生命周期和控制中断恢复实测；没有新的同负载CPU因果对照，降幅为null。UDP echo不是CS2 jitter/loss/Miss。未部署长期NSS控制器，未验收300Mbps或真人游戏；没有杀常驻分类器/路由服务，也没有放宽6/27/100秒及字节上限。

版本拼接中的本地路径/标记/检查器错误均保留。首次中断测试把审计文件误计为目录，在kill前拒绝；其原控制器仍完成正常20秒及恢复，不能算中断恢复成功。随后修正只枚举目录，并实际执行一次kill证明。分类器/内核gate/原138及149factory均未改。

终态常驻NSS68/config581b5d46…c791d7、31657/17139、publication upTag0不变；完整原审核source3.05秒，ECM关闭全零，无事务/stage/state/模块，两物理wan/lan4原mq+四fq_codel精确恢复。20个已有有限负载端点/客户端与自有SSH发送/接收器关闭，WAN4既有认证down和四路failover保持。heartbeat仍暂停。

下一步是单WAN有限常驻supervisor试运行，继续一TCP BULK＋一UDP RT、fresh owner和独立恢复，处理真实改类/退出和控制器restart；通过后才考虑延长运行、多flow或第二WAN。真人体验只在用户方便时集中一次，不要求持续挂游戏、重复Steam下载。

证据：[主线](../evidence/nss152-mainline.json)、[改类](../evidence/nss152-class-transition.json)、[中断](../evidence/nss152-controller-crash.json)、[实际轮次](../evidence/nss152-trials.json)、[失败](../evidence/nss152-failures.json)、[终态](../evidence/nss152-final-audit.json)、[物理根](../evidence/nss152-physical-final.json)、[端点](../evidence/nss152-endpoint-client-closure.json)

## NSS150及更早历史

# 单 WAN 自动生命周期已通过有限两代实测

更新：2026-10-06 12:28，北京时间。最新 NSS150。用户使用电脑，本轮仅后台自有受控下载＋小UDP，无桌面、Steam、CS2 操作。

**同一真实 TCP BULK＋UDP RT，在 WAN3 自动完成两代各20秒：第一代精确撤销和完整恢复后，自动取得新的分类 query、checkpoint、owner、kernel pin 和两个新 CI；原 socket、CT、完整 mark、NAT 与 WAN affinity 不变。每代 ECM0→2→0、四tag/四FQ-CoDel leaf及独立恢复通过。**

| 代 | NSS秒 | 下载payload Mbps | softirq % | UDP收到/发出 | UDP RTT p95 ms | native续租 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 20.01 | 26.715 | 1.875 | 918/918 | 197.383 | 6 |
| 2 | 20.01 | 26.533 | 4.798 | 910/910 | 197.359 | 6 |

这是有限两代生命周期验收；没有本轮 software/NSS/software CPU因果对照，降幅为null；UDP是自有echo，不是CS2 jitter/loss/Miss。未部署长期NSS控制器、未验收300Mbps或长期稳定，未在新supervisor中复测改类/退出。

修复了客户端准备时长误用、两个审核依赖遗漏、旧轮次连接参照路径。WAN5初始阶段UDP上行51包/下行0导致拒绝，未加载gate或开启ECM；其回包缺口根因仍未知，未放宽原1.2秒窗口或6/27/100期限。失败均保留。NSS149第一代20.01秒成功，第二代写前期限拒绝也单独保留。

常驻仍NSS68/config581b5d46…c791d7、31657/17139、publication upTag0；ECM关闭全零，无事务/stage/state/实验模块；wan与lan4原mq+四fq_codel精确恢复；16负载端点/客户端、SSH下载发送器关闭。WAN4既有认证down，四路failover未改。heartbeat保持暂停。

接下来仅把真实改类/退出事件接入这一已实测supervisor，并验证中断时独立恢复；之后再做单WAN有限常驻试运行。保留NSS承担主要QoS的方向，CAKE作为fallback/对照；不扩第二WAN、共享预算、Wi-Fi、autorate或新游戏下载。

证据：[主线](../evidence/nss150-mainline.json)、[两代](../evidence/nss150-trials.json)、[失败](../evidence/nss150-failures.json)、[终态](../evidence/nss150-final-audit.json)、[物理根](../evidence/nss150-physical-final.json)、[端点](../evidence/nss150-endpoint-client-closure.json)。

## NSS148及更早计划

# 下一步：按阶段验收，不要求持续挂游戏

更新：2026-10-06 11:17，北京时间。最新NSS148整理／147实测。用户正在使用电脑，本轮采用自有端点后台受控下载＋小UDP，没有启动或操作Steam/CS2、桌面或新增游戏。常驻仍NSS68/config581b5d46…c791d7、worker31657/guardian17139，全部实验已撤销。

**修复了20秒软件对照误用旧6秒准入epoch的测试程序缺陷。147真实单WAN5、一TCP BULK＋一UDP RT完成三段各20.01秒、123帧、ECM0→2→0和7次native续租；实际四tag/四FQ-CoDel leaf、完整PBR/ct mark/NAT/WAN affinity及精确恢复通过。**

见 [汇总](../evidence/nss148-mainline.json)、[实测轮次](../evidence/nss148-trial.json)、[完整指标](../evidence/nss148-metrics.json)、[失败记录](../evidence/nss148-failures.json)、[受控入口资格](../evidence/nss148-controlled-entry-qualification.json)、[真人入口资格](../evidence/nss148-real-entry-qualification.json)、[只读现网](../evidence/nss148-readonly-readiness.json)、[完整终态](../evidence/nss148-final-audit.json)、[物理队列](../evidence/nss148-physical-final.json)、[端点关闭](../evidence/nss148-endpoint-client-closure.json)。

| 指标 | software A | NSS B | software A2 |
|---|---:|---:|---:|
| 实际下载payload Mbps | 26.681 | 26.971 | 25.442 |
| softirq % | 17.549 | 3.008 | 8.061 |
| CPU busy % | 34.171 | 18.820 | 25.983 |
| time_squeeze / softnet drop | 0 / 0 | 0 / 0 | 0 / 0 |
| UDP echo 收到/发出 | 863/864 | 873/875 | 824/838 |
| UDP RTT p95 ms | 192.725 | 191.813 | 192.785 |
| 其它WAN RX＋TX Mbps | 3.556 | 2.650 | 2.028 |

- 功能闭环通过；严格CPU可比条件未通过，因为用户正常上网的背景流量超过原0.5Mbps/0.25Mbps范围。保存原七项判定、comparability=false和降幅null，不从以上原始softirq给出正式降幅，不要求用户停网重复追阈值。UDP echo未返回和RTT变化是受控端点数据，不能充当CS2 loss/jitter/Miss。
- B附近异步leaf计数：下bulk＋48,285包/drop379，下RT＋922包/drop0；上bulk＋39,640包/drop0，上RT＋888包/drop0。支持真实加速流进入独立可控队列、RT leaf在这轮无自身丢弃，不能据此证明精确长期限速、游戏体验或把bulk drop都归因FQ/AQM。DOWN30/bulk29/RT1，UP60/bulk59/RT1/default950保持；软件A/A2也保留相同实验队列，比较的是软件转发和fast path。
- 原140完整ABA此前从未跑过；145在A约4.5秒即旧6秒epoch过期拒绝，146虽修内层却漏顶层facade参数，仍在ECM前拒绝。147只在两frontend已stop、全部ECM计数0的软件段比较中跳过旧准入epoch截止；当前source/完整class/CT/producer严格，活动B的27秒native及续租/100秒owner不改，支持改类的精确撤销体不改。146即时恢复审核另有instance断言失败；随后原完整终态通过，两份结果分开保留。
- 147实际factory完整硬件ABA通过；目标RAM仅8个完整Consumer案例＋9个实际compare/phase/facade案例，模型显式mock inspector，未声称整个factory在RAM执行。实际payload73,686/guardian8,899字节，资格模型73,685/8,903，原9000/65536/73728及1MiB边界不放宽；1518项实际绑定与冻结副本精确匹配。
- 143真人候选读取因23TCP＋82UDP使命令9311>9000写前拒绝，两个压缩候选仍超限。最终只裁剪候选可见性reader中无用操作API，原inspect/readContext/candidates token stream不变；同历史输入6551，真实新读取6483。上一轮第一次UI点击发生在guard失败之后，不能声称下载始终提前受guard保护；后来v2验证及自然到期/物理Esc记录保留，本轮没有任何UI。
- 144漏两个本地审核依赖、145/146失败、146三个模型资格/尺寸拒绝及helper语法失败、147未观测checkSeconds分析失败全部保留。新分析将该时长写null/observed=false，没有伪造持续时间，也没有为分析重跑硬件。
- 已将147实测factory接回148真人入口，保留Steam TCP/CS2 UDP程序socket归属、checkpoint后最终选择、精确单WAN gate和改类撤销。1527绑定，默认inspect已真实只读运行，0pair/no writes。这个wrapper的完整真人ABA仍未执行；不再推荐有已知完整软件段缺陷的140入口。
- 每轮stage有新checkpoint下载/SHA/gzip和控制连接外独立PPID1 owner写前证明；成功147精确早退恢复，最终source4.59秒、selectors4由原native ownership审核验证，ECM关闭全零、无事务/stage/state/模块，两物理wan/lan4原mq＋四fq_codel的options/handles精确恢复。11个已有自有负载unit inactive/MainPID0，canonical防火墙匹配、临时规则/端口/客户端/guard/SSH发送器0残留。WAN4原认证down和四路failover不变，未主动认证或改校园策略。
- 阶段判定：单WAN自动class→NSS双向bulk/RT功能和真实改类撤销／新代重学已证明；受控上传128约30Mbps可比短窗CPU是历史证据。当前版本下载功能已证明，300Mbps主下载、长期、多WAN、ECN、真人CS2体验和完整CAKE替代尚未验收。夜间heartbeat维持暂停。继续工程可以用后台受控负载；真人体验只留用户方便时一次集中验证，不要求持续挂机，不扩第二WAN/共享预算/WiFi/autorate。

## NSS142及更早历史

# 下一步：一次集中真人验收

更新：2026-10-06 09:43，北京时间。NSS142为本夜最后一次只读收尾，常驻仍NSS68/config581b5d46…c791d7，worker31657、guardian17139。实验已经撤销，ECM保持关闭全零。

**晨间完整核验通过：自动分类器身份、原完整保护审核、两处物理队列、自有测试端点和客户端均已核验。140真人入口的1385项实际输入仍与既有冻结副本逐字节一致。此轮只封存终态，没有重新试装、开启NSS、运行负载或操作桌面。**

见 [晨间汇总](../evidence/nss142-mainline.json)、[完整审核](../evidence/nss142-final-audit.json)、[物理队列](../evidence/nss142-physical-final.json)、[端点与客户端](../evidence/nss142-endpoint-client-closure.json)、[输入绑定](../evidence/nss142-prepared-bindings.json)、[失败记录](../evidence/nss142-failures.json)。

- 原完整来源年龄1.53秒，动态selectors14由原native ownership审核验证；配置、服务、PBR/ct mark/NAT/连接粘性保护不变。无事务/stage/state/实验模块，物理wan与lan4原mq＋四fq_codel的options/handles精确匹配。
- 七个既有有限负载的端点全部inactive/MainPID0；TCP/UDP端口关闭，临时规则0、七个canonical防火墙基线一致；Windows精确自有路径匹配的客户端/guard和自有SSH receiver均0残留。只读确认，不发送stop、不改防火墙。
- WAN4仍认证down且无IPv4，既有四路健康权重100/100/100/0/100及300桶四路各75保持；未主动认证、重启或修改校园策略。
- 139真实同CT自动BULK→BE精确撤销及新代重学仍为历史硬件证据；128约30Mbps受控上传可比短窗softirq相对低48.64%仍为历史性能证据。140新整合版本完整A/B/A2、真人CS2、300Mbps主下载、长期运行及完整CAKE替代均尚未验收。本轮没有新增CPU或游戏结论。
- 晨间第一次批量调用在本地JavaScript语法解析即被拒绝，未派发检查/连接路由器；失败原样保留后修正调用，随后完整检查通过。不覆盖141及更早被冻结证据。
- 本夜工作在发布检查、推送和实际Git archive读回后结束，立即暂停athena-nss；10:00授权截止，之后不新开生产实验，临时keep-awake自到期，不改电源计划。
- 用户醒来后只集中一次：用140默认inspect确认真人CS2 UDP与已有正常下载的Steam BULK TCP同一健康WAN，再获取新分类/kernel pin/checkpoint和独立owner，做三段各20秒software→NSS→software。记录jitter/loss/Miss/体感及softirq/squeeze/吞吐；若改类，精确撤销、结束旧代，新epoch重进，中断不能算完整ABA。继续仅一TCP＋一UDP，不扩第二WAN/共享预算/WiFi/autorate/ECN。

## NSS141及更早历史

# 下一步：最后集中真人验收

更新：2026-10-06 07:14，北京时间。最新NSS141整理、140入口离线整合；常驻NSS68/config581b5d46…c791d7，worker31657、guardian17139。本轮没有生产试装，ECM保持关闭。

**已经把139实测的改类精确撤销接入最后真人入口。学习前按完整实际class映射双向bulk/RT tag；保留程序连接归属和完整CT/mark/NAT/query/leaf/lease证据。若B段发生受支持的真实BULK→BE，停止新学习、核验完整同query证据、精确撤销TCP CI并检查原UDP，再结束旧代；该次中断不能算完整A/B/A2，也不会在旧代强续或改tag。重新学习必须重新进入入口，取得新分类/kernel pin/checkpoint/owner。**

见 [整合汇总](../evidence/nss141-mainline.json)、[入口资格](../evidence/nss141-entry-qualification.json)、[新增撤销检查](../evidence/nss141-fast-qualification.json)、[只读现网](../evidence/nss141-readonly-readiness.json)、[终态](../evidence/nss141-final-audit.json) 与 [失败](../evidence/nss141-failures.json)。

- `work/nss140/real-session.mjs` 默认只读inspect，显式aba才可实验。当前1385项绑定含原138的1340项和原真人77的全部355项；45新输入当前及本地冻结逐字节匹配。真实默认inspect已运行，无游戏/下载对，未创建checkpoint/stage/开放ECM。
- 新fast完整目标RAM语法通过，仅新增observe/retire分支10项模型执行；程序归属Lua过滤10项RAM和8项Node拒绝、1份历史完整分类帧映射通过。旧138真实生命周期及128可比CPU是历史实测；**140新整合版本完整factory A/B/A2未在模型或硬件跑过，不能把分支检查写成真人验收。**
- 正常测量保留三段各20秒、同观察器/同QoS与完整mark/NAT/affinity检查。仅一健康WAN、一TCP BULK＋一UDP RT；UP60（bulk59/RT1）、DOWN30（bulk29/RT1）、fallback950保持。来源6秒/native27秒/owner100秒、9000/65536/73728字节及1MiB读上限不放宽；有效渲染73574字节、guardian8907，另三份仅尺寸模型73575/73417/73588均在上限内。实际新输入仍须现场编码检查，尺寸模型不授权flow。
- 原140第一次默认inspect因临时placeholder命名的字节相等断言拒绝，发生在PC读取及路由器连接之前；43份首资格源码已冻结，只允许该确切namespace替换，展开guardian不变。第一尺寸模型漏protocol、保留额外TCP neighbor并报告错误尺寸，原输出虽标passed仍明确作无效证据保留；修正后校验实际protocol。两次combined模型命令过大写前拒绝、两个alias候选被文字/属性检查拒绝，也未隐藏。
- 原完整终态source4.40、动态selectors2由native审核验证；ECM关闭全零，无事务/stage/state/模块，两物理mq＋四fq_codel和自有SSH receiver零残留。WAN4仍down，既有四路failover与认证/代理/Tailscale不动。未操作UI/下载/对局；没有新CPU或游戏体验结论。
- 最后集中真人窗：用户醒来后用已有正常待下载内容和真人CS2，不购买/重装/新增下载；先只读确认同WAN精确pair，再新checkpoint与独立owner并核验后做20秒A/B/A2。记录HUD jitter/loss/Miss/体感及softirq/squeeze/吞吐；下载负载不匹配或窗口中断就分开报告功能和性能。随后才讨论长期NSS策略与扩WAN。睡眠期间仅保存准备，09:50晨间收尾、10点前暂停本夜heartbeat，不重复CPU/试装/广泛准备。

## NSS139历史

# 下一步：最后集中真人入口

更新：2026-10-06 06:30，北京时间。最新NSS139整理、实际138；常驻NSS68/config581b5d46…c791d7，worker自然恢复为31657、guardian17139未变。全部实验已撤销。

**真实同一TCP/UDP完成了自动改类、精确撤销和新代重学：TCP上传暂停后，同源完整分类帧判定BULK→BE/cooldown；比较器仅报告TCP受影响，ECM2→1，UDP保留原CI及双向RT tag；旧代结束为0。恢复应用发送后，同一CT/mark/NAT/WAN用新的分类、内核pin、独立checkpoint/owner重学，新ECM编号得到2→0。**

见 [完整生命周期](../evidence/nss139-class-lifecycle.json)、[汇总](../evidence/nss139-mainline.json)、[成功守护结束](../evidence/nss139-owner-completion.json)、[失败记录](../evidence/nss139-failures.json)、[分类器恢复](../evidence/nss139-classifier-recovery.json)、[端点关闭](../evidence/nss139-endpoint-closure.json)、[原完整终态](../evidence/nss139-final-audit.json)。

- 实际单WAN2、一TCP BULK＋一UDP RT；完整分类query1031/0.18秒，明确TCP仍有相同CT/zone/mark/original/reply/WAN且为BE，UDP仍获准RT。仅投影缺失不能证明改类或CT退出。CPU同步barrier不是firmware销毁ACK；另验实际目标CI缺失、ECM仅剩原UDP、pending全0，剩余旧分类lease约2.29秒后结束旧代，不强续terminal gate、不在旧CI存在时改tag。
- 两次新checkpoint下载/SHA/gzip与独立守护写前核验、两份1340项实际输入当前及冻结副本逐字节匹配；两次原完整前后审核/精确恢复通过。来源6秒/native27秒/owner最大100秒/client180秒、9000/65536/73728字节和1MiB读上限保持。成功只在模块、tag、两物理根、WAN/mwan3/state全部恢复且ECM关闭零计数后，留5秒记录宽限再退出独立owner；失败仍保留原100秒到期路径。没有发送取消信号或提前放弃失败回滚。
- NSS135已有同样真实精确TCP撤销，但第二代因客户端期限不足未开始，原overall失败保留。NSS131连接helper并发修改进程cwd、NSS133 Lua多返回值误作tonumber进制、NSS137预检误带执行后报告字段等失败分别定位并修复；132回包不足与136预算拒绝未stage。完整失败及本地调用错误不改成成功。11项新的目标RAM成功结束边界与原12项完整分类模型分开；旧模型源码相同继承，未反复重跑。
- 常驻worker4859在129负载中自然apply失败（status256、0.35秒），procd恢复31657，guardian17139与源/config不变。实际child PID/stderr缺失，旧orphan batch与PID重用只是未证实线索；没有为此主动重装/重启常驻分类器。新实例实际通过原完整身份审核，不能继续把4859当现网PID。
- 本轮只验功能生命周期，没有新增CPU对照、300Mbps、Steam主下载或真人CS2指标。128此前约30Mbps上传可比短窗的softirq相对低48.64%保持为历史证据，不能扩大成长期/游戏收益。最终source0.91、selectors0、ECM关闭全零，无事务/stage/state/实验模块，两物理原mq＋四fq_codel恢复；七个有限负载、临时规则/端口/客户端已关闭，自有SSH接收器0残留。WAN4仍认证down，既有四路failover保持。
- 下一步把已经证明的撤销/重学规则并入最后集中真人短测入口；先做必要离线绑定/拒绝路径检查。睡眠期间不操作桌面、Steam/CS2或新下载，不扩WAN/共享预算/WiFi/autorate/ECN，不重复CPU阈值试验。09:50不新生产试验，10点前完成晨间终态/发布并暂停本夜heartbeat。

## NSS128历史

# 下一步：单WAN改类精确撤销与重学

更新：2026-10-06 05:02，北京时间。最新NSS128；常驻68/config581b5d46…c791d7、4859/17139保持，实验已撤销。

**消费者上行tag已直接按实际class生成，绑定同源完整CT/mark/NAT/lease。真实WAN1、一TCP BULK＋一UDP RT，学习前映射及实际NSS四tag/四leaf正确，20秒A/B/A2、ECM0→2→0、六续租/精确恢复通过。上传29.837/30.372/29.747Mbps，softirq 10.034/5.246/10.393%，软件段均值10.21→NSS5.25，短窗可比条件下相对低48.64%。**

见 [实际映射](../evidence/nss128-actual-class-mapping.json)、[指标](../evidence/nss128-metrics.json)、[可比分析](../evidence/nss128-comparison.json)、[轮次](../evidence/nss128-trial.json)、[汇总](../evidence/nss128-mainline.json)、[关闭](../evidence/nss128-endpoint-closure.json)、[终态](../evidence/nss128-final-audit.json)。

- 用实际分类结果和源sequence/完整身份决定上8e05/06、下8f05/06；未知类、未获准RT、mark/NAT/实例/来源/lease变化均拒绝，保留原detached重新分类、kernel pin和默认deny。学习前映射与NSS实际双向tag逐一一致。常驻publication upTag0不改，未为字段重装classifier。
- 127有1个真实历史完整帧回放＋13模型反例/跨协议例，14项通过；TCP RT/UDP BULK只证明mapper按class选值，生产入口仍仅TCP BULK＋UDP RT，不能声称其它组合硬件已验收。128原native/gate/队列/发送器逐字节相同；同实际pair/tuples构成的完整bundle与125一致，3项入口检查/1069绑定，实际checkpoint与控制连接外100秒撤销写前核验。
- 本轮为映射验证并顺带保存同观察器CPU指标，未额外重复CPU探针追126背景门槛。其它WAN总RX＋TX 0.071/0.198/0.269Mbps，原七项可比合同全部通过；每段20秒、选中吞吐/physicalwan发送与UDP发送率接近。softirq相对低48.64%只限约30Mbps受控上传短窗，非随机/长期/300Mbps、拥塞AQM或真人结果，包速差异保留。
- UDP收/发718/718、781/781、720/720、四leaf drop0、squeeze/softnet drop0，端点RTT非CS2 jitter/loss/Miss。下行是TCP ACK与小UDP，未覆盖Steam主下载方向的这套新双向版本。现阶段可确认映射与收益信号；改类的真实精确撤销/新epoch重学尚需独立窄测试。
- 原完整终态source2.87、ECM关闭全零、无事务/stage/state/模块；两物理mq＋四fq_codel恢复，1临时端点与客户端全关闭，WAN4仍down、自然四路PBR不改。旧126 runtime原字节保留，原始完整输入私有冻结；没有UI、游戏/新下载、账户/认证或上游操作。
- 下一步仅真实class变化的精确撤销/重学：先查原模块slot close/drain与全局续租约束、完整同源分类读取能力，再在一个自有TCP＋UDP上暂停TCP上传诱发BULK→BE，比较器应只报告TCP受影响。关闭新学习、只撤销目标CI并核验其缺失/剩余UDP短窗，再结束旧epoch；新分类与新kernel pin后才重学。原6/27/100与独立恢复保持。若只有投影缺失，不能代替实际改类/CT退出证明。不得为了剩余UDP强续已terminal gate或在旧CI未退时改tag。
- 后续仍只这条自动分类→NSS leaf主线，最后集中真人一次；不扩WAN/共享预算/WiFi/autorate、不重装/新下载/UI。09:50起不新实验，整理晨间终态与报告、推送后暂停本夜接续。

## NSS126历史

# 当前单WAN自动映射主线

更新：2026-10-06 04:45，北京时间。最新NSS126整理、实际125入口；常驻68/config581b5d46…c791d7、4859/17139不变，实验已撤销。

**只给三段同一个观察器加五rpwan＋physicalwan＋lan4计数；UP60/DOWN30/有界32上传不改。实际WAN2完整20秒A/B/A2、ECM0→2→0、四leaf/mark/NAT/affinity/六续租和精确恢复通过。服务器确认30.356/29.956/30.734Mbps，softirq 10.237/4.496/10.011%，与124重复出现接近相同吞吐下的CPU下降。**

见 [实际指标](../evidence/nss126-metrics.json)、[背景和对照](../evidence/nss126-comparison.json)、[轮次](../evidence/nss126-trial.json)、[汇总](../evidence/nss126-mainline.json)、[失败](../evidence/nss126-preparation-failure.json)、[关闭](../evidence/nss126-endpoint-closure.json)、[终态](../evidence/nss126-final-audit.json)。

- 三段未选中WAN总RX＋TX 0.167/0.099/0.350Mbps，约80/64/103pps，选中TX约2942/2683/2951pps；TCP回复/ACK的包速差异保留。所有squeeze/softnet drop0，四leaf drop0；UDP收/发774/774、746/748、771/771，B少2个echo回复，仍非CS2指标。
- 完整指标显示CPU信号与124一致，足以继续最小消费者工程；严格分析合同的背景流量范围0.2513Mbps略超过0.25，原comparability=false和没有正式相对收益值保留。它不作为扩大实验或重复追阈值的理由。短窗、非随机、部分包速不同和其它CPU工作未完全等同这些边界保持；非300Mbps/拥塞延迟/完整CAKE验收。
- 首次125上传SSH握手6秒超时后客户端退出，0上传B、未checkpoint/stage/改队列/开放ECM；原失败冻结。126外部driver对同一1033项125入口只重试一次，没有修改源或超时。新观察器4项检查含目标机7接口实际只读、语法、bundle73521<73728和预计完整记录697727<原1MiB读上限；未放宽6/27/100或传输边界。
- 实际新checkpoint/SHA/gzip、独立100秒owner写前核验，两个端点180秒FW/210秒客户端全退出；最终source3.05、ECM关闭全零、无事务/stage/state/模块，两个物理mq＋四fq_codel恢复，WAN4仍down/自然四路PBR不改。旧124 runtime原字节保留、实际输入私有冻结。
- 下一步直接把消费者的上行tag映射绑定到实际class和同源身份，未知/未准入RT拒绝；保留resident upTag0、gate/kernel pin/lease，改类精确撤销后才重学，不因字段改变重装常驻。仅这条自动分类→双向leaf主线，不再追加CPU对照来追背景阈值；之后最后一次集中真人。UI停用、不新下载/扩WAN/WiFi/共享预算/autorate；09:50起收尾并暂停本夜接续。

## NSS124历史

# 当前单WAN主线

更新：2026-10-06 04:28，北京时间。最新NSS124；常驻68/config581b5d46…c791d7、4859/17139不变，实验已撤销。

**上行受控组30→60Mbps（bulk29→59、RT1、ceil60），下行30与有界32Mbps上传不改。实际自然WAN5、同一对flow完整20秒A/B/A2，ECM0→2→0、四leaf/mark/NAT/affinity/六次续租/恢复通过；服务器确认30.709/30.774/30.727Mbps，B不再降至约16Mbps。**

见 [实际指标](../evidence/nss124-metrics.json)、[轮次](../evidence/nss124-trial.json)、[汇总](../evidence/nss124-mainline.json)、[拒绝](../evidence/nss124-prewrite-refusal.json)、[匹配失败](../evidence/nss124-matching-refusal.json)、[关闭](../evidence/nss124-endpoint-closure.json)、[终态](../evidence/nss124-final-audit.json)。

- softirq 9.479/4.758/9.655%，time_squeeze/drop均0；UDP收/发826/826、827/828、828/828。上下行bulk/RT queue drop均0，客户端B少一个echo回复，不能写成网络零丢包或CS2效果。选中TCP吞吐可比，暂未同时捕获其它WAN背景，严格整机CPU收益不新增验收。
- 与119同WAN5且同32发送器；上行预算增大后吞吐恢复，支持原30组拥塞相关因素参与，不把跨轮网络变化排除或写成精确AQM根因。60组未饱和，尚未验收60准确限速、拥塞延迟或完整CAKE替代。
- 120经121匹配后，旧只读hint遇发布rename在checkpoint/stage前拒绝，未改路由器。122只将已替换读数丢弃、最多重读一次；8目标RAM边界与实际只读hint通过，原5秒wait/6秒runner及完整审核不改。123强求WAN5而轮换UDP后匹配失败；端点只允许原NAT peer，冲突是合理线索，实际新UDP WAN/peer未捕获，不声称已定因。124保留UDP socket/peer，只自然轮换自己的TCP，未改PBR/认证/端点规则范围。
- 1000项新入口，native27/owner100/source6和9000/65536/73728字节边界不改。实际新checkpoint下载/SHA/gzip与独立守护在写前核验；三端点FW180/客户端210均清理，124首次关闭SSH查询超时原记录保留，随后只读确认规则基线和端口关闭。
- 最终source3.03、ECM关闭全零、无事务/stage/state/模块，两物理根原mq＋四fq_codel恢复；WAN4仍down、自然四路PBR不改。旧119 runtime原字节保持，完整私有输入冻结。未操作UI/下载/游戏、不改常驻upTag0、不提交上游。
- 下一步只补所有WAN的相同只读计数，保持当前队列/负载/来源和期限，做一次CPU对照；随后收敛真实class到双向leaf的最小消费者映射及改类精确撤销，不重装整套或长期放行未知flow。最后一次集中真人CS2验收；第二WAN/共享预算/WiFi/autorate仍后置。09:50起收尾、报告和推送后暂停本夜接续。

## NSS119历史

# 当前单WAN上传后续

更新：2026-10-06 03:51，北京时间。最新NSS119；常驻68/config581b5d46…c791d7、4859/17139保持，实验全撤销。

**32Mbps上传改为最多64KiB信用，避免阻塞期间累积补发债务；原双向30/29/1队列和6/27/100期限不变。WAN5完整20秒A/B/A2、ECM0→2→0、四leaf/mark/NAT/affinity及恢复通过。服务器确认30.607/16.331/31.192Mbps，A/A2回到约31Mbps，B仍只有16.33Mbps。**

见 [实际指标](../evidence/nss119-metrics.json)、[完整轮次](../evidence/nss119-trial.json)、[汇总](../evidence/nss119-mainline.json)、[上行](../evidence/nss119-uplink-proof.json)、[关闭](../evidence/nss119-endpoint-closure.json)、[终态](../evidence/nss119-final-audit.json)。

- UDP收/发798/798、811/811、814/814，上下RT drop0，上bulk drop36、parent overlimits+9804；新CPU/游戏/精确限速均不验收。B吞吐仍降，当前发送器债务不能作为唯一解释。与118的WAN1不同，本轮为WAN5，不把两轮差异直接归因pacer；本轮A/B/A2是同一对flow。
- 4项本地合同验证含真实callback时长模型及10秒阻塞后的64KiB上限，硬件helper与118/116逐字节相同。新的890项入口/独立100秒守护/完整checkpoint、端点180秒FW与210秒客户端均完成；终态source2.97、ECM关闭全零、无事务/stage/state/模块，两物理mq/fq_codel恢复，WAN4仍down四路PBR不改。旧118 runtime逐字节保存，原始私有证据冻结。
- 下一步只提高受控上行组30→60Mbps，bulk29→59/RT1/ceil60，保留下行30和同一有界32Mbps发送器。自然选择WAN5而非改PBR；未知flow默认拒绝。先验证方向布局/原预算错误拒绝/部分恢复及payload上限，再新checkpoint与独立撤销。若不拥塞时吞吐恢复，再定位30组的拥塞/AQM，不靠同时调整RT/其它参数。
- 不动常驻classifier/upTag0，不重装/操作UI/新下载/扩WAN/共享全局预算/WiFi/autorate；最后一次集中真人CS2验收。夜间到10:00，09:50起收尾和晨间报告、推送后暂停接续。

## NSS118历史

# 当前单WAN上传后续

更新：2026-10-06 03:41，北京时间。最新NSS118，常驻68/config581b5d46…c791d7、4859/17139不变；实验均撤销。

**只把上传目标48→32Mbps，原30/29/1双向队列和6/27/100秒来源/native/owner不变。单WAN1完整三段各20秒，ECM0→2→0、四leaf/CT mark/NAT/affinity、7次续租及精确恢复通过；服务器确认上传32.260/16.590/39.189Mbps，较小切换仍未恢复B吞吐。**

见 [实际指标](../evidence/nss118-metrics.json)、[完整轮次](../evidence/nss118-trial.json)、[汇总](../evidence/nss118-mainline.json)、[上行](../evidence/nss118-uplink-proof.json)、[关闭](../evidence/nss118-endpoint-closure.json)、[终态](../evidence/nss118-final-audit.json)。

- UDP收/发703/703、817/817、864/864、上下行RT drop0；B端点RTT p95约204.37ms，平均相邻RTT差约0.294ms。上bulk drop32、parent overlimits+10573，shaper实际工作；B上传四个5秒段仍约15–17Mbps。不能把softirq下降算同负载CPU收益，也不是真人CS2或300Mbps验收。
- 本地发送器按连接开始后的累计目标补发，B阻塞后A2实际超过32Mbps；目标是累计平均，非严格各段瞬时offer。服务端确认字节仍真实，此机制是对照负载问题，未证明它解释NSS B降速。下一步先只给发送器加有限信用上限，避免积累补发债务；原队列、RT负载和全部期限保持。之后若仍降速，再单独提高受控上行预算以区分拥塞/AQM与fast path，不同时修改。
- 新857项入口/9项本地边界检查，硬件六helper与116逐字节相同；不是重新安装分类器。单次checkpoint下载/SHA/gzip、独立100秒守护，端点180秒FW与210秒客户端全退出。最终source1.27、ECM关闭全零、无事务/stage/state/模块，两物理默认mq/fq_codel恢复。WAN4仍down，自然四路PBR不变。旧117 runtime及全部失败原字节保存，私有输入冻结，未提交凭据/CT/nonce/配置/checkpoint/二进制。
- 只推进受控单WAN主线，不扩第二WAN/共享全局预算/WiFi/autorate、不操作UI或新下载。真人留最后一次集中验收。夜间到10:00；09:50不新实验，完成清理、晨间报告与推送后暂停接续。

## NSS117历史

# 当前单WAN上传后续

NSS117完成上传A/B/A2，实际parent overlimits与bulk drop已证明shaper活动，但B吞吐14.7→20.2Mbps回升，尚未稳定。下一步只降发送48→32Mbps；维持原30/29/1队列、默认950和全部期限，先定位吞吐切换及RT隔离，不先改预算。每次新flow/producer/checkpoint和独立撤销、新输入绑定、未知flow默认拒绝。保持常驻68与upTag0；不重装、扩WAN、共享全局预算、WiFi、autorate或桌面/新下载；最后一次集中真人。09:50起不新实验，完成终态和报告后暂停本夜接续。

## NSS115历史计划

# 下一步：只补单WAN双向QoS缺口

NSS114真实四leaf路径已证明，见 [STATE](STATE.md)。无需重复CAKE调参或重新安装68分类器。

1. 继续114/793入口，每次新的flow/producer/checkpoint与独立撤销。只允许健康非WAN4、精确一TCP一UDP，学习前双向tag、完整ct mark/NAT/WAN affinity和持续六秒来源不变。
2. 先保持30/29/1队列与20秒三段期限，用同一自有SSH TCP连接的上行负载确认实际上传和RT路径。服务器确认收到的字节才能作为上传吞吐；客户端提交字节不等于交付。再根据实际容量一次只调整必要的上行受控预算，使拥塞能被NSS而非未知上游独占控制；不同时改方向与预算。
3. 当前物理wan共用五MacVLAN，default950进入该树的EAPOL/其它软件流需要有范围明确的连续性观察。不能把一对flow成功称所有业务保证；不改认证、PBR或学校策略。
4. 常驻upTag0尚未改；受控映射依真实class、明确leaf表和getter已成功。先决定消费者映射的最小长期形式；不要为了发布字段重装整套或长期开放未知flow。已加速改类仍精确撤销/重学。
5. 主线工程具备后，只集中一次真人CS2＋正常下载HUD/体感验收；echo不是CS2。第二WAN、共享预算、Wi-Fi、autorate、ECN/bridge/HTB backlog保持后置。
6. 夜间接续到10:00，09:50后不新开生产测试，完成独立恢复/端点/原完整审核与证据推送后暂停本夜接续；不需要用户逐步确认。

## NSS109历史计划

# 下一步：接回单WAN NSS QoS主线

NSS109两次捕获已缩小约4%受控echo缺口的位置，见 [STATE](STATE.md)。现有软件队列链内没有对应缺包；此echo不能代表真人CS2，上游与网卡早期仍未区分。

1. 保留68分类器与已修复auth PID读取，沿既有认证/学校政策恢复WAN4；不改凭据、不重复强制认证、不触发五路重启。对实际健康四路采用明确前置epoch并绑定声明的auth/manifest修复及300桶自然故障切换，不能把原105旧入口的历史资格视为当下准入，也不能覆盖旧冻结证明。
2. 尽快回到已通过的单WAN bulk/RT工程闭环：选健康WAN、真实一TCP一UDP同WAN，学习前tag/ct mark/NAT/WAN affinity精确，期限和默认拒绝不变。只验证未完成的同WAN预算与NSS关键上行范围；已有CPU收益不反复重做轻载准备。
3. 19个缺包不支持发生在已观测software IFB/CAKE或PC接收链；别以修改CAKE或放宽ECM入口解决这个外部缺口。额外网卡早期/上游定位列为非阻塞证据，不扩扫描、改学校网络政策或用未知端点。
4. 工程条件具备后只集中一次真人CS2＋正常下载，采真实HUD jitter/loss/Miss与体验；当前未完成真人验收、300Mbps或完整CAKE替代，实际upTag0仍需说明。
5. 多WAN、共享全局预算、Wi-Fi、autorate、ECN/bridge/HTB backlog仍后置，不新下载或重装维持准备。

## NSS107历史计划

# 下一步：完成单WAN拥塞与RT回程闭环

以NSS107的实际结果为准。工程用自有受控TCP/UDP；无需长期Steam/CS2。禁止把启动原始错误隐藏成零，观测基线不是对加速flow错误tag的容忍。

1. 保留常驻68，用新的真实实例/流/分类来源。105入口662项，启动原始计数必须留存，未来错误零新增，完整20秒软件段通过后才准许ECM。若新轮失败，先定位实际失败帧；不重复安装分类器或反复改速率碰运气。
2. 只核实同WAN拥塞预算、RT真正回程和leaf排队是否一致。软件fallback与NSS预算独立是风险，但不是已证明缺包根因；这一主线尚未完成，不扩第二WAN、共享全局预算/Wi-Fi/autorate。必要的单WAN预算修正先依据源码和实际计数，逐项checkpoint与独立撤销。
3. 工程功能、限速与回程具备可靠证据后，最后集中一次真人CS2＋正常下载HUD jitter/loss/Miss/体验；UDP echo不代替真人验收。已有可比CPU收益不重新追求相同短测，新的不同吞吐结果不算收益。
4. 当前仅LAN4下行，真实upTag0。补足关键上行范围与完整CAKE替代缺口之前，不长期开放未知TCP/UDP，也不让NSS自行五WAN负载均衡。新连接Linux PBR，已有flow按CT WAN粘性保持。

## NSS98历史计划

# 下一步：收尾单WAN拥塞QoS，再一次真人验收

32Mbps三段可比和48Mbps B/A2的NSS softirq收益已通过；40Mbps组出现bulk丢弃、RT零丢弃/UDP全回复。见 [STATE](STATE.md)。继续使用自有有限端点，不要求每轮Steam/CS2。

1. 保留常驻NSS68和原生flow/来源/期限检查；48Mbps使用96，拥塞40Mbps组使用97。每次新case、新checkpoint、独立撤销、精确一TCP一UDP；不重装、不重放旧准备。
2. 单WAN用可回滚的集中长窗口查清首段过渡与限速稳定性，真实客户端吞吐为准，区分软件转发与ECM，两者保持同QoS plan。bulk drop与RT零drop已经观察到，但异步qdisc计数、几秒窗不证明精确恒定40Mbps或完整多流公平。
3. 52Mbps的缺口已经不支持现有IFB/CAKE或PC程序主要丢包；保留该端点原始序号/CT证据，不靠放宽gate或反复空窗口推进。更细的物理tap/上游定位若必要应独立小范围做，不阻塞已经有效的48Mbps功能路径。
4. 真人CS2＋正常下载只留最后一次集中HUD jitter/loss/Miss和体验验收；echo与没有UDP回复的窗不能代替游戏指标。实装测试通过不等于当前永久开启NSS。
5. LAN4下行leaf已证明；TCP/UDP upTag0，上行NSS QoS尚缺，不能称完整CAKE替代。确认游戏主线后，再按源码/运行能力确定加速上行与单WAN常用运行方式；第二WAN、共享预算、Wi-Fi、autorate及五WAN继续后置。

## NSS92历史计划

# 下一步：定位52Mbps受控UDP回程，再完成高一档单WAN闭环

32Mbps相同负载下实际NSS CPU收益和自动bulk/RT映射已通过；原18Mbps结论也保留。当前唯一工程缺口是52Mbps窗口回包不稳定，见 [STATE](STATE.md)。

1. 不再重装分类器、重放准备或要求用户反复Steam/CS2。读实际68部署与原完整审核，保持新实例/新flow/新checkpoint/独立撤销。
2. 用自有受控端点的序列包只读定位server egress→router ingress/egress→client receive缺口；原87 IP-only tap看不到TX，须用已纠正的ETH_P_ALL。没有router tcpdump，不能把server发出当PC收到，也不能把丢包直接归因NSS或带宽。
3. 只改变一个负载或端点变量，保持60Mbps预算和已通过的89计数合同；入口91适用32Mbps、89适用52Mbps。缺少真实双向tag包继续在原期限内拒绝，不能靠放宽流范围或伪造指标通过。
4. 用同一TCP/UDP、单WAN、新checkpoint/独立45秒owner做software→NSS→software；记录真实客户端吞吐/softirq/squeeze/leaf/UDP。完整且吞吐可比后再评价52Mbps，当前32Mbps短窗66.41%不外推300Mbps或长期稳定。
5. 工程更高一档通过后，最后集中一次真人CS2＋正常下载HUD和体验验收；再评估单WAN常用运行方式。多WAN、共享预算、Wi-Fi、autorate、bridge shaper/ECN/HTB dump backlog后置。

## NSS82历史计划

# 下一步：提高单WAN受控带宽，再一次真人验收

NSS79/82已完成受控真实连接工程闭环和18Mbps可比softirq对照。新的用户授权允许以自有端点TCP/UDP推进工程，不必等待游戏或反复Steam下载；见 [STATE](STATE.md)。

1. 使用当前NSS82受控入口，读实际部署/原完整审核/端点归属/真实socket；不要复用旧流、旧producer或过期owner。
2. 新目录里只提高单WAN受控组带宽这一主要QoS变量，发送负载明确记录。当前20Mbps是已验证试验值，不是假定的永久上限；变更先做目标语法/参数验证，再新checkpoint＋独立45秒撤销。继续精确一TCP一UDP，不改PBR，不开放未知流。
3. 保持学习前标签、ct mark/NAT/出口和6秒来源/12秒native session等期限；加速中改类仍须精确撤销再学习。计数精确偏差仅一次重读，第二次原严格检查不通过就撤销。
4. 直接测完整同流A/B/A2；以客户端真实吞吐判断可比，记录softirq/time_squeeze/pps/RTT/未返回和bulk/RT leaf计数。发送速率不等于实际吞吐，WAN NSS计数批量更新不作客户端速率替代。
5. 工程带宽测试通过后，仅集中一次真实CS2＋正常下载，记录真实HUD jitter/loss/Miss和体感。受控UDP不是真人验收。最后再评估单WAN常用配置；第二WAN、共享预算、Wi-Fi、autorate仍在后面。

## NSS78历史计划

# 下一步：直接用NSS77完成真实单WAN闭环

最新为NSS78轻载只读时序诊断，实验入口355项不变；见 [STATE](STATE.md)。

1. 每次读当前部署、原完整审核和真实应用连接；当前下载已完成。复用今后正常待下载内容，不重下已完成游戏、不找新游戏维持准备。
2. 有持续的真实CS2 UDP及Steam TCP同WAN配对时，直接运行77入口。新checkpoint、独立45秒撤销、一WAN一TCP一UDP、20Mbps及原所有期限保持；无配对不写NSS。
3. 完整A/B/A2后核对相同flow、bulk/RT leaf、mark/NAT/WAN affinity、总/单WAN/受控份额，再解释softirq、time_squeeze、吞吐和实际HUD。轻载时序观察不授予加速资格。
4. 不重装分类器、重放旧资格或扩第二WAN/共享预算。若77失败，针对实际失败帧定位，不再同时扩展候选变量。
5. 本轮用户“继续”后只读观察客户端。若再次物理Esc停止Computer Use，立即停止当轮应用输入；任何新的下载/对局窗口须另设客户端期限与精确恢复。

## NSS77历史计划

# 下一步：仅完成修正后的单WAN真实闭环

当前355项入口为 `work/nss77/real-session.mjs`，常驻仍NSS68。77仅准备/目标RAM检查通过，未现场试用。见 [STATE](STATE.md)。

1. 用户恢复桌面操作后，先读当前部署和原完整保护审核，读取当前游戏/现有Steam真实流；不重装、不重放旧准备、不再找新游戏维持准备。当前下载已经完成，不能拿0bps当高负载。
2. 用77实际验证initial来源预算与76学习前getter顺序，checkpoint/独立45秒owner、一WAN一TCP一UDP、20Mbps保持。若无真实同WAN持续配对，不写NSS；不把RAM通过当现场资格。
3. 一次完整A/B/A2，记真实flow身份、leaf计数、ct mark/NAT/WAN affinity、CPU/softirq/time_squeeze、吞吐、HUD。选中TCP只能在stage之前最终选择，现有gate不重定向；阶段中退出必须精确撤销。
4. 对比总负载、单WAN和受控份额，解释五秒观察器开销、客户端HUD滚动值及非真人闲置边界。没有完整可比结果不声称改善，不扩第二WAN/共享预算/Wi-Fi/autorate。
5. 用户物理Esc停止Computer Use后，不能再次操作游戏/Steam；已撤下此次客户端关机guard，不把它当UI恢复证明。新的客户端窗口要单独绑定实例和撤销期限。

## NSS68历史计划

# 下一步：直接集中真实CS2＋现有下载单WAN闭环

NSS68已保留候选并绑定新入口，17检查与现场原完整准入/恢复审核通过。当前23634/17139、ECM关闭全零。无需重复publication试装或旧准备。见 [状态](STATE.md)。

1. 读实际 `work/nss68/deployment-latest.json`，核验原完整持锁审核、guardian、producer、保护配置和无残留。旧47/49/过期trial仅是历史，不能当现网引用。
2. 只使用 `work/nss68/real-session.mjs` 与一次真实CS2＋已有黎明杀机下载。原241+16共257输入和全部原来源/owner/流量门槛保持；没有当前真实同WAN配对即不stage或放行，不能用合成流授予资格。
3. 新checkpoint和独立45秒owner，记录software→NSS→software三段相同TCP/UDP和WAN，实际bulk/RT leaf、ct mark/NAT/affinity、加速0→2→0；producer在实验中变化即拒绝、撤销、重新学习，不能复用旧帧。
4. 同窗口HUD jitter/loss/Miss与真人体验、LAN4/单WAN/受控份额、softirq/time_squeeze/吞吐均完整并可比后才判断收益。助手观战和低负载读数不是真人验收。未通过前不扩第二WAN/共享预算/Wi-Fi/autorate。
5. 本轮自然tc回收失败保存诊断；命令/child PID/阻塞栈缺失，不扩大时限或旁路守护。若再次发生在目标短测内，先精确恢复并定位本项目监督边界，保持主线。

## NSS67历史计划

# 下一步：精确绑定候选部署，再集中单WAN闭环

NSS67已在真实372/367/385Mbps窗口运行发布候选，高负载期间两次原完整审核3.62/4.41秒通过；180秒自然回滚精确恢复47，ECM关闭全零。无需重复轻载试装、旧合同准备或新游戏下载。见 [状态](STATE.md) 与 [接续调用位置](PUBLICATION_ENTRY_HANDOFF.md)。

1. 只读核验当前47/config478818…a900和实际9454/9455；每轮重新读实际实例，不沿用旧producer、过期trial或旧别名。已有暂停的黎明杀机负载可复用，不要求用户反复重下。
2. 在checkpoint与独立撤销保护下形成候选的实际保留部署。消费者、原完整审核与NSS stage必须共同绑定正确base/config/worker/producer和已验证部署；不能将committed:false的180秒试装直接冒充已提交部署、覆盖原资格或混淆45秒NSS owner。详见接续文档。
3. 新轮次入口保留原241项所有输入及原证明，对实际变更的context传递单独验证/绑定，全部原断言、来源1/2/6/9秒、200ms child、20Mbps、一TCP一UDP、45秒owner保持。高负载publication成功不是新的NSS入口资格。
4. 集中真实CS2和已有下载，一次完成同流同WAN software→NSS→software、实际bulk/RT leaf与完整ct mark/NAT/affinity、HUD jitter/loss/Miss及真人体验。先判断LAN4/单WAN/受控份额/吞吐可比，再解释softirq/time_squeeze；未通过前不扩其它支线。

## NSS65历史计划

最新NSS65已完成publication候选现场试装、两次原审核和独立180秒自然精确恢复，常驻47、ECM关闭全零。无需重复轻载试装、分类器安装或旧合同准备。见 [状态](STATE.md)。

1. 每轮先读当前47配置与实际新实例20030/20031并核验原完整审核；不要沿用20682或候选9414的producer。旧64/63所有失败和证据不覆盖。
2. 在真正高负载窗口复用本轮单项publication trial/undo，保持checkpoint下载验证、独立撤销、全部字段/原审核/source期限。记录完整publish和消费者成本，判断原source7.41>6的缺口是否补上；自然0.02–0.03Mbps和编码夹具不能替代。不要用新游戏维持准备。
3. 只在候选实际配置/worker/producer与完整输入正确绑定后使用集中单WAN真实CS2+Steam配对。保留NSS63的241项全部原输入或精确等义重绑定证明，不能把本轮试装当新NSS入口资格。20Mbps、一TCP一UDP、45秒owner、1/2/6/9秒source及200ms child条件不变。
4. 做完整同流同负载software→NSS→software A/B/A2，记录LAN4/单WAN/受控leaf份额、softirq、time_squeeze、实际HUD jitter/loss/Miss/真人体验。负载不可比或A2缺失即未验收，之后才扩第二WAN/共享预算/其它支线。

## NSS64历史计划

最新NSS64：完整字段一致的JSON发布候选、真实快照编码CPU约23.92%改善、目标精确编译通过；尚未安装。现网仍NSS47、ECM关闭全零、NSS63入口241项。见 [状态](STATE.md) 和 [候选](ISSUE_JSON_PUBLICATION_COST.md)。

1. 直接核验20份冻结源、候选SHA和当前47配置/实例。无需重跑旧99/13或本轮已完成的合同/编译，也不用挂游戏或安装大游戏维持准备。
2. 为publication边界单项准备精确旧worker/config/指针恢复；checkpoint下载/哈希/gzip、独立超时守护写前核验后才短时变更。保持完整字段/原审核/source/owner期限，失败定位后精确撤销。编码收益是否补上高负载缺口仍未证明，不因希望通过而延长期限或扩大改动。
3. 真实高负载publication→完整审核在原门槛内通过后，集中做单WAN同TCP/UDP流、负载可比software→NSS→software A/B/A2及实际HUD/真人体验；通过后才扩第二WAN/共享预算/Wi-Fi/autorate。

## NSS63历史计划

最新 NSS63，常驻仍 NSS47，实验入口241项；本轮真实 A+B/客户端 HUD 是功能进展，完整同负载与真人收益未通过。见 [当前状态](STATE.md) 和 [失败定位](ISSUE_NSS63_MAINLINE.md)。下面的旧 NSS49 步骤保留为历史验收边界。

1. 核验本轮最终清理与当前47实例；旧worker5411已自然更换20682，不能沿用旧producer。最新241项入口只通过依赖/RAM资格，实际在checkpoint前因source7.41秒拒绝，不能把15模拟案例当现场转发稳定性。
2. 在本地保存的真实拒绝帧及源码中拆分 classification→apply/audit→snapshot 发布延迟和原审核消费成本。NSS63完整query→publish3.84秒，消费者检查时source7.41；metadata hint只能调度，不能替代6/9秒完整持锁原审核。先找可缩短的实际工作，勿延长期限或跳过规则/配置检查。准备不需要游戏或新下载。
3. 单一变量候选在新目录核验，保持原source/epoch、45秒owner、20Mbps、一TCP一UDP、200ms child条件。短子进程部分读取必须整次拒绝/重新发现；guard错误、PID复用不能作为可重试成功。极窄counter witness只容许原已见+1 TCP下载包/+1500B、其它计数完全对齐且unexpected/neighbor为0后多读一次，仍必须通过原strict getter。
4. 准备完成后仅集中取得真实CS2＋Steam自然负载。沿用原checkpoint/独立45秒守护，记录完整A/B/A2与实际HUD；先检查LAN4、pps、单WAN负载和受控份额，再解释softirq/time_squeeze/游戏体验。助手闲置不能验收真人体验；5秒短段的滚动HUD不能当独立瞬时采样。
5. 本轮NSS实际加速份额很小且吞吐下降，不把softirq下降称收益，不因此扩流数、预算或多WAN。完整闭环通过后才另立必要的范围变更候选。软件CAKE仍仅基线和fallback；不扩ECN/HTB dump/其它backlog。

## NSS49 验收步骤与保持的边界

唯一主线：自动分类 → NSS bulk / RT leaf → 真人 CS2＋Steam 单 WAN。**完整原生功能控制器已经在 NSS49 通过。** 不再重放分类器修复或相同离线准备。当前常驻 `work/nss47/deployment-latest.json`，现入口 `work/nss49/real-session.mjs`。见 [实际证明](../evidence/nss49-actual-aba.json) 与 [当前状态](STATE.md)。

1. **先只读核验当前实例与清理。** 常驻 NSS46 三项可靠性修复＋NSS47 纯地址缓存，匹配当前完整 config 哈希；旧引用是历史。健康/原完整保护审核、ECM 全零、无事务/暂存/实验模块仍需每次核验。19/37/47 份新源码与 121 项实际入口输入保持冻结。
2. **直接准备可解释的实际窗口。** 已有用户授权由助手恢复下载、进入在线 CS2，无需逐步询问。应用候选不存在则默认拒绝，不为补负载购买或卸载重装游戏。在线观战用于真实应用/客户端 HUD，与真人操作和体感分开；用户自然游玩时集中取得一次真人记录，不要求持续挂机。
3. **先启动客户端记录，再进入实验。** 用原生时钟锚点将 HUD 对齐 uptime；覆盖 A/B/A2，遮挡/菜单/缺失字段不填零。NSS49 第一次错过 B、第二次下载完成，原因已保存，不推断改善。优先实际客户端记录，不要求反复抄指标。
4. **保持独立回滚与单 WAN 范围。** 每次写前 checkpoint 下载/哈希/gzip、独立 owner 身份验证。20 Mbps、一 TCP＋一 UDP、owner45秒、初始 <1秒 / 预学习 <2秒、软件6秒 / 发布9秒、epoch5秒不变。初始无包等待最多1.2秒，错误tag立即拒绝，全四向正计数才可继续。不通过扩 TTL / 来源期限或流数碰运气。
5. **用 NSS49 再做实际身份和恢复验证。** 同一 socket/CT ID/zone/双向tuple、完整mark/NAT/WAN保持，tag先于学习；ECM0→2→0、正确bulk/RT leaf、一次续租、精确撤销、完整控制器成功与原完整 AFTER 审核每次记录。功能已经证明，但不免除新窗口的身份/回滚检查。
6. **先判断可比性，再解释性能和游戏。** 总 LAN4/pps、选中 WAN 吞吐各相对跨度≤10%才继续解释，仍不证明offered load一致。NSS49 168/194/171 Mbps、WAN66/84/66 Mbps不满足。重点softirq/time_squeeze、受控份额、吞吐，busy辅助。当前子组约占leaf字节8.56%，不能把整机小变化归于两条连接。计数包含建立/撤销边界，RT0drop不能代替客户端loss，未取得体感如实缺失。
7. **主线通过才扩展。** 第二 WAN 同时加速、共享预算、Wi-Fi、ECN/autorate/五 WAN 留待后续。NSS 是主要数据面 QoS方向，CAKE仅软件基线与未放行flow fallback；host fairness/N100不作为目标。若20 Mbps子组不足以回答性能问题，另建单一变量候选、资格核验/回滚后讨论份额，不能修改冻结入口暗中扩大。

NSS46真实轻载apply/crash、NSS47目标解析收益/自然恢复、NSS48取证失败和NSS49模拟/硬件成功分别保留。完整高负载故障恢复/长期稳定仍未证明。其它 backlog 不阻塞主线，没有上游提交。下次使用 [集中验收记录](SINGLE_WAN_ACCEPTANCE.md)。
