# 夜间受控多WAN已封存；晨间最后审核待执行

更新：北京时间2026-10-07 05:32。v20的三流跨WAN、五WAN队列/下行共享借用/RT优先级已在硬件证明；当前没有五WAN同时加速、正常程序新factory或长期常驻声明。v27首TCP超时发生在NSS前，端点/FW/客户端与05:19原完整路由器审核/两物理默认队列均恢复通过，e90c4a6已推送并实际archive验证。额外只读input规则顺序没有发现无条件末尾drop，不能借此确定TCP超时根因。

07:40晨间只读收尾入口已准备：[run.mjs](code/work/morning-20261007/run.mjs)。依次原完整路由器审核、原两物理默认qdisc选项/handle对照、自有端点和canonical防火墙/端口、Windows自有客户端/发送器/守护/控制器核查；17个已知端点单元来自本地记录，05:31本地客户端库存为0。源码语法和默认inspect通过；**最后晨间现场审核尚未执行**。每次新目录保留失败，不重开生产实验。完成真实晨间结果、报告、检查/提交/推送/实际archive后暂停heartbeat，08:00前结束本轮授权。

当前无活跃实验或fixture，必要准备已完成；到07:40前若无新可执行条件，保持安静，不制造轮次或重复报告。无桌面/Steam/CS2/新下载；不盲重试五流或放宽源过滤/期限/认证。正常流入口v26仍只读0流、数据面复用v20，留下一次正常使用中验证，不要求挂机。

证据：[晨间准备，未执行](evidence/morning-preparation.json)、[输入规则只读](evidence/night-input-rule-order.json)、[追加源码](evidence/morning-preparation-source-proof.json)。

## 保留的实测与失败

# 多 WAN高级QoS受控通过；五流新负载在NSS前拒绝

更新：2026-10-07北京时间05:20。v20三流跨WAN和五WAN队列/共享借用硬件结论保持；v26正常Steam/CS2入口已发布并实际archive校验4975bcc。正常整合factory仍仅只读0流，五WAN同时加速和长期常驻未验。

v27唯一改动为四条自有SSH bulk数据连接改成nonce认证raw TCP，固定小UDP/总32Mbps/合64KiB credit/client180及独立210退出保持；五槽native、数据面Lua、PBR/tag/队列/180秒owner与独立恢复均不变。实际sender本地socket10检查、33协议模型、2761绑定通过。现场首TCP约8.008秒首包超时、payload0，NSS stage/checkpoint/模块/放行均未开始；不能归因NSS/固件。旧SSH失败、首次只读诊断语法错误和实际失败保留。

只读端点核查服务就绪、无未处理异常，精确TCP放行规则packet0、UDP规则packet1；控制SSH也曾超时后恢复。不能区分TCP路径与外部源地址差异，根因未定。独立防火墙到期后原canonical基线一致、规则0、精确端点关闭；客户端原实例独立退出通过。05:19完整终态audit source1.00、五WAN健康/保护配置不变/ECM关闭全零、两物理原mq＋四fq_codel、无实验gate。

不盲重试五流或放宽源过滤/期限/认证。睡眠期间无桌面、游戏下载或认证操作。已成立的多WAN原型是两TCP BULK＋一UDP RT、DOWN18共享借用和UP60每WAN12硬上限、RT优先级0/FQ-CoDel；新的普通程序入口一次正常会话和长期连续代列为未验。剩余夜间整理报告并保持安静，07:40做最后完整健康/恢复/端点/客户端核验，07:50不新开实验，08:00前保存推送并暂停heartbeat。

证据：[原生TCP前提与恢复](evidence/v27-raw-prerequisite.json)、[资格](evidence/v27-entry-qualification.json)、[本地实际sender与模型](evidence/v27-raw-models.json)、[源码](evidence/v27-source-proof.json)。[负载说明](code/work/v27-raw/README.md)。

## 保留的正常入口与历史硬件证明

# 多 WAN 高级 QoS：受控硬件通过，正常流入口只读就绪

更新：2026-10-07北京时间05:08。已通过的范围仍以v20真实硬件为准：两TCP BULK＋一UDP RT跨两个或三个WAN、60秒/121帧/ECM3/20续租；上下行五WAN各18class、11leaf，DOWN18共享借用、UP60每WAN12硬上限，RT优先级0/FQ-CoDel。完整tag、ct mark、NAT、WAN affinity和恢复通过。该范围是受控有界原型，尚未长期常驻或覆盖所有正常连接。

新的正常流入口`v26-normal`直接接已有Steam、CS2 socket归属和自动分类，选择两个不同WAN的Steam BULK TCP＋一个已准入CS2 RT UDP；无造流、无启动游戏或下载。18选择/拒绝模型与46相对依赖检查通过，2586绑定；native/Lua/tag builder/QoS沿用v20确切字节。现场inspect为0游戏/0下载/0准入，无NSS写入。正常程序整合factory尚未硬件执行，不能用历史数据面替它宣布新入口或真人验收。

五槽native候选同内核编译、63控制/68CT模型、20运行节/675重定位逐项比对及14目标RAM检查通过，55872字节runtime SHA574ffbec…ceb7d4；尚未加载硬件。五流尝试共五次均在NSS前结束：首次自然配齐五WAN但客户端恢复余量不足；一次本地旧目录拒绝；三次自有SSH建连/轮换失败。v24最初四次依次握手成功，后续轮换仍超时，原因未定；不得归因NSS/固件、放宽准入或修改SSH/学校策略。所有端点/FW恢复，四个原客户端独立退出证明通过。

复制换行、错误复制qualifier、缺失本地依赖与sanitizer编码错误原始失败保留，分别更正后才继续。五槽初始78220/81331字节bundle超限原失败保持；现模型72868、guard8763、NFT46750，原9000/65536/73728/49152/1MiB、source6/kernel90最大120/owner180/client180均未放宽。压缩仅JSON数据，无损重构及完整guard分发等价已在目标RAM验证。

04:55完整终态audit source0.95：保护配置不变、五WAN健康、ECM关闭全零；无实验gate，两物理原mq＋四fq_codel。常驻分类器NSS68/config581b5d46…c791d7保持。没有新增CPU因果、300Mbps/长期或真人体验声明。历史CPU证据继续复用；五WAN同时加速不算已通过。

本轮剩余：封存/推送/实际Git archive读回，07:40最后只读终态核验和晨间报告，08:00前暂停heartbeat。无新的五流实验，除非有明确的新可执行前提；不重新开Steam/CS2或下载。下一正常使用时只需一次新整合入口会话，检查实际体验；长期连续新代、五流fixture和扩大加速池进入后续。

证据：[进度和失败](evidence/v26-progress.json)、[独立客户端和尺寸](evidence/v26-restoration-limits.json)、[正常入口资格](evidence/v26-normal-entry-qualification.json)、[五槽源码模型](evidence/v26-five-native-source-models.json)、[目标RAM](evidence/v26-five-target-ram.json)、[源码](evidence/v26-source-proof.json)。[入口说明](code/work/v26-normal/README.md)。

## 保留的五WAN队列硬件证明

# 五 WAN NSS 队列映射与共享借用通过

更新：2026-10-07北京时间03:50。上下行各18个HTB class、11个FQ-CoDel leaf已实际建立和完整读取，涵盖WAN1..5的BULK/RT以及default950。共同DOWN18：每WAN保障3、ceiling18可借用；共同UP60：每WAN12硬上限。原三槽native gate和常驻自动分类器保持，只放行两TCP BULK＋一UDP RT；实际自然WAN4／5，不声称五WAN同时fast path。

60.00秒／121帧、ECM3、20续租，六tag、完整ct mark、NAT和WAN affinity正确。2533绑定，record844813字节在1MiB内；附近异步窗bulk6.72／8.28Mbps、合14.99，超过3Mbps保障并在共享18内，空闲份额借用继续成立。RT双向leaf drop0；保守B内部57.24秒UDP2434发／2434返，RTT中位197.68ms、p95 198.74ms、p99 200.14ms，仅自有echo，不代替CS2或真人体验。未活跃WAN/类别leaf保持零包。

原完整audit、模块、private WAN、两物理原mq＋四fq_codel、端点/FW/客户端恢复通过。没有新CPU因果、长期或永久NSS声明；历史v18真实改类与失败不覆盖。下一步评估五条精确CT的同时准入，保持同一五WAN QoS政策、默认拒绝和独立撤销；实际前必须确认原传输/记录预算可容纳。07:40收尾、07:50不新开生产、08:00前暂停。

证据：[五WAN映射/借用/RT与恢复](evidence/v20-five-hardware.json)、[入口](evidence/v20-five-qualification.json)、[新增映射RAM模型](evidence/v20-five-native-qualification.json)、[源码](evidence/v20-five-source-proof.json)。入口：[控制器](code/work/v20-five/pilot-supervisor.mjs)。

## 三流跨WAN借用与更早历史

# 多 WAN NSS 共享预算借用实测通过

