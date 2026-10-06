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

## NSS148及更早记录

# NSS143–148 · 修复软件对照段并完成后台下载闭环

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

本轮发布第一次在本地reports目录缺失时中断，部分导出已经完成，但没有开始提交或推送。原导出脚本及已生成证据保持原字节；单独的complete-publication接续只创建明确目录并复制原HTML、增加自身白名单和失败证明，随后重新校验，不重跑硬件。见 [发布失败](../evidence/nss148-publication-failure.json)。

首次仓库校验把资格模型bundle73,685误作实际stage长度，拒绝了原本正确保存73,686的实测轮次。提交链停止，失败checker原源码和输出留本地，保留正确实测证据，仅更正checker与新报告文字；模型guardian8,903和实际8,899继续分开，未重跑硬件。见 [校验失败](../evidence/nss148-validation-failure.json)。

暂存whitespace检查另拒绝六份冻结源码副本的原有空行；提交前停止，仅添加六个明确路径属性保留原字节，其它检查不放宽。见 [whitespace失败](../evidence/nss148-whitespace-failure.json)。

首次实际Git archive的仓库checker已通过，但额外历史比较误用了Windows CRLF工作副本哈希；失败的107文件在原提交和新archive的Git字节实际相同。停止完成发布标记，保留第一verifier和失败，新增v2直接按原Git blob逐字节核验全部历史源码/证据，不修改旧文件。见 [归档校验失败](../evidence/nss148-archive-verifier-failure.json)。

## NSS142及更早历史

# NSS142 · 晨间只读收尾

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

# 最新实验

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

# 实验记录

## NSS129–139 · 2026-10-06 06:30 · 真实改类精确撤销及新代重学

更新：2026-10-06 06:30，北京时间。最新NSS139整理、实际138；常驻NSS68/config581b5d46…c791d7，worker自然恢复为31657、guardian17139未变。全部实验已撤销。

**真实同一TCP/UDP完成了自动改类、精确撤销和新代重学：TCP上传暂停后，同源完整分类帧判定BULK→BE/cooldown；比较器仅报告TCP受影响，ECM2→1，UDP保留原CI及双向RT tag；旧代结束为0。恢复应用发送后，同一CT/mark/NAT/WAN用新的分类、内核pin、独立checkpoint/owner重学，新ECM编号得到2→0。**

见 [完整生命周期](../evidence/nss139-class-lifecycle.json)、[汇总](../evidence/nss139-mainline.json)、[成功守护结束](../evidence/nss139-owner-completion.json)、[失败记录](../evidence/nss139-failures.json)、[分类器恢复](../evidence/nss139-classifier-recovery.json)、[端点关闭](../evidence/nss139-endpoint-closure.json)、[原完整终态](../evidence/nss139-final-audit.json)。

- 实际单WAN2、一TCP BULK＋一UDP RT；完整分类query1031/0.18秒，明确TCP仍有相同CT/zone/mark/original/reply/WAN且为BE，UDP仍获准RT。仅投影缺失不能证明改类或CT退出。CPU同步barrier不是firmware销毁ACK；另验实际目标CI缺失、ECM仅剩原UDP、pending全0，剩余旧分类lease约2.29秒后结束旧代，不强续terminal gate、不在旧CI存在时改tag。
- 两次新checkpoint下载/SHA/gzip与独立守护写前核验、两份1340项实际输入当前及冻结副本逐字节匹配；两次原完整前后审核/精确恢复通过。来源6秒/native27秒/owner最大100秒/client180秒、9000/65536/73728字节和1MiB读上限保持。成功只在模块、tag、两物理根、WAN/mwan3/state全部恢复且ECM关闭零计数后，留5秒记录宽限再退出独立owner；失败仍保留原100秒到期路径。没有发送取消信号或提前放弃失败回滚。
- NSS135已有同样真实精确TCP撤销，但第二代因客户端期限不足未开始，原overall失败保留。NSS131连接helper并发修改进程cwd、NSS133 Lua多返回值误作tonumber进制、NSS137预检误带执行后报告字段等失败分别定位并修复；132回包不足与136预算拒绝未stage。完整失败及本地调用错误不改成成功。11项新的目标RAM成功结束边界与原12项完整分类模型分开；旧模型源码相同继承，未反复重跑。
- 常驻worker4859在129负载中自然apply失败（status256、0.35秒），procd恢复31657，guardian17139与源/config不变。实际child PID/stderr缺失，旧orphan batch与PID重用只是未证实线索；没有为此主动重装/重启常驻分类器。新实例实际通过原完整身份审核，不能继续把4859当现网PID。
- 本轮只验功能生命周期，没有新增CPU对照、300Mbps、Steam主下载或真人CS2指标。128此前约30Mbps上传可比短窗的softirq相对低48.64%保持为历史证据，不能扩大成长期/游戏收益。最终source0.91、selectors0、ECM关闭全零，无事务/stage/state/实验模块，两物理原mq＋四fq_codel恢复；七个有限负载、临时规则/端口/客户端已关闭，自有SSH接收器0残留。WAN4仍认证down，既有四路failover保持。
- 下一步把已经证明的撤销/重学规则并入最后集中真人短测入口；先做必要离线绑定/拒绝路径检查。睡眠期间不操作桌面、Steam/CS2或新下载，不扩WAN/共享预算/WiFi/autorate/ECN，不重复CPU阈值试验。09:50不新生产试验，10点前完成晨间终态/发布并暂停本夜heartbeat。

## NSS128发布字段修正

发布复核：128分析模板末尾的旧false覆盖了原本待独立分析的nullable字段，首次仓库校验失败却误提交5a57ecd。现保留原发布v1指标/轮次字节，仅更正该元数据字段为null；独立CPU比较七项及48.64%结果和所有实测数据不变，原37份源码/私有输入不改，追加一份修正源与严格比对，校验现已通过。见 [字段修正](../evidence/nss128-analysis-label-correction.json)。

## NSS127–128 · 2026-10-06 05:02 · 实际class直接映射双向leaf

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

## NSS125–126 · 2026-10-06 04:45 · 同观察器与全部WAN背景

更新：2026-10-06 04:45，北京时间。最新NSS126整理、实际125入口；常驻68/config581b5d46…c791d7、4859/17139不变，实验已撤销。

**只给三段同一个观察器加五rpwan＋physicalwan＋lan4计数；UP60/DOWN30/有界32上传不改。实际WAN2完整20秒A/B/A2、ECM0→2→0、四leaf/mark/NAT/affinity/六续租和精确恢复通过。服务器确认30.356/29.956/30.734Mbps，softirq 10.237/4.496/10.011%，与124重复出现接近相同吞吐下的CPU下降。**

见 [实际指标](../evidence/nss126-metrics.json)、[背景和对照](../evidence/nss126-comparison.json)、[轮次](../evidence/nss126-trial.json)、[汇总](../evidence/nss126-mainline.json)、[失败](../evidence/nss126-preparation-failure.json)、[关闭](../evidence/nss126-endpoint-closure.json)、[终态](../evidence/nss126-final-audit.json)。

- 三段未选中WAN总RX＋TX 0.167/0.099/0.350Mbps，约80/64/103pps，选中TX约2942/2683/2951pps；TCP回复/ACK的包速差异保留。所有squeeze/softnet drop0，四leaf drop0；UDP收/发774/774、746/748、771/771，B少2个echo回复，仍非CS2指标。
- 完整指标显示CPU信号与124一致，足以继续最小消费者工程；严格分析合同的背景流量范围0.2513Mbps略超过0.25，原comparability=false和没有正式相对收益值保留。它不作为扩大实验或重复追阈值的理由。短窗、非随机、部分包速不同和其它CPU工作未完全等同这些边界保持；非300Mbps/拥塞延迟/完整CAKE验收。
- 首次125上传SSH握手6秒超时后客户端退出，0上传B、未checkpoint/stage/改队列/开放ECM；原失败冻结。126外部driver对同一1033项125入口只重试一次，没有修改源或超时。新观察器4项检查含目标机7接口实际只读、语法、bundle73521<73728和预计完整记录697727<原1MiB读上限；未放宽6/27/100或传输边界。
- 实际新checkpoint/SHA/gzip、独立100秒owner写前核验，两个端点180秒FW/210秒客户端全退出；最终source3.05、ECM关闭全零、无事务/stage/state/模块，两个物理mq＋四fq_codel恢复，WAN4仍down/自然四路PBR不改。旧124 runtime原字节保留、实际输入私有冻结。
- 下一步直接把消费者的上行tag映射绑定到实际class和同源身份，未知/未准入RT拒绝；保留resident upTag0、gate/kernel pin/lease，改类精确撤销后才重学，不因字段改变重装常驻。仅这条自动分类→双向leaf主线，不再追加CPU对照来追背景阈值；之后最后一次集中真人。UI停用、不新下载/扩WAN/WiFi/共享预算/autorate；09:50起收尾并暂停本夜接续。

## NSS120–124 · 2026-10-06 04:28 · 上行预算与真实吞吐恢复

更新：2026-10-06 04:28，北京时间。最新NSS124；常驻68/config581b5d46…c791d7、4859/17139不变，实验已撤销。

**上行受控组30→60Mbps（bulk29→59、RT1、ceil60），下行30与有界32Mbps上传不改。实际自然WAN5、同一对flow完整20秒A/B/A2，ECM0→2→0、四leaf/mark/NAT/affinity/六次续租/恢复通过；服务器确认30.709/30.774/30.727Mbps，B不再降至约16Mbps。**

见 [实际指标](../evidence/nss124-metrics.json)、[轮次](../evidence/nss124-trial.json)、[汇总](../evidence/nss124-mainline.json)、[拒绝](../evidence/nss124-prewrite-refusal.json)、[匹配失败](../evidence/nss124-matching-refusal.json)、[关闭](../evidence/nss124-endpoint-closure.json)、[终态](../evidence/nss124-final-audit.json)。

- softirq 9.479/4.758/9.655%，time_squeeze/drop均0；UDP收/发826/826、827/828、828/828。上下行bulk/RT queue drop均0，客户端B少一个echo回复，不能写成网络零丢包或CS2效果。选中TCP吞吐可比，暂未同时捕获其它WAN背景，严格整机CPU收益不新增验收。
- 与119同WAN5且同32发送器；上行预算增大后吞吐恢复，支持原30组拥塞相关因素参与，不把跨轮网络变化排除或写成精确AQM根因。60组未饱和，尚未验收60准确限速、拥塞延迟或完整CAKE替代。
- 120经121匹配后，旧只读hint遇发布rename在checkpoint/stage前拒绝，未改路由器。122只将已替换读数丢弃、最多重读一次；8目标RAM边界与实际只读hint通过，原5秒wait/6秒runner及完整审核不改。123强求WAN5而轮换UDP后匹配失败；端点只允许原NAT peer，冲突是合理线索，实际新UDP WAN/peer未捕获，不声称已定因。124保留UDP socket/peer，只自然轮换自己的TCP，未改PBR/认证/端点规则范围。
- 1000项新入口，native27/owner100/source6和9000/65536/73728字节边界不改。实际新checkpoint下载/SHA/gzip与独立守护在写前核验；三端点FW180/客户端210均清理，124首次关闭SSH查询超时原记录保留，随后只读确认规则基线和端口关闭。
- 最终source3.03、ECM关闭全零、无事务/stage/state/模块，两物理根原mq＋四fq_codel恢复；WAN4仍down、自然四路PBR不改。旧119 runtime原字节保持，完整私有输入冻结。未操作UI/下载/游戏、不改常驻upTag0、不提交上游。
- 下一步只补所有WAN的相同只读计数，保持当前队列/负载/来源和期限，做一次CPU对照；随后收敛真实class到双向leaf的最小消费者映射及改类精确撤销，不重装整套或长期放行未知flow。最后一次集中真人CS2验收；第二WAN/共享预算/WiFi/autorate仍后置。09:50起收尾、报告和推送后暂停本夜接续。

## NSS119 · 2026-10-06 03:51 · 32Mbps上传仍未稳定

更新：2026-10-06 03:51，北京时间。最新NSS119；常驻68/config581b5d46…c791d7、4859/17139保持，实验全撤销。

**32Mbps上传改为最多64KiB信用，避免阻塞期间累积补发债务；原双向30/29/1队列和6/27/100期限不变。WAN5完整20秒A/B/A2、ECM0→2→0、四leaf/mark/NAT/affinity及恢复通过。服务器确认30.607/16.331/31.192Mbps，A/A2回到约31Mbps，B仍只有16.33Mbps。**

见 [实际指标](../evidence/nss119-metrics.json)、[完整轮次](../evidence/nss119-trial.json)、[汇总](../evidence/nss119-mainline.json)、[上行](../evidence/nss119-uplink-proof.json)、[关闭](../evidence/nss119-endpoint-closure.json)、[终态](../evidence/nss119-final-audit.json)。

- UDP收/发798/798、811/811、814/814，上下RT drop0，上bulk drop36、parent overlimits+9804；新CPU/游戏/精确限速均不验收。B吞吐仍降，当前发送器债务不能作为唯一解释。与118的WAN1不同，本轮为WAN5，不把两轮差异直接归因pacer；本轮A/B/A2是同一对flow。
- 4项本地合同验证含真实callback时长模型及10秒阻塞后的64KiB上限，硬件helper与118/116逐字节相同。新的890项入口/独立100秒守护/完整checkpoint、端点180秒FW与210秒客户端均完成；终态source2.97、ECM关闭全零、无事务/stage/state/模块，两物理mq/fq_codel恢复，WAN4仍down四路PBR不改。旧118 runtime逐字节保存，原始私有证据冻结。
- 下一步只提高受控上行组30→60Mbps，bulk29→59/RT1/ceil60，保留下行30和同一有界32Mbps发送器。自然选择WAN5而非改PBR；未知flow默认拒绝。先验证方向布局/原预算错误拒绝/部分恢复及payload上限，再新checkpoint与独立撤销。若不拥塞时吞吐恢复，再定位30组的拥塞/AQM，不靠同时调整RT/其它参数。
- 不动常驻classifier/upTag0，不重装/操作UI/新下载/扩WAN/共享全局预算/WiFi/autorate；最后一次集中真人CS2验收。夜间到10:00，09:50起收尾和晨间报告、推送后暂停接续。

## NSS118 · 2026-10-06 03:41 · 32Mbps上传仍未稳定

