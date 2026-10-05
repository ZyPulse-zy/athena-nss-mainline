# 当前状态

更新：2026-10-06 01:04，北京时间。最新NSS109；常驻仍68/config581b5d46…c791d7，ECM关闭全零，无实验残留。

**两次实际8秒nonce/序号捕获定位到：484个请求均到服务器并发出echo；路由器最早Linux物理接口tap只见465个，之后private WAN→IFB→bridge→LAN→PC全部465个相同，链内缺包零。19/484（约3.93%）缺口在server软件TX→router最早Linux tap之间；上游链路与网卡接收早期尚未分开。**

见 [序号证据](../evidence/nss109-path-localization.json)、[认证修复](../evidence/nss109-auth-repair.json)、[自然故障切换](../evidence/nss109-wan4-failover.json)、[捕获器边界](../evidence/nss109-instrumentation.json)、[关闭](../evidence/nss109-endpoint-closure.json)、[终态](../evidence/nss109-final-audit.json)。

- 首窗236发/227收，后窗248发/238收；内部窗口裁掉首1秒/尾2秒，使用最终PC日志和确切nonce序号，不假定服务器/路由器UTC同步。对应TCP44.407/47.999Mbps、UDP p95约209.51/209.35ms。自动分类实际TCP BULK WAN3、UDP RT WAN2：这是软件路径定位，非同WAN拥塞对照；没有NSS leaf、同窗CPU/softirq/squeeze或真人CS2新验收。
- NSS108首次捕获自身drops160、退出2，不能作缺包定位；其server捕获被异常中断，不称完整保留。109只修socket接收顺序：protocol0→socket filter→bind ETH_P_ALL，两次实际drops0、九接口方向可见。host/目标解析同6例通过；WSL不支持AF_PACKET的实际socket测试失败，未把它称通过。helper本身最多12秒、外部14秒，checkpoint和独立480秒临时目录清理先于上传；108观察到到期后自然消失、109owner/inode核验后取消。
- 写前发现WAN4认证进程无PID，旧恢复脚本set -e让jsonfilter缺失字段的退出1跳过空PID分支。真实最小复现与6目标RAM结构案例通过，只改PID读取为校验ubus结构的Lua；保护清单仅更新对应一行。checkpoint下载/SHA/gzip、独立180秒撤销写前验证，原完整native审核、单独SSH和其它运行配置核验后保留。没有主动重启认证/接口，本轮未做新的自然180秒回滚。写后原始动态tc文字比较失败保留，随后用原完整ownership审核验证动态selector。
- 现有watchdog在修复后一次自然恢复请求返回0，但WAN4仍认证失败/接口down，无IPv4；不称五WAN恢复。原健康控制器权重[100,100,100,0,100]，300桶按实际源码严格复现为四路各75桶，仅60个旧WAN4桶重派、healthy移除WAN4、3个WAN4 DHCP路由规则消失，固定ct mark规则保留。是既有故障切换，非实验写PBR。原全5WAN旧快照严格审核的拒绝保留；本轮对声明修复和精确自动切换后的其它配置/原完整native审核通过，不是新的NSS入口资格。
- 终态worker4859/guardian17139/source3.34，ECM stop1/所有count0，无事务/stage/state/实验模块。两个端点FW180秒独立恢复、client210秒退出、unit/端口关闭均通过；凭据/实际端点配置/CT/nonce/二进制/检查点/完整清单留本地。
- 历史32Mbps约66.41%与48Mbps B/A2约72.19% softirq收益保持；本轮没有加速写入/新收益/真人指标。仅LAN4下行/upTag0的缺口保持。旧107/98/92/82 runtime逐字节保留。下一步回到实际四路基线下的单WAN入口和NSS QoS预算/关键上行，不再用这两窗约4%缺包要求反复调整CAKE；最后一次集中真人验收，不扩WAN/Wi-Fi/autorate/共享全局预算。

## NSS107历史状态

# 当前状态

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

## NSS98历史状态

# 当前状态

更新：2026-10-05 19:50，北京时间。最新NSS98；常驻仍NSS68，所有实验NSS已撤销。

**48Mbps真实单WAN完成完整功能A/B/A2。NSS与返回软件两段吞吐47.981/48.004Mbps，softirq5.245/18.860%，相对下降72.19%。另一次40Mbps受控预算拥塞短测bulk新增丢弃148、RT零丢弃，NSS段UDP223/223收到回复。**

见 [本轮汇总](../evidence/nss98-mainline.json)、[三轮现场](../evidence/nss98-trials.json)、[48Mbps原始指标](../evidence/nss98-matched48.json)、[40Mbps拥塞指标](../evidence/nss98-congested40.json)、[回程定位](../evidence/nss98-return-localization.json)、[终态审核](../evidence/nss98-final-audit.json)。

- NSS96：60Mbps组、发送48Mbps、WAN2，一TCP一UDP。ECM0→2→0、两次续租、学习前tag、真实bulk/RT leaf、完整ct mark/NAT/WAN affinity和精确撤销通过。三段5秒/11帧，实际TCP47.031/47.981/48.004；第一段约2%低且UDP157/234，不能算三段严格相同吞吐或游戏改善。CPU收益仅采用吞吐差0.05%的B/A2；两段UDP241/241、243/243，leaf drop0/0。原32Mbps三段可比66.41%结论保持。
- NSS97：同一发送48Mbps，只把受控QoS组60改40，bulk保障39、RT保障1、共同ceil40、fallback950，单WAN3。7目标RAM native-option记录布局案例通过；实际4queue/5class/9命令及两次续租、加速/恢复通过。实际TCP32.868/35.091/33.274Mbps，不接受CPU对比或长期40Mbps精确限速结论。异步B附近bulk drop+148、drop_overlimit增量0、RT drop0；bulk仍有backlog、RT backlog0，符合AQM/隔离的解释，但未把异步计数当精确B瞬时统计。UDP205/205、223/223、217/217，B RTT p95约189.883ms；受控echo不是CS2网络指标。ECN、多流公平、长窗限速未验收。
- NSS93/94全程只读、ECM关闭，分别104/64个逐流CT帧；保持同一TCP/UDP/mark/NAT/WAN，52↔32Mbps切换。NSS94实际32.002/51.998Mbps；32回包1144/1144匹配，52服务器egress1092、PC匹配701。8个0回包窗CAKE/redirect/softnet丢弃都0、Voice没有新增包；全部选择窗CAKE也drop0。WAN物理rx_drop仅各组1，不能解释数百缺包。支持缺口在可观测软件IFB/CAKE交付之前，不支持PC程序或这些队列为主要丢包位置；没有物理接口精确nonce tap，上游与未计数入口仍未分开。server/PC按nonce序号匹配，不能直接用未校准服务器UTC。
- NSS95仍发送52、60Mbps组，测试前UDP120发/0收；原1.2秒内拒绝initial down0，无A、无ECM。独立45秒恢复与完整审核通过，失败原义保持。第一次端点关闭检查早于180秒自然expiry，准确拒绝2条规则未到期；后来实际自然撤销、FW全局基线和端口/unit/客户端关闭均通过。
- 三个stage每个checkpoint下载/SHA/gzip和写前独立PPID1/45秒守护、最终恢复通过；五个端点FW180秒守护写前核验、规则0/全局基线恢复、临时unit/端口/client关闭、210秒精确客户端守护通过。常驻4859/17139/config581b5d46…c791d7未改；最终source1.64秒通过原完整审核，ECM关闭全零，无事务/stage/state/实验模块。没有Steam/CS2/UI/新游戏下载/第二WAN/五路认证PBR改动。
- 当前NSS树仍只有LAN4下行，实际TCP/UDP upTag均0；未建立加速上行QoS，不能依赖软件WAN CAKE约束已经绕过它的flow。没有完整CAKE替代验收。多人公平不是需求；DiffServ4未复刻，现为明确bulk/RT两leaf、FQ-CoDel参数5ms/100ms/1024flows，autorate未接入NSS。
- 下一步只收尾单WAN关键功能：先用集中长一点的受控窗口核实拥塞时实际限速/RT延迟与自动分类，处理首段过渡影响；再集中一次真人CS2＋正常下载HUD/体感验收。52Mbps US UDP端点缺口作为已定位到软件队列之前的独立待查，不再反复用无回包窗口卡住所有工程。NSS96/556为48Mbps收益入口，NSS97/580为40Mbps拥塞入口；不重装分类器、重放已通过准备、扩第二WAN/共享预算/Wi-Fi/autorate。原完整私有输入和捕获仍本地，旧92/82 runtime原字节保持。

