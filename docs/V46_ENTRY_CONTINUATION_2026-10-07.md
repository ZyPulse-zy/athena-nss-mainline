# 同字节v45入口接续：并发启动已实测，完整整合未通过

北京时间2026-10-07 18:38。端点只读已恢复连接、精确端口/单位零残留、原入口RESTORED后，本次复用原24模型/3406绑定的v45入口源字节，只接续一次自有四TCP＋模拟UDP，不重做离线准备和v42核心证明。

四个初始PID分别在0.076/0.079/0.083/0.087秒发布，四路第一次同时有payload在10.71秒；并发启动已实际执行。v44历史全部PID齐备16.01秒，只作不同窗口的记录，不声称同负载CPU或固定收益。

原实际CIM/socket/CT/WAN核对发现重复WAN后，在原30秒取得窗内只替换自有tcp3/tcp4候选；tcp/tcp2实际WAN1/WAN5保持。第三条TCP的第3候选8秒没有首包，原重试上限拒绝，客户端在24.57秒退出，最后分类读随退出失败。原driver codes为0/0/0/1/0，10次匹配读，最后完整五WAN pair为0。没有扩大重试、期限、流池、PBR或分类门槛。

TCP客户端payload 63242240字节；全fixture UDP 1040发/1025返。没有NSS B段，停止边界的未返回包不归因NSS。没有NSS checkpoint、owner、stage或ECM；首包超时根因未知，不能归因firmware/gate/lease。**并发启动功能已得到现场证明，完整可复用NSS入口仍未验收。**

按原180秒FW守护自然到期后关闭精确端点，规则0/canonical基线与单位关闭通过。原客户端180秒/独立210秒guard保持，精确自有进程0。最终source 0.98秒/selectors2，五WAN健康/保护配置不变/ECM关闭全零，两物理wan/lan4原mq＋四fq_codel的全部选项/handle一致；RESTORED、锁解除。原v45失败、源码和报告保持，heartbeat仍暂停。

v42五WAN五流60.01秒/ECM5/20续租/2373RT全部返回、十tag/leaf/完整mark/NAT/affinity与恢复仍成立；DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel不变。没有操作CS2/Steam、新CPU测试或永久开启NSS。

当前限制是自然WAN去重与候选SSH首包取得失败，普通应用factory、长期/永久/全网仍未验收；v41计数差异和WiFi/autorate/ECN等后续边界保持。本次停止新增fixture，保留证据；下一项应针对实际候选首包取得条件，不继续为配WAN盲重试或重复已验收NSS数据面。

证据：[实际入口](../evidence/v46-entry-continuation.json)、[恢复](../evidence/v46-restoration.json)、[源码](../evidence/v46-source-proof.json)、[当前入口](BOUNDED_MULTIWAN_ENTRY.md)、[v42硬件](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