更新：2026-10-07北京时间03:45。保持v18的DOWN18借用／UP60硬上限政策与v16三槽gate，唯一负载变化28＋4→24＋8Mbps，总32和64KiB credit不变。实际WAN1／4／5三条TCP BULK、TCP BULK、UDP RT完成60.01秒／121帧，ECM持续3、20次续租；六tag、完整ct mark、NAT和WAN affinity正确。2497实际绑定，record808129字节在原1MiB内。

附近异步队列窗两路bulk约7.05／8.26Mbps、合15.31；各WAN保障6Mbps，两个bulk均超过保障，且合计在共同18Mbps预算内，证明空闲份额借用已生效。RT上下行FQ-CoDel leaf drop0；保守B内部57.15秒的自有UDP2470发／2470返，RTT中位203.89ms、p95 204.93ms、p99 205.92ms。该echo不代表CS2 jitter/loss/Miss或真人体验；本轮不新增CPU因果、长期限速精度或常驻结论。

原完整audit与模块、private WAN、两物理mq＋四fq_codel、端点、精确FW和客户端恢复全部通过。v18低速TCP真实改类失败保留；没有修改分类阈值或伪造BULK。下一步只扩QoS映射为五WAN的bulk/RT leaf，保留三条精确加速连接和未知默认拒绝；这是五WAN队列覆盖，不能称五WAN同时fast path。07:40收尾、07:50不新开生产、08:00前暂停。

证据：[真实借用/RT与恢复](evidence/v19-borrow-hardware.json)、[入口](evidence/v19-borrow-qualification.json)、[复用RAM证明](evidence/v19-borrow-native-qualification.json)、[源码](evidence/v19-borrow-source-proof.json)。入口：[控制器](code/work/v19-borrow/pilot-supervisor.mjs)。

## 保留的改类失败与更早历史

# 共享预算借用配置已建立；低速 TCP 改类后精确结束旧代

更新：2026-10-07北京时间03:35。三条自然WAN1／4／5流进入ECM3，DOWN18共同父预算下按WAN和leaf可借用空闲份额、UP60按WAN硬上限保持，初始tag/ct mark/NAT/affinity正确。但B仅3.09秒，不能宣称60秒或借用吞吐验收通过；原控制器failed结果保持。

同query完整来源显示仅tcp2由BULK转成BE/cooldown：窗口速率1639.42Kbps，低于常驻2000Kbps的bulk门槛。TCP仍在、CT/完整mark/NAT/WAN均相同；另一TCP仍BULK、UDP仍RT。不是将投影缺失当退出。控制器停止新学习、精确关闭这三条旧代CI、ECM3→0，撤销tag并完整恢复模块、private WAN、两物理原mq＋四fq_codel；原完整audit和端点/FW/客户端关闭通过。没有改分类门槛或给BE流硬贴bulk标签。

负载为自有TCP28＋4Mbps、总32Mbps与64KiB credit，UDP50pps。该失败是测试负载未保持BULK类别，不能据此归咎NSS/固件或取消已成立的v16/v17证明。下一轮只将发送器改成24＋8Mbps，总量仍32，借用政策、三槽gate与所有恢复限制保持；先以实际自动分类决定是否准入。BE流仍走软件fallback，当前有限控制器会结束耦合旧代，这项限制进入后续部署backlog。

2461绑定；源6/native90(最大120)/owner180/client180以及9000/65536/73728/1MiB不放宽。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间无桌面、Steam/CS2、新下载或认证操作。

证据：[真实改类与恢复](evidence/v18-borrow-retirement.json)、[入口](evidence/v18-borrow-qualification.json)、[预算RAM模型](evidence/v18-borrow-native-qualification.json)、[源码](evidence/v18-borrow-source-proof.json)。入口：[控制器](code/work/v18-borrow/pilot-supervisor.mjs)。

## 已完成的预算响应与更早历史

# 多 WAN NSS 下行预算响应与 RT 共存通过

更新：2026-10-07北京时间03:20。唯一数据面改动为共享DOWN30→18Mbps，UP60保留；三槽native gate、分类器/标签/精确CT pin及其它Lua均复用v16字节。TCP BULK自然WAN3／WAN2、UDP RT在WAN3；60.00秒/121个B帧、ECM3、20次续租、六tag/完整ct mark/NAT/affinity正确，结束ECM0并完整恢复。2425绑定，实际guardian8831／bundle72637／record747019都在原上限内。

两路bulk约6.54／6.70Mbps、合计13.24Mbps，RT双向leaf drop0、squeeze/drop0。相比先前DOWN30的22.16Mbps，流量描述性比例约0.597，与预算18/30的0.6接近；WAN/CT已不同，不能称同流因果A/B。未跑到各WAN9Mbps的90%，不宣称精确跑满或长期限速精度。bulk AQM有drop，TCP利用率和WAN/远端RTT影响列为后续描述，未自动升级blocker。

直接复用既有PC时间、来源uptime和receipt时间戳，偏移不确定度0.85秒并排除边缘；NSS B内部可确定的57.15秒，UDP2365发／2365返、RTT中位199.62ms、p95 200.59ms、p99 201.71ms。是自有Dallas echo，不是CS2 jitter/loss/Miss或真人验收。没有新增tap/故障注入或CPU门槛。

模块、private WAN、两物理原mq＋四fq_codel、精确端点FW和客户端全部恢复，原完整audit通过，常驻NSS68分类器未修改。下一步验证共享预算借用：保持总DOWN18和RT保障，让繁忙WAN在共同父预算下借用空闲份额；使用明确不对称但总量仍32Mbps的自有bulk负载。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间不操作桌面/Steam/CS2或新下载。

证据：[真实硬件/队列/RT窗口与恢复](evidence/v17-cap-hardware.json)、[入口](evidence/v17-cap-qualification.json)、[新增预算RAM模型](evidence/v17-cap-native-qualification.json)、[源码](evidence/v17-cap-source-proof.json)。入口：[控制器](code/work/v17-cap/pilot-supervisor.mjs)。

## 三流跨WAN及更早历史

# 三流跨 WAN NSS 与独立 QoS leaf 实测通过

更新：2026-10-07北京时间03:05。两条自有 TCP BULK 自然走WAN1／WAN2，小UDP RT走WAN2。新三槽gate实际运行60.01秒、121个B帧，ECM全程3、20次续租，结束后0。六个上下行按WAN/类别派生的tag、完整ct mark、NAT、LAN/bridge入口和WAN affinity全部正确。实际2389绑定，常驻自动分类器未修改。

真实两路bulk分别进入8f15／8f25下行和8e15／8e25上行FQ-CoDel；RT进入WAN2的8f26／8e26。附近异步队列快照下行bulk约10.54／11.62Mbps，RT双向队列drop0，错误WAN类别leaf零包。DOWN共享30、UP共享60，每WAN15／30Mbps，RT保障1Mbps。已证明跨WAN两路bulk＋RT实际共存；总负载未跑满预算，尚不宣称饱和限速精度。

新gate使用同内核/ECM，不升级固件；CT/predicate/control模型、实际二进制关联和三CI硬件运行成立。三个精确CT对象及zone0/fullmark/NAT约束、未知默认拒绝、全代租约保留。独立守护的连接身份放到原有SHA-pinned bundle中，owner/模块/恢复信息与硬截止仍独立。实际guardian8831、bundle72637、record925671字节都在原9000／73728／1MiB内；source6、kernel90(最大120)、owner180、client180未放宽。三流改类时结束旧代，不直接换tag；没有声称新增选择性改类分支通过。

路由器模块、两个private WAN、两物理原mq＋四fq_codel完整恢复，原完整audit通过；自有端点、精确FW和客户端全部关闭。全fixture UDP5469发／5458返，11未返中9在停止前1秒内；RTT中位200.71ms、p95 201.26ms，仅自有Dallas echo描述，不能归为NSS特定丢包或CS2指标。B-only softirq4.37%、busy16.71%、squeeze/drop0是描述，不新增CPU因果或300Mbps/真人/长期部署结论。

下一步只改变DOWN共享预算到16Mbps，让现有两路受控bulk压住各WAN8Mbps上限，观察限速与RT共存；UP60及其它主要变量保留。07:40晨间收尾、07:50不新开生产、08:00前暂停。睡眠期间不操作桌面/Steam/CS2、不新下载或主动认证。

证据：[硬件与恢复](evidence/v16-three-hardware.json)、[入口绑定](evidence/v16-three-qualification.json)、[RAM模型](evidence/v16-three-native-qualification.json)、[gate构建](evidence/v16-three-gate-build.json)、[UDP描述](evidence/v16-three-udp-descriptive.json)、[失败](evidence/v16-three-failures.json)、[源码](evidence/v16-three-source-proof.json)。入口：[控制器](code/work/v16-three/pilot-supervisor.mjs)。

## 双WAN两槽及更早历史

# 双 WAN 独立类别 tag 与 NSS QoS 预算实测通过