## NSS92历史状态

# 当前状态

更新：2026-10-05 18:42，北京时间。最新NSS92；常驻仍NSS68，所有NSS实验已撤销。

**60Mbps受控QoS预算下，真实32Mbps的一TCP＋低速UDP完成完整单WAN A→B→A2。客户端31.996/32.023/32.003Mbps，softirq15.19→4.97→14.43%，相对两段软件均值下降66.41%；UDP239/239、238/238、239/239，bulk/RT零丢弃。ECM0→2→0、NAT/PBR/WAN affinity和精确恢复通过。**

见 [汇总](../evidence/nss92-mainline.json)、[六次现场记录](../evidence/nss92-trials.json)、[32Mbps完整对照](../evidence/nss92-matched32.json)、[标签计数修正](../evidence/nss92-tag-reader.json)、[回程与客户端故障](../evidence/nss92-load-observations.json)、[终态审核](../evidence/nss92-final-audit.json)。

- 用户已允许工程以受控真实TCP/UDP推进；无需每轮开Steam/CS2。真人游戏保留为最后集中验收。永久分类器未改，4859/17139连续，config581b5d46…c791d7；终态source2.88秒通过原完整审核，ECM关闭全零，无事务/stage/state/实验模块。
- 主要QoS变量从20提高到60Mbps，bulk保障59Mbps、RT保障1Mbps，二者ceil60，默认fallback950；目标原生选项7案例通过。当前32Mbps没有压到60Mbps上限，不能声称60Mbps限速精度或拥塞/AQM/ECN已验收；这套NSS队列仅覆盖LAN4下行；实际TCP/UDP upTag都为0，未建立NSS上行队列，不能把WAN软件CAKE当作已加速流的上行QoS保证。
- 84/88多规则计数继续出现1包40/60/1500字节偏差，第二次也可偏差。89替换活动counter严格同瞬时相等假设：精确完整policy验证保持，错误tag/neighbor包和字节必须全零；最多重读一次，两帧所有total/expected需单调且交叉区间相交，学习前仍要真实双向包。30目标RAM案例包含真实88帧与错误字节、缺方向、倒退等反例；91现场两次边界重读成功。6秒来源/12秒native/45秒owner等未改。原失败保持。
- 87实际客户端在Windows status原子替换时EPERM退出，之后TCP不在分类投影。88对EPERM/EBUSY延后状态上报、数据连接继续，其它IO失败仍退出；3本地案例通过。实际后续没再次捕获EPERM，不冒充现场故障注入恢复。
- 52Mbps下当前UDP回程窗口不稳定：正确ETH_P_ALL端点tap曾249发出/249客户端收到；另一5秒247入、246发出、仅33客户端记录。缺包在安装tag前和撤销后也有。89两次使用新检查均因initial UDP-down为0，在原1.2秒内拒绝且不开放ECM；不能归因NSS，也不假定是52Mbps造成。根因暂定位在自有服务器egress至客户端接收之间，尚未区分上游/路由器/Windows。
- 六个stage各checkpoint下载/SHA/gzip、写前独立PPID1/45秒守护与完整恢复审核通过；九个负载端点FW180秒独立恢复、规则0、原全局基线恢复、临时unit/端口关闭、客户端/210秒精确守护退出。没有新游戏下载、游戏/HUD/UI、购买/卸载、固件/内核、生产分类器或五WAN/PBR改动。
- 可直接使用32Mbps已通过入口`work/nss91/controlled-session.mjs`（555实际绑定输入），52Mbps诊断入口`work/nss89/controlled-session.mjs`（533输入）。源码/完整输入按新case冻结，不能修改旧证据。原始CT/nonce/端点配置/凭据/checkpoint/模块仍私有；[旧82 runtime原字节](../evidence/nss82-runtime.json)保持。
- 下一步集中定位受控UDP回程缺包：优先只读关联服务器发出、路由器收/发和客户端接收；不能用没有回包的窗口评价RT QoS。随后同一60Mbps预算补52Mbps完整可比A/B/A2，再一次真人CS2＋正常下载验收。已经通过的分类器安装、30项计数检查、32Mbps闭环不重放；不扩第二WAN、共享预算、Wi-Fi或autorate。

## NSS82历史状态

# 当前状态

更新：2026-10-05 17:05，北京时间。最新NSS82；常驻仍NSS68，实验NSS均已撤销。

**受控真实TCP＋UDP完成两次完整单WAN A→B→A2。相同约18Mbps的客户端吞吐下，softirq为9.65→4.31→9.48%，相对两段软件均值下降54.97%。32Mbps发送负载下bulk丢弃143、RT零丢弃，NSS段UDP213/213收到回复。工程闭环已通过，300Mbps和真人CS2收益尚未验收。**

见 [实测汇总](../evidence/nss82-mainline.json)、[五个现场案例](../evidence/nss82-trials.json)、[相同18Mbps对照](../evidence/nss82-matched18.json)、[32Mbps拥塞观察](../evidence/nss82-saturated32.json)、[终态审核](../evidence/nss82-final-audit.json)。

- 用户新授权：工程调试使用自有端点的受控真实TCP＋低速UDP，不再把Steam下载和CS2对局作为每轮硬前提。真人CS2保留为最后集中游戏指标/体验验收，不把echo当游戏指标。
- 永久分类器未改、未重装。4859/17139连续；config581b5d46…c791d7，原完整审核source1.15秒通过。ECM关闭全零，无事务/stage/state/实验模块；保护配置、认证、PBR、NAT、十个生产队列恢复。
- 79在WAN5、82在WAN2分别成功，均一次只有一个WAN、一TCP一UDP；不是两WAN同时扩大。真实自动BULK/RT分类、学习前tag、firmware bulk/RT tag、ct mark/NAT/出口粘性、续租、精确撤销与0→2→0均通过。
- 32Mbps轮A/B/A2实际吞吐14.90/17.16/18.08Mbps，不同负载，不能引用其CPU降幅作收益。所有time_squeeze和softnet drop增量0；短窗不能证明高负载稳定。
- 80一次TCP达到450MiB有限上限提前退出；另一次完整三段但末尾ACK计数差1包/60字节拒绝。81初始计数差1包/1500字节拒绝。82统一在五个getter位置只允许一次这两种精确偏差重读，第二次原严格getter必须通过。实际82用了TCP-down分支；ACK新分支仅17项目标RAM通过，不冒充现场触发。原失败保留。
- 自有UDP端点独立180秒防火墙恢复基线、临时规则0、服务已退出/端口关闭；客户端达到字节上限后退出，独立精确guard通过。没有新游戏下载、购买/卸载、桌面/HUD改动。原始端点连接、密钥、nonce、CT、checkpoint和完整实际输入留本地。
- 下一步直接提高单WAN受控预算、验证更接近实际WAN速率的同负载收益与拥塞行为；之后集中一次真人CS2验收。不要再重装分类器、重放旧准备或同时扩第二WAN/共享预算/Wi-Fi/autorate。

