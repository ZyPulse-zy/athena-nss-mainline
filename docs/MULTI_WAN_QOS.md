# 多 WAN NSS 与高级 QoS的实际边界

| 能力 | 当前证据 |
|---|---|
| 同时加速跨WAN的两TCP BULK＋一UDP RT | v16、v19、v20实际60秒；ECM3和恢复通过 |
| 五WAN上下行RT/BULK队列映射 | v20实际完整建立/读取，十个类别leaf加default950 |
| 共享下行预算与空闲份额借用 | DOWN30→18响应、保障/ceil分离；v19/v20实测借用 |
| RT优先级与FQ-CoDel | RT保障1Mbps、prio0，BULK prio1，target5ms/interval100ms/1024流；B内自有echo全返回，RTleaf drop0 |
| PBR/NAT/完整ct mark/WAN粘性 | Linux决定新连接；已选CT/快路径保持原出口，六tag实际命中 |
| 正常Steam和CS2自动进入新的多WAN入口 | v26实现18模型、46导入检查和现场只读0流；新整合NSSfactory尚未硬件运行 |
| 五条不同WAN flow同时NSS | 仅五槽编译/离线模型；所有尝试在NSS前拒绝，未加载硬件 |
| 全网/长期常驻、所有连接主要由NSS QoS处理 | 尚未交付；当前只选三条精确CT，其余软件fallback |

上行总60Mbps、每WAN12Mbps硬上限；下行共享18Mbps、每WAN保障3Mbps可借用至18Mbps。五WAN保障合15Mbps，剩余3Mbps属于共同父预算余量。default950保障未加速物理fallback；其软件路径原IFB/CAKE继续存在。

NSS用分层预算、RT/BULK优先级与每leaf FQ-CoDel替代这部分关键QoS。它没有复刻CAKE的NAT后host公平、diffserv4四tin、COBALT或autorate；用户已明确多人公平性不必要。target5ms是配置值，不是整个互联网连接的RTT保证。自有echo不是CS2的jitter/loss/Miss；新范围未增加CPU因果证明，旧NSS128的同负载softirq收益继续成立。

## 后续明确范围

1. 用户正常玩CS2和下载时，运行一次v26新整合有界入口，保留实际游戏体验与恢复；不用再下载游戏制造负载。
2. 五槽候选的现场前提：先解决自有TCP端点可达性的独立fixture问题；SSH版本和nonce认证raw TCP版本均在NSS前失败。当前根因未知、不是已确认NSS故障，不能靠改学校或SSH策略解决。
3. 扩大精确加速池、连续新代和长期启停。当前三CT耦合旧代中任一flow改类/退出会结束该代并恢复；禁止直接更改已加速tag。
4. 普通共享预算、Wi-Fi、autorate、ECN全面验证及极端生命周期故障留后续；不影响本轮已成立的受控跨WAN原型。

截至08:00的夜间授权在07:40进入最终恢复核验、07:50禁止新实验，完成报告和推送后暂停自动化。任何未来生产会话仍需新checkpoint和控制连接外独立恢复。