更新：2026-10-07北京时间02:35。受控TCP BULK自然走WAN3、UDP RT走WAN2。60.01秒、121帧全程ECM2，20次续租；四个按WAN/方向/类别派生的tag、完整ct mark、NAT及连接粘性正确。NSS gate与常驻自动分类器未变，实际2335绑定。测试结束ECM0，模块、两private WAN、两物理原mq＋四fq_codel、端点FW和客户端完整恢复；原完整审核通过。

两物理NSS HTB上分别设置共享DOWN30／UP60预算，选中两WAN各15／30Mbps；各WAN有BULK与RT FQ-CoDel leaf，RT保障1Mbps、bulk使用余量。下行WAN3 bulk和WAN2 RT、上行对应leaf实际有包；其它选中WAN类别leaf零包。附近60.46秒异步快照bulk下行约10.78Mbps、drop98，RT双向drop0。配置命令和真实leaf生效已证明；没有跑满15Mbps，不能宣称限速精度或两路bulk竞争已经通过。RT队列drop0不代表端到端零丢包。

现有NSS HTB class dump将parent打印成root，实际层级依据本机源码和成功的parent attach命令判断，不用错误dump做层级证明。FQ-CoDel原参数保持；不新增ECN、Wi-Fi、autorate或完整CAKE语义结论。B-only busy13.71%、softirq0.90%、squeeze/drop0仅描述，不重跑CPU门槛或外推300Mbps/真人/常驻。

source6／kernel90(最大120)／独立owner180／client180保持；record767123字节小于1MiB，payload72446小于73728。初次尺寸模型不等价、端点SSH超时均保留；修正后才继续，所有写前新checkpoint下载SHA/gzip与控制连接外自动恢复照常核验。

下一步：两条受控TCP下载同时跨WAN加速，加一条UDP RT，验证共享与每WAN预算实际竞争。07:40收尾、07:50不新开生产、08:00前暂停；睡眠期间无桌面/Steam/CS2、新游戏下载或认证操作。

证据：[实际硬件与恢复](evidence/v15-qos-hardware.json)、[新增准入](evidence/v15-qos-qualification.json)、[目标RAM模型](evidence/v15-qos-native-qualification.json)、[保留失败](evidence/v15-qos-failures.json)、[源码](evidence/v15-qos-source-proof.json)。入口：[控制器](code/work/v15-qos/pilot-supervisor.mjs)。

## 双WAN60秒及更早历史

# 双 WAN 60 秒 NSS 运行与完整恢复通过

更新：2026-10-07北京时间02:15。真实受控 TCP BULK 自然走WAN4、小UDP RT走WAN3，Linux PBR仍决定出口。NSS B段60.01秒、121帧全程ECM2、20次续租，四tag/完整ct mark/NAT/WAN affinity正确；结束后ECM0、模块/两WAN/两物理原mq＋四fq_codel/端点FW/客户端全部恢复，原完整审核通过。

上下行四个FQ-CoDel leaf均有实际流量。64.19秒附近异步队列快照下行bulk112566包/drop25，RT上下行2754/2621包/drop0；RT队列零drop不代表端到端零丢包。B仅描述性CPU busy14.16%、softirq0.96%、time_squeeze/softnet drop0，没有重新做CPU因果对照，不外推300Mbps、真人或长期部署。

原two-slot gate二进制未变，仍只一TCP＋一UDP、两个自然健康WAN，未知流默认拒绝。source6秒；本次kernel90秒/最大120，独立owner180秒，client180/其它硬截止保留。2300实际绑定，完整紧凑record623180字节小于1MiB；每次生产写前新checkpoint下载SHA/gzip及控制连接外独立恢复已核验。原v13及所有失败证据保留。

下一步只实现按WAN与类别映射可控NSS预算，再扩大受控bulk准入；保留Linux PBR连接粘性与CAKE fallback。07:40收尾、07:50不新开生产、08:00前暂停。睡眠期间无桌面/Steam/CS2操作或新游戏下载。

证据：[硬件与恢复](evidence/v14-duration-hardware.json)、[准入范围](evidence/v14-duration-qualification.json)、[源码](evidence/v14-duration-source-proof.json)。入口：[60秒双WAN控制器](code/work/v14-duration/pilot-supervisor.mjs)。

## 双WAN20秒及更早历史

# 双 WAN NSS 硬件闭环通过

用户最新授权：自主推进到2026-10-07北京时间08:00，目标扩展为多 WAN 与高级 QoS。旧 v1 冻结及停止扩展的计划属于历史；其技术证据继续复用，真人体感未验仍保留。

**一条真实受控 TCP BULK 与一条 UDP RT 在两个自然 WAN 完成约20秒 NSS 与恢复。** 实际生产范围仍只两条精确连接：一 TCP BULK＋一 UDP RT，自然分属两个健康 WAN；Linux 继续决定新连接 PBR，NSS 不重做负载均衡。完整 ct mark、NAT、WAN affinity 与 kernel CT pin 保留，未知流默认拒绝。

已完成：新 gate 在原 Linux6.18.44 SDK 编译，15个实际 C 准入条件检查通过；独立两 WAN 模式 helper 的正常及第二步失败恢复模型通过。实际 `ip` 只返回 `link:wan`，已按真实格式核验接口 index/MAC/父接口名；历史 WAN4 排除与旧 import 失败保留。原生 OpenSSH 32Mbps 下载已实际收包，负载专用短保活已关闭，180/185/210秒硬截止保留。模型不能代替硬件。

当前会话沿用20秒 B／27秒 kernel／100秒独立回滚／6秒分类来源，源与实际输入共2272项绑定。每次生产写前新 checkpoint 下载 SHA/gzip 与控制连接外独立恢复核验，保护五路认证/PBR/sing-box/Tailscale和十 CAKE fallback。没有桌面/Steam/CS2操作、购买或新游戏下载，没有认证请求、固件/内核/分区修改。

QoS 当前是两物理口上的共享 bulk/RT HTB＋四 FQ-CoDel leaf，UP60（59/1）／DOWN30（29/1），未准入流 fallback950。还不能称为各 WAN 独立预算、五路同时加速或常驻服务。下一步顺序：双 WAN 实测 → 延长有界会话 → 可实现的共享／每 WAN预算和高级分类，不重复旧 CPU 门槛或 NSS159 gap。

07:40最终恢复/审核/报告，07:50不新开生产，08:00前暂停 heartbeat。失败原证据保留；新源码与脱敏证据按白名单发布，完整 CT/nonce/凭据/config/checkpoint/二进制只本地。

证据：[当前主线](evidence/v13-night-mainline.json)、[硬件结果](evidence/v13-night-hardware.json)、[资格范围](evidence/v13-night-qualification.json)、[保留失败](evidence/v13-night-failures.json)、[源校验](evidence/v13-night-source-proof.json)。入口：[双 WAN 有界控制器](code/work/v13-two/pilot-supervisor-v6.mjs)。

## v1.1及更早历史

# v1.1 单 WAN 有界启停入口已交付

更新：2026-10-07 00:04，北京时间。用户要求一次推进交付，复用 v1 历史证据，不新增 NSS161 实验编号或重新打开 gap/CPU/故障注入支线。

本次将后台启用、状态、停止、真实程序 socket/自动分类、单 WAN bulk/RT 映射、独立 checkpoint/回滚和原完整恢复审核集中接入 `work/v11/`。一启用最多等正常流十分钟，只执行一段约20秒 NSS 后恢复退出；等待阶段只读，不启动桌面/游戏或制造下载。没有改新的路由器 Lua、gate 二进制或常驻分类器。

**现场后台启动→无实际游戏/下载流而只读等待→拒绝重复启动→停止退出通过。NSS 未开启、没有生产实验写入。** 11个新增 host 调度案例通过；真实历史应用帧 payload73325字节与原 single-B builder 完全相等，复用2137历史绑定、总2151。这些是 host/历史整合检查，**不是新入口整段NSS硬件验收**；旧单段生命周期硬件证据保留。

新的原完整只读审核source5.03秒通过，五WAN健康，NSS68/31767/17139/config581b5d46…c791d7不变；ECM关闭全零，无事务/stage/state/实验模块。后台停止后零实验会话、本地准入锁已撤销。没有重新验证已有 checkpoint/rollback 故障路径；未来每次实际会话仍由既有入口创建新 checkpoint 并确认独立回滚。

实际限制：内核 session 最长30秒，当前控制器27秒/有效段约20秒。因此这是有界启停入口，**不是常驻 NSS 或全电脑加速**。停止禁止新准入，已有独立会话按原期限恢复，不强杀守护；未核验恢复时保留本地准入锁。新入口首次整段硬件执行留到正常使用，之后只推进单WAN可持续试用，不再复刻 v1 验收。