## NSS78历史

更新：2026-10-05 14:56，北京时间。最新记录为NSS78只读诊断；实验入口仍是NSS77，常驻仍NSS68。

**轻载下已直接观察到NSS77需要的准备时间窗口。当前Steam下载完成、CS2在菜单，没有真实同WAN连接对；没有新的NSS写入或A/B。下一步只做一次真实有负载的77闭环，不再重复准备。**

见 [本轮诊断](../evidence/nss78-mainline.json)、[终态审核](../evidence/nss78-final-audit.json)、[两份新增源码](../evidence/nss78-source-proof.json)。

- 16.08秒、154次读取、6个实际分类发布。发布延迟0.27–0.32秒，查询间隔2.99–3.01秒；64次来源age<1.65秒，82次age<2秒。分类快照只有1–3条，不能外推到300Mbps负载。
- 7次观察到core sleep出生age≤200ms，其中2次同时满足初始来源预算；只是时间重叠，不是完整身份、分类、mark/NAT或真实gate准入证明。
- 新的两次原完整审核通过，常驻4859/17139、config581b5d46…c791d7未变。14:56:23 source3.67秒，ECM关闭全零，无事务/stage/state/实验模块。
- Steam队列无待下载大文件，RDR2完成，网络/磁盘均0bps；游戏菜单可见，实际0游戏候选/0Steam bulk/0同WAN对。本轮仅显示Steam窗口，没有新增下载、启动对局或改HUD。前一轮Esc后的完整客户端恢复仍未补证，当前菜单观察不覆盖旧记录。
- 未调用77的aba；355项绑定和已完RAM证明保持，不重放。没有CPU/softirq、time_squeeze或真人游戏收益结论，也没有新增回滚试验。
- 原77 runtime原字节冻结，新增2份白名单源码、累计992。原始运行数据、core-guard原文和桌面内容留本地，未提交上游Issue/PR。

## NSS77历史

更新：2026-10-05 14:21，北京时间。最新为NSS77；以下68及更早为历史。

**真实连接和两类加速的功能历史证明仍成立，当前瓶颈是控制器准备时间与分类有效期不一致。本轮只有部分B，完整同负载闭环仍未通过。最新修正已完成目标RAM检查，尚未现场测试。**

见 [实际轮次](../evidence/nss77-mainline.json)、[终态原完整审核](../evidence/nss77-final-audit.json)、[新源码](../evidence/nss77-source-proof.json)。

- 常驻仍是 `work/nss68/deployment-latest.json`，配置 `581b5d46c9d3772ccd94f5f36510bccf665899f210c43b4deaa5155067c791d7`。本轮没有重装分类器或改变生产配置；worker4859/guardian17139，14:21 source1.89秒、ECM关闭零计数，无事务、暂存、state或实验模块。
- NSS71真实A5.17秒、B1.56秒，ECM2；B未达五秒并因续租过晚停止，无A2。LAN4约336/326Mbps、softirq52.03/50.17%、squeeze38/5，窗口长度不同，不是CPU收益。
- 73/74失败帧里选中Steam TCP不在同源完整分类快照，游戏UDP仍身份/mark/NAT/WAN/tag正确。不是已证明CT消失或分类器故障。75把最终精确TCP选择移至checkpoint下载与编译之后、独立stage之前，原游戏连接和单WAN范围固定。
- 75软件A5.06秒/11帧完成，最后学习余量2.68秒不满足3秒。76把耗时getter移至最终分类证明之前，保留六秒source/native、3秒学习、1.2/1.5秒core、20Mbps和45秒owner；实际失败发生在更早initial ready通过age2.94秒之后，未到A。
- 77只修正initial ready准备预算为age<1.65秒，使后续原标签age<2秒门槛有余量。355项绑定，9目标RAM检查和完整fast语法通过；IO/时钟/分类器模拟，**没有77现场stage/加速证明**。76的getter顺序也没有取得新的实际B证明。
- 本轮本地测试生成错误均保留原raw，修正之后才核验；不作为源码/内核缺陷。69可选stat EOF仅夹具复现，原现场没有具体EOF/PID，不能判定现场根因。
- 客户端通过官方死斗产生真实UDP，助手闲置，未取得真人体感。HUD有保存但不完整对应B，条件显示隐藏值不能记为零。75下载暂停与菜单/HUD恢复单独通过；最后76下载已完成、验证文件仍运行。用户物理Esc停止桌面操作，已停止UI并撤下精确任务guard，不能声称76最终菜单/HUD已恢复。
- 原68 runtime按字节保存，新增122份白名单源，累计990。原始CT、端点、截图、checkpoint、凭据和二进制均留本地；没有提交上游Issue/PR。

## NSS68历史

更新：2026-10-05，北京时间。最新为NSS68；下方67及更早为历史。

**发布候选已实际长期保留，新的257项入口已经绑定同一个committed部署，现场原完整准入/恢复审核通过。NSS仍关闭；真人同负载闭环尚未验收。**

见 [本轮实测](../evidence/nss68-mainline.json)、[新入口绑定](../evidence/nss68-entry-binding.json)、[终态审核](../evidence/nss68-final-audit.json) 和 [调用位置](PUBLICATION_ENTRY_HANDOFF.md)。

- 当前部署 `work/nss68/deployment-latest.json`，config `581b5d46c9d3772ccd94f5f36510bccf665899f210c43b4deaa5155067c791d7`，32,019字节worker SHA `40169ce6c8e866cc989c651b24d435777bc422bf10f67c58f5e9ab033e7f3828`。旧47/49引用只作历史，未覆盖。
- 一个checkpoint下载/SHA/gzip，独立480秒stage和180秒生产undo写前核验；原完整持锁审核source2.49通过后远端commit、配置/worker/pointer读回验证，候选留驻，常驻健康守护保留。本轮没有再测自然180秒撤销；66/67自然恢复证明保持。只按owner/inode取消已提交后的passive stage。
- 入口 `work/nss68/real-session.mjs` 原241项全部保留，新16项、共257，17绑定检查通过。分类读取、原完整审核、stage共同使用新committed部署；原Lua消费者、stage/payload与1/2/6/9秒、200ms child、20Mbps、一TCP一UDP、45秒owner均不变。实际只读准入source1.46秒、同producer恢复审核1.26通过，未运行新NSS stage，不能称高负载gate已验收。
- 10:32:50–52候选17138自然退出，日志为 `tc child cleanup not proved`，apply256、4.35秒。原47相同TC监督代码也有历史apply失败；该次发生在本轮恢复下载之前。只有边界证据，没有具体tc命令、child PID和阻塞栈，不能归因发布改动、下载或内核。自动恢复后23634/17139，最新准入/恢复同producer，长期稳定未验收。见 [监督记录](ISSUE_TC_SUPERVISION.md)。
- 现有暂停的黎明杀机恢复，界面瞬时312Mbps后回到暂停；真实4秒仅2.879Mbps/425pps、busy34.91/softirq7.46/squeeze0；实际审核窗0.587Mbps，未形成300Mbps对照。没有CS2、HUD、真人或NSS CPU收益。暂停原因未确认，不称助手主动暂停；观察到暂停和0bps才取消独立360秒客户端守护。
- 10:37:28原完整终态审核source3.24通过，ECM关闭全零，无事务/stage/state/实验模块，五WAN认证/PBR/NAT/十个生产qdisc与保护配置保持。23份白名单源累计868，12份完整私有运行输入和257绑定输入冻结；旧67runtime原字节保留。
- 下一步直接使用新68入口做一次集中真人CS2+现有下载同TCP/UDP、单WAN可比A/B/A2。新轮次先读实际worker/guardian/producer；实验期间producer更换必须拒绝并精确恢复。不要再试装相同publication、重放旧准备、装新游戏或扩WAN。