更新：2026-10-06 03:41，北京时间。最新NSS118，常驻68/config581b5d46…c791d7、4859/17139不变；实验均撤销。

**只把上传目标48→32Mbps，原30/29/1双向队列和6/27/100秒来源/native/owner不变。单WAN1完整三段各20秒，ECM0→2→0、四leaf/CT mark/NAT/affinity、7次续租及精确恢复通过；服务器确认上传32.260/16.590/39.189Mbps，较小切换仍未恢复B吞吐。**

见 [实际指标](../evidence/nss118-metrics.json)、[完整轮次](../evidence/nss118-trial.json)、[汇总](../evidence/nss118-mainline.json)、[上行](../evidence/nss118-uplink-proof.json)、[关闭](../evidence/nss118-endpoint-closure.json)、[终态](../evidence/nss118-final-audit.json)。

- UDP收/发703/703、817/817、864/864、上下行RT drop0；B端点RTT p95约204.37ms，平均相邻RTT差约0.294ms。上bulk drop32、parent overlimits+10573，shaper实际工作；B上传四个5秒段仍约15–17Mbps。不能把softirq下降算同负载CPU收益，也不是真人CS2或300Mbps验收。
- 本地发送器按连接开始后的累计目标补发，B阻塞后A2实际超过32Mbps；目标是累计平均，非严格各段瞬时offer。服务端确认字节仍真实，此机制是对照负载问题，未证明它解释NSS B降速。下一步先只给发送器加有限信用上限，避免积累补发债务；原队列、RT负载和全部期限保持。之后若仍降速，再单独提高受控上行预算以区分拥塞/AQM与fast path，不同时修改。
- 新857项入口/9项本地边界检查，硬件六helper与116逐字节相同；不是重新安装分类器。单次checkpoint下载/SHA/gzip、独立100秒守护，端点180秒FW与210秒客户端全退出。最终source1.27、ECM关闭全零、无事务/stage/state/模块，两物理默认mq/fq_codel恢复。WAN4仍down，自然四路PBR不变。旧117 runtime及全部失败原字节保存，私有输入冻结，未提交凭据/CT/nonce/配置/checkpoint/二进制。
- 只推进受控单WAN主线，不扩第二WAN/共享全局预算/WiFi/autorate、不操作UI或新下载。真人留最后一次集中验收。夜间到10:00；09:50不新实验，完成清理、晨间报告与推送后暂停接续。

## NSS116–117 · 2026-10-06 03:31 · 服务器确认上传与双向leaf

更新：2026-10-06 03:31，北京时间。最新NSS117；常驻68/config581b5d46…c791d7仍4859/17139，所有实验已撤销。

**双向QoS的实际上传路径也已完成：只改变自有同一SSH TCP的负载方向，原30/29/1队列、27秒native、100秒owner与20秒A/B/A2保持。单WAN1服务器确认上传48.097/17.201/42.156Mbps，ECM0→2→0、上下行四leaf、mark/NAT/affinity和精确恢复通过。**

见 [汇总](../evidence/nss117-mainline.json)、[实际两轮](../evidence/nss117-trials.json)、[上传指标](../evidence/nss117-metrics.json)、[上行leaf](../evidence/nss117-uplink-proof.json)、[关闭](../evidence/nss117-endpoint-closure.json)、[终态](../evidence/nss117-final-audit.json)。

- 首116因发布文件更新与读检查重合，在ECM开放前拒绝，双物理树完整恢复；117只用同一825项入口一次重试，没有放宽一致性/时间或重装分类器。原失败保留。新客户端明确按服务器已读stdin字节计数，不把本地write提交当吞吐；11解析边界与真实本地1MiB/EOF receiver共12项检查，和现场证据分开。
- 三段softirq13.053/4.513/13.424%，UDP收/发864/864、820/820、850/850；全量busy、squeeze、pps、RTT和异步leaf见原指标。B上传明显低于软件段，不能计算严格CPU收益，echo不是真人CS2。实际上行parent overlimits+12640、bulk drop21、RT drop0，证明shaper活动；B的四个5秒上传窗口14.71/16.17/17.82/20.20Mbps持续回升，尚未稳在30Mbps。不能把这个短窗降速定为限速精度或根因证明；先前32/48MbpsCPU证据保留。
- 仍仅一个WAN、一TCP一UDP；上下行两个30Mbps组和默认950fallback未改，常驻发布upTag0不改。物理wan共用MacVLAN，未知flow拒绝；尚未保证全部EAPOL/其它业务在高负载树下的连续性、全套CAKE语义或五WANQoS。当前WAN4仍认证故障，自然四路PBR与学校策略保持。
- 两次stage各新checkpoint下载/SHA/gzip和独立100秒守护，两个端点独立FW180/客户端210秒恢复和端口关闭。最终原完整source1.80秒、ECM关闭全零、无事务/stage/state/模块，两物理根mq＋四fq_codel恢复；旧115 runtime原字节存档。源/实际绑定与私有原输入冻结，凭据/CT/nonce/配置/检查点/二进制不进Git。
- 下一步只把发送48降到32Mbps，维持30/29/1队列及所有期限，观察较小负载切换下B吞吐能否稳定及RT隔离；不先改预算。保持UI停用、不新下载/游戏、不扩WAN/WiFi/共享全局预算/autorate；最后集中一次真人验收。夜间继续至10:00，09:50停止新实验并完成报告、清理和推送后暂停本夜接续。

## NSS110–115 · 2026-10-06 03:05 · 四路准入与真实双向NSS leaf

更新：2026-10-06 03:05，北京时间。最新NSS115整理，实际双向硬件测试NSS114。常驻68/config581b5d46…c791d7仍4859/17139；实验全部撤销。

**首次完整证明：同一真实单WAN TCP＋UDP经ECM进入物理LAN4下行bulk/RT、物理wan上行bulk/RT四个NSS FQ-CoDel leaf。三段各20秒，ECM0→2→0，完整mark/NAT/WAN affinity正确、七次续租、两物理根及模块精确恢复。**

见 [汇总](../evidence/nss115-mainline.json)、[实际各轮](../evidence/nss115-trials.json)、[上行实测](../evidence/nss115-uplink-proof.json)、[端点关闭](../evidence/nss115-endpoint-closure.json)、[终态](../evidence/nss115-final-audit.json)、[物理队列恢复](../evidence/nss115-physical-final.json)。

- NSS110按声明auth修复与精确四WAN故障切换基线进入，WAN5完整功能A/B/A2；原整体恢复因未选中故障WAN4自然PID/running变化拒绝，失败仍保留。NSS111只允许该进程变化，其它路由、保护文件、服务仍严格相同；WAN5整体通过，实际此轮未触发新进程例外。111 TCP25.717/26.998/27.004Mbps，softirq9.706/0.876/11.881%，UDP840/840、909/909、835/835；为本轮观察，不新增完整高负载CPU或真人验收。
- NSS112新双向队列方案20目标RAM＋格式检查通过，完整包75489B先拒绝；仅删除单行源格式/注释后73011B，原73728B上限不变。一次现场guardian传输大小拒绝，checkpoint已核验但未启动stage/改队列。WAN4 procd脚本会正常exec到minieap，旧脚本argv假设产生独立拒绝；只读观察和受保护wrapper源码确认，未改认证。
- NSS113以原判定实际使用的队列字段缩小plan、保留counter原记录，原9000B传输不变；正常脚本或精确minieap argv/执行文件/PPID/start均校验，绝不输出账户参数。两物理树实际构建且恢复；旧normalizer仅允许下行标签，ECM前拒绝“Unapproved setter”，失败保持。113实际原完整恢复通过，并观察到未选中WAN4进程变化；这不等于WAN4认证恢复。
- NSS114只补四个明确class/direction writer的标签白名单和8e native alias，27目标RAM反例通过。单WAN2三段实际TCP26.378/26.998/25.884Mbps，softirq9.859/5.421/15.644%，time_squeeze全0；UDP868/868、933/933、866/866。下行bulk新增204drop、RT0；异步近B上行bulk/RT分别+36842/+923包，均0drop/backlog0。实际ECM TCP/UDP上下行tag、CT mark/NAT/WAN2正确，默认未知flow拒绝。不同吞吐和软件段差异不算新CPU收益，echo不是真人CS2。
- 两物理树各30Mbps组、bulk29/RT1、共同ceil30、默认950fallback。上行数据主要TCP ACK与小UDP，尚未证明上行拥塞限速/实时延迟、EAPOL在高负载队列下连续性或完整CAKE替代。物理wan被五MacVLAN共用，仅一对flow获加速；不是每个private WAN直接挂NSS qdisc，也不声称其它流完全没有经过新增physical root。
- 常驻发布upTag仍0；本次受控映射依据实际BULK/RT class在ECM学习前生成8e上行tag，未改永久分类器。新114入口793项必须每次重新读当前实例。既有32/48Mbps收益保留，真人/300Mbps/多WAN未验收；不要用完成的工程探针代替用户体验。
- 四个stage各checkpoint下载/SHA/gzip与控制连接外100秒owner，均精确清理；五个端点FW180/客户端210秒关闭。110两次SSH关闭查询超时原记录保留，独立只读复核最终基线/端口关闭。115原完整终态source1.70、ECM关闭全零、无事务/stage/state/模块；两物理根原mq＋四fq_codel确认。WAN4仍down，现有自动四路PBR不改。旧109 runtime原字节保存，完整私有CT/配置/nonce/检查点/凭据不进Git。
- 夜间继续到今天10:00；09:50停止新生产实验、整理终态。保持用户Esc后的UI停用，不新下载、不启动游戏、不提交上游。下一步只补单WAN上行压力/RT及自动映射缺口，之后一次集中真人验收；多WAN、共享预算、Wi-Fi、autorate和ECN backlog继续后置。

## NSS108–109 · 2026-10-06 01:04 · 精确UDP路径定位与认证恢复修复

更新：2026-10-06 01:04，北京时间。最新NSS109；常驻仍68/config581b5d46…c791d7，ECM关闭全零，无实验残留。

**两次实际8秒nonce/序号捕获定位到：484个请求均到服务器并发出echo；路由器最早Linux物理接口tap只见465个，之后private WAN→IFB→bridge→LAN→PC全部465个相同，链内缺包零。19/484（约3.93%）缺口在server软件TX→router最早Linux tap之间；上游链路与网卡接收早期尚未分开。**

见 [序号证据](../evidence/nss109-path-localization-v2.json)、[认证修复](../evidence/nss109-auth-repair.json)、[自然故障切换](../evidence/nss109-wan4-failover.json)、[捕获器边界](../evidence/nss109-instrumentation.json)、[关闭](../evidence/nss109-endpoint-closure.json)、[终态](../evidence/nss109-final-audit.json)。

- 首窗236发/227收，后窗248发/238收；内部窗口裁掉首1秒/尾2秒，使用最终PC日志和确切nonce序号，不假定服务器/路由器UTC同步。对应TCP44.407/47.999Mbps、UDP p95约209.51/209.35ms。自动分类实际TCP BULK WAN3、UDP RT WAN2：这是软件路径定位，非同WAN拥塞对照；没有NSS leaf、同窗CPU/softirq/squeeze或真人CS2新验收。
- NSS108首次捕获自身drops160、退出2，不能作缺包定位；其server捕获被异常中断，不称完整保留。109只修socket接收顺序：protocol0→socket filter→bind ETH_P_ALL，两次实际drops0、九接口方向可见。host/目标解析同6例通过；WSL不支持AF_PACKET的实际socket测试失败，未把它称通过。helper本身最多12秒、外部14秒，checkpoint和独立480秒临时目录清理先于上传；108观察到到期后自然消失、109owner/inode核验后取消。
- 写前发现WAN4认证进程无PID，旧恢复脚本set -e让jsonfilter缺失字段的退出1跳过空PID分支。真实最小复现与6目标RAM结构案例通过，只改PID读取为校验ubus结构的Lua；保护清单仅更新对应一行。checkpoint下载/SHA/gzip、独立180秒撤销写前验证，原完整native审核、单独SSH和其它运行配置核验后保留。没有主动重启认证/接口，本轮未做新的自然180秒回滚。写后原始动态tc文字比较失败保留，随后用原完整ownership审核验证动态selector。
- 现有watchdog在修复后一次自然恢复请求返回0，但WAN4仍认证失败/接口down，无IPv4；不称五WAN恢复。原健康控制器权重[100,100,100,0,100]，300桶按实际源码严格复现为四路各75桶，仅60个旧WAN4桶重派、healthy移除WAN4、3个WAN4 DHCP路由规则消失，固定ct mark规则保留。是既有故障切换，非实验写PBR。原全5WAN旧快照严格审核的拒绝保留；本轮对声明修复和精确自动切换后的其它配置/原完整native审核通过，不是新的NSS入口资格。
- 终态worker4859/guardian17139/source3.34，ECM stop1/所有count0，无事务/stage/state/实验模块。两个端点FW180秒独立恢复、client210秒退出、unit/端口关闭均通过；凭据/实际端点配置/CT/nonce/二进制/检查点/完整清单留本地。
- 历史32Mbps约66.41%与48Mbps B/A2约72.19% softirq收益保持；本轮没有加速写入/新收益/真人指标。仅LAN4下行/upTag0的缺口保持。旧107/98/92/82 runtime逐字节保留。下一步回到实际四路基线下的单WAN入口和NSS QoS预算/关键上行，不再用这两窗约4%缺包要求反复调整CAKE；最后一次集中真人验收，不扩WAN/Wi-Fi/autorate/共享全局预算。

## NSS99–107 · 2026-10-05 23:56 · 20秒拥塞与启动观测

更新：2026-10-05 23:56，北京时间。最新NSS107，常驻仍NSS68；实验均撤销。

**每段20秒的单WAN工程观察已完成两轮；新启动观测入口在单WAN完整20秒A/B/A2通过，后续错误tag零新增。**

见 [实测汇总](../evidence/nss107-mainline.json)、[所有stage](../evidence/nss107-trials.json)、[启动观测检查](../evidence/nss107-startup-epoch-qualification.json)、[端点关闭](../evidence/nss107-endpoint-closure.json)、[终态](../evidence/nss107-final-audit.json)。

