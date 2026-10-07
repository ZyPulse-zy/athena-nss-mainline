# v45 提前取得入口：软件检查通过，端点连接前置失败

北京时间2026-10-07 18:04。本次接续用户“继续”，只修改四条自有TCP的初始启动时序和取得阶段的进程就绪条件；没有操作CS2、Steam或下载游戏。v42五WAN高级QoS的已有硬件功能证据保留。

## 改动及验证

原v44逐条等待首包后再启动下一条TCP，四个PID齐备约16.01秒，四条首包齐备约18.88秒；原30秒自然取得窗口的有效观察时间因此缩短。v45让相同四条初始SSH连接同时启动，四个唯一自有PID发布后可提前进行原CIM/socket/真实CT/WAN核对。进程就绪只允许提前观察；最终进入NSS仍需四条真实BULK、一条已准入RT、四条首包、五个不同WAN、完整身份/mark/NAT/affinity及原checkpoint/独立恢复。

24项入口模型与默认inspect通过，3406绑定=原3354+52。七Lua、原32Mbps/64KiB、180秒客户端/210守护/250端点、30秒取得/8候选及source6/kernel90最大120/owner180和各字节上限保持。首次模型断言误用了另一文件的错误文本，原失败代码和记录保留后更正；没有现场流量。

## 唯一一次实际入口

原完整前置审核通过。端点控制SSH随后连接超时（exit255），在第一条只读端点checkpoint命令返回前退出。本地只创建了准备目录；无端点checkpoint/deadline、远端服务、防火墙写、客户端配置/launch、负载指针、NSS checkpoint/owner/stage/ECM。**实际入口尝试1次，fixture流量0次；新启动时序的现场作用尚未验证，完整可复用入口验收仍未通过。**

只做一次失败相关的只读端点诊断，SSH已能连接，精确端口占用0、本次单位0，自有fixture进程0。不能因此宣称SSH超时已修复或确定根因；没有重新开启fixture碰运气。

## 最终状态

本次入口直接完成最终审核，无额外恢复补轮：source 1.34秒 / selectors 0，五WAN健康、保护配置不变、ECM关闭全零；wan/lan4原mq＋四fq_codel的全部选项/handle一致。独占锁解除，ledger RESTORED。常驻NSS68/config不变，heartbeat继续暂停，没有永久部署。

## 前次报告标注更正

v44旧记录字段`tcpWanSetInSlotOrder:[1,1,2,4]`实际是native数组顺序。用同一冻结完整帧的自有socket本地端口映射，真实槽顺序为TCP1 WAN4、TCP2 WAN2、TCP3 WAN1、TCP4 WAN1，UDP WAN3。原证据和报告字节保持；本页和新更正证据说明标注错误。未配齐五WAN和NSS写前退出的原结论不变，不是WAN affinity变化。

## 使用范围与后续

五WAN核心功能继续采用v42实测：60.01秒、ECM5、20续租、2373/2373模拟RT回包、十tag/leaf/CT/mark/NAT/affinity和完整恢复；DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel。v45是有界显式入口的软件候选，尚未证明自动整合稳定或长期/永久/全网可用。新一次整合须有新的可执行条件和用户授权；不自动开新轮，不放宽取得期限/认证/PBR。v41计数差异、偶发SSH连接超时、自然WAN未配齐及普通应用factory未验保留为限制；连续新代、长期部署、WiFi/autorate/ECN仍在v1.1/v2。

证据：[入口](../evidence/v45-entry-startup.json)、[终态](../evidence/v45-restoration.json)、[v44标注更正](../evidence/v44-slot-order-correction.json)、[源码与冻结](../evidence/v45-source-proof.json)、[入口使用](BOUNDED_MULTIWAN_ENTRY.md)、[v42硬件](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