## NSS66–67历史

更新：2026-10-05，北京时间。最新为 NSS66–67；以下 NSS65 及更早章节是历史。

**发布候选已在真实 Steam 372 / 367 / 385 Mbps 窗口运行，高负载期间两次原完整审核 source3.62 / 4.41秒通过。两轮独立180秒自然撤销精确恢复。常驻仍47、ECM关闭全零；这不是新的NSS转发或CPU/真人收益验收。**

见 [NSS67实测](../evidence/nss67-mainline.json)、[实际窗口](../evidence/nss67-pipeline.json)、[最终审核](../evidence/nss67-final-audit.json)、[NSS66前一轮](../evidence/nss66-mainline.json) 和 [入口接续位置](PUBLICATION_ENTRY_HANDOFF.md)。

- 两轮各一个checkpoint，下载/SHA/gzip通过；各自独立480秒stage和独立180秒生产守护写前确认，再只改32,019字节publication worker及config.files/事务身份。四模块、分类策略/学习、PBR/NAT、生产根qdisc、原完整字段与1/2/6/9秒来源/6秒runner均未变。
- NSS66实际候选两窗209.06 /147.86Mbps；原完整审核source0.74 /1.74秒通过，不能拿Steam331.7Mbps界面峰值当整窗300Mbps。前两公共负载探针403/429失败保留，429后停止不重试。
- NSS67三个候选四秒窗371.50 /366.78 /385.08Mbps、30.7k/30.3k/31.8k pps；busy84.51 /78.70 /82.36%，softirq60.72 /51.89 /55.77%，squeeze+11 /0 /0。含观察器成本、负载未控制，不构成CPU因果对照。候选完整快照实际145–285条；审核与四秒流量窗相邻，不是同窗。
- 候选worker31721/guardian31722/producer连续，轻载/启动审核source1.63，以及两次高负载期间原完整审核3.62 /4.41秒，全部保留原6秒限期。支持本次高负载publication可运行，不能保证所有峰值、长期恢复或新NSS入口成功。
- NSS66/67各保留一次到期后候选context审核拒绝：生产独立期限已过、原配置已恢复，候选SHA不符，在配置断言即拒绝；不是source超时。失败输出不覆盖，之后恢复后的原审核通过。NSS67失败窗口仅10ms，计数统计不作性能证据。
- 两轮均未发控制器回滚命令，180秒自然撤销精确恢复旧worker/config/指针及四模块；之后精确owner/inode取消stage，不声称该stage自然480秒到期。NSS67恢复后同窗原完整审核314.06Mbps/source5.97秒通过，距原6秒仅0.03秒，不能保证稳定，也不是与候选的同负载比较。
- 01:09最终完整保护审核/清理通过，worker9454/guardian9455/source2.22秒，常驻47/config478818…a900，ECM关闭全零，无事务/stage/state/gate/qdisc模块；不是旧20030/20031连续实例。
- 已授权Steam库内负载：Disco Elysium 8.7GB自然完成；首个360秒客户端守护确实自然执行精确Steam实例-shutdown。随后黎明杀机放D盘（要求61.01GB、可用298.21GB），短测到17%已暂停，网络/磁盘0bps，守护随后取消，317KB旧安排未操作。无购买/卸载/游戏启动/CS2/HUD/真人体验；部分下载保留暂停。
- NSS63入口241项保持，未新绑候选入口或放行ECM；本轮publication试装不是NSS准入资格。两个保留部署与消费者/审核/stage的实际context需统一绑定后，才集中做现有暂停下载＋真实CS2的单WAN可比A/B/A2。
- 22份新增白名单源/累计845，14份实际完整运行输入仅私有冻结；旧65/runtime原字节留存，旧64及更早证明保持。未重跑旧36/29或99/13，未提交上游。报告源验证通过，浏览器渲染未核验。

**下一步只做候选实际保留部署与NSS入口的精确重绑定，再集中一次真人CS2＋现有暂停下载的可比A/B/A2。** 不再重复轻载试装或大游戏准备，不重装分类器、放宽门槛、扩第二WAN/共享预算。

## NSS65历史

**完整JSON发布候选已实际短时运行，两次原完整审核通过；独立180秒自然撤销精确恢复原worker/config/版本指针。常驻仍47，ECM关闭全零。高负载发布、整机CPU与真人闭环仍未验收。**

见 [现场试验](../evidence/nss65-mainline.json)、[自然发布窗口](../evidence/nss65-pipeline.json)、[恢复后原审核](../evidence/nss65-final-audit.json) 和 [冻结源](../evidence/nss65-source-proof.json)。

- checkpoint下载/SHA/gzip通过；独立480秒暂存守护与独立180秒生产撤销在写前分别验证，生产守护PPID1、命令/启动身份/boot/checkpoint/deadline均符合原条件。没有控制器主动回滚命令，自然到期恢复通过。
- 只替换32,019字节publication worker及其config.files/事务身份，其余四个模块未写入；分类策略/学习、PBR/ct mark/NAT/gate、完整字段/原审核及全部原期限不变。只发生分类器的试装/恢复restart，未重装整套分类器、重建十个生产根qdisc或开放NSS。
- 候选期间同worker9414/guardian9415/producer，sequence16→37，两次原完整持锁审核source2.69/1.78秒。之后精确旧worker/config SHA、原四模块SHA与版本指针核验，恢复后00:04完整审核/清理通过，worker20030/guardian20031/source2.43；不是旧实例连续。
- 两个四秒候选窗及一个恢复窗只有0.025/0.031/0.018Mbps，pps11.5/17.6/8.2、squeeze均0；busy16.50/15.21/21.11%，softirq4.61/0.13/5.12%，背景负载不匹配且包含观察器成本。完整周期首次可见约0.77/0.73/0.85秒，仅观测界限，不能比较CPU收益或声称高负载发布修复。
- 生产自动恢复已证明后，精确owner/inode取消本轮暂存，无事务/stage/state/gate或qdisc模块；不声称该stage自然480秒到期。候选未留驻，常驻47配置478818…a900不变，ECM全零。
- NSS63入口241项保持，没有为临时候选创建新NSS入口绑定，也没有NSS加速、真实Steam高负载、CS2 HUD/真人体验或可比A/B/A2。本轮不重跑旧36/29及99/13、不操作游戏GUI或新下载。
- 8份公开白名单源码冻结/累计823，另8份实际owner/完整输入原字节仅私有；旧64及更早runtime按字节保留，未提交上游。报告源检查通过，浏览器渲染未核验。

**下一步直接沿用已通过的单项试装/精确恢复路径，做真实高负载publication→原完整审核；在实际候选输入正确绑定后集中单WAN同流同负载A/B/A2。** 不重装/重放已完准备、用新游戏维持准备或扩WAN/共享预算。

## NSS64历史

**常驻仍 NSS47，ECM 关闭全零。完成完整字段一致的 JSON 发布候选：真实319条快照编码 CPU 179.06→136.22 ms（−23.92%），目标精确32,019字节编译通过，尚未安装。没有新增NSS放行、整机收益或真人闭环。**

见 [本轮](../evidence/nss64-mainline.json)、[完整编码](../evidence/nss64-encoding.json)、[规模测量](../evidence/nss64-scale.json)、[被动链路](../evidence/nss64-pipeline.json) 和 [问题候选](ISSUE_JSON_PUBLICATION_COST.md)。