- NSS99：40Mbps组、发送48，WAN2三段TCP34.417/36.069/34.872，7续租、ECM0/2/0，bulk新增363drop/RT0。UDP811/832、815/852、809/834；不是全部回包，不验收端到端QoS/精确限速或新CPU收益。
- NSS100首次客户端SSH约11秒keepalive超时，路由器写前拒绝；NSS101同入口一次重试。30组受LAN4其它流量260/308/320Mbps影响，TCP5.498/15.754/7.679，UDP833/867→23/955→2/714，squeeze45/101/130，RT leaf仍0drop。缺口在返回软件后继续，不归因NSS。用户随后暂停下载，LAN4只读降至0.039Mbps，路由器其它WAN仍约67Mbps。
- NSS103暂停后短测initial发现TCP-down错误1包1500B，在ECM前拒绝并完整恢复。forward writer与postrouting getter跨钩子发布可能捕获已越过writer的包，此为解释假设，没有内核/固件缺陷证明。
- NSS105将启动原始计数保留，建立仅用于观测的基线，允许原始启动边界至多这1个TCP-down/1500B；其它错误/neighbor拒绝，未来错误必须零新增、所有计数单调/完整policy和学习前双向正包保持。100ms软件等待包含在原1.2秒getter期限内；软件A20秒仍先于ECM。没有清空counter或CT，18目标RAM案例/完整语法通过。初次8个自然TCP未同WAN，在路由器写前停止；106同一662项入口一次重试。新启动观测入口在单WAN完整20秒A/B/A2通过，后续错误tag零新增。新轮实际TCP 25.058/27.131/26.567Mbps；UDP收到/发出 761/793 → 867/904 → 794/820；续租7次，bulk/RT drop 293/0。本轮原始启动错误为零，1包启动例外仅目标RAM案例覆盖，尚未现场触发；RTT p95约238.08/240.69/237.75ms，squeeze全0，UDP仍约4%未返回。异步leaf含38字节overhead约28.12Mbps，不作精确30Mbps限速验收。
- 当前期限：native固定27秒≤原30秒上限，真实分类租约最大6秒，独立owner100秒；每轮只一WAN一TCP一UDP。实际四个stage各checkpoint/SHA/gzip/控制连接外恢复，六端点FW180/客户端210秒关闭。最终4859/17139/config581b5d46…c791d7/source2.97，原完整审核通过，ECM关闭全零，无残留。
- 本轮没有永久NSS、常驻分类器更换、真人CS2、300Mbps验收或上行QoS。先前32Mbps三段66.41%与48Mbps B/A2约72.19% softirq收益保留；此轮只看拥塞和功能，不用不同吞吐计算收益。实际upTag仍0，仅LAN4下行；CAKE完整替代尚未成立。
- 背景观测第一次原始文件被后一次覆盖：156.94Mbps等聚合从实际工具输出恢复，原始帧不再可用；暂停后的0.039Mbps原始证据另存。已向用户说明，未伪造原始SHA或补帧。其它完整运行输入、CT、凭据、checkpoint/模块仍私有，旧98/92/82 runtime保持。

## NSS93–98 · 2026-10-05 19:50 · 高一档CPU收益与拥塞队列

假设：52缺包应能缩小位置，48Mbps有相同吞吐的NSS CPU收益，低于发送负载的40Mbps NSS组可隔离RT。

执行与观测：两个只读固定flow 52↔32诊断；95沿用89/533入口52在initial UDP-down0拒绝；96仅发送改48/60组完整单WAN2；97同发送只将组改40/39/1、7目标native-option布局案例及单WAN3实装完整A/B/A2。详细实测、原失败、checkpoint/守护、来源和配置恢复见[三轮现场](../evidence/nss98-trials.json)、[回程诊断](../evidence/nss98-return-localization.json)。

结论：48的B/A2吞吐47.981/48.004、softirq5.245/18.860，支持72.19%相对下降；A首段77UDP缺包、吞吐47.031，不并入严格相同比较。40组bulk148新增drop、drop_overlimit不增、RT0，B UDP223/223支持两个leaf隔离；短窗异步统计不证明精确恒定40Mbps/ECN/多流公平，其CPU比较不接受。52缺包队列drop全0，主位置更像可观测IFB/CAKE之前，但物理tap缺失保留不确定性。没有真人CS2结论，只有LAN4下行，上行tag0。

恢复：3个stage都checkpoint+独立45秒守护写前核验/完整恢复；5个端点180秒FW自然撤销和基线、unit/端口/client/210秒guard通过。95早期检查2规则尚未到期拒绝与最终自然expiry通过分列。原完整终态source1.64，4859/17139连续、常驻68不变，ECM关闭全零，无残留；源码与原输入冻结，旧runtime字节保持。


## NSS32 — 2026-10-03 14:17 左右，受控低负载

- 假设：自动分类结果可驱动 bulk/RT leaf，三阶段保持同一队列预算与共同观测循环。
- 负载：3 Mbps TCP、20 pps 合成 UDP；不是 CS2/Steam。
- A/B/A2：5.08 / 5.26 / 5.07 秒，加速数 0 / 2 / 0；NSS 阶段续租 2 次。
- softirq：5.91% / 5.99% / 6.46%；busy：20.92% / 23.48% / 23.46%；time_squeeze 均 +0。
- WAN5、完整 mark `0x50000`、NAT 与 tag 正确；bulk/RT leaf 有流量，精确撤销和恢复通过。
- 结论：流程成立，没有证明高负载 CPU 或游戏体验收益。

## NSS33 — 2026-10-03 14:44–15:22，真实负载准备与一次失败的准入

- 修复前软件诊断：14.44 秒，LAN4 405.86 Mbps、33,575 pps、busy 88.85%、softirq 60.23%、time_squeeze +133。包含背景流量和观测开销，不是匹配 A/B。
- 同帧发布微测量：338 flow / 475,855 B → 候选 30 flow / 45,209 B；解析 0.95 → 0.06 秒。只说明发布/读取开销下降。
- 分类发布修复：53 项检查；完整身份/决策/leaf/有效期保持一致。实测独立 180 秒到期回滚通过，然后重新 checkpoint、部署与提交。
- 新版本连续健康观测时下载已停止，约 0.84 Mbps，不能和 405.86 Mbps 窗口相减当收益。
- 15:11，真实 CS2 UDP + Steam TCP 同属 WAN4，完整 mark `0x40000`，入口检查通过。45 秒独立守护已启动。
- WAN4 临时 bridge → private、物理 LAN4 队列树准备成功。认证进程、地址与接口身份保持，未触发/验证续认证。
- 初始准入约剩 6.84 秒，报 `Insufficient fresh-classifier margin for complete ABA`。tag 尚未设置，gate 未加载，ECM 未开启；bulk/RT leaf 都是 0 包。
- 默认 leaf 快照有 311,153,125 B / 200,538 包，只说明默认出口承载流量，不是 RT 成功。
- WAN/队列/服务/模块/状态完整恢复，全部受保护配置核验通过。
- 后续 18 秒只读演练：66 次检查、6 次合格；41 次 pre-learning 余量不足，19 次 tag 设置预留不足；所选连接全程存在。
- 原失败没有逐次拒绝记录，根因未定。候选代码已补诊断，未放宽任何有效期或期限。
- 没有 CS2 jitter/loss/Miss 数据，没有本轮 NSS 收益结论。

## NSS34 — 2026-10-03，已结束；只读

- 开始时复核：长期分类器健康，配置与部署匹配，ECM 关闭且计数为零。
- 当前 PC 虽有 CS2/Steam 进程，真实获准游戏/下载候选均为 0；不启动现场 NSS 试验。
- 15 秒初始循环分解：636 次，完整进程枚举 6 次；guard 检查平均约 1.32 ms、最大 60 ms；最多一次循环读取 603 项。
- 仅年龄条件有 128 次合格。这不是完整准入结果；轻负载不能反推上次高负载故障。
- 本轮尚无路由器配置变更，不加载 gate/qdisc，不启动下载负载。
- 用户要求建立私有 GitHub 仓库，先整理主线证据、代码和接续状态。
- 未改动的实际 Lua adapter + 初始等待代码通过 87 项离线检查，包含 66 个记录时间包络的回放。IO、时钟和序列化使用模拟，连接身份使用 fixture；未重演真实内核或历史连接生命周期。
- 发现：fresh 时 RT 候选消失会报告候选拒绝；同一候选消失而来源变旧后，首先命中时间余量检查；外层最终统一报时间不足。逐次诊断会保留两种内部原因，因此旧的单一外层错误不能定根因。
- 仓库自带独立离线回放入口，已在现有 Lua 5.1 运行时复跑通过；无需 router/SSH、游戏或下载。
- 结束核验发现 producer/PID 变化。服务日志明确记录 15:54:43、16:00:11 两次退出；最新 `last-error` 是 `/sbin/ip -j -4 address show` 的 2 秒 wrapper 返回 143。捕获的是失败触发点，未捕获当时的阻塞栈或外部信号来源。
- 16:03 检查时新 worker/guardian 健康；随后 8 次同样受限的地址查询均约 10 ms、RC 0，未复现故障。不能把“最终恢复”当作分类器全程稳定。
- 没有安装新修复。先解决常驻分类器稳定性，再继续真人准入与高负载 A/B。

## NSS35 — 2026-10-03 16:10 起，分类器地址查询恢复

- 假设：地址查询失败不必强制整个分类器重启，但只有有界查询、确认进程组清理、撤回候选与精确软件恢复后才可原地重试。底层原始阻塞原因未定。
- 开始核验通过；NSS33 worker 健康，ECM 停止且计数全零。未请求真人游戏或下载。
- 变更仅限 worker 地址查询与 worker/guardian 的严格 typed degradation 协作。分类核心、CT 来源、good samples、cooldown、预算、mark/NAT/leaf、NSS 有效期不变。源文件哈希见 STATE 和 source-manifest。
- 136 项检查通过：46 恢复分支、11 本地不安全进程状态、11 目标地址查询、13 核心重新预热与旧地址拒绝、55 发布/准入/精确撤销规划。
- 真实目标 Lua/nixio 的半截 JSON 超时、派生进程组超时约 2.16–2.17 秒完成；所有测试子进程均退出。未知/未清理 runner 状态继续终止。没有向常驻生产服务注入假地址或故障。
- 16:27 首次 checkpoint、独立 staging guard、180 秒事务回滚核验后试装；35 次观测健康，快照与候选的身份/决策/leaf/有效期相等。
- 第一次回滚轮询比 180 秒期限更早结束，返回“尚未核验”；未视为回滚失败、未强制回滚。再次读取于 16:30:36 确认独立到期恢复旧 worker、配置和健康服务，受保护配置复核通过。
- 16:31 第二次创建 checkpoint 和独立守护后重新安装；35 次观测健康、所有受保护配置与自有规则审计通过，随后提交保留。当前部署引用 `work/nss35/deployment-latest.json`，旧轮次引用保持冻结。
- 试装窗口 17.17 秒，LAN4 0.921 Mbps / 138.44 pps，busy 19.13%，softirq 5.31%，time_squeeze +0；保留前窗口 17.14 秒，0.933 Mbps / 138.33 pps，busy 17.10%，softirq 1.29%，time_squeeze +0。
- 以上均为自然轻负载软件转发，包含观测开销，不能计算修复或 NSS 收益。没有真人 jitter/loss/Miss，没有本轮加速 flow 或 NSS leaf 流量。
- 结束核验：ECM IPv4/IPv6 关闭且相关计数全零，生产 qdisc 与认证/PBR/服务配置不变，无实验事务/暂存/状态/gate/qdisc 残留。producer 与保留观测相同。
- 下一步重新绑定 NSS 控制器的当前部署哈希并验证生命周期/准入，再集中真人单 WAN 测试。长期/高负载稳定性与完整新版本 crash/换端口仍未全面验收。

## NSS36 — 2026-10-03 16:50–17:25，当前绑定、真人准入失败与时序定位

- 假设：保持当前分类策略、身份、有效期和原生 gate 不变，完成当前部署绑定与更精确的拒绝处理后，可用真实同 WAN TCP/UDP 开始闭环。
- 开始及结束 producer 相同。NSS35 常驻配置未修改；旧 NSS33 引用与证明保持冻结。
- 299 项分层检查/场景通过：212 准入、21 续租/精确撤销、26 分类生命周期、19 自有软件规则恢复、11 目标 Lua/jsonc RAM A/B/A2 模拟、10 同 WAN 选择约束。108 组新旧准入结果及成功输出一致；66 个历史时间包络结果不变。
- 修改仅在新轮次控制器：身份/类别检查先于时间余量，仅明确时间失败重试，结构/owner/候选错误立即退出；没有延长 TTL 或改 gate。目标语法与完整 tag policy roundtrip 通过，传输上限仍 9000 字节。
- 用户集中开启对局与下载。17:14–17:15 两次应用归属核验后，选中 WAN1 / 完整 mark `0x10000` / 同 NAT 的 Steam TCP 与 CS2 UDP。独立检查点下载校验通过，45 秒 owner 脱离控制连接且先于变更生效。
- WAN1 临时 private 和 LAN4 物理 NSS 队列准备成功；约 5.93 秒初始窗口 44 次拒绝，其中 pre-learning 余量不足 36 次、tag setup reserve 不足 8 次。原始逐次来源序号未记录，不能确定所有时延成因。
- packet tags 尚未设置，gate 未加载，ECM 未开启；bulk/RT leaf 均 0 包；默认 leaf 有 287,841,635 B / 185,866 包。这不是 RT 成功或 A/B 完成。
- 独立 owner 完成恢复：WAN/队列/模块/状态节点恢复，全部受保护配置和 ECM 全零复核通过；认证进程与 DHCP 身份保持，未触发续认证。
- 后续 18.03 秒只读窗口 58 次检查，原 TCP 全程存在、原游戏 0 次存在；是另一个时间窗口，不回推失败时游戏退出。发布延迟 0.77–1.21 秒，完整读取最高 0.26 秒；部分时刻来源/发布已超过有效期。
- 该软件诊断窗口 LAN4 407.82 Mbps / 33,737 pps，busy 88.11%，softirq 58.95%，time_squeeze +20。包含观测成本，游戏候选已退出；没有同负载 NSS 阶段，无收益结论。
- 单次只读采集/RAM 回放 455 行连接：CT 查询 0.28 秒、标准化 0.55 秒、核心冷回放 0.28 秒；现有候选解析/编码 0.01/0.05 秒。未给生产 worker 注入计时器，不能当作生产全路径追踪。
- 结束首次审计因来源年龄断言退出，随后复查通过；分类器实例未改变。无实验事务/暂存/状态/模块残留。不能以最终通过抹去中间数据过旧。
- 结论：精确诊断生效，本次失败确实止于时间门槛；当前发布/读取时延与小于 1 秒的初始窗口不匹配。NSS 可加速性沿用历史证据，本轮未验证。下一步针对采集/分类开销差分验证，保持所有期限，不再要求用户维持游戏。