源码：[入口说明](code/work/v11/README.md)、[后台控制](code/work/v11/service.mjs)、[单段会话](code/work/v11/session.mjs)。证据：[交付](evidence/v11-entry-delivery.json)、[新增校验](evidence/v11-package-qualification.json)、[实际启停](evidence/v11-live-start-stop.json)、[现网健康](evidence/v11-current-health.json)。v1原 `current-runtime.json` 是冻结快照，保持原字节；本次状态以本段和新交付证据为准。

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

证据：[主线](evidence/nss160-mainline.json)、[真实指标](evidence/nss160-functional-metrics.json)、[缺口判断](evidence/nss160-gap-decision.json)、[历史CPU](evidence/nss160-historical-cpu-reuse.json)、[恢复](evidence/nss160-final-audit.json)、[客户端](evidence/nss160-client-restore.json)、[失败](evidence/nss160-failures.json)

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

证据：[主线](evidence/nss159-mainline.json)、[下行数据](evidence/nss159-download-metrics.json)、[可比性](evidence/nss159-download-comparison.json)、[UDP缺口](evidence/nss159-udp-gap.json)、[续租源码核查](evidence/nss159-renewal-source-inspection.json)、[恢复](evidence/nss159-flow-rollback.json)、[失败](evidence/nss159-failures.json)、[晚间审核](evidence/nss159-evening-final-audit.json)、[端点](evidence/nss159-evening-endpoint-client-closure.json)

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

证据：[主线](evidence/nss158-mainline.json)、[改类实测](evidence/nss158-class-lifecycle.json)、[三段数据](evidence/nss158-aba-metrics.json)、[可比性](evidence/nss158-aba-comparison.json)、[失败](evidence/nss158-failures.json)、[入口](evidence/nss158-qualification.json)、[完整恢复](evidence/nss158-final-audit.json)、[端点](evidence/nss158-endpoint-client-closure.json)

首次暂存whitespace检查在提交前拒绝，提交/推送链已停止；保留原失败，只给四个固定冻结源码加路径专属blank-at-eof/blank-at-eol属性，原源码SHA不变。见 [格式检查证据](evidence/nss158-publication-whitespace-check.json)。

## NSS156及更早历史

# 真实TCP退出、新TCP与原UDP重学通过

更新：2026-10-06 16:38，北京时间。最新NSS156。后台自有流量，未操作桌面/Steam/CS2。

**WAN3真实ECM0→2→0→2→0。ECM2时关闭自有TCP；旧双流代停止新学习、撤销并完整恢复，原UDP应用继续。旧固件/标签/队列恢复后才创建新TCP；新分类query、checkpoint、owner、kernel pin及两个新CI完成第二代20.01秒并恢复。UDP的socket/CT/完整mark/NAT/WAN保持，TCP为新socket/CT，旧gate未重开。**

后继服务器确认上传30.009Mbps，busy14.361%、softirq0.883%，time_squeeze/drop均0；UDP 696/696，四个NSS bulk/RT双向FQ-CoDel leaf均有包、drop0。UDP echo RTT中位201.13ms、p95 201.97ms。没有同负载软件对照，CPU降幅null；echo不是CS2 jitter/loss/Miss，当前下行主要ACK与小UDP，不是300Mbps、真人或长期验收。

匹配准备改为四条自有软件TCP共享同一个32Mbps/64KiB credit pacer；按真实分类/mark/NAT选择后关闭其它socket，只一TCP BULK＋一UDP RT进入NSS。四个额外端口留给旧代恢复后的新TCP，共8个候选，不改PBR/mark/NAT/affinity或扩大NSS允许范围。每代1909实际绑定和冻结输入核验、新checkpoint下载SHA/gzip、写前PPID1独立恢复；source6/native27/owner100/client180及9000/65536/73728/1MiB保持。

最初raw TCP连接超时或用尽候选；第三轮仅最后候选匹配而拒绝；旧目录白名单生成错误在写前拒绝并修正。SSH仅此测试进程取消2秒保活，硬截止不变；一次80秒软件上传无该错误但未找到同WAN对，未证明保活是根因。全部六次失败保留且未开启router checkpoint/NSS stage。后处理时校时工具旧目录白名单在连接前拒绝，保留原源后只修正路径再分析。首版封存程序引用两个证明文件时漏了JSON后缀，在Git内容变更与提交前拒绝；修复生成器默认GBK读取也在改动前拒绝；原源保留后使用明确UTF8修正路径。未扩大FW来源/端口，没有系统SSH配置改动。

终态原完整审核source3.39秒，NSS68/31657/17139配置不变，ECM关闭全零、无事务/stage/state/模块；两物理原mq+四fq_codel恢复，34个历史端点/客户端及自有SSH接收器关闭。WAN4既有down/四路failover保持。

下一步把151已证明的精确BULK→BE CI撤销接回155 whole-pair终态，再做有限单WAN pilot。当前生产native仍是155 whole-pair分支；不把未整合的离线候选写成部署完成。仍按授权推进至20:00，19:40收尾、19:50不新开生产实验；凭据/CT/nonce/配置/checkpoint/二进制仅本地，仓库按用户明确偏好保持public。

证据：[主线](evidence/nss156-mainline.json)、[两代实测](evidence/nss156-trials.json)、[入口](evidence/nss156-qualification.json)、[失败](evidence/nss156-failures.json)、[软件准备](evidence/nss156-software-preparation.json)、[终态](evidence/nss156-final-audit.json)、[端点](evidence/nss156-endpoint-client-closure.json)

首轮仓库checker把实际字段nssScopeOneTcpBulkOneUdpRt漏写Rt，提交链当即停止；仅修正checker字段名，原冻结源码/硬件证据保留。

## NSS155及更早历史

# 真实流退出通过，新TCP后继仍待验证

更新：2026-10-06 15:39，北京时间。最新NSS155。两次在真实ECM2时关闭自有TCP上传socket，旧双流代停止新学习、精确范围内撤销整个pair并完整恢复；原UDP应用继续收发。WAN5与WAN2分别验证，每次只有一个健康WAN。

**退出与恢复已证明；新TCP后继没有通过。** 首次SSH保活超时发生在router checkpoint/stage前；第二次退出成功但8个候选端口用尽，未开启新代；第三次先保留候选，退出成功后新SSH上传再次保活超时。失败原样保留，不把原代恢复写成后继重学通过。

1831与1836项实际绑定/冻结副本对应两次退出。每次新checkpoint下载SHA/gzip、写前PPID1独立恢复、source6/native27/owner100/client180秒和9000/65536/73728/1MiB保持；端口仍8个。常驻分类器、kernel gate和QoS计划不变；本实验只给native fast/guardian加whole-pair terminal分支，未声称149完整factory不变。投影缺失不推断CT退出，本轮不声称仅TCP CI撤销；先前151精确BULK→BE证据仍按原字节保留，部署整合时必须接回该分支。

纯软件两条连续SSH连接在约2.62Mbps及32Mbps分别短测成功，未复现保活超时，根因仍未证明。下一步使用现有自有端点的nonce认证raw TCP上传＋UDP，替代SSH上传fixture，继续新TCP重学；不改学校策略/PBR/NAT/affinity，不扩大WAN/预算/期限，不新增游戏下载。

本轮没有20秒后继、同负载CPU对照、300Mbps或真人CS2验收，CPU降幅null。终态完整原审核source1.18秒、NSS68/31657/17139配置不变，ECM关闭全零，无事务/stage/state/模块；两物理原mq+四fq_codel恢复，27个历史端点/客户端和自有SSH接收器关闭，WAN4既有down/四路failover保持。两份postcheck旧输出路径触发EEXIST，独占创建阻止覆盖，原错误源码保存；只修正路径后检查通过再发布。

继续至20:00；19:40收尾，19:50不新开生产实验。凭据/完整CT/nonce/配置/checkpoint/二进制只在本地。旧154及更早runtime和证据原Git字节保存，仓库按用户明确偏好保持public。

证据：[主线](evidence/nss155-mainline.json)、[退出实测](evidence/nss155-trials.json)、[入口](evidence/nss155-qualification.json)、[失败](evidence/nss155-failures.json)、[软件传输诊断](evidence/nss155-software-transport-diagnostics.json)、[终态](evidence/nss155-final-audit.json)、[端点](evidence/nss155-endpoint-client-closure.json)

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

证据：[主线](evidence/nss154-mainline.json)、[两代实测](evidence/nss154-trials.json)、[入口](evidence/nss154-qualification.json)、[失败](evidence/nss154-failures.json)、[终态](evidence/nss154-final-audit.json)、[队列](evidence/nss154-physical-final.json)、[端点](evidence/nss154-endpoint-client-closure.json)

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

证据：[主线](evidence/nss153-mainline.json)、[两代实测](evidence/nss153-trials.json)、[入口](evidence/nss153-qualification.json)、[失败](evidence/nss153-failures.json)、[终态](evidence/nss153-final-audit.json)、[队列](evidence/nss153-physical-final.json)、[端点](evidence/nss153-endpoint-client-closure.json)、[仓库设置纠正](evidence/nss153-repository-visibility-correction.json)

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

