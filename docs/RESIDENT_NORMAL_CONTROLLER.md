# 当前入口：连续合格代

2026-10-08，取消健康代90秒退出和20分钟四次启动限制。合格流持续自动续租；分类/socket6秒新鲜度、native滚动120秒、guardian滚动180秒及失联撤销保持。实际RT mask2连续NSS 196.75秒／393采样校验／65续租，跨原90/120/180秒后主动Stop和完整恢复通过。

正常程序精确进程/socket归属、分类/预算/CT/NAT/完整mark/WAN affinity与未知默认拒绝保持。新流仍需要新代，不热插入旧epoch。原数据面/CPU证明复用；持续运行的日志仅保留32采样与16续租尾部及累计校验计数。[实现、实测与限制](RESIDENT_CONTINUOUS.md)

## 以下保留历史记录

# 当前控制：dev-i独立准入已集成并保留

原工作区使用 powershell -File work/resident-service-dev-i-20261008/service.ps1 -Mode Status / Stop / Start。现有手动任务仅启动参数更新，其它任务、权限、触发/重启/终止设置保持。当前进程运行、启动审核通过、准入未暂停；无合格流时ECM0，进程运行不当作当下NSS命中。

RT单独进入的实际90秒/ECM1/30续租和完整撤销已通过。独立最多2BULK＋1RT、同WANTCP允许，仍需原分类与预算/精确OS归属/CT/mark/NAT/affinity/pin/lease；新流进入新代，旧epoch不热插入。原每代90秒/20分钟四次及全部保护不变，不是永久全网NSS。[实测与限制](../evidence/resident-independent-admission.json)。

## 以下保留历史记录

# 当前控制：dev-h独立合格流常驻候选

原工作区运行 powershell -File work/resident-service-dev-h-20261008/service.ps1 -Mode Status / Stop / Start。任务Athena-NSS-Controller-Manual，仅启动参数变更，其它相关任务、权限、触发、重启和终止设置保持；进程运行与实际ECM分别核对。当前运行、BULK0/RT0、0新代，完整现场集成待自然合格负载。

任一合格BULK或已准入RT可独立进入；最多2BULK＋1RT，TCP无需不同WAN。新代仍严格原分类/归属/CT/NAT/mark/affinity/pin/tag/lease、fresh checkpoint及独立恢复；已启动epoch不热替换。没有合格流就等待；只有已证明无NSS且完整恢复的初始准入缺失可再等新源，未知失败暂停。每代90秒/20分钟四次，非永久全网NSS；新native本地资格已通过、硬件待验。见[事实](../evidence/resident-service-dev-h.json)。

## 以下保留历史记录

# 当前接续：dev-g已恢复自动观察，当前RT1／BULK0

2026-10-08 13:32只读快照：CS2 RT1，下载BULK0、组合0；控制器运行，准入未暂停，三次读取成功且来源序列推进，实际ECM关闭全零。使用 work/resident-service-dev-g-20261008/service.ps1 Status / Stop / Start，先核对状态，不重复启动。启动完整健康和两物理原队列全部选项/handle通过。下载保持，不操作游戏或制造流量，heartbeat仍暂停。

13:18完整分类和本机socket匹配已确认CS2 RT在WAN3，约197pps、1.26Mbps。旧RT0仅表示当时未匹配合格候选；早先快照缺记录的精确原因未证明，不能据此认定游戏无UDP或CT退出。dev-f 13:15另一次真实入口在Windows socket查询后source6过期，checkpoint/stage前退出；中间恢复审核拒绝原输出保留，最后完整审核和原物理队列恢复通过。

本批只修P2读取时序对P1准入的影响：首次分类只发现端口，Windows精确归属之后读取最终分类，分别保留source6和OS6，完整计入最终网络耗时；owner变化、query倒退及未查过端口仍拒绝。119入口＋61服务本地检查、实际Lua5.1语法、34 JS／2 PS通过。六份其它数据面Lua保持RC1、classifier.lua保持dev-f，分类/QoS/期限/checkpoint/独立恢复不改。仅切换已有手动任务启动参数，两个其它任务保持。