## NSS37 — 2026-10-03 17:47–18:16，等价属性解析与安全保留

- 假设：减少 CT 文本重复属性搜索可以降低标准化开销，同时保持所有输出、拒绝规则与新鲜度边界。优化是否足以解决真人高负载准入，需要另测。
- 只读目标 RAM 分解：207 行文本、3 次回放，属性提取 CPU 0.054441 秒，总 CPU 0.100881 秒。未给生产 worker 注入计时器。
- 只修改 `conntrack-source.lua / attrs()`：字面量定位键，继续检查原空白边界、非空值、重复项。worker、guardian、核心和 backend 不变；配置只变来源文件哈希与安装事务号。
- 9,087 项解析检查通过（2,688 属性案例、6,381 完整标准化差分、18 独立预期）；另有 26 项实际核心/leaf 生命周期模拟通过。未给生产服务注入 crash。
- 目标 Lua 16 对交替新旧测量，全部输出相等。204 行真实采集文本平均 CPU 27.043 → 15.470 ms（−42.8%）；512 行合成文本 64.393 → 38.408 ms（−40.4%）。背景 0.639 Mbps；没有发测试流量，不能推算整机或 NSS 收益。
- 两次安装均先 checkpoint 下载/哈希/压缩校验，再核验脱离控制连接的 480 秒暂存守护和 180 秒事务守护。
- 首次试装 35 次观测健康，完整/精简身份、分类、leaf、有效期相等；18:03:42 确认独立到期恢复旧解析器、配置、worker/guardian 和健康服务，控制端未发提前回滚。
- 新 checkpoint 后重新安装，35 次观测健康，18:07:55 提交保留。新常驻引用 `work/nss37/deployment-latest.json`，旧别名与证明保持不变。
- 安装前 / 试装 / 保留前窗口分别 17.15 / 17.13 / 17.12 秒，LAN4 2.788 / 0.793 / 1.207 Mbps，316.50 / 134.97 / 161.39 pps，busy 14.48% / 14.43% / 14.06%，softirq 1.55% / 4.96% / 2.28%，time_squeeze 均 +0。不同自然轻负载，包含观测成本，不是匹配 A/B。
- 各窗口 query age <1 秒均为 6/35；保留窗口发布延迟 0.25–0.29 秒。不能据此断言真人高负载准入已修复。
- 主线控制器已绑定 NSS37 新配置与 66 项清单，目标编译/tag policy 往返及 10 项同 WAN 选择检查通过。NSS36 未改变的消费者/backend 证明沿用，不重复计为本轮新检查。
- 18:11:17 只读真实应用检查：CS2 RT 1、Steam bulk 0、同 WAN 连接对 0。本轮没有 fast path 尝试，ECM 始终关闭；无新的 NSS leaf/加速出口/mark/NAT/WAN 或 jitter/loss/Miss 验收。
- 18:15:57 最终核验通过，producer 与保留前相同，last-error 属于首次试装到期。受保护服务/认证/PBR/生产队列无变化，ECM 全零，无实验事务/暂存/状态/模块残留。
- 结论：解析开销假设得到支持；高负载发布时间、整体软中断收益和真人闭环未证明。下一步先只读时序验收，继续单 WAN 主线，不扩 QoS 支线；未提交上游 Issue/PR。

## NSS38 — 2026-10-03 22:05 起，真人 WAN2 失败、准入候选与一次自然重启

- 常驻引用仍是 NSS37，本轮未更改常驻源码/配置。起始与真实尝试后 worker/guardian 健康、ECM 全零。
- 用户开启下载后，18.14 秒软件发布窗口 LAN4 353.25 Mbps / 29,241 pps，busy 77.25%、softirq 56.85%、time_squeeze +1；81 次观测，观察程序 CPU 1.705 秒。发布延迟 0.56–0.81 秒，8 次来源年龄 <1 秒。尚不是同负载转发 A/B。
- 随后识别真实 CS2 UDP 与 Steam TCP；22:10 完整只读准入 44 次、6 次通过，两条所选连接 44 次均存在，发布延迟 0.47–0.66 秒。
- 22:11 再次核验应用归属，选择 WAN2、完整 mark 0x20000、同 NAT。checkpoint 下载/哈希/压缩核验及 45 秒独立恢复先于变更；单 WAN private 和物理 LAN4 NSS 队列准备成功。
- 初始 5.61 秒内 32 次时间拒绝（23 次 pre-learning、9 次 tag reserve）；packet tag、gate、ECM 尚未开放，bulk/RT leaf 0 包。默认 leaf 229,813,353 B / 151,640 包不代表 RT 成功。未记录各次来源序号，所有原因未定。
- 独立恢复完成，WAN/队列/模块/状态节点与 14 项受保护配置通过；认证/DHCP 身份保持，未测续认证。保存 70 份哈希匹配的当次源码/证明副本。
- 后续独立 12 秒诊断 402.75 Mbps / 33,315 pps，busy 89.41%、softirq 59.67%、time_squeeze +17；观察程序自身 CPU 8.434 秒。105 次所选类别均不再准入，未重新核验应用归属，不回推原试验流程。
- 该诊断完整进程枚举 3 次、局部 102 次，最大 phase/adapter 用时 0.24/0.19 秒。之前一次扫描因 core guard 数量变化退出，未证明底层原因。发布监测的子进程阶段计数因缺少 CONFIG_PROC_CHILDREN 不可用，不能将 0 写成没有维护活动。
- 未安装准入候选只去掉 ready/observe 同帧重复完整检查；1,470 决策差分、5 调用次数、212 准入、21 续租/撤销检查通过。首次更宽修改改变撤销错误形态，被测试否决且未用于现场。
- 目标原生 Lua/jsonc 内存微测量 12 对、120 次 ready 成功。2 / 32 / 64 合成候选，单次 CPU 2.141→1.773 / 16.090→11.845 / 32.974→24.048 ms，降幅 17.2% / 26.4% / 27.1%。固定时钟、模拟文件系统，背景 6.19 Mbps；仅证明检查开销，不是 NSS 收益。
- 带逐次时序诊断的候选再通过 1,470 决策对照、230 准入/诊断案例、目标 Lua 编译；仍未安装，尚未完成全套当前控制器绑定。重复场景不累加成新的独立覆盖量。
- 22:27:08 自然发生 `/sbin/tc -j qdisc show dev rpwan1` 读取返回 143 / Terminated，apply 子进程失败，旧 worker 退出。日志确认精确恢复，procd 重启新 worker、guardian 未变。22:33 新实例健康，现网审核与清理通过；之后同一查询 8 次约 10 ms、RC 0。底层阻塞/信号来源未定，未注入生产故障。
- 22:44:46 最后复核仍是同一新实例，健康、现网配置与清理通过，ECM 全零；这不是连续稳定性追踪。
- 结论：本轮真人闭环仍失败；准入检查可等价减负，但高负载及时性没有验收。分类器长期稳定性又出现反证，下一步先诊断读取失败与安全恢复、完成候选资格，再集中单 WAN 复测。无加速后的 mark/NAT/WAN、CS2 jitter/loss/Miss 或 NSS CPU 收益结论；未提交上游。


## NSS39 — 2026-10-03 22:50 起，监督修复保留与当前控制器资格

- 当前 NSS37/现网先只读核验。现有 BusyBox 1.38.0 + group-runner 隔离复现：内层超时 143、外层截止 124；此前自然失败缺少外层状态，完整根因不定。
- 官方 release 校验通过、只读源码显示独立监视会话。4/20 次真实只读查询各 4 对，完整 wrapper 1037.5→215 / 1150→395 ms；查询本身 30→42.5 / 147.5→230 ms。背景 0.865 Mbps，墙钟等待降低，不是 CPU 或 NSS 收益。
- tc 改为现有进程组中的受监督直接子进程；原有三个参数形状、2/6 秒截止保持。16 本地模型、13 参数、8 原生隔离案例通过；未知清理仍终止，失败没有变成功，未生产注入部分 batch 写故障。
- 4 次安装均 checkpoint/独立守护先行。前 3 次均实际独立到期恢复；两次保留窗口因本地准备/诊断耗时不足。第三次立即采样读到 3 个旧实例发布，正确拒绝保留；增加当前配置/进程/守护/新序列就绪确认。第 4 次 35/35 健康并保留，所有截止未延长。
- 最终软件自然负载窗口 17.14 秒：2.045 Mbps / 214.41 pps，busy 19.02%、softirq 5.09%、time_squeeze +0。其它独立窗口见证据，不作不匹配负载的差分收益结论。
- NSS38 相同精简/诊断源码与当前 NSS39 绑定，68 项 manifest；新执行 230 准入、21 续租/撤销、26 核心生命周期、19 自有规则、10 affinity 检查。历史 1470+5 差分证明沿用。
- 完整 RAM 测试包被原传输上限拒绝，未放宽上限；改用已 checkpoint、独立清理的内存暂存目录。原生完整 adapter 17 项、完整 A/B 控制器 11 项通过，均为模拟 IO/时钟/内核确认；暂存移除核验通过。11 个单元编译、tag 策略往返通过，启动参数 8875/9000 字节。
- 23:25 没有 CS2 进程与 Steam 下载候选，未做真实 fast path；没有真实 leaf、加速后 mark/NAT/WAN 或游戏指标。最终核验同一保留实例健康、ECM 全零、保护配置不变，无实验残留。
- 本地监督组合 Issue 候选已整理，无上游提交。自然高负载稳定性和真人 NSS 收益仍需验证；下一步集中一次真人单 WAN 闭环，不扩支线。


## NSS40 — 2026-10-03 23:46 至 10-04 00:00，真实高负载只读准入、写前拒绝

- 当前 NSS39/68 项资格、同一 worker 与守护、保护配置、ECM 关闭全零先通过只读核验。起初没有游戏；用户同意集中短测后检测到真实对局与下载。
- 本地入口重定位曾误读新目录下的 wan-scope 源码，执行到只读前即拒绝；改回已绑定 NSS39 源码。完整只读诊断包被既有 9000 字节传输上限拒绝，仅去掉未调用的方法后命令 8719 字节，保留全部 ready/pair/inspect/phase scan 判断。
- 23:52 真实同 WAN5 CS2 RT UDP＋Steam bulk TCP，完整 mark 0x50000、zone 0、同 NAT，应用 socket/CT 实例和元组经 reader/adapter 校验。9.27 秒 LAN4 322.80 Mbps / 26,712 pps，busy 85.15%、softirq 51.33%、time_squeeze +0；密集观察自身 CPU 6.247 秒，不能当无干扰基线。
- 94 次完整只读入口探测，4 次通过（2 个新序列）；59 次 pre-learning、31 次 tag reserve 拒绝。最小来源年龄 0.81 秒，最大 adapter/phase 0.20/0.28 秒。初始 <1 秒、预学习 <2 秒未变。
- 23:52:59 实际 A/B 入口在保护审核 operational-audit.lua:32 的联合年龄断言失败。尚未 checkpoint/独立事务、改 WAN、创建 qdisc/tag 或加载 gate/开放 ECM；没有 leaf 或 B 阶段，回滚不适用。未重试游戏负载，已告知用户可以结束游戏/下载。
- 原失败缺少具体快照年龄/阶段时间，selected pair 尚未冻结，原始应用 latest 后来已刷新；此前 rehearsal 选中元组不冒充失败瞬间。失败后按未变哈希保存 72 份源码/证明。
- 只读源码确认 compact 发布 → 同步持锁软件维护/审核 → full snapshot 发布；不把该顺序当具体失败根因。后续轻载带计时审核 0.29 秒通过、来源年龄 2.67 秒。
- 新增本地完整审核诊断入口，保留所有断言与固定截止，保存阶段时间及拒绝时年龄；目标只读集成通过。新增每次应用快照封存入口验证通过。均未改常驻 worker，未接回被冻结的失败控制器。
- 最终轻载 35/35 次健康，同帧完整/精简身份、分类、leaf、有效期一致；同一 NSS39 实例，无新自然重启记录。保护配置、规则所有权、清理通过，ECM 全零；旧 last-error 为先前试装到期。
- 支持当前 adapter 在真实高负载下存在初始准入窗口；尚不支持入口可靠性、真实 bulk/RT NSS leaf 命中、NSS CPU 收益或游戏 jitter/loss/Miss 改善。无上游提交，不扩第二 WAN。


## NSS41 — 2026-10-04 00:18 起，取证入口接入、真人 WAN1 功能与验收缺陷