证据：[主线](evidence/nss152-mainline.json)、[改类](evidence/nss152-class-transition.json)、[中断](evidence/nss152-controller-crash.json)、[实际轮次](evidence/nss152-trials.json)、[失败](evidence/nss152-failures.json)、[终态](evidence/nss152-final-audit.json)、[物理根](evidence/nss152-physical-final.json)、[端点](evidence/nss152-endpoint-client-closure.json)

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

证据：[主线](evidence/nss150-mainline.json)、[两代](evidence/nss150-trials.json)、[失败](evidence/nss150-failures.json)、[终态](evidence/nss150-final-audit.json)、[物理根](evidence/nss150-physical-final.json)、[端点](evidence/nss150-endpoint-client-closure.json)。

## NSS148及更早接续

# 接续此研究

最新NSS148整理／147实测：用户使用电脑，不操作UI/Steam/CS2。自有32Mbps有界下载＋小UDP，单WAN5三段20.01秒/123帧、ECM0/2/0、四tag/四leaf/完整mark/NAT/affinity/7续租/精确恢复通过。下载26.681/26.971/25.442，softirq17.549/3.008/8.061；背景3.556/2.650/2.028违反原可比条件，comparison=false/降幅null，UDP不作CS2。下bulkdrop379/两RTdrop0，非300/真人/长期/完整CAKE验收。147修闭软件段旧epoch过期并补顶facade传参：只能stop且ECM全零时跳过旧6秒准入截止；当前source/class/CT仍严，active27/owner100不改。145/146 ECM前失败和146即时instance恢复审核失败／后续成功分开保留。1518实际绑定冻结精确、actualpayload73686/actualguardian8899；8consumer+9phase RAM分项，不称整个factory RAM。148真人wrapper用147已实测factory/143精简visibility reader，1527项/defaultinspect现场0pair/no writes，真人wrapper完整ABA未执行。1439311/9203/9175>9000失败及首UIguard失败后点击保存；144漏审核依赖、146资格/模型尺寸/语法、147分析缺字段均保存。常驻68/config581b5d46…c791d7/31657/17139/upTag0不变，最终ECM全零无残留/两根精确恢复，11端点/客户端/SSH sender关闭，WAN4down四路failover保持。142 runtime归档原字节，heartbeat保持暂停，不扩WAN/共享预算/WiFi/autorate/新游戏下载。工程可继续后台自有受控测试；最后真人只在用户方便时一次，不重复CPU门槛、不重装classifier。以STATE开头为准。

## NSS142及更早历史

# 接续此研究

最新NSS142：09:40后晨间只读完整终态、两物理根、七端点与客户端/SSH receiver关闭核验全部通过；140准备入口1385当前/旧冻结输入精确相同，没有重跑模型/生产写入/ECM/负载/UI。常驻68/31657/17139、upTag0/config不变；WAN4仍down，既有四路failover精确不变。首次本地调用语法拒绝原记录保留，141 runtime原Git字节归档，旧证据不改。发布archive验证后立即暂停本夜heartbeat，10点后不新实验，临时keep-awake自到期。下一步用户醒来一次集中真人CS2＋已有下载的140单WAN三段20秒闭环；140整合完整ABA尚未执行，139撤销/重学和128约30Mbps CPU仅历史实测，不扩WAN/不新下载/不重复准备。以STATE开头为准。

## NSS141及更早历史

# 接续此研究

最新NSS141：140最后真人入口已离线整合，1385绑定/原355全部继承，完整class/程序tuple/双向tag保留，新增撤销10RAM/程序过滤10RAM及8Node，默认inspect现场0pair/no writes。正常20秒A/B/A2；受支持BE改类先stop新学习、完整同query→仅TCP CI撤销/原UDP核验，再结束旧代，不能作为完整ABA，必须新分类/pin/checkpoint/owner重进。140整合factory完整ABA未执行，139实测和128 CPU只继承历史。6/27/100及字节上限不变；初断言/无效尺寸模型/alias/过大模型命令原失败冻结。常驻68/31657/17139不改，终态ECM全零无残留/两根/receiver恢复，WAN4down四路不动。最后真人留醒来集中一次，不UI/新下载/CPU重复/扩WAN，09:50晨间收尾10点前暂停本夜；STATE为准。

## NSS139及更早历史

# 接续此研究

最新NSS139：实际138/1340项，单WAN2完整真实BULK→BE同query/同CT，比较器只TCP，ECM2→1/原UDP RT CI保持，再旧代0；恢复同socket后新分类/kernel pin/checkpoint/owner与不同CI重学2→0。两完整审核/两根/端点恢复，success-only完整恢复后5秒记录宽限，失败仍100秒，6/27/100/180及字节上限不变。135仅第一撤销过、第二期限拒绝；129/131/132/133/136/137原失败和原因分开冻结。129常驻4859自然apply256/0.35秒退出，procd31657/guardian17139、68/config/upTag0不变；orphan batch只是未证实假设，不改classifier。终态source0.91、selectors0、ECM关闭全零，无事务/stage/state/模块，两物理原根/7负载/SSH receiver已恢复，WAN4仍down四路failover不动。旧128 runtime原字节保存，本轮无CPU/300Mbps/真人验收。下一步仅把实测撤销/重学并入最后真人入口，先离线；睡眠不UI/新下载/扩WAN/CPU重复。09:50收尾10点前暂停本夜；STATE为准。


最新NSS128：消费者双向tag按实际class/同源完整CT mark NAT lease派生，未知与未准入RT拒绝；生产仍TCP BULK＋UDP RT。127一真实历史帧＋13模型共14过，TCPRT/UDPBULK仅模型；128三入口检查/1069项、同tuple完整native bundle不变。实际WAN1完整20秒A/B/A2、ECM0/2/0、四tag/四leaf/mark/NAT/affinity/6续租/精确恢复过，上传29.837/30.372/29.747，softirq10.034/5.246/10.393%，可比7条件全过，短窗相对低48.64%（非300/长期/真人）；UDP718/718、781/781、720/720、四leafdrop0/squeeze0。原完整终态source2.87/4859/17139/68upTag0不变、ECM全零无残留、两根恢复、端点关闭，WAN4仍down。下一步只真实改类精确撤销/新epoch重学：先审slot close/drain/全局续租和同源完整分类，受控TCP暂停诱发BULK→BE；投影缺失不当改类/CT退出，旧CI未退不改tag/terminal不能强续。6/27/100/checkpoint/独立撤销不改；不再追CPU阈值、不扩WAN/共享预算/WiFi/autorate/新下载/UI。09:50收尾10点前暂停本夜；STATE为准。


最新NSS126整理/实际125：仅扩同观察器到5rpwan/wan/lan4，UP60/DOWN30/32上传保持；WAN2真实20秒三段、ECM0/2/0、四leaf/mark/NAT/affinity/6续租及恢复通过，上传30.356/29.956/30.734、softirq10.237/4.496/10.011%，背景0.167/0.099/0.350Mbps，UDP774/774、746/748、771/771，四leafdrop0/squeeze0。背景范围0.2513略超分析0.25，原严格comparison=false保持；重复CPU信号可继续工程，不为了阈值重做CPU试验，也非真人/300或完整CAKE验收。125首SSH握手超时/0上传/未stage失败冻结；126同1033项入口只重试一次，无源/超时变更。2端点关闭、新checkpoint及独立100秒守护、原完整终态source3.05/4859/17139/68不变、ECM全零无残留，两根恢复、WAN4仍down。下一步实际class→双向tag最小消费者绑定/未知拒绝/改类精确撤销，再最后真人一次；不重装/新下载/UI/扩WAN；09:50收尾10点前暂停本夜；STATE为准。


最新NSS124：只把UP30/29→60/59，RT1/ceil60、DOWN30、有界32发送与6/27/100期限保持；实际WAN5完整20秒三段，ECM0/2/0、四leaf/mark/NAT/affinity/6续租及恢复通过，确认上传30.709/30.774/30.727Mbps、softirq9.479/4.758/9.655%、UDP826/826、827/828、828/828，四leafdrop0/squeeze0。B恢复约31，不新增严格整机CPU/真人或60限速验收。120hint rename写前拒绝、123有限匹配失败原义保持；122只读最多重读1次，124保留UDP peer/只换TCP自然同WAN，不改PBR/认证。1000项入口、checkpoint/独立100秒守护和3端点关闭，124首次SSH关闭超时保留、只读复核通过；终态source3.03、4859/17139/68配置不变、ECM全零无残留，两根恢复，WAN4仍down。下一步所有WAN同观察器CPU对照，再最小class→双向leaf/精确撤销，最后真人一次；UI停用、不新下载/重装/扩WAN；09:50收尾、10点前暂停本夜接续；STATE为准。


