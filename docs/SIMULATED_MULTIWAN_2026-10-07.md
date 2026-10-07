# 模拟实时流＋两条下载：跨 WAN NSS 短测通过

更新：北京时间 2026-10-07 12:59。按用户最新要求停止 CS2 测试，改用自有脚本发送 128 字节双向 UDP，配合两条自有 TCP 下载。**本次在真实路由器上完成 WAN3/WAN5 的 60 秒 NSS 段、20 次续租和完整恢复。**

## 本次结果

- 原常驻自动分类器识别 TCP BULK / UDP RT / TCP BULK；TCP 分别走 WAN3、WAN5，UDP 走 WAN3。没有手工指定分类或改新连接 PBR。
- NSS 段三个确切连接同时加速，ECM 全窗为 3，退役后为 0；双向六个 tag、对应 bulk/RT leaf、完整 ct mark、NAT、WAN affinity 验证通过。
- 五 WAN 队列映射保持上下行各 18 class / 11 leaf；DOWN18 共享预算借用已观察，两个 bulk leaf 在附近异步计数窗口分别约 6.82 / 8.40 Mbps，合计 15.22 Mbps。UP60 每 WAN12 硬上限及 RT prio0/FQ-CoDel保持。这里是两 WAN 上三流同时加速。
- 约 57.17 秒的 NSS 内部窗口，2443 个 UDP 请求全部得到回包，RT 上下行 leaf drop 均为 0。回复统计到自有 fixture 结束；时钟映射不确定度 0.83 秒、两端保守排除边缘。RTT 中位 199.92 ms，P95 200.79 ms，P99 202.51 ms，P95 减中位约 0.86 ms。

UDP 配置目标 50 包/秒，内部实际约 42.7 包/秒；RTT包含自有海外端点路径，抖动描述来自脚本回包。它不提供 CS2 HUD 的 jitter/loss/Miss 或真人体感。TCP 提供负载目标为 24＋8＝32Mbps，附近异步 leaf 速率不作为长期限速精度或新 CPU 对照。

## 已保留的失败和修正

v35 的选择排序与失败帧保存已完成 10 本地 / 7 目标 RAM 模型，2806 绑定；用户停止 CS2 后没有运行新的普通应用 NSS 会话。直接启动游戏曾被 VAC 签名检查拒绝，未进服、未恢复下载；临时 Steam 32000Kbps 数值清空、限速关闭，原下载仍暂停。

v36 第一轮自有负载的第二条 SSH 下载首包为 0，约 32.39 秒后超时。第一 TCP 和 UDP 正常，原分类曾见一 BULK/一 RT；该轮在 checkpoint / gate / ECM 前结束，原错误、匹配帧、独立客户端退出与端点恢复全部保留。不能归因 NSS、固件或学校网络。

后续只给自有未准入 TCP 增加 8 秒首包等待、最多 3 次且总计前 30 秒内的连接取得；准备配对成功就冻结，已有 payload 或已准入阶段不自动重连，不延长 180 秒客户端期限，也不改防火墙来源。v37 本地新目录的转义路径漏改，连接前拒绝，原源码及错误保存；v38 对普通路径和正则转义一并接续，2979 实际绑定冻结。本次两 TCP 均第一次连接成功，新的重连分支未实际触发，不能宣称超时根因已修复。

## 完整恢复

独立撤销、模块卸载、tag 删除、两物理原队列、WAN/mwan3 与状态目录清理通过。最终原完整只读 audit source 2.03 秒、native selectors 4 通过，五 WAN 健康、保护配置/服务 epoch 保持，ECM 关闭全零。wan/lan4 原 mq＋四 fq_codel 的全部选项和 handle 精确恢复。两个自有端点临时规则为 0、canonical 防火墙基线一致、确切端点关闭；客户端、controller、guard、SSH sender 均无残留，CS2为0，Steam保持暂停且限速恢复。

首次本机退出读取因宽泛目录匹配误把只读检查的父进程计入残留，原输出/源码已保留；核实不是 fixture、pilot 或 guard 后，仅重查这一失败的只读步骤一次通过。没有重跑 NSS 或完整网络审核。heartbeat保持暂停，未改电源计划。

## 后续范围

**受控模拟实时流的两 WAN NSS 功能验收通过。** v1及v20既有功能/CPU证据继续复用。本次只有一个 B 段，软件进入和结束恢复均通过；不把它写成新的 CPU A/B/A2、Steam正常应用factory或真人游戏验收。

后续主线可继续使用脚本模拟游戏包；不再把启动 CS2 当作继续测试的前提。本轮到此封存，不因未复现的 SSH 超时继续重试。五 WAN 同时 fast path、多流公平、长期/永久运行、Wi-Fi/autorate/ECN与其余高级QoS扩展留后续范围；当前没有永久启用 NSS。

证据：[硬件及回包](../evidence/v38-simulated-hardware.json)、[完整终态](../evidence/v38-simulated-restoration.json)、[源码保存](../evidence/v38-simulated-source-proof.json)、[首次传输失败](../evidence/v36-owned-transport-refusal.json)、[本地目录拒绝](../evidence/v37-local-namespace-refusal.json)。
