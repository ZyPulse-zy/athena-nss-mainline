# 当前剩余工作与已完成项

恢复表修复已按用户新授权完成一次受控部署。安装源码 `2996d40`
包含 `f848caf` 修复；实际只替换 writer，其他安装文件保持。2026-10-10 19:26:35 北京时间核验
native-running/sourceFresh，未确认回执 0。180 秒自然观察 NSS 0..4，
标签一致 129 个流样本、差异 0，来源新增暂停/恢复
0/0，自动恢复新增 0。五 WAN、原保护文件、
十个软件 CAKE 根、自启以及认证/分类器/autorate/代理/Tailscale 服务身份保持。

剩余：完整上游构建/评审、原生 Linux 的 nftables 文本/JSON 无 hook 复现、完整逐流恢复链、最终空口与有线长连接、来源中断根因、代表性覆盖和长期负载。短窗不代表这些验收完成。

本次单次部署授权已用于这次切换，不据此自动重复部署、重启、故障/拥塞测试或修改无线/学校网络。
游戏/Wi-Fi 正式验收仍延期，既有正常服务继续运行。ECM 上游 #78 为未部署的草稿，
还需完整模块/软件包构建与固件验证；PR #1 保持 draft，不合并。

[部署和短窗证据](DORM_V2_RECOVERY_DEPLOYMENT.md) · [恢复表逻辑](DORM_V2_RECOVERY_LEDGER.md) · [ECM 草稿 #78](https://github.com/qosmio/nss-packages/pull/78)

<details>
<summary>此前阶段记录（历史事实，部署授权不可沿用）</summary>

### 历史记录：常驻部署后续

当前手动常驻进程已保留，首次自然负载准入和更长正常使用soak待出现；通过后再决定登录自启与默认部署。不新开模拟fixture或重复核心证明。非阻塞限制见[使用文档](RESIDENT_SERVICE.md)。

## 以下保留历史待办

### 历史记录：2026-10-08 08:10 — 正常流常驻控制器批次

正常流入口和四代有界常驻协调通过，实际COMPLETE，恢复通过。57本地检查集中收敛P2，四代协调的实际时长与限制见[正常流控制器](RESIDENT_NORMAL_CONTROLLER.md)。数据面/CPU历史证据复用；不逐bug创建硬件版本。

## 以下保留历史记录

### 历史记录：当前后续范围：RC1有界常驻控制器之后

北京时间2026-10-08 00:41。低速整形BULK保留与闭态学习读取竞态已修复，90秒集成及预定控制器soak结果见[当前交付](RESIDENT_CONTROLLER.md)。本开发阶段不主动寻找新边界问题。

- 下一milestone：更长正常使用观察与默认resident部署决策，保留独立恢复及原硬截止。
- P2已知限制：自然候选/WAN取得未齐、偶发SSH首包或UDP回显拒绝；有界退出，零自动fixture重试。
- 跟进但不阻塞：固件计数变化精确解释、完整普通应用factory覆盖、长期及重启恢复。
- Wi-Fi、autorate、ECN、新分类、新QoS、CPU benchmark与极端故障注入继续不扩展。

## 以下保留历史backlog；已成立的五WAN/QoS证明以STATE当前范围为准

### 历史记录：v1.1 当前交付边界

单 WAN host 启停入口已交付，真实空闲启停验证通过。下一项只为新入口的一次正常使用会话，以及解除30秒 session 上限后可持续单WAN试用；未开始改gate/常驻部署。v1 gap、更多CPU门槛、五WAN/Wi-Fi/共享预算/ECN/极端恢复均不重开为当前验收。

### 历史记录：v1 冻结后的已知限制与 v1.1 / v2

当前技术闭环完成，停止自动实验；真人体感由用户选择仅HUD而未验，不能伪写完整真人通过。

- 已知限制：NSS159连续36个echo缺口无位置/因果/稳定复现证明，未修复；只有明确v1使用损害才重新升级blocker。
- 稀疏CS2 HUD、缺失A2 HUD、软件原有Loss尖峰与没有真人主观反馈，限制体验结论。
- 仅单WAN一TCP BULK＋一UDP RT，有界UP60/DOWN30；实验后NSS关闭，常驻分类器及CAKE fallback保留。
- v1.1：正常用户体验确认；按真实需求考虑长期启用与支持范围。无需自动重放旧CPU/checkpoint/生命周期证明。
- v1.1/v2：第二WAN、五WAN共享预算、Wi-Fi、autorate、完整CAKE语义、ECN、多流公平、300Mbps长压、重启恢复、极端crash/故障注入/race、更多根因调查。均不是当前v1 blocker。
- bridge B-shaper、tc JSON、HTB dump、普通IFB/private MacVLAN直接挂NSS qdisc等兼容发现保留Issue/PR backlog，未提交上游。
- 历史BULK→BE精确撤销/新epoch重学已由NSS138/139/158证明；下方旧“待验”说法属于历史，不能据此继续实验。

## 旧支线记录（历史，不自动重开）

### 历史记录：暂存支线

这些事项不能阻塞主线，也不代表确认的上游缺陷。

- bridge B-shaper、普通 IFB/private MacVLAN 直接挂 NSS qdisc 的限制。
- ECN、tc JSON、HTB dump 兼容性。
- NSS FQ/AQM、限速精度与拥塞行为；在主线可稳定运行后验证。
- 五 WAN QoS 映射、共享下行预算、Wi-Fi、autorate。
- 原生改类后的精确撤销与重学、长期硬件过期行为，需要独立现场验收。

本地已知问题：大 JSON 发布成本；旧控制器固定 WAN5；控制器与原生 gate 的 full-mark 条件不完全一致；初始准入失败缺少逐次原因记录。已有修复或诊断不能自动提升为上游驱动 Issue。

潜在 Issue/PR 应包含仓库/文件/版本、最小复现、修改前后证据、回滚与限制。当前没有提交上游。


NSS39 新增 [本地监督组合 Issue 候选](ISSUE_TC_SUPERVISION.md)：已有最小复现、源码位置、前后等待时间和回滚证据。属于本项目集成兼容问题，未提交上游；自然 143 的完整原因仍不明。

</details>