最新NSS119：只给32Mbps上传增加64KiB信用上限、890项/4合同；WAN5真实完整20秒A/B/A2、ECM0/2/0、四leaf/mark/NAT/affinity/6续租及恢复通过，确认上传30.607/16.331/31.192Mbps，UDP798/798、811/811、814/814、RTdrop0、上bulk36/parent9804 overlimit。A/A2约31、B约16，未验收CPU；较118 WAN1变化不作因果比较。下一步仅上行组30→60、bulk29→59/RT1/ceil60、下行30，保持有界32发送与全部期限，自然选择WAN5不改PBR。原120候选尚未现场；常驻68不变、终态4859/17139/source2.97、ECM全零、双mq/fq_codel恢复、端点关闭、旧118原字节保留。UI停用、不新下载/重装/扩WAN/WiFi/共享预算/autorate；09:50后收尾、10点前暂停本夜接续；STATE为准。


最新NSS118：只改上传48→32，857项/9边界；单WAN1完整20秒A/B/A2、ECM0/2/0、四leaf/mark/NAT/affinity/7续租及恢复通过，确认上传32.260/16.590/39.189Mbps，UDP703/703、817/817、864/864，RTdrop0、upbulk32/parent10573 overlimit；较小步幅未恢复B吞吐，不算CPU或真人收益。发送器会在阻塞后补发累计债务，A2超过目标，下一步只加信用上限，再必要时单独查上行预算，不同时改。原队列30/29/1、6/27/100期限和常驻68不动，终态4859/17139、source1.27、ECM全零、双mq/fq_codel恢复、端点关闭，WAN4仍down，旧117原字节保留。UI停用、不新下载/重装/扩WAN/WiFi/共享预算/autorate；09:50后收尾、10点前暂停本夜接续；STATE为准。


最新NSS117：同825项116入口，仅负载方向改上传；首发布读取竞态在ECM前拒绝并恢复，117一次重试成功，原失败保留。单WAN1三段各20秒/ECM0→2→0，服务器确认上传48.097/17.201/42.156Mbps，softirq13.053/4.513/13.424，UDP864/864、820/820、850/850，双向四leaf/完整mark/NAT/affinity和恢复通过；不从不同吞吐计算CPU，不是真人/300Mbps/完整CAKE或上行拥塞验收。常驻68/4859/17139/config不变、upTag0仍保持；队列30/29/1/默认950不变，6秒来源/27native/100owner不放宽。两个stage、两个端点均关闭，终态ECM全零无残留、双物理原mq/fq_codel恢复，WAN4仍down四路PBR，旧115 runtime逐字节保留。下一步只降发送48→32Mbps、维持队列及期限看吞吐切换与RT；不重装/重放/扩WAN/WiFi/共享预算/autorate/新下载/UI，最后一次真人。夜间到10:00，09:50后收尾并暂停本夜接续；STATE为准。


最新NSS115整理/实际114：单WAN2真实TCP+UDP、20秒A/B/A2/ECM0→2→0，物理LAN4下行8f05/06与wan上行8e05/06四leaf命中，mark/NAT/affinity/7续租/两根及模块恢复通过；TCP26.378/26.998/25.884，UDP868/868、933/933、866/866，下bulkdrop204/RT0，上bulk/RT+36842/+923包/0drop。不是真人/300Mbps/完整CAKE或上行拥塞验收；常驻upTag0不变、受控由真实class映射。114新入口793项，9000/65536/73728传输上限、6秒来源、27native/100owner不放宽。110原恢复拒绝保留，111整体通过；112传输写前拒绝/未stage，113两树建成却旧normalizer拒绝、ECM未开，全部原义保持。113只修procd脚本正常exec minieap的精确身份审核，未改认证；失败未选中WAN4PID变化单独允许，其它配置/路由/服务严格。四stage与五端点均清理，115终态4859/17139/source1.70、ECM关闭全零无残留，两物理默认根恢复，WAN4仍down四路自动PBR不改，旧109 runtime逐字节保留。下一步上行压力/RT与最小自动映射，之后一次集中真人；不扩WAN/共享预算/Wi-Fi/autorate、不重装/新下载/UI。夜间至10:00，09:50不新生产实验；STATE为准。


最新NSS109：两次实际8秒捕获484请求/484serverTX，router最早Linux tap465，之后private WAN/IFB/bridge/LAN/PC均465，19缺口前于tap，上游与NIC早期未分开。TCP44.407/47.999Mbps，BULK WAN3/RT WAN2，非同WAN/NSS/CPU/真人验收。首108自身capture drops160拒绝且server提前中断保留；109先filter后接收两次drops0。auth-recover PID缺失set-e故障仅查询修复并保留，checkpoint/180秒独立撤销/SSH/native审核，保护manifest一行改变；自然恢复请求后返回0但WAN4仍down，不称认证恢复。既有健康控制器[100,100,100,0,100]的300桶严格源码模型通过，四路75/75/75/0/75，旧全5WAN审核拒绝保留。终态4859/17139/config不变，ECM关闭全零、无残留，两端点关闭；旧107/98/92/82 runtime保持。105/662仅历史资格，新写前须绑定声明auth修复和实际四路基线。下一步接回单WANNSS预算/关键上行与最终一次真人，不扩WAN/共享预算/新下载/重装；STATE为准。


最新NSS107：更新：2026-10-05 23:56，北京时间。最新NSS107，常驻仍NSS68；实验均撤销。 新启动观测入口在单WAN完整20秒A/B/A2通过，后续错误tag零新增。新轮实际TCP 25.058/27.131/26.567Mbps；UDP收到/发出 761/793 → 867/904 → 794/820；续租7次，bulk/RT drop 293/0。本轮原始启动错误为零，1包启动例外仅目标RAM案例覆盖，尚未现场触发；RTT p95约238.08/240.69/237.75ms，squeeze全0，UDP仍约4%未返回。异步leaf含38字节overhead约28.12Mbps，不作精确30Mbps限速验收。 新105/662入口，启动原始边界至多TCP-down1包1500B可记录但不能作ECM许可；100ms等待/未来错误零新增/原完整policy/双向/20秒A仍先于ECM，原失败103保留。常驻4859/17139/config581b5d46…c791d7不变，终态ECM全零无残留；旧98/92/82 runtime原字节保留，六端点均关闭。仅LAN4下行/upTag0，没有新CPU/真人/300Mbps验收；首背景raw覆盖已披露仅恢复实际工具聚合，不伪造。下一步只补单WAN拥塞/回程，不扩WAN/共享全局预算/重装/新下载，STATE为准。


先读 `docs/STATE.md`、`docs/PLAN.md`、最近一轮 `docs/EXPERIMENT_LOG.md`。用户在对话中的新指示优先；不能把历史授权或证据扩展到新的危险动作。

最新NSS98：48Mbps单WAN2完整功能A/B/A2，ECM0/2/0、bulk/RT/ct mark/NAT/affinity/两续租/精确恢复通过。47.031/47.981/48.004Mbps；首A UDP77未回复，CPU只接受B/A2吞吐差0.05%、softirq5.245/18.860（降低72.19%），不称三段严格可比或游戏改善。97只改60→40Mbps预算、发送48、bulk39/RT1/ceil40、fallback950；7RAM及实际4queue/5class通过，bulk+148drop/overlimit增量0，RT0，B UDP223/223，吞吐32.868/35.091/33.274不接受CPU对比/长期限速。93/94只读104/64CT帧同flow52↔32，52缺口在可观测软件IFB/CAKE交付之前，队列drop0，不支持Windows/CAKE主要丢包；上游与未计数入口未分开。95原52 UDP120/0在ECM前拒绝。3checkpoint/45秒独立恢复、5端点180秒FW/210秒客户端退出通过；95首次早于expiry关闭检查拒绝、后来自然expiry通过分开。19:50原完整终态4859/17139/source1.64，常驻68不变ECM全零无残留。当前96/556、97/580，真实加速upTag仍0，仅LAN4下行；旧92/82 runtime保持。下一步收尾单WAN拥塞/首段过渡，再一次真人验收；不把52端点空窗卡住所有工程，不重装/重放/新下载/扩WAN。STATE为准。

最新NSS92：60Mbps组下32Mbps真实同WAN2 TCP/UDP完整A/B/A2、ECM0→2→0、正确bulk/RT/NAT/PBR/续租/撤销通过；31.996/32.023/32.003Mbps可比，softirq15.19/4.97/14.43%，相对软件均值降66.41%，UDP239/239、238/238、239/239，leaf drop0/0。活动counter观察改为最多一次单调/交叉范围重读、wrong tag包/字节0、完整policy与双向包保持；30 RAM与91两次实际边界通过，原TTL/native scope不变。87客户端EPERM退出故障保存，88容忍临时status共享冲突3案例，实际未再触发不称注入恢复。52窗口回程不稳，新getter两次initial down0写后/ECM前拒绝；server发出246/PC33，亦有249/249，根因未定，不归因NSS。6 checkpoint/独立45秒恢复，9端点180秒FW恢复、unit/端口/client退出。18:42原完整审核4859/17139/source2.88，常驻68不变、ECM关闭全零无残留。当前成功入口91/555、52诊断89/533；旧82 runtime原字节与原失败保持。下一步只定位UDP回程后补52Mbps可比闭环，再一次真人验收，不重装/重放/新游戏下载/扩WAN；STATE为准。

