# 五 WAN 首次同时命中；分类变化触发精确恢复

更新：北京时间 2026-10-07 14:15。**五个不同 WAN 的四条 TCP BULK＋一条 UDP RT 已实际进入 NSS，ECM=5；60 秒维持验收未通过。** 模拟流测试没有操作 CS2 或 Steam。既有 v38 两 WAN / v20 多 WAN与高级 QoS、历史 CPU 证据继续保留。

## 本次推进

v40 保存的 10 次读取约21秒，每次只轮换第一条重复 WAN 的 TCP，且须等四条全部 BULK。v41 在前30秒自然连接取得阶段处理所有当前重复槽位，利用已核验的自有 TCP 传输 WAN 元数据筛选；仍须原永久分类器明确判为 BULK、UDP为已准入 RT、五个 WAN不同，才能冻结并进入原控制器。PC读取携带同一次进程身份，变更/缺失时不猜测WAN；整批命令先校验再启动，旧已完成命令保持无操作。没有修改 Linux PBR、分类阈值、NSS gate或QoS。

11个针对新策略的本地检查通过；历史完整帧用于模型，不能授权新现场。3303实际绑定及pilot/控制器原源码副本逐字节冻结，复用五槽编译与63控制/68CT/14RAM，不重跑历史CPU或旧准备。本次11次自然读取取得 TCP WAN2/4/5/3＋UDP WAN1；第三 TCP 取得第4个自然候选，其它TCP为第1个。没有对不同随机WAN分配声称可比提速。

新checkpoint下载SHA/gzip和控制连接外独立恢复在写前核验；实际bundle 72939 / exec 8799字节符合原73728/9000上限。随后五条精确流实测加速，双向十tag、上下leaf、完整ct mark、NAT、WAN affinity以及LAN4/bridge路径通过。

## 60 秒窗口未通过的确切条件

B段持续 3.90 秒，6次保存采样均为ECM5，续租0次。下一分类query完整同源帧确认四TCP均仍存在，CT/zone/完整mark/WAN/双向tuple全部匹配；四条均变为BE/cooldown，报告速率约1506–1689Kbps，低于原2000Kbps BULK阈值。UDP保持RT/interactive及预算准入。投影缺失没有被解释为CT退出。

控制器停止新学习、结束旧代、撤下五条精确流及tag，并恢复软件路径。原本请求60秒，实际提前退出，因此 `automaticLifecycleEpochCompleted=false`，原控制器失败和完整记录保留，**不能把短时命中写成60秒或长期验收**。

附近 3.95 秒的下行leaf计数显示四TCP约3.64/4.28/4.51/4.58Mbps，合计17.00Mbps；共享DOWN18和UP60每WAN12队列合同保持，UDP上下leaf均零drop。这些窗口与分类计数窗口不同，尚不能据此认定NSS统计反馈错误或精确根因；不作为新的CPU、端到端零loss、CS2/HUD或真人证明。

## 恢复与下一边界

最终原完整只读audit source 1.16 秒，五WAN健康、原保护配置与epoch保持、ECM关闭全零。wan/lan4原mq＋四fq_codel所有选项和handle精确一致，实验gate/stage/state/模块零残留。端点独立到期后规则0、canonical FW基线一致、确切端点关闭，原client/guard/controller/sender全部退出。常驻NSS68原config保持、heartbeat仍暂停，电源计划未改。

已新增的证明是五WAN同时NSS启动及十tag/leaf/CT/NAT/affinity；未解决的是五流带宽共享期间的BULK分类维持边界。后续只针对这项实际失败，先核对当前真实计数窗口与分类反馈，再决定有证据的修正；不放宽分类或期限，不强行把BE当BULK，不盲重跑五流，也不回到CS2测试。长期常驻、多流公平、WiFi/autorate/ECN不在本轮。

离线报告检查首次假定checkpoint有`passed`字段而拒绝，原源码/失败保存；改为验证实际gzip字段和下载文件SHA后通过。没有修改原运行记录或重跑生产实验。

证据：[五WAN实际命中与提前撤销](../evidence/v41-five-initial-hit.json)、[终态恢复](../evidence/v41-five-restoration.json)、[源码保存](../evidence/v41-five-source-proof.json)、[先前两WAN60秒](SIMULATED_MULTIWAN_2026-10-07.md)。