新候选现场只读来源3.04秒及当前1.23秒通过，完整90秒NSS集成尚未完成，游戏丢包P1仍待闭环。最短路径仅接续已有自然下载＋RT；缺合格组合则等待，不新增fixture、边界、CPU或QoS实验。见[本批事实](../evidence/resident-service-dev-g.json)。

## 以下保留历史记录

# 当前正常入口：dev-f

[入口生成器](../code/work/resident-normal-dev-f-20261008/materialize-normal.mjs)接续dev-e不同自然WAN排序和严格checkpoint前空候选等待。仅classifier.lua的stable辅助函数允许三个发布通道一次50ms内重读；其余分类／CT／mark／NAT／WAN／lease检查及六Lua原字节。104入口本地回归通过，原dev-e实际NSS3／54.07秒／18续租后中断已恢复；dev-f完整90秒硬件尚未完成。常驻使用[控制脚本](../code/work/resident-service-dev-f-20261008/service.ps1)，未知/进入后失败仍暂停，不把缺失投影当真实CT退出，不重复历史数据面/CPU证明。

## 以下保留历史记录

# 正常流入口和四代有界常驻协调通过

北京时间2026-10-08 08:10。沿用 RC1 已证明的数据面，接入正常本机进程/socket归属和当前自动分类；controller自身不启动游戏、下载或测试流。只有两条不同自然WAN的TCP BULK和一条已准入UDP RT可进入原三槽NSS，其它/未知/归属不明确流保持软件路径。

本批57项本地回归及15份源码语法检查通过，集中修复清理重入和部分启动目录登记等P2。七份数据面Lua逐字节复用RC1，没有重复五WAN、QoS或CPU实验。

预定四代各90秒、controller900–1200秒。实际状态 **COMPLETE**；控制器运行 **900.14秒**，完成 **4代**，NSS累计 **360.02秒**。每代独立下载/SHA/gzip checkpoint及写前恢复守护，完整撤销后才进入下一代。终态ECM关闭全零、五WAN健康、保护配置及两物理原队列全部选项/handle一致，端点规则和自有客户端残留0。实测明细见[结果](../evidence/resident-normal-controller.json)。

该集成由独立自有模拟器提供正常socket和连接轮换，未操作CS2/Steam；这是正常入口集成与有界协调证明，不声称第三方应用全面覆盖、连续15分钟NSS或默认永久常驻。

## 使用

原工作区运行 `node work/resident-normal-dev-20261008/controller.mjs inspect|status|run|stop`。默认inspect只检查本地；run观察已有负载，在预定20分钟以内最多完成四代，无合格流则等待并有界退出。stop禁止新准入，当前独立owner按原硬截止恢复，不停止用户应用。单代入口为`normal-entry.mjs inspect|status|run|stop`。源码：[controller](../code/work/resident-normal-dev-20261008/controller.mjs)、[正常流入口](../code/work/resident-normal-dev-20261008/normal-entry.mjs)。当前原工作区含本地凭据/模块/部署输入，公开代码不能替代这些私有写前条件。

## 已知限制与下一milestone

- 正常入口仍为两TCP BULK＋一UDP RT；五WAN同时ECM5/QoS/CPU历史证明继续有效。
- 已通过的是独立模拟器提供的进程/socket，第三方程序及长期无人值守覆盖留后续。
- 默认永久NSS保持关闭；后续只评估正常使用和默认常驻部署，独立恢复和原硬截止不放宽。
- 自然流量不足/类型变化/偶发SSH或端点取得拒绝有界结束；不自动重试fixture、不强换WAN或tag。
- Wi-Fi、autorate、ECN、新分类、新QoS、CPU benchmark、极端崩溃与新增边界继续不扩展。

本开发批次到此收尾，不主动寻找新的边界问题。[源码摘要](../evidence/resident-normal-source-proof.json)。