最新NSS82：用户已接受工程用自有端点受控TCP＋低速UDP，Steam/CS2只留最后集中体验验收。79/82完整单WANA/B/A2、ECM0→2→0、真实自动bulk/RT leaf、mark/NAT/affinity及恢复通过；18Mbps实际吞吐可比，softirq9.65→4.31→9.48%，约54.97%相对降幅，只是短窗。82发送32Mbps、实测14.90/17.16/18.08不匹配，不验收其CPU；bulk丢弃143、RT0、B UDP213/213回复。80字节上限退出及ACK1包60字节拒绝、81初始down1包1500字节拒绝原失败保留；82所有五个getter只对精确两种偏差重读一次、第二次仍原严格检查，实际触发down分支，ACK仅17RAM不称现场。5 checkpoint/独立45秒全恢复；17:05原完整审核4859/17139/source1.15通过，常驻68/config不变，ECM关闭全零，无残留。端点FW180秒独立恢复、规则0、临时unit/端口/客户端已退出；完整实际输入和端点凭据留本地。下一步直接提高单WAN受控预算，不重装/重放/新游戏下载/扩第二WAN；真人CS2和300Mbps尚未验收。STATE为准。

最新NSS78：仅只读时序诊断，入口仍77/355项、常驻仍68。16.08秒/154次/6个发布，64次age<1.65，发布延迟0.27–0.32、周期2.99–3.01；快照仅1–3条，不是高负载资格。当前Steam下载完成0bps、CS2菜单、0真实同WAN对，无77 stage/ECM放行/A/B或收益。14:56原完整审核通过4859/17139、source3.67、ECM关闭全零，无事务/stage/state/模块。原77runtime原字节留存，2新源/累计992。下一步只用77做一次有真实负载的集中闭环，不重装/重放/新游戏下载/扩WAN；轻载时间重叠不当准入。下方77及更早是历史。

最新NSS77：常驻仍为NSS68/config581b5d46…c791d7。真实CS2/Steam现场已跑至NSS76；71实际ECM=2但B仅1.56秒，无完整A/B/A2或收益验收。73/74同源完整帧确认选中TCP缺失，UDP保留；75把最终TCP选择移到checkpoint后，完成A5.06秒后标签读耗时消耗学习余量；76初始ready在age2.94秒通过，后续pair/标签准备所需余量不一致。77只收紧初始准备age<1.65秒，继承76先读getter再做最终分类证明；355绑定/9目标RAM/完整fast语法通过，未现场试77。所有已stage轮次checkpoint和独立45秒守护，最终14:21原完整审核通过，4859/17139、ECM关闭全零、无事务/stage/state/模块。用户物理Esc停止桌面操作，已停止UI并撤下精确客户端guard，不声称本轮最终UI恢复。既有RDR2下载完成、最后UI仍验证文件；不再新下载/重装/重放/扩WAN。下一步只用77做一次集中同负载闭环，先实测资格再解释收益。

最新NSS68（下方67及更早为历史）：publication候选32,019字节已实际保留，部署work/nss68/deployment-latest.json、config581b5d46…c791d7；workerSHA40169c…3828。checkpoint下载/SHA/gzip、独立180秒守护写前核验，原完整审核和远端commit读回通过；本轮没有新自然回滚，复用66/67证据。四模块不变，47/49旧引用原字节不覆盖。新入口work/nss68/real-session.mjs原241+16=257项，17新绑定检查通过，消费者/原完整审核/stage同一明确committed部署；现场只读准入source1.46和恢复1.26通过，未执行新的NSS stage或ECM放行。17138自然退出：10:32:50 tc child cleanup未获证明，apply256/4.35秒，先于下载，TC监督与47同字节；自动恢复23634/17139，长期稳定未验收，不能归因JSON或下载。现有黎明杀机恢复界面瞬时312后回暂停，真实4秒2.879Mbps/425pps；审核0.587Mbps，不是高负载证明。下载已暂停0bps、360秒客户端守护观察暂停后取消；未开CS2/新下载/购买/卸载，无HUD/真人或CPU收益。10:37原完整终态source3.24通过，ECM关闭全零，无事务/stage/state/模块。23新源/累计868，12私有运行输入及257绑定输入冻结，旧67runtime原字节保持。下一步直接集中真人CS2+现有Steam单WAN同负载A/B/A2，每轮读新实例；不重装/重放/扩WAN。STATE为准。

最新NSS66–67（下方65及更早为历史）：publication候选32,019字节在真实372/367/385Mbps、约3万pps运行；高负载期间原完整审核source3.62/4.41<6通过，含观察器且非同窗CPU对照。66实际209/148Mbps，仅较低负载。两轮各checkpoint+独立180秒自然撤销精确恢复原47/config/指针、四模块不变，stage后按owner/inode取消；两次到期context SHA拒绝原失败保留，非source超时。01:09原完整最终审核/清理通过，worker9454/guardian9455/source2.22，ECM关闭全零，无事务/stage/state/模块。恢复后原审核同窗314Mbps/source5.97，仅0.03秒余量非稳定证明。Disco Elysium8.7GB完成；黎明杀机D盘17%已暂停、网络/磁盘0bps，未购买/卸载/启动游戏，独立客户端360秒首轮自然-shutdown实际验证、后续确认完成/暂停才取消。NSS63/241项不变，无新候选入口/ECM放行/CS2/HUD/真人或CPU验收。22新源/累计845、14完整实际输入私有冻结，旧65runtime原字节保持。下一步候选实际保留部署与消费者/原审核/stage共同精确绑定，然后集中现有暂停下载+真实CS2单WAN可比A/B/A2；不重复轻载试装/旧36/29/99/13/新下载准备/重装/扩WAN。STATE为准。

最新NSS65（下方64及更早为历史）：publication候选32,019字节实际短时运行，两次原完整审核source2.69/1.78通过；checkpoint/独立180秒撤销写前核验，自然到期精确恢复旧worker/config/指针，四模块未变。候选worker9414/guardian9415同producer；00:04恢复后完整审核/清理通过，常驻47配置不变、worker20030/guardian20031/source2.43，ECM关闭全零，无事务/暂存/state/模块。三个自然窗0.025/0.031/0.018Mbps，非同负载，不能算CPU或高负载收益。stage在生产自然恢复后按owner/inode取消，未宣称480秒自然到期。NSS63/241项不动、没有新候选入口绑定/高负载/游戏GUI/下载/真人指标，旧36/29和99/13未重跑。8份白名单源/累计823，8份实际完整输入私有冻结，旧64runtime原字节留存。下一步直接高负载完整发布/原审核与正确绑定后的集中可比单WAN A/B/A2，不重装/重放/扩WAN/新游戏维持准备；STATE为准。

最新NSS64（下方63及更早“最新”为历史）：只读定位和JSON发布边界候选，常驻47/config不变、ECM关闭全零。真实319条三对编码CPU179.06→136.22ms（−23.92%），规模夹具完整字段相同，不是整机/高负载收益。最新native36投影/29完整编码，32,019字节候选目标SHA精确编译，未执行watch/安装，NSS63入口241项保持。2048组合runner124/观察器时长2失败保留、六秒不放宽。自然4.03秒仅0.023Mbps。23:15原完整审核/清理通过、同worker20682/guardian5412/producer/source2.61，无事务/暂存/state/模块；无游戏GUI/新下载/生产配置写入/新checkpoint或回滚试验。20源码冻结/累计815，旧63runtime原字节保留。下一步只做publication单项checkpoint+独立撤销短测，再测高负载原完整审核与集中可比A/B/A2；不重装整套分类器、重复已完准备、用新游戏维持准备或扩WAN。STATE开头为准。

最新 NSS63（以下53等“最新”按历史理解）：常驻47/config不变，最终ECM关闭全零。入口`work/nss63/real-session.mjs`241项；NSS56 WAN1真实A+B、ECM0→2→0、bulk/RT+4755/+549、完整mark/NAT/affinity与恢复通过，A2计数拒绝。两段304/262Mbps、WAN58/31不匹配；B实际HUD有loss/Miss0、jitter1–2ms，但助手在线闲置、没有真人体验，CPU/游戏收益未通过。12现场案例/5独立45秒暂存恢复（1个WAN1、4个WAN2，非同时），只有56放行。NSS61首次AFTER stale失败及后来原审核通过分开保留。62短子进程竞态15 RAM案例/63同字节复用，200ms不变；63依赖导入修复，最新在原完整source7.41>6写前拒绝，未现场验证新helper转发。worker自然5411→20682、guardian5412，未主动restart，原因未知。最终21:26完整审核/清理通过，全部新游戏下载自然完成、零速率，CS2退出服务器/HUD恢复。144新增源码冻结/旧53runtime原字节留存；报告WAN投影错误已对实际selected更正、原v1私有保留，运行时不变。下一步仅修高负载完整发布/审核延迟，再补负载可比A/B/A2；不重装/重复99+13/新增下载长期准备/扩大流数TTL或第二WAN同时加速。见STATE和PLAN。

