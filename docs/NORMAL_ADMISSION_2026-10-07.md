# 正常程序通过 checkpoint 后选择；owner 准入拒绝，恢复通过

更新：北京时间 2026-10-07 11:56。v34已实际进入Cache死斗新回合，再以独立180秒客户端守护恢复已有Hades下载，临时限速32Mbps。自动分类识别1条CS2 RT、11条Steam BULK及一组跨WAN三流。**先前准备时冻结TCP的阻塞已越过，但独立owner最终分类准入拒绝，没有NSS B段或普通程序factory验收。**

## 本次推进与实际边界

原完整audit后，先读取现有候选WAN的原native前置条件，再从最新实际分类和程序socket中选定TCP与WAN范围；保持原CS2身份。只读准备覆盖5个候选WAN，不表示五WAN同时NSS。13项本地模型仅针对这一顺序，native前置条件是模型数据；旧18＋14模型、硬件数据面及post-checkpoint原WAN/full mark/NAT合同保持，未重复旧测试。资格2723＋39＝2762绑定、61相对依赖；default inspect已实际运行且0游戏/0下载/0pair/no writes。

实际选中WAN1/2/5上的两TCP BULK＋一UDP RT。新checkpoint已下载并通过SHA/gzip检查；checkpoint后的最新分类仍为BULK/RT/BULK，原CS2及冻结WAN合同通过。控制连接外的独立stage撤销守护在第一生产写前就绪，暂存上传完成，临时物理QoS确实配置。随后initial alignment第一次探测报`Selected class is not admitted`，owner拒绝继续：gate模块未加载、ECM未放行、没有60秒NSS测量。

本地诊断只复核已有文件，未增加远端查询或重试。最后PC帧属于checkpoint后选择，不能当作失败时owner分类帧；owner失败时未保存完整分类快照，确切缺失slot/改类根因未知。缺失准入候选不能当CT退出或firmware故障。原错误、checkpoint、guard、完整私有输入和2762份实际绑定来源保持。

## 客户端及 HUD

Cache正常死斗回合先连接，9:46的软件HUD见ping15ms、上下loss0%；下载后7:56和7:30画面也见ping15ms、上下loss0、绿色网络图。8:27未显示的数值保持未知。没有数值jitter/Miss、连续遥测或用户本人体验确认，全部是软件阶段，不能写成NSS游戏质量通过。

下载实际UI约32–33.4Mbps。11:48在原守护期限内暂停到34%/网络磁盘0bps，并清空32000、关闭限速；原守护11:49自然精确退出CS2/Steam。后来为恢复Steam界面重开时又自动续传，见327.2Mbps，已立即再次暂停，11:51视觉确认48%/网络磁盘0bps、原限速OFF及区域/bit显示/游戏中下载设置保持。这段在原守护之外，**累计严格180秒/720MB不成立**；原guard从未重置，自动续传片段如实保留，不能用进程退出替代UI恢复。

## 完整恢复及后续

独立stage已经精确撤销：自身目录/状态目录消失、guard结束、gate和QoS模块消失、WAN/mwan3及两物理队列恢复。11:51最终原完整audit source1.22秒、native selectors2通过，保护配置/服务epoch/五WAN健康保持、ECM关闭全零；wan/lan4原mq＋四fq_codel的所有选项和handle精确一致。CS2、controller、guard零残留；Steam恢复为可用暂停状态。

v20受控三流跨WAN、五WAN队列映射、DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel及NSS128历史CPU证据继续复用。本轮只有新的正常入口准备/准入结果，不是多WAN数据面失败，也不是正常程序NSS验收通过。剩余具体边界是checkpoint后选择与owner最终准入未能衔接，失败时的具体slot和分类变化仍未知；本轮不放宽准入、不盲重试，不增加tap或新的验收条件。后续只处理已证实影响正常入口的这一步，并先保证恢复启动不会突破下载窗口；五WAN同时fast path、长期/永久运行和其它高级支线继续留后续，heartbeat保持暂停。

证据：[入口资格](../evidence/v34-normal-entry-qualification.json)、[13模型](../evidence/v34-prepared-selection-model.json)、[实际准入拒绝](../evidence/v34-admission-refusal.json)、[客户端/HUD](../evidence/v34-client-window.json)、[终态](../evidence/v34-normal-restoration.json)、[源码保存](../evidence/v34-normal-source-proof.json)。
