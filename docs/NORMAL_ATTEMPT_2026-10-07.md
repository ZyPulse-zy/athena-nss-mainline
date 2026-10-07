# 正常程序三流已识别；控制器在 NSS 写入前安全拒绝

更新：北京时间 2026-10-07 11:12。v33已实际进入Mirage死斗，同时恢复已有Hades下载，约32Mbps。自动分类识别1条CS2 RT、9条Steam BULK及一组跨WAN三流，完整控制器确实被调用。**准备期间两条已选TCP不再合格，控制器在checkpoint、stage和ECM之前拒绝；普通应用NSS验收仍未通过。**

## 实际结果

| 项目 | 观察与结论 |
| --- | --- |
| 真实游戏与下载 | 游戏先连接，再启动新的独立180秒客户端守护、恢复限速32000Kbps的已有下载；原窗口未重置。没有购买、启动Hades或新增其它下载 |
| 自动分类 | 负载就绪帧1个实际CS2 RT、9个Steam BULK、一组两TCP不同WAN的三流；源与程序socket归属保留本地 |
| 控制器 | 退出1，原错误为 `Exact controlled socket pair changed before staging`。checkpoint、detached owner、stage、NSS模块和ECM均未开始，原失败/完整输入/2723绑定源码保存 |
| 原连接状态 | 拒绝帧中原UDP仍合格，两条已选TCP不合格；两条对应socket仍在Steam库存。原WAN槽合格替代0组，其它WAN槽有1组。这不能证明原CT退出、改类根因或NSS/固件故障，也不授权改已冻结WAN范围 |
| HUD | 软件阶段9:50和8:23见ping15ms、上/下loss0%，jitter图绿色。8:53死亡屏幕隐藏值保持未知。没有数值jitter、Miss值或真人体感确认；本次HUD不能作NSS B段游戏证明 |
| 客户端 | 原180秒守护自然执行精确应用退出，CS2/controller/guard零残留。守护到期时UI恢复尚未完成，后来手动重开Steam、暂停下载、清空32000并关闭限速，11:06视觉核实30%暂停、网络/磁盘0bps及原设置保持 |

Steam初次启动和手动重开恢复设置时都曾自动续传。这些片段没有累计时长测量，不能将守护退出写成严格180秒总下载证明。部分Hades内容留存且暂停；原失败、到期时UI未恢复及后来实际恢复分别保存。

## 最终恢复

11:01原完整只读audit通过：source1.24秒、native审核2 selectors，保护配置/服务epoch/五WAN健康保持，ECM关闭全零。11:02两物理wan/lan4的原mq＋四fq_codel全部选项和handle一致；客户端inventory证明CS2、controller、guard零残留。之后仅恢复Steam界面设置，没有router配置写入。

v33只改新目录引用和本次11:30截止；数据面、分类阈值及v31的选择合同保持。2687＋36＝2723绑定、57相对依赖/语法通过，18选择模型与14实际拒绝模型复用未重跑，完整factory没有在模型或硬件完成。本次30份实际输入按字节另存；资格36份及实际runtime2723绑定逐字节验证。v32/v31和全部旧code/evidence保持。

## 剩余边界

已成立的v20三流多WAN、五WAN队列映射、DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel硬件结论与历史CPU证据继续复用。正常下载TCP候选在准备期间变化，是当前正常入口仍未验收的具体边界；没有依据放宽准入、强行固定原TCP、改已冻结WAN范围或盲重试。本轮停止新生产实验；后续只处理有证据支持的正常入口准备顺序，再用新目录进行一次有限实际会话。五WAN同时fast path、长期常驻、更多故障/CPU/WiFi/ECN测试留后续，heartbeat继续暂停。

证据：[入口资格](../evidence/v33-normal-entry-qualification.json)、[实际拒绝](../evidence/v33-normal-refusal.json)、[客户端与HUD](../evidence/v33-client-window.json)、[终态](../evidence/v33-normal-restoration.json)、[源码保存](../evidence/v33-normal-source-proof.json)。