- 原NSS63失败：query→发布时间标记3.84秒，提示消费完成约5.47秒；交接0.29秒、哈希0.35 / journal0.03 / selector0.51 / 完整解析0.76秒，最终source7.41>6。标记在编码前采样，不是rename；不能将之后全部时间归于JSON。
- 最新目标RAM36投影/29完整编码案例通过，包括共享引用、循环/错误值/键拒绝、slot map和未知字段。不同组不宣称唯一独立案例总数，旧99/13未重跑。三对计时用同一冻结真实内存夹具；不是高网络负载或整机A/B。
- 仅编码规模128/256/512/1024条：旧29.96/64.54/156.96/422.87ms CPU，分块23.77/55.39/108.93/198.18ms，完整解析字段一致；投影CPU不在此组内。是离线形状重复，不是实际CT/准入资格。上游JSON-C线性visited查重与趋势相符，目标二进制精确commit未确认。
- 候选 `work/nss64/candidate-worker.lua` 只改完整快照JSON边界，非快照序列化和其余worker字节不变；全部字段/原完整审核、分类策略/学习、PBR/ct mark/NAT/gate、所有期限不变。目标SHA精确编译，未执行watch、安装或绑定新NSS入口；当前仍NSS63/241项。
- 首次2048组合模拟六秒runner返回124；观察器初版请求不支持时长，在执行Lua前返回2。原失败保留，没有提高六秒上限。随后分拆和四秒自然观察通过；没有生产配置写入、checkpoint或新回滚试验。
- 自然4.03秒：LAN4 0.023Mbps /18.11pps，busy17.04%、softirq3.21%、time_squeeze+0，含观察器成本。两个完整周期query→可见约0.63–0.86秒，stamp→可见约20–80ms观测窗。没有高负载/HUD/体感或同负载转发结论。
- 23:15原完整审核/清理通过、source2.61秒，同worker20682/guardian5412/producer，NSS47/config不变。ECM全零，无事务/暂存/state/实验gate/qdisc模块。未操作游戏GUI/新下载；未刷新客户端Steam/HUD，旧客户端状态不当新验证。
- 20份源码冻结、累计815，旧NSS63及更早runtime原字节保留，完整私有数据不上传。只证明最新native合同和编译，不增加准入/高负载稳定资格。报告源检查通过，浏览器渲染未核验；未提交上游。

**下一步直接做publication边界单项短测：checkpoint、独立超时撤销，保留原完整审核与期限；原47能精确恢复后再测真实高负载发布与可比单WAN A/B/A2。** 不重装整套分类器、重复已完准备、用新游戏维持准备或扩WAN/共享预算。

## NSS63历史

**常驻仍 NSS47，最终 ECM 关闭全零。本轮 NSS56 完成真实 WAN1 CS2 UDP＋Steam TCP 的 A→B，ECM 0→2→0、bulk/RT leaf、完整 mark/NAT/WAN affinity 与精确恢复正确；A2 未完成。已取得 B 段实际 HUD，但吞吐不匹配、没有真人操作，CPU / 游戏收益仍未通过。**

见 [本轮汇总](../evidence/nss63-mainline.json)、[实际阶段](../evidence/nss63-partial56.json)、[客户端](../evidence/nss63-client56.json)、[失败与恢复](../evidence/nss63-attempts.json)。

- 最新实验入口 `work/nss63/real-session.mjs`，241 项来源绑定。已修正发布读取竞态、独立语法传输尺寸、极窄计数重读、提示返回契约和短命子进程读取；依赖实际导入也已核验。它没有替换常驻分类器；最新现场因完整来源 7.41 秒超过原 6 秒在 checkpoint 前拒绝，不能称高负载闭环修复完成。
- 五次单 WAN 临时暂存：NSS56 为 WAN1，随后四次为 WAN2，始终一次一个 WAN。每次先下载 checkpoint、核验 SHA/gzip，再确认独立 45 秒守护身份。仅 NSS56 放行 ECM；其余均未放行。全部精确撤销、暂存清理，四次即时原完整 AFTER 通过；NSS61 第一次 AFTER 来源过期，暂停下载后的原完整恢复审核另行通过。不是五次自然 45 秒到期试验。
- NSS56 两段各 11 帧 / 5.04、5.03 秒：LAN4 303.75→261.64 Mbps，选中 WAN1 57.87→31.23 Mbps，softirq 52.77→47.66%，busy 75.98→71.21%，time_squeeze +42→+20。总吞吐跨度 14.90%、选中 WAN 跨度 59.79%，均超过可比条件；加速子组仅 20 Mbps，主要字节仍走 fallback。较低 softirq 不能归因于 NSS。
- B 段实际 bulk/RT leaf 增加 4755 / 549 包，bulk drop 7、RT drop 0；两方向 NAT/mark 与 WAN1/物理 WAN/LAN4/br-lan 均由原 ECM 解析器核验。一次续租与精确撤销通过。队列计数覆盖建立 / 撤销边界，不能代替客户端 loss。
- 时钟映射不确定性约 100 ms，各段中央 5 张完整游戏截图逐张检查：A ping 16 ms、下行 jitter 2–3 ms、loss 0.1–0.5%、Miss 0.8%；B ping 16 ms、jitter 1–2 ms、loss/Miss 均 0。是助手进入在线服务器闲置，HUD 为滚动/峰值显示，没有 A2、真人体验或改善结论。
- 12 个实际控制器案例均保留原失败；5 次有暂存、1 次开 ECM、1 次 A+B、另 2 次只有 A。NSS62 另有本地缺少 payload 导入错误，连接路由器前发生；NSS63 修复依赖拷贝。原 200 ms child 出生条件、20 Mbps、TCP/UDP 各一条、45 秒 owner、source/epoch 期限均未放宽。
- NSS54/55 发布 join 目标 RAM 分别 13/14 案例；NSS57/59 极窄计数见证各 7；NSS58 notice 10；NSS60 metadata 10；NSS61 契约 14 本地断言；NSS62 子进程读取 15 目标 RAM 案例，NSS63 同字节复用。旧 99/13 不重放或重新计数。模拟、只读、真实转发分别记录。
- 常驻 worker 从 5411 自然换为 20682，guardian 5412 保持；没有主动 restart/crash，原因未证明。最终 21:26 原完整保护审核通过、source 4.56 秒、14 个 owned selector、配置未变，ECM 全零，无事务/暂存/state/gate/qdisc 模块。不能写成全程同实例或高负载长期稳定。
- Steam 测试负载最终自然完成：DOOM（2016）19:44；巫师3/Hades 21:12；Disco Elysium 21:13。之前暂停的队列自动接续，不能写成最终仍暂停。最终网络/磁盘均 0 bps，无即时下载；未购买、卸载、启动新游戏或重下 DOOM Eternal。CS2 已退出服务器、三项临时 HUD 恢复。
- 144 份新增可读源码冻结，795 份仓库源码累计；完整实际输入、CT/socket、配置、模块、截图与凭据留本地。离线报告曾误把缺失 wanAfter 字段默认为 WAN1，实际 selected 验证发现并更正四个 WAN2 案例，原 v1 留私有；运行时选择/准入未受影响。NSS53 runtime 原字节保留。

**下一步只定位并缩短高负载 classification→完整 snapshot 发布及原持锁审核的延迟。** 不重装分类器、不重放旧准备、不要求用户长期挂机，不用继续下载安装新游戏维持准备。新代码单变量核验后再取得完整、负载可比的 A/B/A2；只有性能与真人闭环通过才扩第二 WAN 同时加速、共享预算、Wi-Fi/autorate。

## NSS53 历史

见 [本轮汇总](../evidence/nss53-mainline.json)、[真实负载时序](../evidence/nss53-phase-load.json)、[拒绝诊断](../evidence/nss53-diagnostics.json) 与 [新入口](../evidence/nss53-entry-binding.json)。

