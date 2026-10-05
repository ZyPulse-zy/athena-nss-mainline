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
