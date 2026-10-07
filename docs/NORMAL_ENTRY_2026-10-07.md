# 正常应用入口：写前拒绝、选流修正与当前终态

更新：北京时间 2026-10-07 09:14。本次承接用户“继续”，实际使用已有 CS2 死斗及已排队的 Steam 更新。没有启动 NSS、checkpoint、detached stage、模块或新的加速代。正常应用多 WAN factory 和主观真人体验仍未验收；夜间 heartbeat 保持暂停。

## 实际结果

| 步骤 | 结果 | 范围 |
| --- | --- | --- |
| v30 正常应用会话 | Inferno 死斗、已有 Dead by Daylight 更新；程序归属读取为 1 个 CS2 RT、24 个 Steam BULK。完整审核后，原第一个 TCP 在合格应用候选中缺失，原 UDP 与第二 TCP 保持；入口写前拒绝 | 2615 项实际输入及源码副本逐字节冻结；没有 checkpoint、stage 或 ECM。缺少候选不能当成精确 CT 已退出 |
| v31 修正 | 固定原游戏 UDP，完整审核后选择当前应用 BULK；checkpoint 下载/SHA/gzip 后，按原 TCP 槽的 WAN、完整 mark、zone、NAT 地址再选当前 TCP，之后才形成不可变 owner/gate | 只改 host 的 pre-stage 选择；原 native/Lua/QoS/分类阈值、期限及 immutable candidate policy 保持。没有对已加速流换 tag 或重定向 gate |
| 修正验证 | 14 项模型使用实际拒绝帧；新选择接受与原 UDP、WAN 约束、错误 mark/分类/保护输入/tag 拒绝通过；原不可变 refinement 仍拒绝 TCP 变化。2651 绑定、61 相对依赖与源码语法通过 | 是离线修正资格，完整 factory 未在模型或硬件执行 |
| v31 本次正常负载 | Mirage 死斗、已有 PUBG 215.8 MB 更新，临时 8000 Kbps；只读识别 1 RT、0 合格 BULK，未配齐正常三流。独立客户端余量不足以完成完整 60 秒段 | 没有调用完整控制器或新 checkpoint/stage；没有重置 180 秒期限或再开负载重试 |

v30 软件段 HUD 见 ping12ms、上下行 loss0.0%、绿色 jitter 图；20ms只是图轴刻度。DBD 更新随后自然完成。v31 scoreboard 见 ping11ms，jitter/loss/Miss未显示。助手没有代替真人实际操作，因此这些只读观察既不是 NSS 体验收益，也不是主观真人验收。

## 恢复与未完成项

v30 拒绝后的原完整 audit 来源3.94秒，保护配置、服务 epoch、五 WAN 健康保持，ECM关闭全零；所有 baseline 检查和原 ruleset 对照通过。此后没有路由器配置写入。09:09新的两物理默认队列读取确认 wan/lan4 原 mq＋四 fq_codel 所有选项和 handle 一致。

两个独立客户端守护均在180秒自然到期，精确自有 CS2 和 Steam 退出，原 guard 和测试控制器零残留。PUBG 已在到期前暂停，界面网络/磁盘0bps；原 Steam 限速关闭已在界面恢复。未声称未启用的数字字段逐字节恢复。

**原 Steam UI 恢复未确认。** 重开先返回无可用窗口；按实际进程路径重开短暂出现登录窗口，捕获前已消失，后续进程/窗口库存为0。没有操作登录或输入凭据，原因未确定；客户端进程退出通过不能代替 UI 恢复通过。这项未完成状态保留，不能把本轮写成完整客户端或正常应用验收。

## 已成立范围与后续

沿用 v20 硬件证明：两 TCP BULK＋一 UDP RT 跨两个或三个 WAN、60秒/ECM3/20续租，六 tag/leaf、ct mark、NAT、WAN affinity 和恢复成立；五 WAN 上下行各18class/11leaf，DOWN18共享借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel。没有新增五WAN同时fast path、长期常驻或CPU结论，历史CPU证据无需重测。

v31已冻结并受当次09:30截止约束；下一次正常使用须以新目录、新截止和实际输入绑定承接这项修正，不能编辑原冻结入口或复用过期授权。先恢复正常Steam客户端，再在自然配齐两不同WAN的真实Steam BULK与原CS2 RT时完成一次有界正常会话。无需挂机、新增游戏下载或重复原型/CPU实验；本次不再自动开始新硬件轮次。

证据：[v30拒绝](../evidence/v30-normal-refusal.json)、[v31资格](../evidence/v31-normal-entry-qualification.json)、[实际帧14模型](../evidence/v31-last-selection-models.json)、[本次只读条件](../evidence/v31-normal-inspect.json)、[终态与UI未完成](../evidence/v31-normal-restoration.json)、[源码保存](../evidence/v31-normal-source-proof.json)。

首次 staged whitespace 检查在两个继承 v26 的 fast-path 空白行处拒绝，提交链在 commit 前停止。仅这两个新副本采用路径限定属性，源码及2615冻结输入不改；更正后检查通过。[原拒绝与字节对照](../evidence/v31-publication-whitespace.json)。