- 常驻引用、配置和保护设置未变。开场与 18:38 收尾原完整持锁审核通过，worker / guardian / producer 连续，序列继续前进；ECM 停止全零，无事务、暂存、实验 state、gate / qdisc 模块。本轮没有路由器实验配置写入、checkpoint 或回滚试验；只读无需恢复生产配置。
- 新入口 `work/nss53/real-session.mjs`：140 项基础＋19 项新绑定，共 159 项。NSS52 进程候选字节相同；原 `waitFresh`、200 ms 出生条件、source / owner / epoch 期限、20 Mbps、一 TCP＋一 UDP及恢复决定保持。来源绑定与适配器差分审核通过，旧 99 / 13 项复用，不重新计为本轮执行。它是实验入口，未替换常驻分类器，也未在本轮完成原生 NSS A/B。
- 用户授权由助手找新的库内下载，选择未安装的 DOOM（2016）。D 盘当时 218.25 GB 可用，下载显示总 59.3 GB，暂停前约 6.1 GB；已确认暂停、网络 0 bps。未购买、卸载、启动新游戏，未重下完成的 DOOM Eternal；本轮未操作 CS2 GUI 或取得 HUD。
- 两组实际完整 consumer `candidates / readContext / inspect` 回调、每组三次 `waitFresh`，6/6 通过。LAN4 365.65 / 353.88 / 330.47 / 300.99 / 297.43 / 293.94 Mbps，约 24.4k–30.3k pps；四次达到 300 Mbps。新子进程接纳结果中的最大出生年龄 180 ms，consumer 读取最大约 180 ms，含读取的回调最大约 200 ms。uptime 约 10 ms 粒度、余量有限；guard 未被改动或 signal。CPU / softirq / time_squeeze 在证据中保留，包含 profiler 开销，各窗不是相同 offered load，不是 NSS 性能 A/B。
- 这将 NSS52 候选从“只有轻载”推进为六个真实负载短窗下的发现验证。历史旧 helper 0/3、NSS51 1/3 保持；不同窗口不构成整机因果 CPU 比较，更不是完整高负载故障恢复或长期稳定证明。
- 源码发现 `classification.json` 是 bulk＋已准入 RT 投影。投影缺失不能直接证明 CT 不存在、退出或改类。新诊断保留原拒绝帧；仅最终拒绝后至多读一次完整 `snapshot.json`，producer / 全部 query 来源相同、原 consumer 校验通过才记录完整分类。来源不同保持未知，不新增 conntrack 查询，不改变准入、重试或恢复。
- 本地 60 断言（原 21 重放＋新增 39），目标原生 JSON helper 14 项通过。实际只读 ready 使用合成不存在键：轻载同源完整帧确认不存在；真实下载中完整帧来源不同，按预期记录未知。完整适配器本地模拟、目标 helper 和目标 ready 三种证据分开，均不授予真实连接加速资格。
- 实际应用只读核查：24 条 Steam bulk、0 条 CS2 对局 UDP、0 同 WAN 配对，原入口默认等待，未暂存或放行 ECM。没有新 bulk/RT leaf、CAKE tin、游戏 jitter/loss/Miss 或体感，不把缺失填零。
- 24 份源码按白名单冻结，原完整私有输入、CT/socket、配置、原始进程、截图与凭据留本地。NSS52 runtime 按原字节保存在 [历史运行记录](../evidence/nss52-runtime.json)。传输/夹具/诊断投影与汇总字段修正均有本地记录，未提高传输或时序上限、未触发生产变更。没有上游提交。

下一步使用 NSS53 已绑定入口，待自然真实单 WAN CS2＋Steam 配对后先对齐 HUD，再按原 checkpoint / 独立 45 秒回滚做同负载 software→NSS→software。可以恢复现有暂停下载，无需重装分类器、重复旧准备或继续下载整款游戏。未通过前不扩第二 WAN / 共享预算 / Wi-Fi / autorate。

## NSS50–NSS52 历史

见 [本轮汇总](../evidence/nss52-mainline.json)、[高负载只读时序](../evidence/nss51-phase-timing.json)、[实际软件负载](../evidence/nss50-partial-software.json) 和 [软件客户端记录](../evidence/nss50-client-software.json)。

- 常驻引用与配置哈希不变：`work/nss47/deployment-latest.json`，`478818d553903aa859c853cab99383e038d4d325f500d68843ffff8b7517a900`。没有安装新的分类器、内核、driver 或 firmware。NSS49 历史 runtime 精确保存在 [nss49-runtime](../evidence/nss49-runtime.json)。
- 用户授权下载库中 DOOM Eternal，由助手控制现有 Steam / CS2。下载于 17:14 完成 79.2 GB、最终速率 0，没有启动 DOOM、购买、卸载或重新下载；CS2 已退出服务器，三项 HUD 显示恢复。是助手在线闲置 / 观战，没有真人操作或主观体验。
- 六次实际尝试：选中分类拒绝、持锁来源 6.47 秒、历史服务 PID 基线拒绝、两次 core-sleep deadline、再一次选中分类拒绝。四次 checkpoint / 独立 45 秒守护 / 单 WAN 临时暂存后精确恢复，完整 AFTER 和最终清理通过；两次暂存前拒绝。全部未放行 ECM，不能称新的 NSS A/B/A2。
- NSS50 只允许实验前健康的 sing-box core / guard PID 与历史安装基线不同，命令、服务集合和运行状态完全相同；固定本次 epoch 后任何漂移仍拒绝。24 项本地边界、新 128 项输入与原完整目标只读审核通过。不推断 PID 变化原因，也没有重启这两个服务。
- 两次仅软件 A 各 11 帧、5.08 / 5.05 秒：LAN4 227.35 / 267.64 Mbps，WAN5 46.25 / 76.29 Mbps，softirq 48.31 / 47.72%，time_squeeze +0 / +1。共同 LAN4 NSS 队列树已经暂存、ECM 全零；不是未暂存的原始基线，负载不同不能彼此作因果比较。没有 B/A2/有效 CAKE tin 对照。
- 实际 HUD 对应 A 的 4 / 5 帧经时钟锚点、完整游戏场景和人工逐帧检查：ping 12 ms，下行 jitter 2–4 / 1–4 ms，loss 0–0.1 / 0–0.8%，Miss 0–1.2 / 0–0.4%。滚动 / 峰值不是独立瞬时采样；没有 B，也没有真人体验，不能声称 QoS 改善。
- 只读 profiler 定位：原 helper 在目标子进程换代后读全机 stat/argv/wchan，约 350 Mbps 实际下载下 0/3 通过，最长回调 740 ms；暂停下载 3/3。NSS51 只发现固定 guard 的直接子进程，22 项模型 / 两次实际只读 / 140 项绑定 / 原完整审核通过。但实际下载只读仍仅 1/3 通过，不是稳定修复。随后真实入口在选中分类断言拒绝，没有到 B。
- NSS52 只把无关进程 stat 的完整字段拆分改为父进程提取。原 22 模型重放＋12 差分、两次轻载只读通过；10,000 遍纯解析 0.623336→0.050266 秒，约 91.94%，不是整机收益。等待源码字节、200 ms 出生条件和全部来源 / owner 期限保持。**候选未安装、未绑定生产入口、无高负载资格。**
- 17:30 最终原完整持锁审核通过，worker / guardian / producer 与先前 NSS49 相同，ECM 停止全零，无事务、暂存目录、实验状态或模块。连续同实例不证明完整高负载 crash / 长期稳定。NSS50/51/52 分别 15/14/7 份可读源码冻结，实际 128/140 项输入副本仍私有，源码冻结不授予新生产资格。

下一步先用下一次真实下载窗验证高负载进程发现稳定，补失败帧具体分类诊断，再一次取得同负载软件→NSS→软件与客户端 HUD。已有分类器安装与旧 99/13 项检查不重复准备；不扩第二 WAN、共享预算、Wi-Fi 或 autorate。详见 [计划](PLAN.md) 与 [本地问题记录](ISSUE_CORE_SLEEP_DISCOVERY.md)。