- 常驻 NSS39 未改，同一 worker/guardian，原期限/策略保持。新增诊断、按次应用封存、selected pair 与源码在第一次审核前冻结。
- 新锁外调度等待严格新 full sequence、source age <2 秒，内部 5 秒/外层 6 秒；原持锁 <6/<9 秒和 native 1/2/45 秒期限不变。最初误传 12 秒被 runner 参数校验 RC2 拒绝，Lua 未运行；原版本/拒绝保留。15 个 planner 边界与 3 个实际入口顺序模拟案例通过，3 次最终轻载原审核通过。
- 00:28 有限普通 TCP 下载 8 连接 / 512 MiB 总上限 / 单请求 25 秒，实际 384920896 B，1 完成、7 期限退出，子进程全结束。27.21 秒 LAN4 125.21 Mbps/10388 pps，busy 46.55%、softirq 28.35%、squeeze +136，最高约 3 秒 234.58 Mbps。104 帧 full age 最高 4.27 秒，3 次原完整审核 0.29–0.43 秒通过。观察 CPU 1.177 秒；低于旧真人 323 Mbps，没有复现/修复根因结论。
- 用户集中启动对局和下载。00:57 当次应用归属与同 WAN1 pair 匹配；先封存完整身份、应用 4 文件和 83 项来源，再完整审核通过、下载校验 checkpoint、确认独立 45 秒 owner，后准备一个 private WAN/物理 LAN4 NSS 队列。
- 原生 software A / NSS B / software A2 各 11 帧、5.07/5.17/5.09 秒，ECM accelerated_count 0/2/0，B 完成一次新序列续租。相同队列预算/观察循环，随后明确提前撤销并全部恢复。
- 原主机终态 false：旧报告 parser 写死 WAN5导致实际 WAN1 被误拒绝；恢复阶段新 full source age <2 秒调度也到期。原结果不覆盖。单独通用 WAN parser 对同一份真实硬件状态重验，两条 flow 的 mode2/NAT/fullmark/privateWAN/物理WAN/LAN层级/down tag通过，6 个错误副本拒绝。旧 parser 不在83项绑定，新增校验源另行冻结；这不是重新做硬件实验。
- B＋撤销 5.83 秒 leaf 增量 bulk 6171 包/9325760 B、RT 517 包/477890 B；RT leaf dropped +0，不能当客户端 loss/Miss。下行 tag 分别2399469568/2399535104，完整 mark0x10000、zone0、同NAT、自然WAN1。
- 整机A/B/A2 LAN4 347.72/379.98/391.11 Mbps、pps28777/31453/32385，busy79.51/82.89/85.31%，softirq59.17/60.64/61.87%，squeeze+0/+0/+2。WAN1负载也变化，只有20Mbps子组/两条流进入NSS，没有同offered-load或CPU收益结论。
- 用户“没注意到，无法比较”，无客户端 jitter/loss/Miss。首次体验询问时窗换算偏约10秒，已更正，不能做体验归因。
- 恢复专用完整原<6/<9审核通过，基线配置/boot/地址/路由/服务/规则/十队列/ECM检查通过，全部暂存/模块/状态/事务清理，认证DHCP身份保持，未测续认证。独立到期已布置但本轮提前恢复，不冒充一次新到期回滚。
- 支持真人单WAN功能路径；不支持固定高负载性能/游戏验收或扩第二WAN。下一轮只纠正验收依赖与恢复调度、稳定同WAN负载/受控份额。没有上游提交，原本冻结证明均保留。

## NSS42 — 2026-10-04 01:20–02:14 起，验收入口修复与持续只读核验

- 假设：NSS41 真人功能路径已成立；本地后处理与恢复用途错误应通过离线重验修正，不能再次扩大现网改动碰运气。
- 新目录复制候选，通用 WAN 后处理接入真实入口；新 flow 学习前与关闭后的恢复审核分开，所有原期限、gate、QoS 预算与原生 payload 保持。
- 90 项本地检查：43 WAN/方向/mark/NAT/tag（含一份冻结真实 WAN1 状态）、23 调度/诊断、8 实际控制器隔离顺序回放、7 静态依赖解析、9 绑定变化拒绝。明确替换外部 IO，不计为现场加速试验。
- 输入清单从 v1 的 99 项到 v2 的 102 项，分别冻结；当前静态图 40 文件/69 关系，历史动态 runtime 68 项另行绑定。外部既有连接源码只记录哈希，连接封装/凭据/私有清单不导出；不宣称覆盖所有 OS/运行时或动态依赖。
- 初次绑定 fixture 使用了 v1 的旧 hash 搭配当前复制源码，正确被拒绝；修正隔离 fixture 的基线 hash 后，9 项通过。生产入口没有被放宽。
- 新调度失败记录观察行与读取阶段。目标 Lua/jsonc 4 项 RAM 序列化检查通过，未向生产分类器注入错误。v1/v2 的 prewrite/recovery 原完整只读审核均通过，学习前和恢复场景分离，均无准入权。
- 02:01:48–02:11:48，600 秒 / 21 次 / 30 秒间隔；21/21 成功、同一 worker/guardian、样本健康、序号增加、来源年龄 2.35–2.56 秒。自然软件负载 1.981 Mbps / 186.93 pps，busy 14.18%、softirq 3.10%、time_squeeze +0，包含观察开销；不能证明高负载或所有时间稳定。
- 本轮未检测到真人 CS2/Steam 下载配对，没有要求用户挂机；无生产配置写入、checkpoint、回滚或新 NSS 实验。结束原完整保护审核、基线与清理检查通过，ECM 关闭且全零，常驻仍 NSS39，旧错误属于此前安装。
- NSS41 重新分析：B＋撤销计数窗 bulk/RT 6,688 包 / 9,803,650 B，占总 leaf 4.37% 包 / 4.11% 字节；包含撤销，不是精确 fast path 份额。20 Mbps 子组和上升的整机/WAN 负载不足以证明 global CPU 收益。
- 下一步稳定同 WAN 与总负载，确认受控份额后集中跑修正后的真人入口；若改变预算/流数须另建候选并资格核验。CPU、游戏 jitter/loss/Miss、完整高负载生命周期仍未通过，第二 WAN 等支线等待。无上游提交。
- 仓库独立重放 42 个合成校验＋23 个调度案例通过，不读取凭据/冻结真实状态，不连接路由器；65 项为已有案例的再次执行，不增加独立案例计数。报告源文件和链接核验通过；浏览器本地文件 URL 策略拒绝，未绕过，页面渲染未核验。


## NSS43 — 2026-10-04 10:01–10:19，Steam 单连接负载与受控份额

- 目标：先解释单 WAN/单 TCP 接管份额，不扩大 NSS42 20 Mbps 预算、流数或 TTL，不要求真人挂机。起止完整原保护审核通过；常驻 NSS39 同一健康实例。
- 用户仅开启 Steam。第一轮 13 次因本地模板编辑导致 JavaScript 语法错误，在连接路由器前失败；原错误保留。修复并补语法检查/失败即止，重新采集 48.02 秒、13/13 成功的实际窗口。
- 每帧按新鲜 PC socket 精确匹配 Steam TCP，再读取现有分类器 CT reply bytes/packets；每帧 bulk 13–16，全窗 23 个 CT 实例，WAN5 无全窗单流。没有 CS2 候选，没有人工生成测试流量，ECM 始终关闭且零计数。
- LAN4 277.73 Mbps / 22,985 pps，4 秒窗 262.32–287.97 Mbps，变异系数 2.36%；busy 71.17%、softirq 49.24%、time_squeeze +49、softnet dropped +0。观察开销包含在内；本轮不是 NSS A/B，也没有全窗 300 Mbps。
- WAN1–5 RX 35.46/62.26/46.58/87.71/51.53 Mbps；最高全窗 CT reply 单流 21.80/17.49/22.99/16.40/未取得 Mbps。reply 窗用 uptime−sourceAge 估计，与物理接口窗略不同；原始 socket/CT 身份保留私有，仅导出匿名实例和聚合。
- 固定软件路径需求的离线模型：20→30 Mbps，WAN1 全机参考份额 +0.65 个百分点，WAN3 +1.08，WAN2/4 无增加；40/60 无额外增加。不能预测移除软件路径后 TCP 需求/CPU/延迟，因此不提高预算，也不增加 flow slot。
- 20 项离线检查覆盖计数/时钟、guest CPU 不重复计入、实例/NAT/mark/zone、缺失流、脱敏及可比性；13 份只读源码冻结。只读工具复核既有 102 项入口，它不是新的生产资格。
- 分开查询 CAKE JSON/文本时 autorate 数值不同，相邻 JSON/文本/JSON 在 5/5 WAN 单位匹配，采样后约 70–90 Mbps。没有更改 CAKE、autorate 或 QoS。
- 新增 10% 相对跨度的观察条件，历史 NSS41 数据不满足；条件本身不能证明 offered load 相同或授权 NSS。历史功能证明、原控制器终态失败和独立恢复证据不改写。
- 10:19 结束审核与清理通过，常驻分类器自主管理 12 个 selector，受保护配置保持，ECM 全零，无事务/暂存/状态/实验模块。本轮没有生产写入、checkpoint 或回滚试验。没有 CS2 jitter/loss/Miss、NSS CPU 收益或第二 WAN 资格；无上游提交。
- 下一步：一次集中真实 CS2＋Steam，仍单 WAN、一 TCP＋一 UDP、20 Mbps，先校验持久同流、0→2→0、两 leaf、mark/NAT/affinity 和独立恢复，再比较游戏指标与可解释的流量/softirq/time_squeeze。无需用户继续挂机。

## NSS44 — 2026-10-04 10:28–11:07，真人写前拒绝、发布链路与自然重启

- 假设：直接使用冻结 NSS42 102 项入口完成这次集中真人窗口；不改变 20 Mbps、一 TCP＋一 UDP、学习/调度/45 秒 owner 期限。开场原完整审核因来源年龄 7.61 秒超过 6 秒拒绝，失败保留。
- 用户回复已进服/下载保持，现场按新鲜应用归属找到 1 个 CS2 RT 和 23 个 Steam bulk 候选。选中 WAN1、完整 mark 均 0x10000、zone 0、同 NAT；这不是原生加速出口验证。
- 原完整入口实际运行，102 份输入源码/证明冻结，原终态 false 保持。写前等待 5.06 秒/39 帧，序号 13555/13556，完整发布延迟 2.91/3.01 秒、来源年龄 4.19–8.19 秒，全健康但均不满足 <2 秒门槛。拒绝发生在 checkpoint/暂存前，无任何 WAN、qdisc、tag、gate、ECM 或生产配置变更，也未启动独立实验 owner。
- 没有 A/B/A2、NSS leaf 增量、原生 fast path affinity 或 CS2 jitter/loss/Miss；本轮不能给新的 CPU、吞吐或游戏收益结论。随即通知用户可结束这次游戏/下载，不要求长期挂机。
- 10:41:17–10:41:23 常驻旧 worker 自然失败：stale-before-write，apply rawStatus 256、3.79 秒；首次精确 recovery rawStatus 31744、6.18 秒、exactRecovery=false。没有故障注入/手动重启/配置变更，也没有证明只读测量是该退出原因。procd 启动新 worker，guardian 实例保持；首次恢复失败不能被最后通过掩盖。
- 源码只读核对：classification 在软件 apply 前发布、完整 snapshot 在 apply/可能审核后发布；NSS 消费者使用前者，NSS42 等待后者。后者约 3 秒发布时延与 <2 秒来源门槛不兼容，是已证明的拒绝机制；apply/recovery 问题仍需独立定位。
- 后续自然轻载只读 27.15 秒/105 帧，观察程序 CPU 0.888 秒；LAN4 0.237 Mbps/37.72 pps、busy 16.53%、softirq 2.23%、time_squeeze +0，compact/full 延迟 0.32–0.35 / 0.58–1.25 秒。未重新确认真人连接对、没有合成负载，不能与之前高负载组成转发 A/B。
- 新只读等待候选使用现有 before-software-baseline classification，随后原完整持锁/native 审核不变；全部期限保持。30 项离线案例和静态等价检查通过；目标只读 hint age 0.76 秒、原完整审核 age 4.28 秒通过，ECM 全零、无加速许可。候选未安装、未绑定生产入口、不解决 apply/recovery 超时，16 份源码冻结只用于只读/未安装候选取证。
- 批量 payload 校验候选每次仍核对全部 12 文件，不缓存；3 对原生只读交替测量 43.33→10 ms，节省约 33.33 ms，子进程 CPU 未计入，背景 0.037 Mbps。该候选未安装，不足以解决约 3 秒发布延迟，不作为主线根本修复。
- 11:01:58 最终新 worker/guardian 健康；原完整保护审核、精确 owned 规则、配置与清理通过，ECM 关闭/零计数，无事务/暂存/实验状态/模块。现网仍 NSS39；高负载连续生命周期仍未通过，last-error 对应本轮失败。
- 下一步在新轮次离线复现并资格核验分类器 apply/recovery、正确发布等待来源和新入口绑定，再集中一次真人窗；不提高预算/流数/TTL，不扩第二 WAN。原始应用/CT/日志/配置和二进制留私有工作区。发布/恢复问题单独列为本地 Issue 候选，未提交上游。
- 报告源文件和链接检查通过；保留既有浏览器本地文件策略拒绝，没有绕过，页面渲染未核验。

## NSS45 — 2026-10-04 11:23–12:42，恢复修复、子进程边界与两次独立到期试装

- 开场读取当前 NSS39 和原保护审核通过；日志显示此前 11:07:30/11:08:02/11:08:10 三次自然 `Source rows exceed bound` 退出。没有本轮主动 crash/restart/生产溢出注入，原自然错误保留。
- 恢复枚举候选只复用初始已核验状态一次，写前/写后重新检查、首次写后不缓存。24 个算法案例在原/新源码各执行一次通过，未知写入者保持。三对目标只读空日志恢复测量 60→40 调用、0.810→0.553 秒；写回调拒绝、无真实 selector 恢复，子进程 CPU 未计入，不能证明高负载 6.18 秒恢复或全局 CPU 收益。
- 行数候选保留 2048/524288 上限，不发布部分观察，只有实际 query 回收证明可报告已知溢出并精确恢复。48 本地与同例目标 RAM、3 原生语法检查通过；7 个真实 native query 子进程案例使用合成参数/输出，验证正常/2049 新旧边界/字节溢出/未知错误的实际回收，未运行真实 conntrack 命令或生产故障注入。
- 12:18 开始 backend-only 试装，12:29 开始 row-only 试装，中间恢复 NSS39。各有新 checkpoint 下载哈希/压缩核验，生产改动前确认独立事务守护进程身份、父进程和 180 秒截止时间；NSS/gate/tag/qdisc/auth/PBR 没有实验变更。
- 各 35 帧约 17 秒观测健康且同一 producer，精简/完整身份、decision、leaf 与期限一致，原完整规则/配置保护审核通过。自然 LAN4 分别 0.050/0.881 Mbps、19.71/131.72 pps，busy 14.38/17.87%、softirq 1.40/0.98%，time_squeeze 和 softnet dropped 均 +0；包含观察开销，负载不同，不是转发 A/B。背景 RT 命中没有 CS2 socket 归属。
- 两次均未 commit/延长期限/主动回滚。接近原安装到期时 worker 与 procd 重试拒绝继续，随后独立回滚恢复四份源码、配置、指针及健康实例，12:21:42/12:32:54 证明通过；随后原完整保护审核通过。两套暂存自然到 480 秒独立清理，没有控制器删除。不能把 35 帧健康写成全 180 秒连续稳定。
- 软件来源过期组合候选未安装，6 秒软件来源/6 秒 mutation/9 秒发布界限不变。34 个局部案例及 8 个实际 backend/ownership 日志交叉场景在本地/目标 RAM 通过，证明模拟的发布撤回、已知规则精确恢复、未知 writer 保留、producer 绑定拒绝与新观察接续；应用子进程、队列 IO、发布部分被替换，完整真实服务资格仍未通过。
- 独立本地案例 114，目标同例不重复计为新案例；7 个真实 query 子进程和 5 个语法检查另记。4 次恢复夹具修正、1 次日志夹具别名修正、2 次传输尺寸拒绝与 1 次本地路径正则拒绝均保留。没有因准备失败进行生产写入或放宽尺寸/安全门槛。
- 最终 12:42:44–12:42:49：常驻仍 NSS39，健康实例与第二次回滚后的实例相同；原完整规则/配置审核通过，ECM 关闭/全零，无事务/暂存/状态/实验模块，没有真实 CS2/Steam 下载配对。last-error 属于 row 试装到期，与当前 worker 不同，开场自然溢出日志不改写。
- 53 份源码冻结，白名单同步脱敏证据；不是 NSS 生产入口资格。NSS41 功能证明和 NSS44 原失败保持。本轮没有新 fast path、leaf、A/B/A2、CPU收益、CS2 jitter/loss/Miss 或第二 WAN 资格。
- 下一项是完整 apply 子进程、既有期限内的服务恢复资格，再按单一变量组合修复，绑定 classification 提示后原完整审核的新入口。准备期间不要求用户开游戏或反复下载。恢复问题进入本地 backlog，未提交上游；报告源检查通过，浏览器渲染未核验，没有绕过既有策略拒绝。

