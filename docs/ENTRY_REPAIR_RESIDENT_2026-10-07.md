# 可复用五 WAN 入口完成；常驻候选尚未进入 NSS

北京时间2026-10-07 21:47。用户要求遇到程序错误继续修复，入口完成后尝试可撤销常驻 NSS 的授权保持。继续使用四条自有 TCP 和模拟 UDP，不操作 CS2／Steam。

## 已完成的入口闭环

v54 实际入口以3421绑定进入五 WAN NSS：四 TCP BULK走WAN1／2／4／5，UDP RT走WAN3；B 60.01秒、121采样、全部ECM5、20续租。新 checkpoint 下载/SHA/gzip与原独立恢复写前通过，七份 Lua 为v42原字节。进入、租约、退出、完整恢复均通过，**可复用入口硬件闭环已完成**。这替代旧STATE“入口未通过”的当前结论；历史失败原字节保留。

TCP载荷取得采用仅限自有SSH子进程的紧凑算法offer。v49实测IPQoS=none在WAN5仍失败，未采用；v50小探针未覆盖WAN5，单独不构成WAN5证明。v51实际三个WAN5 TCP收到载荷并持续传输，四首包约2.59—2.69秒。v51软件UDP1928发／0返，未进入NSS；后来增加三个实际载体同tuple的UDP20包预检，v54各20／20通过。

修复了端点写请求未获确认时丢失清理指针的问题：在systemd／FW写前保存启动意图，再以原250秒服务／180秒FW独立期限和精确单位／端口／规则基线判断恢复。v52原wrapper过早推断无端点的结果保留；随后独立只读精确服务／端口缺席证明通过。

## 控制传输与候选取得修复

控制SSH改用短启动命令，将原dispatcher的确切解压字节和后续帧放入同一256字节／20ms串行stdin队列；认证、全局SSH、8秒连接与20秒命令限制不变。v56实际本地socket原端口到CT匹配，WAN5短启动渠道16KiB输入完整通过；同批旧渠道也通过，**未证明MTU根因或排除所有偶发SSH问题**。v53以远端NAT端口匹配本地CT的诊断未取得WAN归属，不把它当WAN5证明。

自然取得现在从已核实PID／socket的实际CT读取WAN，提前轮换重复WAN；Linux PBR／mark／NAT不写，路由归属不授予BULK资格。最终仍需要四实际BULK＋已准入RT。复用路由器控制连接，CIM身份与源帧每次重新读取；15秒单次读取、30秒自然轮换、最多8候选、8秒首包保持。v57小数timeout导致Node写前拒绝，v58已取整修复；修正版9模型／3424绑定、11归属模型／9 RAM和完整Lua语法通过。最初Lua字符串转义、RAM测试长括号和model指针EEXIST失败与输入均保留，未将其标为硬件证明。

## 本次常驻候选的实际范围和结果

候选只将固定B从60改为90秒，native hard由90改为原已存在的最大120秒；source6／owner180／client180／guard210／server250和字节上限不变。六份其它Lua、native、分类／QoS／失效撤销不变，**不能称七Lua全字节相同**。这是一代有退出的router detached controller候选，尚无长期、永久或自动连续新代部署。

v55因缺WAN2，在NSS checkpoint／stage前退出；端点控制与首只读清理超时原失败保留，v56只读精确规则0／FW基线／单位端口关闭证明补齐，原UNCONFIRMED结果不改，仅可变ledger修正RESTORED。

v57因timeout参数类型错误在NSS前退出；修复后v58实际连接已走TCP WAN2／1／4／5和UDP WAN3，但34次分类读最后只有3BULK＋1RT，第四TCP不在准入投影中。全fixture客户端错误0。该缺失不能当作CT退出或真实BE改类证据，也未证明是NSS／firmware故障。原窗口结束，未开始NSS checkpoint／owner／stage／ECM，**90秒常驻硬件验收未通过**。不强制改类／tag或放宽期限，也不为配齐资格无条件重开fixture。

## 最后恢复和下一步

所有本轮实际会话均最终RESTORED／锁解除。最新完整audit source1.76秒／selectors12，五WAN健康、保护配置不变、ECM关闭全零、两物理原mq＋四fq_codel全部选项／handle一致，端点规则0／基线和客户端残留0。NSS68分类器原配置保持，heartbeat暂停。

当前可用成果是显式一次的五WAN60秒入口闭环；常驻控制器仍是未进入NSS的90秒候选。保留的问题是自然候选／分类投影取得、偶发控制SSH、历史v41进入窗计数差异、普通应用factory未验及长期／永久常驻。后续只依据实际缺失分类的完整同query证据修复或接入常驻控制，不重复五WAN核心、CPU或真人游戏验收。

证据：[入口与候选结果](../evidence/v58-entry-repair-resident.json)、[源码与保留证明](../evidence/v58-source-proof.json)、[入口用法](BOUNDED_MULTIWAN_ENTRY.md)。
