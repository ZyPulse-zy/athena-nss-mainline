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