## NSS47–NSS49 历史功能与缓存证明

见 [本轮汇总](../evidence/nss49-mainline.json)、[实际对照](../evidence/nss49-actual-aba.json)、[原失败](../evidence/nss49-failed-attempts.json)、[客户端边界](../evidence/nss49-client-boundaries.json)。

- 当前常驻引用 `work/nss47/deployment-latest.json`，配置 `478818d553903aa859c853cab99383e038d4d325f500d68843ffff8b7517a900`。NSS46 三项修复保留，NSS47 仅加每次发现重置、各 1024 项纯地址缓存，CT 实例/zone/mark/NAT/计数不缓存。4550 差分样本、目标 527 行每版本 80 次解析与 3 个完整快照一致，解析 CPU 4.740→3.489 秒（26.4%），不是整机收益。第一试装独立 180 秒自然恢复，第二次另建 checkpoint/回滚/完整审核后保留，暂存守护已退出。另一约 1.9% 扫描候选未安装。
- NSS46 原入口真实应用对已找到，但39次观察的精简发布延迟 1.03–1.26 秒，初始 <1 秒拒绝。NSS48 新 cache 绑定满足初始 0.72 秒，却在 0.3 秒标签窗 TCP 全零、UDP 正确时拒绝；没有错误 tag 证据。两次暂存/独立守护、精确恢复和原完整审核通过，均未放行 ECM。
- NSS49 入口 `work/nss49/real-session.mjs` 绑定 121 项输入、99 项本地案例、13 项目标 RAM 模拟。仅初始无包等待至多 1.2 秒，受原 epoch / owner 余量约束；错误 tag 立即拒绝，正计数才可放行。初始 <1 / 预学习 <2 / 软件 <6 / 发布 <9 秒、20 Mbps、一 TCP＋一 UDP、45 秒 owner 保持。实际成功 getter 1 probe / 0.16 秒，不能说扩等待导致本次成功。其余 NSS Lua 与 NSS48 字节相同；继承的 unchanged 字段不覆盖 helper 差异。
- 14:52–14:53，助手按授权恢复现有下载、进入在线死亡竞赛观战。真实 WAN2 一 TCP＋一 UDP、mark 0x20000，三段各 5.03 秒 / 11 帧，ECM 0→2→0。TCP downTag 0x8f050000 / UDP 0x8f060000、upTag 0，NAT、WAN affinity 2、LAN4/br-lan 层级正确，一次续租通过。完整控制器成功，不只是功能片段；没有真人操作 / 体感。
- LAN4 A/B/A2 167.90 / 193.94 / 170.86 Mbps；WAN2 66.31 / 83.86 / 66.02 Mbps；softirq 41.14 / 41.71 / 44.81%；time_squeeze +0/+1/+4，softnet drop 全零。总吞吐跨度 14.66%、选中 WAN 24.75%，超过预设 10%；offered load 也未证明相同。busy 62.35/60.69/60.99% 仅为观察，CPU 因果收益未验收，全窗未到 300 Mbps+。
- 建立至撤销约 5.43 秒 leaf 窗：bulk +11,531,555 B / 7635 包 / 13 drop，RT +644,562 B / 713 包 / 0 drop，fallback +130,118,774 B / 84,625 包。包含边界，非精确 B 净速率；RT 0 drop 不是客户端 0 loss。受控 leaf 约占字节 8.56%，软件 CAKE 保留未加速流 fallback。
- 38 张实际截图经 125 ms 往返锚点校准，A/B 无完整有效帧、A2 有 3 帧。缺失字段不填 0。第二轮 Steam 已完成，游戏候选1/bulk0，router/NSS 写前等待；部分截图前台遮挡，全部不用于验收。已退出测试服务器，没有为补负载购买 / 卸载重装游戏。
- NSS49 每次写前 checkpoint 下载/哈希/gzip、独立 45 秒 owner 身份通过；主动精确撤销，未触发新的自然 45 秒到期证明。WAN/mwan3、队列/tag/state/模块恢复，原完整 AFTER 审核通过。15:07–15:08 最终完整审核通过、worker 5411 连续、sequence645，ECM 关闭全零，无事务/暂存/模块。约半小时同实例不等于完整高负载故障恢复或长期稳定。
- NSS47/48/49 19/37/47 份可读源码冻结，实际完整输入副本留私有。原 NSS46 current-runtime 精确保存在 nss46-runtime，历史失败、RAM 模拟和新硬件证明分开。没有上游提交。

下一步使用已通过的 NSS49 入口补同负载客户端对照，不再重复分类器准备。提前同步 HUD，确认同一应用连接持续；功能、性能与真人体验分别验收。未通过前不扩第二 WAN 同时加速、共享预算、Wi-Fi 或 autorate。见 [计划](PLAN.md)。

15:34 补充只读核验：[退出游戏后的原完整审核](../evidence/nss49-post-game-audit.json) 通过，同一 worker 5411、sequence1189、source age1.73秒，ECM仍关闭全零。当前4个selector可能属于背景流，仅数量不能证明真实CS2旧流退出，也不增加CPU/游戏或长期稳定结论；之前15:07–15:08证明保持。

## NSS46 历史实装与资格

见 [本轮证据](../evidence/nss46-mainline.json)、[真实过期恢复时序](../evidence/nss46-fault-timing.json) 和 [新入口绑定](../evidence/nss46-entry-binding.json)。

- 当前常驻引用是私有工作区 `work/nss46/deployment-latest.json`，配置 SHA256 `f244567a5fea40b7259500271627a4fc22df4c7b4345958414d98fb60ffdeb12`。`work/nss39/deployment-latest.json` 已成为历史引用，不能替代当前状态。
- 先保留 NSS45 已独立验证的 backend 恢复初始枚举复用，再单独保留软件来源过期处理，最后单独叠加行数溢出处理。各次有 checkpoint、下载哈希/压缩核验、写前独立 180 秒回滚身份确认、目标语法检查和原完整保护审核。未改变 policy、CAKE 根队列、PBR、认证或服务架构。
- 一次真实 watch 观察仅延迟时间，连接元数据不改写。真实 apply 子进程保留原请求序列化、producer/PID/start/锁绑定，在来源年龄 6.27 秒时拒绝 batch；两个发布撤回、pending intents 精确清理，真实 recover 子进程 0.80 秒，同一 worker 继续新观察。是轻载真实故障证明，不是高负载恢复证明。
- 在无活动 worker 子进程并持事务锁时，精确 kill 一个空闲 worker；procd 在 7.56 秒恢复新实例、新鲜发布和健康 guardian。两个故障试装均在原 180 秒自然到期恢复四份源码、配置、指针及健康实例；480 秒暂存也自然清理。没有延长期限或扩大连接范围。
- expiry 保留观测开头三帧为旧 producer / guardian 预热；提交前新实例原完整审核通过。最终版本独立 35 帧观测全健康；随后 60 帧、29.61 秒自然轻载同一实例健康，来源年龄最高 3.17 秒。背景 RT 命中没有 CS2 socket 归属，不算游戏验收。
- 新入口 `work/nss46/real-session.mjs` 等待 before-software-baseline classification 后执行原完整审核。112 项来源绑定、99 项本地入口案例通过，目标等待来源年龄 0.30 秒，原完整审核来源年龄 0.70 秒。NSS 数据面 Lua 与已验证 NSS39 字节一致；原 NSS42 102 项入口保留不动。20 Mbps、一个 TCP＋一个 UDP、45 秒 owner 和原 1/2/6/9 秒门槛保持。
- 最终 13:49:55–13:49:56：worker 30050 / guardian 30051 健康，原完整规则与保护配置审核通过，ECM 停止且全零，无活动事务、暂存、实验状态或模块。last-error 来自受控 crash 试装临近期限退出，属于旧实例。没有当前 CS2＋Steam 配对，没有 NSS 写入或新的 CPU/游戏结论。
- 84 份本轮源码已冻结并按白名单导出。入口夹具路径/seed 绑定和故障摘要 JSON 重复引用问题已纠正，原失败输出保持；这些准备问题没有触发 NSS。源码冻结与入口资格、真实故障和真人高负载证据分别记录。