## 2026-10-04 NSS46：可靠性修复实装、真实故障恢复与新入口

- 当前常驻切换为 `work/nss46/deployment-latest.json`，三项修复按 backend→软件来源过期→行数溢出逐变量安装并保留。每次 checkpoint 下载、哈希/压缩验证、写前独立 180 秒守护核验、目标语法和原完整保护审核通过；无 qdisc 根重建、CT 全清、认证/PBR/服务架构变更。
- 实际 watch 对真实接纳的连接观察只延迟一次，未修改元数据。真实 apply 绑定父 producer/PID/start/原锁，请求/结果序列化保留；来源年龄 6.27 秒拒绝 batch，两个发布撤回，intent 精确清零；实际 recover 0.80 秒，同 worker 继续运行。
- 在持事务锁、确认没有 worker 子进程时精确 kill 一个空闲 worker，procd 新实例在 7.56 秒恢复新鲜发布与健康 guardian。两个故障试装均自然到期恢复四份源码、配置、generation 指针及健康实例；480 秒暂存自然清理。
- expiry 保留初始三帧旧 producer/新 guardian 预热如实保持，新实例完整审核后才提交。最终 row 版本 35 帧全健康；随后自然轻载 60 帧、29.61 秒，同实例健康，来源最大年龄 3.17 秒，LAN4 0.047 Mbps。未当作 CPU/高负载收益。
- 新入口 `work/nss46/real-session.mjs` 使用 classification 提示后原完整审核，112 项来源绑定、99 个入口本地案例、现场来源年龄 0.30 秒及完整审核通过。NSS Lua 数据面与已验证 NSS39 字节一致；原 NSS42 102 项入口不动。20 Mbps、一条 TCP＋一条 UDP、45 秒 owner、原 1/2/6/9 秒门槛不变。
- 组合回归 48 个 row＋34 个 expiry 断言通过；相同七个历史实际 query 子进程证明按精确 helper/normalizer 字节复用，不重复计为本轮 native 新案例。入口夹具旧路径/seed 绑定、故障摘要 JSON 重复引用和保留脚本本地重名错误已修正，原输出保留；未因此开启 NSS。
- 最终 13:49:55–13:49:56：worker/guardian 健康、保护审核通过、ECM 关闭全零、无事务/暂存/状态/实验模块；last-error 是受控 crash 试装临近到期，属于旧 worker。当前没有 CS2＋Steam 配对。新入口现场检查没有授予 NSS。
- 84 份本轮源码冻结，按明确白名单同步。当前镜像与历史源码检查分别绑定；原 NSS45 current-runtime 精确保存在 nss45-runtime，历史证据不因常驻升级改写。只请求一次真实窗口，未要求重复挂机。剩余为真人 software→NSS→software 及高负载恢复/游戏指标，未扩第二 WAN/共享预算/Wi-Fi/autorate，未上游提交。

## 2026-10-04 NSS47–49：地址缓存保留、无包取证修正、完整单 WAN 控制器成功

- 用户授权由助手自行恢复下载并进入游戏；恢复现有 Steam 下载、进入在线死亡竞赛观战。真实应用连接与真人操作分开记录，没有让用户再准备或抄指标，没有购买/卸载重装游戏。
- 原 NSS46 入口在真实应用对下实际执行，初始39次观察的精简发布延迟1.03–1.26秒，未满足<1秒。独立45秒owner与暂存队列建立，但未打开ECM；拒绝、精确恢复和原完整审核保持，112项输入副本冻结。不能把这次写后拒绝说成完全无生产暂存。
- 只读/目标RAM定位解析开销，扫描候选4.049→3.972秒、约1.9%，未安装。纯IPv4缓存候选4550差分样本/744接受一致；目标527行/200接受、每版本80遍冷缓存、3完整快照一致，解析CPU4.740→3.489秒、26.4%。9,612断言为1,200地址/两遍及错误/容量检查，不当独立案例数。缓存各1024、每观察重置，CT/mark/NAT/计数不缓存，原策略/行字节界限/来源期限不变。
- NSS47第一次缓存试装独立180秒自然恢复通过，前core及其它四份源码/config/健康实例恢复。没有取得该试装安装窗完整负载时序，不伪造。第二安装另建checkpoint/下载哈希gzip/独立180秒守护/原完整审核，通过后提交；暂存守护退出核验通过。现网config478818d…7517a900，常驻引用work/nss47/deployment-latest.json。之前350/173/83/282 Mbps观察负载不同，不作缓存整机CPU A/B。
- NSS48实际cache绑定入口119项输入，初始age0.72秒通过。初始0.3秒getter TCP各方向全零、UDP2/5包标签正确，原错误Tag getter mismatch并非已观察到错误映射。未打开ECM，精确回滚/完整审核通过，实际原119项清单冻结。
- NSS49只改变初始无包等待至多1.2秒，且受原epoch-0.5/owner-32余量约束；错误tag立即失败、四向正计数才继续，后续严格getter保持。source1/2/6/9秒、epoch5秒、owner45秒、20 Mbps/一TCP＋一UDP不变。13项目标RAM模拟覆盖稳定/延迟TCP/持续无包/改类/NAT漂移/错误tag/WAN/加速退出，IO/时钟/ACK替代，非硬件证明。新入口121项绑定、99项本地案例、目标语法/前后审核通过。其余NSSLua与NSS48一致、kernel/FW/driver未升级；继承unchanged元数据不描述本helper变化。
- 14:52–14:53实际WAN2同一CS2 UDP＋Steam TCP完整software→NSS→software成功，三段各5.03秒/11帧，ECM0→2→0，一次新classification序列续租。原生TCP client-first/UDP server-first，完整mark0x20000，downTag分别0x8f050000/0x8f060000、upTag0，NAT/WAN affinity2/LAN4/br-lan层级正确。getter0.16秒/1probe通过，没有用到扩等待余量；不能声称这项等待变化导致本次成功。
- 实际LAN4 Mbps167.90/193.94/170.86，WAN2 Mbps66.31/83.86/66.02，LAN4 pps13,929/16,088/14,174；busy62.35/60.69/60.99%，softirq41.14/41.71/44.81%，time_squeeze+0/+1/+4，softnet drop全零。吞吐跨度14.66%/24.75%超预设10%，未证明offered load一致，也非全窗300Mbps+；不作CPU因果收益。
- 建立至撤销5.43秒leaf窗：bulk11,531,555B/7635pk/13drop，RT644,562B/713pk/0drop，fallback130,118,774B/84,625pk。包含边界，非精确B速率；受控约8.56%字节，RT0drop不是客户端端到端0loss。
- 第一轮38张实际Sky界面截图，125ms往返时钟锚点校准后A/B完整有效帧0，A2有3帧，不能将随后绿色HUD填回B。第二轮15:05已无bulk（Steam15:03完成86.7GB），入口写前返回等待，routerWrites=false/nssPermit=false；有前台遮挡的截图不用于指标。游戏已退出测试服务器，未继续挂机；没有真人体感/客户端B段jitter/loss/Miss结论。
- 所有写前checkpoint下载/SHA/gzip、独立45秒owner身份核验通过。主动精确提前撤销，本次非新自然45秒到期证明。WAN/mwan3、队列/tag、state和模块恢复，完整AFTER审核通过。15:07–15:08最终worker5411原启动身份连续、sequence645、完整保护审核通过，ECM关闭全零，无事务/暂存/实验模块。短时同实例不代表长期稳定/完整高负载故障恢复。
- NSS47/48/49分别19/37/47份可读源码冻结，成功/失败完整输入副本留本地；原NSS46 current-runtime精确保存在nss46-runtime，部署镜像按当前config匹配。白名单输出不含连接/凭据/备份/截图/模块。报告源/链接检查通过；已有本地文件策略拒绝保持、未绕过，未声称视觉验收。无上游提交；无包误判放本地backlog。
- 下一步只补同负载客户端验收，直接用NSS49，不重做已通过的准备；第二WAN同时加速/共享预算/Wi-Fi/autorate继续等待。性能/真人闭环未通过，不能永久开放NSS。
- 15:34补充只读原完整审核通过，同一worker5411、sequence1189、source age1.73秒，ECM仍关闭全零；4个selector不等于真实CS2旧流退出，背景归属没有重作真人判定。前一次最终证明保持，新snapshot单独保存。

## 2026-10-04 NSS50–52：实际软件 HUD、高负载入口定位与未安装候选

- 用户授权下载库中DOOM Eternal作负载，79.2GB于17:14完成，未购买/启动；助手控制在线CS2闲置/观战，与真人体验分开。仅在Steam最小化工具无法恢复时请求一次打开窗口，回复后继续，无重复游戏准备要求。
- 六次实际尝试分别为选中分类拒绝、持锁来源6.47秒、历史服务PID基线、两次core-sleep deadline、再一次选中分类拒绝。四次有checkpoint下载/SHA/gzip与独立45秒owner身份核验后进行单WAN/private/LAN4队列/gate模块暂存，全部精确恢复、独立清理和原完整AFTER通过；两次在暂存前拒绝。ECM全程未放行，没有本轮完整A/B/A2。首次/第六次缺具体拒绝槽位，后续流退出/下载完成不能倒推错误帧原因。
- NSS50只改变实验前服务PID历史基线：健康sing-box core/guard命令/状态完全相同才接纳PID变化，随后固定epoch；期间任何服务变化仍拒绝，原分类器原生PID/start/argv/锁归属审核保持。24项本地边界、128项来源绑定、原完整目标只读审核通过；未重启服务、没证明历史PID变化原因。
- 第四/第五次只完成软件A，各5.08/5.05秒、11帧，LAN4 227.35/267.64Mbps、WAN5 46.25/76.29Mbps，LAN4 18,863/22,214pps，busy75.64/72.52%、softirq48.31/47.72%、time_squeeze+0/+1、softnetDrop+0/+0。LAN4共同NSS队列树已暂存但ECM全零、CAKE fallback工作；不是未暂存原始基线，不能彼此因果比较。未取得B/A2/有效CAKE tin对照。
- 实际Sky截图映射到软件A的4/5帧，中央2/3帧，往返时钟锚点/完整场景逐帧检查。ping12ms，下行jitter2–4/1–4ms，loss0–0.1/0–0.8%，Miss0–1.2/0–0.4%。HUD滚动/峰值，中央帧不去除历史；没有NSS B或真人体感，不作改善结论。
- 只读根因：旧helper子进程换代后全机stat/argv/wchan扫描，完整consumer路径暂停下载3/3通过，实际约350Mbps下载0/3、最长740ms。NSS51只为固定guard直接子进程读取完整身份、结束重验guard，原缓存/初始全局发现/200ms出生条件保持。22模型/两次实际只读/140项完整绑定/原完整目标审核通过；实际下载仍1/3通过、最长250ms，不能称稳定解决。随后真实入口初始分类拒绝，未走到NSS B。
- NSS52只把无关进程stat完整字段拆分改为父进程提取，waitFresh与原身份/4096进程界限/全部期限不变。旧22模型重放＋新增12解析差分、两次轻载只读通过；10000遍纯解析0.623336→0.050266秒，91.94%，不是整机收益。未安装、未生产绑定、未新的高负载资格。源码构建和时钟夹具的本地错误原输出保持，修正后才资格核验，未因这些准备错误进行生产写入。
- 17:30最终原完整持锁审核通过，同一worker/guardian/producer，queryAge3.28秒、sequence3488，2个selector可能为背景流；ECM停止全零，无事务/暂存/状态/gate或qdisc实验模块。CS2退出测试服务器，三项HUD恢复“条件较差时”，Steam速率零；同实例连续不代表高负载crash或长期稳定。
- NSS50/51/52分别15/14/7份可读源码冻结，实际128/140项完整输入副本与原始HUD/CT/socket/serviceepoch仍私有。NSS49 runtime精确保留，旧成功/失败和新候选分开；冻结不是额外生产准入。报告源验证通过，未声称浏览器渲染验收。上游Issue/PR只本地backlog，未提交。
- 下一步只验证高负载进程发现、补该帧分类诊断，然后集中取得同负载软件→NSS→软件/客户端HUD。NSS49功能成立，不重复分类器安装或旧99/13项准备；第二WAN、共享预算、Wi-Fi、autorate继续等待，CPU/真人收益未验收。

## 2026-10-04 NSS53：真实下载发现 6/6、拒绝帧诊断与新入口绑定