最新 NSS53：常驻仍 NSS47，ECM 关闭全零。`work/nss53/real-session.mjs` 已绑定159项（140基础＋19新项），NSS52进程候选同字节，在真实Steam294–366Mbps下六次只读发现6/6通过；原200ms出生条件不变，实际接纳最大180ms，余量有限。原拒绝帧诊断已绑定，投影缺失不判CT退出；最终拒绝后至多读一次严格同producer/query的完整分类，来源不同记录未知、不改权限/重试。60本地断言（21重放＋39新断言）/14原生helper/轻载与下载实际只读ready保持；合成不存在键不是真实加速。未更换常驻、没有路由器实验写入或新NSS A/B；24Steam bulk/0CS2/0同WAN对。DOOM（2016）负载已暂停、0bps，未购买/启动/卸载或重下DOOM Eternal，本轮没操作CS2 GUI。18:38完整保护审核/清理通过、同worker/guardian/producer。24源码冻结、旧52runtime原字节保留；下一步直接用53做同负载客户端闭环，不重复安装/99+13旧准备，不扩WAN。以下52/49等“最新/当前”为当轮历史，以STATE开头为准。

最新为NSS50–52，实际当前状态见`evidence/current-runtime.json`。常驻仍NSS47，ECM停止全零。已资格绑定入口`work/nss51/real-session.mjs`（140项），六次新尝试未放行ECM，四次单WAN临时暂存/独立45秒恢复和完整审核通过；两次仅软件A完成，客户端实际HUD已归档。NSS50仅接纳实验前健康且命令相同的sing-box core/guard PID变化，期间变化仍拒绝。NSS51进程发现实际下载仍1/3通过；NSS52仅父进程字段解析候选、34项检查/两次轻载只读通过，未安装/未生产绑定/未高负载资格。先解决该根因和拒绝帧分类诊断，再补同负载客户端闭环；不重复安装和旧99/13项准备。15/14/7份源码冻结不是额外准入。DOOM已完成、未启动，CS2已退出测试服、HUD恢复；无需用户持续挂机。下方NSS49“当前入口”等是该轮历史说明，以本段和STATE为准。

当前常驻引用 `work/nss47/deployment-latest.json`，配置 `478818d553903aa859c853cab99383e038d4d325f500d68843ffff8b7517a900`。NSS46 三项可靠性修复上仅叠加每观察重置、各 1024 项的纯 IPv4 缓存。CT/mark/NAT/计数不缓存，4550 差分样本和目标 527 行/3 个完整快照一致，解析 CPU 约下降 26.4%，不是整机收益。独立 180 秒自然恢复及另一保留安装的 checkpoint/回滚/完整审核通过。

当前入口 `work/nss49/real-session.mjs`，121 项绑定、99 项本地入口案例、13 项目标 RAM 模拟。仅初始无包等待由 0.3 改为至多 1.2 秒，并受原 epoch/45 秒 owner 余量约束，错误 tag 立即拒绝、无包不能放行；初始 <1 / 预学习 <2 / 软件 6 / 发布 9 秒、20 Mbps、一 TCP＋一 UDP 不变。实际 WAN2 CS2＋Steam 完整控制器成功：三段各 5.03 秒/11 帧、ECM 0→2→0、bulk/RT +7635/+713 包、mark/NAT/affinity 正确、一次续租和精确撤销通过。是助手进入在线观战，没有真人体感；168/194/171 Mbps 不匹配，B 段 HUD 缺失，CPU/游戏收益未验收。第二轮下载已完成，写前等待，无 NSS 写入。最终 ECM 关闭全零、无事务/暂存/模块，worker 5411 连续健康。不要重放已通过的准备，先补同负载客户端证据。

NSS46 历史三项修复及轻载真实 apply/recover/crash 保持：apply 年龄 6.27 秒拒绝、recover 0.80 秒，同 worker；精确 crash 后 7.56 秒新实例健康。两次独立 180 秒自然恢复、480 秒暂存自然清理保持。其旧常驻引用/84 份源码/112 项入口不改写。NSS47/48/49 分别 19/37/47 份可读源码冻结，实际完整绑定副本留私有。原 NSS46 高负载初始年龄失败、NSS48 TCP 无包取证失败均未放行 ECM，完整恢复通过，不被 NSS49 成功覆盖。

NSS46 历史入口的 112 项绑定/99 项案例/0.30 秒 classification 提示及原完整审核保持。原 NSS42 102 项入口不改写。NSS49 继承的 `nssRouterPayloadsUnchanged` 字段不描述本轮 helper 差异，必须按精确哈希和 13 项新证明解释；其余 NSS Lua 与 NSS48 相同，内核/driver/固件未升级。高负载故障恢复、CPU/游戏收益仍未通过，不把模拟/短时在线观战当真人验收。

NSS45 两项临时试装、114 个本地案例、目标 RAM/7 个真实 query 子进程与全部历史失败保持原义。其当时未保留/未安装的结论是历史快照，不代表 NSS46 现网。换端口/旧流退出仍主要为算法证据；不可伪造真人 CS2 指标。

NSS44 真实 WAN1 配对、39 次写前过期拒绝、自然 stale-before-write/首次恢复失败证据不改写。其等待候选已由 NSS46 新入口另行资格核验和绑定，不能覆盖旧失败或使用旧来源清单。

NSS41 的真人 fast path/leaf/mark/NAT 功能与原失败、NSS42 的 90＋4 项检查/600 秒自然轻载、NSS43 的 48 秒只读负载证据保持。20 Mbps、一条 TCP＋一条 UDP、原学习/调度/owner TTL 不变。不要重跑冻结旧入口或暗中扩大预算；NSS44 的 16 份只读/未安装候选源码冻结不是生产准入资格。

## 主线与证据

- 主线只有：自动分类 → NSS bulk/RT leaf → 真人 CS2 + Steam 单 WAN 闭环。
- 未通过真人同负载 A/B/A2 前，不扩第二 WAN、共享预算、Wi-Fi、autorate 或五 WAN。
- CAKE 是软件基线和未加速流 fallback。不要继续长期优化 CAKE。
- 多人 host fairness 不作为目标；基本不考虑 N100。
- 严格区分代码检查、模拟、低负载硬件实验、真实高负载实验。请求了 A/B 的字段不代表 A/B 成功。
- ICMP 或合成 UDP 不能代替 CS2 jitter/loss/Miss。没有客户端数据就明确未测到。
- 新建连接由 Linux PBR 决策；已建立连接保持 WAN affinity。完整 ct mark、NAT、zone、实例 ID 和双向元组均应核对。

## 现场变更

- 先核验部署哈希、现网、认证/PBR/服务、ECM 状态和上次清理结果。
- 所有路由器变更前先 checkpoint，再布置独立于控制连接的超时回滚；不能独立恢复的风险不执行。
- 一次一个主要变量，单 WAN / 单连接对优先。不要为了通过而延长有效期或跳过准入检查。
- 禁止刷机、升级内核、修改 ART/GPT/U-Boot/分区、清空全部 conntrack、重建全部生产 qdisc、破坏五路认证/PBR/sing-box/Tailscale。
- 不运行来源不明的在线脚本，不绕过学校网络政策。
- 无需每一步请求用户确认；在已授权边界内自主推进。先完成离线与只读准备，再集中请求一次真人测试，不要求长期挂游戏或反复下载。

## 文件与版本

- 此仓库没有登录凭据、原始 CT/socket 转储、备份、部署私有配置或模块二进制。不要把这些加入 Git。
- `code/` 保存精确源文件，`source-manifest.json` 给出它们的原始路径。部署代码与候选代码分开描述。
- 原工作区的 NSS32/NSS33 证明文件是冻结证据。不要覆盖它们来迎合新代码；新一轮使用新目录与新证明。
- NSS36 实际失败目录已保存 59 份与当次 manifest 一致的源码/证明副本。后续候选从新轮次开始，保留这次失败与回滚证据。
- NSS37 源文件/证明已经被当前 66 项 manifest 绑定。修改任一绑定文件须在新轮次重新资格核验；不要把沿用的 NSS36 消费者/backend 检查计为新执行的检查。
- NSS38 实际失败的 70 份源码/证明副本已冻结；其 `classifier.lua` 和现场入口仍使用 NSS37。`candidate-*.lua` 是分开的未安装候选，不能把候选本地通过写成现场通过。
- 修改后运行与变化相关的离线检查；现场验证结果单独记录。完成后更新 STATE、PLAN、EXPERIMENT_LOG 和结构化证据再提交。
- 上游 Issue/PR 仅进入 backlog；缺乏最小复现与修改前后证据时，不提交上游。
