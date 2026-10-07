# 五 WAN 模拟功能验收完成

更新：北京时间 2026-10-07 14:52。**自有四条 TCP BULK 和一条模拟 UDP RT 在五个不同 WAN 同时进入 NSS，并完成一次有界 60.01 秒窗口、121 次 ECM5 采样和 20 次续租。** 双向十 tag / bulk、RT leaf / 完整 ct mark / NAT / WAN affinity 及软件恢复通过。本轮没有操作 CS2 或 Steam。

## 实际数据与高级 QoS

实际分配：TCP WAN2、TCP2 WAN3、TCP3 WAN4、TCP4 WAN5，UDP WAN1。所有新连接仍由 Linux PBR 自然分配，冻结后没有替换 WAN、tuple、CT 或 tag。实际五槽 native 与 v24 相同，准入来自原 NSS68 永久自动分类器，BULK 2000 Kbps 门槛、RT 预算和 source6 / kernel90最大120 / owner180 / client180 期限没有放宽。

五 WAN 上下行各18 class / 11 leaf、RT prio0 / FQ-CoDel 的原硬件队列合同保持。共享下行18 Mbps，四条 TCP 的附近异步 leaf 窗口约 4.31/4.12/4.27/4.00 Mbps，合计 16.70 Mbps；超过各 WAN 3 Mbps 保证份额的共享借用已观察到。上行共享60 Mbps、每WAN12 Mbps硬上限的实际配置和 native 选项已验证，未宣称本轮分别压满五WAN上行或长期公平性。

约 57.06 秒的保守内部窗口发出 2373 个认证 UDP echo，2373 个在整份 fixture 中返回，未返回0；跨设备映射不确定性约 0.95 秒，窗口边缘各排除1秒。RTT中位/P95/P99约 196.47/198.68/200.36 ms，P95减中位约 2.21 ms，RT上下 leaf 零drop。这是自有海外服务器的模拟包测量，不是 CS2 HUD jitter/Miss、真人体验或新CPU收益。

## v41 异常的有限判断

先对齐已有 v41 记录：query1767→1768的finished窗口为3.01秒，PC时钟区间不确定性0.82秒，原四个socket/进程实例未变；客户端stdout交付的保守速率下限约2.57/2.31/3.44/2.48 Mbps，而原完整分类帧为BE/cooldown、1.51–1.69 Mbps。进一步排除两次CT读取时段后，三条流的保守下限仍高于2000 Kbps，另一条不足以作此判断。SSH管道缓冲未被pacer credit限制证明，因此没有把这些数值当作精确线速或已证实的固件同步根因。

本次只在既有fast path增加初始ECM读时间，以及停止新学习后、撤销前最多一次受保护的现有ECM状态读取；没有增加tap、抓包、分类器安装或阈值调整。完整60秒内没有再次触发v41改类，终止诊断分支未执行，原分类/改类拒绝和恢复规则保持。

**v41原失败未删除、未称已修复；本次未复现使其不再阻止这次有界五WAN模拟功能验收。** 它保留为已知限制：五流进入NSS时曾发生BULK→BE/cooldown提前退出，准确根因与长期发生频率未知；原控制器会拒绝续租并结束旧代。一次60秒成功不能证明长期可靠性，永久常驻推广仍需后续证据。没有为追求完整根因继续开启轮次。

## 写前安全与完整恢复

3354实际绑定及pilot/控制器完整源码副本逐字节冻结，历史五槽63控制/68CT/14RAM与CPU证据复用，未重做旧准备。新checkpoint已下载、SHA/gzip核验，控制连接外独立恢复在写前证明。实际bundle73138 / guardian exec8799 / 记录634752字节，均在原73728/9000/1MiB上限内。

NSS控制器正常结束并恢复，原完整baseline检查通过。随后监督器的端点关闭SSH连接超时，退出码1、原stderr和失败保留；没有远端关闭命令成功执行的证据。已过原独立端点最大期限后，只做一次新目录只读重查，确认精确服务MainPID0、端口45817/45818关闭、临时规则0、canonical FW基线一致。

最终完整审核source 1.12 秒 / selectors 6，五WAN健康，原保护配置/服务epoch保持，ECM关闭全零、无实验gate/stage/state/模块。wan和lan4原mq＋四fq_codel全部选项/handle精确恢复，自有client/controller/guard/sender零残留。自有客户端独立提前退出证明通过；用户独立应用未被清理。常驻NSS68原config、heartbeat暂停，电源计划未改。

封存脚本首次将空进程枚举误当作必有原始文件而拒绝，原源码、错误和候选文件均保留。改为引用实际保存的零自有进程审核摘要后继续封存，没有重复网络试验。

## 交付范围与后续

已完成的是**五 WAN 的五条精确流、一次60秒NSS维持及既有高级QoS共享预算的受控功能验收**。已有v38两WAN / v20多WAN与历史CPU证据保留。普通用户全网、永久NSS、长期运行、五WAN多流公平、不同应用负载和极端故障恢复尚未验收；WiFi、autorate、ECN仍在后续范围。本轮结束新增生产实验。

已知非阻塞问题进入后续清单：v41进入窗口分类计数差异；自有SSH连接偶发首包/控制连接超时；正常应用factory尚未验收。后续先复用已成立的核心证据，只有新问题明确影响选定使用目标时才继续修复或新开有界验证。

证据：[五WAN硬件](../evidence/v42-five-wan-hardware.json)、[终态和原SSH失败](../evidence/v42-five-wan-restoration.json)、[v41窗口对齐](../evidence/v42-v41-window-alignment.json)、[源码保存](../evidence/v42-five-wan-source-proof.json)、[v41原失败](FIVE_WAN_INITIAL_HIT_2026-10-07.md)。