NSS46 当时的下一步已由上述 NSS47–49 推进；该轮原配置/入口是历史，当前来源以本文开头为准。

## NSS45 历史现场

见 [本轮证据](../evidence/nss45-mainline.json)、[轻载试装采样](../evidence/nss45-trial-timing.json)、[真实 query 子进程检查](../evidence/nss45-query-cleanup.json) 和 [本地恢复问题记录](ISSUE_CLASSIFIER_RECOVERY.md)。

- 开场只读日志确认此前 11:07:30、11:08:02、11:08:10 三次自然退出均为原 2048 行上限的未分类错误。没有主动 crash/restart 或制造生产溢出；开场原完整保护审核通过。
- 两项修复分开执行，彼此之间恢复 NSS39。第一轮只改变 backend 的恢复初始枚举，第二轮只改变行数溢出处理（worker/guardian/source 三份源码）。各有新 checkpoint，下载、哈希与压缩完整性检查通过；修改前核验独立守护进程身份和 180 秒回滚事务。
- 两次试装各 35 帧、约 17 秒轻载观测均健康，单一 producer，完整与精简发布的身份/decision/leaf/期限一致；原完整持锁规则与保护配置审核通过。背景软件 RT 命中没有 CS2 socket 归属，不能当真人游戏命中。
- 两次均自然到期恢复四份源码、配置、generation 指针和健康旧版本实例，随后原完整保护审核通过。接近安装到期时 worker/procd 重试按原期限拒绝继续工作；没有把 35 帧健康写成全 180 秒稳定。最终 last-error 是第二次受控安装期限退出，且不属于当前 worker；此前自然溢出错误仍保留。
- 空日志恢复复用已核验的初始读取一次；实际写前与写后检查保留，首次写后禁用缓存。24 个算法案例分别在新旧源码执行通过，未知写入者保持；目标三对只读空日志测量 60→40 次调用、平均 0.810→0.553 秒。未恢复真实 selector、子进程 CPU 未计入，不能证明高负载 6.18 秒问题已解决或整机收益。
- 行数候选 48 个本地案例与同例目标 RAM 重放、3 份目标语法检查通过；原 2048/524288 界限不变，不接受部分观察。7 个目标真实 query 子进程案例验证正常输出、2049 行新旧差异、字节溢出及未知错误拒绝，实际回收证明通过；查询参数/输出为合成，未运行真实 conntrack 命令或完整服务溢出故障。
- 软件来源过期候选保留 6 秒来源/6 秒 mutation/9 秒发布期限。34 个局部案例与 8 个实际 backend/ownership 日志交叉模拟在本地和目标 RAM 通过，过期发布撤回、已知规则精确恢复、未知写入者保留、新观察接续均通过模拟。应用子进程、队列 IO 和发布部分被模拟；候选未安装，完整子进程与高负载服务资格未通过。
- 独立本地案例总数 114；目标同例重放不再加作新案例。5 份语法检查及 7 个真实 query 子进程案例分开记。4 次恢复夹具修正、1 次日志夹具修正、2 次传输尺寸拒绝与 1 次本地路径正则拒绝均留存；这些准备失败没有生产变更，原尺寸/安全门槛未放宽。
- 最终 12:42:44–12:42:49 核验：NSS39 分类器健康、完整原规则/配置审核通过，ECM 关闭且全零，无事务、暂存、实验状态或模块；未检测到 CS2/Steam 下载连接对。没有新 fast path/leaf/A/B/A2/客户端 jitter/loss/Miss，未扩 WAN。53 份源码和脱敏证据已冻结；不是新 NSS 准入资格。

下一步验证真实 apply 子进程与既有期限内的完整恢复，再按单一变量逐步组合修复，核验 classification 提示后原完整审核的新入口。准备期间无需用户挂游戏或下载。两次实际轻载试装不能代替真人高负载生命周期与性能验收。

## NSS44 真人写前拒绝与后续证据

见 [本轮证据](../evidence/nss44-mainline.json)、[实际拒绝时序](../evidence/nss44-failed-admission-timing.json)、[后续轻载发布时序](../evidence/nss44-publication-timing.json)。

- 用户已进服并保留下载；新鲜应用归属找到 1 个 CS2 RT、23 个 Steam bulk 候选，选中 WAN1、完整 mark 均 0x10000、zone 0、同 NAT。这是连接归属证据，尚未进入原生加速出口校验。
- 未修改 NSS42 入口实际执行。102 份输入源码/证明冻结，原失败保持；写前等待 5.06 秒、39 次健康观测，完整发布 query→publish 2.91/3.01 秒，来源年龄 4.19–8.19 秒。未满足 <2 秒门槛，在 checkpoint/暂存前拒绝。没有 owner、WAN/队列/tag/gate/ECM 变更，没有 A/B/A2、leaf 或客户端指标。
- 开场原完整审核还因来源年龄 7.61 秒超过 6 秒而拒绝，原断言没有放宽。
- 10:41:17–10:41:23 观察到常驻 worker 的 `snapshot stale before write` / apply 子进程失败（3.79 秒）；首次精确 recovery 失败（6.18 秒、rawStatus 31744）。procd 自动启动新实例，guardian 实例保持；没有注入 crash 或手动重启，也没有证明只读观察导致该退出。高负载稳定性仍未通过。
- 源码确认：精简 `classification.json` 在软件规则应用前发布，完整 `snapshot.json` 在应用及可能审核后发布；NSS 消费者读前者，NSS42 学习前调度却等待后者。延迟的完整发布无法满足原 <2 秒等待门槛，这是已定位的拒绝机制；不是全部高负载故障已解决。
- 只读候选改为等待已有 before-software-baseline classification，然后执行未修改的原完整持锁/native 审核。年龄/调度/owner 全部不变。30 项本地检查通过；目标只读 hint 来源年龄 0.76 秒、原完整审核来源年龄 4.28 秒，通过且 ECM 关闭。候选未安装、未用于生产、没有新入口资格；它不修复 apply/recovery 超时。
- 后续自然轻载 27.15 秒、105 帧，LAN4 0.237 Mbps，compact/full 发布延迟 0.32–0.35 / 0.58–1.25 秒，softirq 2.23%、time_squeeze +0。未重新确认真人连接对，含观察开销，不能与此前高负载比较成 NSS 收益。
- 批量校验 12 个 payload 的未安装候选，目标只读 3 对交替测量约节省 33 ms，仍每次校验全部文件；不足以解决约 3 秒发布延迟，子进程 CPU 未计入。不是当前优先修复。
- 最终 11:01:58 新 worker/guardian 健康；原完整审核、配置/精确规则和清理通过，ECM 关闭且计数为零，无事务、暂存、实验状态或模块。首次恢复失败和旧错误日志仍保留，不能写成全程稳定。

下一步先修复并资格核验分类器 apply/recovery 和正确的发布等待来源，绑定新入口后再集中真人验收。用户无需继续挂游戏或下载，16 份只读/未安装候选源码快照不能授权加速。

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

这轮只读负载观测仍有效；后续按 NSS44 新发现先完成稳定性与入口资格，再使用 [单次真人验收记录](SINGLE_WAN_ACCEPTANCE.md)。

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