- 开场与18:38末次原完整持锁保护审核通过，常驻NSS47/config478818d…7517a900不变。固定service epoch期间服务集合/命令/健康/身份无漂移，同worker/guardian/producer；sequence从4211推进至4840。ECM关闭全零，无事务、暂存、实验state或gate/qdisc模块。本轮没有路由器实验配置写入、checkpoint、回滚试验或NSS B。
- NSS52父进程解析候选保持同字节，原waitFresh、200ms条件与source/owner/epoch期限不变。NSS53入口绑定140基础＋19新项共159项，stage/controller差分只改明确候选、诊断和新目录。原20Mbps、一TCP＋一UDP、独立45秒owner恢复保持；旧99/13准备复用不重计。当前是实验入口，未替换常驻分类器，未本轮完整转发资格。
- 新同帧诊断源码确认classification是bulk＋已准入RT投影。保留导致拒绝的原采样；仅终态拒绝后最多读一次snapshot，producer与全部query来源字段一致且原consumer.inspect有效，才补完整分类。否则明确未知，不重新查CT、不改准入/重试/恢复。原第一/第六次拒绝仍缺完整槽位，不能倒推历史原因。
- 本地60断言（21旧适配器重放＋39新增）、原生JSON helper14项通过；本地适配器IO/时钟/ACK被替代。目标实际ready路径两次均用合成不存在键：轻载sourceAge1.39秒，同源完整帧确认不存在；下载时sourceAge1.64秒、check0.05秒，完整来源不相同则未知，retry=false，ECM仍全零。不是实际连接NSS准入/加速证明；目标RAM省略未用renewal函数，不宣称完整原生转发模拟。
- 用户授权另找库内下载，助手选择未安装DOOM（2016），D盘当时可用218.25GB、磁盘需求68.69GB、网络59.3GB；暂停前约6.1GB、页面曾显示323.3/336.4Mbps。已核验暂停/0bps，未购买、卸载、启动游戏或重下DOOM Eternal。本轮未操作CS2 GUI，没有HUD；运行着CS2进程不等于对局。
- 完整consumer candidates/readContext/inspect＋原guard真实子进程换代，两组三次各6.01/5.40/5.36与3.18/5.27/5.16秒，6/6通过。LAN4 Mbps365.65/353.88/330.47/300.99/297.43/293.94，pps30305/29350/27478/25000/24684/24445。CPU busy84.80/79.07/76.24/77.61/74.09/71.52%，softirq54.41/55.67/53.00/47.35/45.40/45.86%，time_squeeze+22/+18/+2/+18/+30/+28、softnetDrop全零。含profiler开销，不同窗口不是同offered load，更不是NSS A/B；softnet0drop不是客户端0loss。
- longest consumer180ms、含consumer回调200ms；实际接纳结果最大出生年龄180ms，uptime约10ms粒度、余量有限。新候选六短窗发现验证通过，不把历史旧helper0/3、51的1/3与本轮计算为整机CPU收益，也不宣称完整高负载crash/recovery或长期稳定。guard未signal/暂停/修改，ECM每帧关闭零计数。
- 应用核查24Steam bulk/0对局UDP/0同WANpair，默认只读等待，未开ECM，无leaf/CAKE tin/游戏指标/体感。下一步直接用53在真实同WAN配对下先记录HUD、原checkpoint/独立恢复、同负载software→NSS→software，不扩WAN，不重复安装/旧准备。
- 三次本地传输长度拒绝、夹具/输出解析、入口切片offset、首版投影解释及汇总缓存年龄/结果字段修正原输出保持，未提高传输或有效期界限、未触发生产变更。24源码冻结，651份总镜像哈希校验；旧52runtime原字节保存。原完整私有绑定、配置/进程/CT/socket/截图仍本地。报告源验证通过，未声称浏览器渲染，未提交上游。

## 2026-10-04 NSS54–63：实际A+B/HUD、五次恢复、发布与读取竞态定位

- 原53入口的完整来源过期在checkpoint前拒绝。54 path-inode join实际竞态、55 held-FD读修复后standalone语法传输过长；56使用独立守护编译精确完整bundle，上限未变。
- 56真实WAN1 A5.04秒/B5.03秒、各11帧；ECM0→2→0、bulk4755/RT549包、原ECM parser确认mark65536/NAT/WAN/lan4/br-lan，续租一次/精确撤销。A2前total/expected下载counter差1pkt/1500B、其它计数对齐，原strict getter拒绝。只有部分A+B，不能冒充完整成功。
- 实际软中断52.77→47.66、busy75.98→71.21、squeeze42→20，但LAN4 303.75→261.64、WAN1 57.87→31.23Mbps，不匹配。原生锚点约100ms不确定性，A/B各5张完整中央HUD实际检查：A16ms/jitter2–3/loss0.1–0.5/Miss0.8，B16ms/jitter1–2/loss0/Miss0。在线闲置非真人；HUD滚动/峰值，未验收性能或游戏收益。
- 57极窄counter witness后一次只读重读，原getter仍mandatory，实际preaudit stale拒绝；58 inode hint/RAM10，真实WAN2只到A后同计数差帧拒绝；59将相同见证用在ECM关闭的A后，RAM7。第一59同源完整分类确认当次TCP缺失；第二59仍preaudit stale。没有扩大budget/TTL/准入重试。
- 60 metadata-only hint/RAM10，native完整审核通过后JS wrapper契约错误写前拒绝；61 normalize/RAM外14本地断言。首61来源margin2.16秒不能学习，恢复flags全真但即时完整AFTER stale；暂停后原完整recovery通过。第二61完成软件A，旧sleep候选wchan自然退出时拒绝，未打开ECM。
- 62整次child读取或nil候选修复，15目标RAM、full helper语法/实际只读scan与waitFresh同字节证明，200ms保留。本地漏payload导入，路由器连接前失败。63精确拷贝依赖并实际module导入，241项资格绑定；实际source7.41>6再次写前拒绝，尚无新helper高负载forwarding稳定证明。
- 共12实际控制器失败案例、5暂存（1WAN1/4WAN2，每次单WAN）、1次ECM；另62本地启动失败。5个checkpoint archive在封存时重验SHA/gzip，独立45秒守护写前身份记录及undo/保护比较保存。4个即时完整AFTER通过；首61失败与后来通过分开。原45秒自然到期未在这5次case中实测。
- 分类器未重装/主动restart，worker自然5411→20682，guardian5412保持，原因未知。最终21:26原完整审核source4.56、14selector、NSS47config不变，ECM全零，清理无事务/暂存/state/实验模块。
- DOOM201619:44完成；助手授权下载新库内Disco/Hades/Witcher，原暂停队列自动接续21:12–21:13均完成。最终0bps、即时queue0，未购买/启动新游戏/卸载/DOOM Eternal重下；CS2测试服退出，三项HUD恢复。不是最终三个下载仍暂停。
- 144份可读源码新增、原实际输入冻结保持，旧53runtime按字节留存。离线WAN投影交叉校验发现四个错误fallback1，已按selected改为2并保留v1、生成v2；运行时选择/权限不变。归档脚本的本地文件路径/缺失比较结果假定已纠正，不改生产门槛。
- 仅下一条主线：缩短高负载完整snapshot发布及消费工作，再补可比A/B/A2。NSS56功能/实际HUD有进展，但CPU、真人收益、长期稳定未通过；未扩第二WAN同时加速/共享预算/其它backlog，未上游提交。

## 2026-10-04 NSS64：完整发布编码候选，只读与RAM资格

- 常驻NSS47不变。开场/23:15收尾原完整持锁审核与清理通过，同worker20682/guardian5412/producer，source1.38→2.61秒；ECM关闭全零，无事务/暂存/state/gate或qdisc模块。未操作GUI/下载，客户端历史状态未刷新；无配置写入/checkpoint/新增自动回滚试验。
- 拆解NSS63原source7.41失败：query→stamp3.84秒、提示消费结束5.47秒、交接0.29/哈希0.35/journal0.03/selector0.51/完整解析0.76秒。stamp在编码前，rename未直接计时，提示读耗时未分离，不能把全部后stamp时间当编码。
- 原投影内联scalar候选native36通过、真实82条投影约12%改善，仅作为该轮早期候选。完整分块编码原投影25/29案例分别通过；最新快速投影＋分块完整边界native36/29通过，真实319条冻结同内存夹具三对原179.06/新136.22ms CPU、−23.92%。36/29不是独立唯一案例数，也不重算旧99/13。没有实际高网络负载或整机收益。
- 预投影512/1024真实形状规模的纯编码156.96→108.93 /422.87→198.18ms CPU，全部字段相同；不计投影CPU，不是真实512/1024条CT或NSS准入。C函数身份已确认，上游visited线性扫描与趋势吻合；目标二进制精确commit未证明。仅本地Issue候选，未提交上游。
- 首次2048组合模拟六秒runner返回124自动结束，失败保留；观察器初版请求超过runner支持范围，执行Lua前返回2。改为原六秒内四秒观察，没有扩大限额。自然4.03秒，LAN4约0.023Mbps、18.11pps、busy17.04/softirq3.21%、squeeze0，包含0.226 CPU秒观察器成本；两个完整周期0.63–0.86秒可见，stamp→可见观测窗20–80ms，只是轻载。
- 单项候选worker32,019字节精确目标RAM编译/SHA通过，剥离该边界补丁与原28,919字节worker逐字节相同；非快照序列化保持原式。未执行watch、安装、改原模块或绑定新NSS入口。策略/学习/字段/原完整解析/审核/PBR/ct mark/NAT/gate及全部期限未变，当前仍NSS63/241项。
- 20份源码冻结/累计815，原63 runtime与全部旧证明按字节保持，原始连接/配置/CT与私有输出不上传。输出中originalJsonProjectionRetained旧布尔已注明指合同、不是同一函数，原raw保留。源码/报告源检查通过，浏览器渲染未验证。下一步直接publication边界checkpoint+独立撤销单项试验，再高负载完整审核和集中单WAN可比A/B/A2，不重装/重放旧准备/扩WAN。

## 2026-10-05 NSS65：publication现场单项试装与自然精确恢复

- 23:56开场原完整审核通过，旧20682/5412。创建一个checkpoint并下载/SHA/gzip核验，先证明独立480秒暂存守护，再证明PPID1且身份/boot/期限/CP绑定的180秒生产撤销，然后仅替换完整snapshot序列化worker32,019字节与config.files/事务身份。四模块、策略/学习、PBR/NAT/gate、root qdisc及原期限保持。
- 候选期间00:00:59和00:02:01两次原完整持锁审核通过，source2.69/1.78秒，worker9414/guardian9415/producer连续，sequence16→37。NSS始终关闭零计数；不是新的241项入口资格。
- 00:03独立180秒自然到期，不发控制器回滚命令；00:03:19已核验rolled-back日志、旧worker/config SHA/指针、四模块SHA、健康fresh snapshot。随后精确stage owner/inode取消本轮暂存；不是该stage自然480秒到期证明。
- 00:04:20原完整审核/保护配置/清理通过，worker20030/guardian20031/source2.43秒，常驻47/config不变，ECM全零、无事务/stage/state/实验模块。实例变化是本轮试装及恢复restart，不能声称原producer/PID连续。
- 两个候选自然窗和一个恢复自然窗：0.025/0.031/0.018Mbps，busy16.50/15.21/21.11%、softirq4.61/0.13/5.12%、squeeze+0，均含观察器成本，未匹配负载。完整周期query→首次可见0.77/0.73/0.85秒为观测界限，不证明高负载来源过期已解决或CPU/游戏收益。
- 不重跑旧36/29与99/13；无GUI、新下载、真实CS2/Steam高负载/HUD/真人体验、NSS放行或A/B/A2。8份白名单源码/累计823和8份完整实际私有输入冻结，旧64/runtime与历史证据保留，未提交上游。下一步直接高负载原完整发布/审核及候选正确绑定后的集中可比单WAN闭环。

## 2026-10-05 NSS66–67：真实300Mbps以上完整发布与独立恢复

- NSS66公共负载探针403/429失败，429后停止不重试、不执行payload；随后已授权Disco Elysium下载。首次客户端360秒自然执行精确实例-shutdown，00:44:57确认原进程退出。publication候选00:46单项试装，经checkpoint下载/SHA/gzip和独立180秒守护；候选实际209/148Mbps，原审核source0.74/1.74通过。到期后继续用候选context的SHA断言拒绝失败保留，00:50自然精确恢复/完整审核/清理通过，12843/12844。下载8.7GB完成，网络/磁盘0，第二客户端守护取消。
- NSS67复用同候选，00:55在新的checkpoint/独立守护核验后试装，D盘已授权黎明杀机负载。候选四秒窗口371.50/366.78/385.08Mbps、约3万pps，busy84.51/78.70/82.36、softirq60.72/51.89/55.77、squeeze+11/0/0，含观察器成本，负载不匹配，不是NSS转发或CPU A/B。
- 原完整审核：启动source1.63，00:56:20和00:57:28高负载期间3.62/4.41秒通过，同31721/31722/producer；原6/9秒与完整字段未改。审核和四秒流量窗是相邻窗口，不冒充同窗观测。只有publication变量，四模块/学习/PBR/NAT/生产根qdisc/gate保持。
- 180秒独立生产恢复已自然执行；00:58:40晚到的候选context审核在配置SHA拒绝，10ms统计不作性能证据。00:59:14原worker/config/指针及四模块恢复通过，之后按精确owner/inode取消stage，非stage自然480秒到期。恢复后原完整审核同窗314.06Mbps/source5.97秒通过，余量0.03秒，不能保证长期稳定或证明候选CPU收益。
- 00:59约17%暂停黎明杀机，随后界面网络/磁盘0、旧317KB安排未操作，01:00:53取消客户端守护。01:09:58原完整最终审核/保护配置/清理通过，9454/9455/source2.22、常驻47/config不变、ECM全零，无事务/stage/state/模块。无游戏启动/购买/卸载/CS2/HUD或真人体验。
- 22份白名单源、累计845与14份实际完整运行输入私有冻结；旧65runtime原字节保持，36/29及99/13不重跑，241项NSS入口不变，本轮publication未当NSS准入。下一步精确绑定候选实际保留部署、消费者/原审核/stage，再集中现有下载和真实CS2可比A/B/A2，不扩大WAN或其它支线。

## 2026-10-05 NSS68：实际保留、统一部署入口与原完整现场审核

见 [本轮实测](../evidence/nss68-mainline.json)、[新入口绑定](../evidence/nss68-entry-binding.json)、[终态审核](../evidence/nss68-final-audit.json) 和 [调用位置](PUBLICATION_ENTRY_HANDOFF.md)。

- 当前部署 `work/nss68/deployment-latest.json`，config `581b5d46c9d3772ccd94f5f36510bccf665899f210c43b4deaa5155067c791d7`，32,019字节worker SHA `40169ce6c8e866cc989c651b24d435777bc422bf10f67c58f5e9ab033e7f3828`。旧47/49引用只作历史，未覆盖。
- 一个checkpoint下载/SHA/gzip，独立480秒stage和180秒生产undo写前核验；原完整持锁审核source2.49通过后远端commit、配置/worker/pointer读回验证，候选留驻，常驻健康守护保留。本轮没有再测自然180秒撤销；66/67自然恢复证明保持。只按owner/inode取消已提交后的passive stage。
- 入口 `work/nss68/real-session.mjs` 原241项全部保留，新16项、共257，17绑定检查通过。分类读取、原完整审核、stage共同使用新committed部署；原Lua消费者、stage/payload与1/2/6/9秒、200ms child、20Mbps、一TCP一UDP、45秒owner均不变。实际只读准入source1.46秒、同producer恢复审核1.26通过，未运行新NSS stage，不能称高负载gate已验收。
- 10:32:50–52候选17138自然退出，日志为 `tc child cleanup not proved`，apply256、4.35秒。原47相同TC监督代码也有历史apply失败；该次发生在本轮恢复下载之前。只有边界证据，没有具体tc命令、child PID和阻塞栈，不能归因发布改动、下载或内核。自动恢复后23634/17139，最新准入/恢复同producer，长期稳定未验收。见 [监督记录](ISSUE_TC_SUPERVISION.md)。
- 现有暂停的黎明杀机恢复，界面瞬时312Mbps后回到暂停；真实4秒仅2.879Mbps/425pps、busy34.91/softirq7.46/squeeze0；实际审核窗0.587Mbps，未形成300Mbps对照。没有CS2、HUD、真人或NSS CPU收益。暂停原因未确认，不称助手主动暂停；观察到暂停和0bps才取消独立360秒客户端守护。
- 10:37:28原完整终态审核source3.24通过，ECM关闭全零，无事务/stage/state/实验模块，五WAN认证/PBR/NAT/十个生产qdisc与保护配置保持。23份白名单源累计868，12份完整私有运行输入和257绑定输入冻结；旧67runtime原字节保留。
- 下一步直接使用新68入口做一次集中真人CS2+现有下载同TCP/UDP、单WAN可比A/B/A2。新轮次先读实际worker/guardian/producer；实验期间producer更换必须拒绝并精确恢复。不要再试装相同publication、重放旧准备、装新游戏或扩WAN。

## 2026-10-05 NSS69–77：真实配对、部分加速和准备顺序定位

见 [实际轮次](../evidence/nss77-mainline.json)、[终态原完整审核](../evidence/nss77-final-audit.json)、[新源码](../evidence/nss77-source-proof.json)。

- 常驻仍是 `work/nss68/deployment-latest.json`，配置 `581b5d46c9d3772ccd94f5f36510bccf665899f210c43b4deaa5155067c791d7`。本轮没有重装分类器或改变生产配置；worker4859/guardian17139，14:21 source1.89秒、ECM关闭零计数，无事务、暂存、state或实验模块。
- NSS71真实A5.17秒、B1.56秒，ECM2；B未达五秒并因续租过晚停止，无A2。LAN4约336/326Mbps、softirq52.03/50.17%、squeeze38/5，窗口长度不同，不是CPU收益。
- 73/74失败帧里选中Steam TCP不在同源完整分类快照，游戏UDP仍身份/mark/NAT/WAN/tag正确。不是已证明CT消失或分类器故障。75把最终精确TCP选择移至checkpoint下载与编译之后、独立stage之前，原游戏连接和单WAN范围固定。
- 75软件A5.06秒/11帧完成，最后学习余量2.68秒不满足3秒。76把耗时getter移至最终分类证明之前，保留六秒source/native、3秒学习、1.2/1.5秒core、20Mbps和45秒owner；实际失败发生在更早initial ready通过age2.94秒之后，未到A。
- 77只修正initial ready准备预算为age<1.65秒，使后续原标签age<2秒门槛有余量。355项绑定，9目标RAM检查和完整fast语法通过；IO/时钟/分类器模拟，**没有77现场stage/加速证明**。76的getter顺序也没有取得新的实际B证明。
- 本轮本地测试生成错误均保留原raw，修正之后才核验；不作为源码/内核缺陷。69可选stat EOF仅夹具复现，原现场没有具体EOF/PID，不能判定现场根因。
- 客户端通过官方死斗产生真实UDP，助手闲置，未取得真人体感。HUD有保存但不完整对应B，条件显示隐藏值不能记为零。75下载暂停与菜单/HUD恢复单独通过；最后76下载已完成、验证文件仍运行。用户物理Esc停止桌面操作，已停止UI并撤下精确任务guard，不能声称76最终菜单/HUD已恢复。
- 原68 runtime按字节保存，新增122份白名单源，累计990。原始CT、端点、截图、checkpoint、凭据和二进制均留本地；没有提交上游Issue/PR。


| 轮次 | 实际阶段/负载 | 停止原因 | 恢复 |
|---|---|---|---|
| NSS68 | 未取得测量阶段 | Optional process stat parser assertion; exact EOF/PID not captured | 原完整恢复通过 |
| NSS69 | A 5.29s, 364.729Mbps | Stale classifier observation during closed core wait | 原完整恢复通过 |
| NSS70 | 未取得测量阶段 | Obsolete extra setup reserve refused | 原完整恢复通过 |
| NSS71 | A 5.17s, 335.973Mbps / B 1.56s (未完成), 325.657Mbps | Too late to renew; B stopped after 1.56 seconds | 原完整恢复通过 |
| NSS72 | A 5.03s, 242.07Mbps | Selected flow not admitted after opening; exact slot unknown | 原完整恢复通过 |
| NSS73 | 未取得测量阶段 | Application pair changed before staging | 原完整恢复通过 |
| NSS73 | 未取得测量阶段 | Same-source complete frame lacks selected TCP; UDP retained | 原完整恢复通过 |
| NSS74 | 未取得测量阶段 | Persistent TCP still disappeared during passive preparation | 原完整恢复通过 |
| NSS75 | A 5.06s, 326.83Mbps | Tag counter read consumed final source learning reserve | 原完整恢复通过 |
| NSS76 | 未取得测量阶段 | Initial readiness accepted age 2.94s; next pair read refused | 原完整恢复通过 |


## 2026-10-05 14:56 — NSS78只读准备时序

见 [本轮诊断](../evidence/nss78-mainline.json)、[终态审核](../evidence/nss78-final-audit.json)、[两份新增源码](../evidence/nss78-source-proof.json)。

- 16.08秒、154次读取、6个实际分类发布。发布延迟0.27–0.32秒，查询间隔2.99–3.01秒；64次来源age<1.65秒，82次age<2秒。分类快照只有1–3条，不能外推到300Mbps负载。
- 7次观察到core sleep出生age≤200ms，其中2次同时满足初始来源预算；只是时间重叠，不是完整身份、分类、mark/NAT或真实gate准入证明。
- 新的两次原完整审核通过，常驻4859/17139、config581b5d46…c791d7未变。14:56:23 source3.67秒，ECM关闭全零，无事务/stage/state/实验模块。
- Steam队列无待下载大文件，RDR2完成，网络/磁盘均0bps；游戏菜单可见，实际0游戏候选/0Steam bulk/0同WAN对。本轮仅显示Steam窗口，没有新增下载、启动对局或改HUD。前一轮Esc后的完整客户端恢复仍未补证，当前菜单观察不覆盖旧记录。
- 未调用77的aba；355项绑定和已完RAM证明保持，不重放。没有CPU/softirq、time_squeeze或真人游戏收益结论，也没有新增回滚试验。
- 原77 runtime原字节冻结，新增2份白名单源码、累计992。原始运行数据、core-guard原文和桌面内容留本地，未提交上游Issue/PR。



## 2026-10-05 NSS79–82：受控真实TCP/UDP与完整工程闭环

- 用户接受以自有端点受控TCP/UDP做工程，不再每轮等待Steam/CS2。公开新端口连通性准备失败保留：Aliyun/SG raw端口不可达，Dallas TCP/UDP初始PBR不同WAN；约1Mbps TCP被原分类器归BE，未强行BULK。最终复用自有SG既有已认证SSH TCP＋自有Dallas nonce等长UDP；自然尝试自己的socket端口找到同WAN，不改路由器PBR/系统服务。
- 79同WAN5、TCP真实17.996/17.989/17.990Mbps，三段各5秒/11帧；ECM0→2→0，softirq9.65/4.31/9.48%、busy25.08/20.60/27.33，squeeze/drop均0。bulk/RT分别+9798/+271包、队列drop0/0；UDP未返回5/4/8，不是CS2指标。支持当前短窗18Mbps软件转发softirq改善，不能外推300Mbps或长期稳定。
- 80第一次TCP450MiB有限上限后退出，A完成但学习前同源完整帧TCP缺失，UDP保留；无B。第二次三段均完成、ECM0→2→0，但A2最后软件NFT total/expected差一个60字节ACK，错误tag计数全0，原overall失败不改。bulk/RT drop69/0；实际吞吐13.66/18.03/17.33，不验收CPU。
- 81最初本地expected SHA把LF字符串与实际CRLF文件混用，写前失败；改为实际字节SHA后新stage在initial getter出现down1包/1500字节偏差，无A/ECM。两个不同位置证据提示多规则counter dump不同时刻；不是已证明firmware误标或内核缺陷。
- 82只统一五个getter的精确一次重读，允许原down1包1500字节或新up ACK1包60字节；所有其它计数需一致/错误tag与neighbor全0，第二次仍原严格getter。17项原生ACK正负案例通过；现场只触发down分支，第二次一致。完整payload目标编译/SHA与原transport大小限制保留。
- 82在WAN2同一TCP/UDP跑完整5.00/5.01/5.02秒、各11帧；ECM0→2→0、正确bulk/RT tag、mark0x20000/NAT/出口、1次续租、精确撤销。发送32Mbps，实际14.90/17.16/18.08，不同吞吐不作CPU收益；softirq11.73/7.24/18.12、busy30.39/22.81/35.95、squeeze0。B观察bulk+8990包/drop143、RT+262/drop0；UDP203/203、213/213、203/202，p95约205.64/205.25/204.86ms，为自有端点RTT而非游戏。
- 五个现场stage各新checkpoint下载/SHA/gzip、独立PPID1/45秒owner写前核验，最后全部保护配置/完整原审核恢复通过。17:05常驻4859/17139、config581b5d46…c791d7/source1.15；ECM关闭全零，无事务/stage/state/模块。临时端点180秒FW独立恢复与客户端guard通过，临时端口已关闭，无生产VPS服务替换、游戏/Steam/UI/HUD改动。
- 新源码与脱敏聚合证据进私有仓库；完整原始CT、nonce、连接/凭据、checkpoint、模块、实际绑定输入仍留本地。旧78 runtime原字节保存。不提交上游；下一步直接提高单WAN受控带宽，再最后集中真人验收，不重装/重放旧准备或同时扩多WAN。


## 2026-10-05 NSS84–92：60Mbps组、计数观察根因与32Mbps可比闭环

- 主要QoS变量20→60Mbps，bulk59/RT1/ceil60，默认950、FQ-CoDel参数不变，实际source反向替换与旧字节相等，原生layout7例。52发送/1GiB/180秒客户端上限，45秒owner及原native/source期限保持。
- 84 ACK1包40字节＋UDP未返回，未执行A/ECM；85按精确ACK及pending做23RAM后，prep90%回包不达，86一轮8个自己TCP候选未同WAN、另一同WAN但缺最近回包；均未stage。87去掉冗余echo质量门槛后A仅2秒/5帧，TCP分类投影消失；实际客户端stderr是Windows EPERM status rename崩溃，完整同源CT诊断不可用，不能只按投影定CT退出。没有ECM。
- 88修客户端临时EPERM/EBUSY，3本地正负例，其它IO错误仍fatal；后来无实际EPERM复发不称现场注入恢复。被动tap改ETH_P_ALL，249入/249出/249客户端回包证明原87 IP-only零TX只是观察限制；后续initial先ACK偏差、重读又TCP-down偏差，UDPdown0，原失败保留且不开放ECM。
- 89按正确观察合同替换逐规则原子相等假设，最多1重读、total/expected两帧单调且交叉范围相交，wrong tag/neighbor包及字节0，原完整NFT policy及新flow/TTL/classifier/native gate不变；30目标RAM正负例含真实88两帧及缺方向仍拒绝。实际52两轮initial UDPdown为0在原1.2秒截止拒绝，均无A/ECM；一次端点5秒247入、246出、客户端只33，安装tag前及撤销后亦有缺包，原因未定。
- 91仅把发送52→32，60QoS和89fast字节不变，WAN2完整A5.01/B5.01/A25.01、各11帧、ECM0/2/0。客户端31.996/32.023/32.003Mbps，LAN4均33.57Mbps左右，softirq15.19/4.97/14.43%、busy28.81/15.93/30.03%，time_squeeze/softnet drop全0。两次A2边界计数bracket现场通过，2次确认renewal、精确retire、mark/NAT/affinity通过。
- 32Mbps相对软件均值softirq下降66.41%；UDP239/239、238/238、239/239，p95约198.39/198.06/198.39ms，为自有端点RTT而非CS2。B附近异步leaf bulk+14541包/+20675746字节、RT+242/+41140，drop0/0；未饱和60，因此不验收60准确限速、拥塞FQ/AQM/ECN或游戏收益。
- 六个实际stage各checkpoint/SHA/gzip、独立PPID1/45秒恢复和前后原完整保护审核通过；九个有限端点全部180秒FW基线恢复、0规则、临时unit/端口关闭、client/210秒精确守护退出。18:42原完整终态source2.88、worker4859/guardian17139连续，ECM关闭全零，无事务/stage/state/module，常驻68不变。
- 92封存实测/源码与旧82 runtime原字节；完整原始CT/nonce/端点凭据/checkpoint/模块/绑定留私有，无上游Issue/PR。下一步只定位52回程并补更高同負载闭环，最后一次真人CS2验收，不重装分类器/重复准备/新游戏/扩第二WAN。

- 最终文档复核纠正上行边界：实际两flow upTag均0，当前仅LAN4下行NSS队列，不能声称上行仍走软件或得到WAN CAKE保障；本轮上传只是ACK＋低速UDP，未验收上传QoS。原实际测试源码/数据不变。
