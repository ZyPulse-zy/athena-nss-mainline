# 正常应用窗口：Steam 恢复、限时下载与真实终态

更新：北京时间 2026-10-07 10:12。本轮承接用户要求继续推进，并取得一次 Hades 家庭库限时下载许可。Steam 已恢复可用，Hades 下载真实达到约 32Mbps，原 180 秒独立客户端守护自然退出。**正常应用 NSS factory 尚未执行；没有新增 checkpoint、stage、模块加载、ECM、CPU 或真人体验验收。**

## 实际结果

| 项目 | 实际证据与结论 |
| --- | --- |
| Steam 恢复 | 当前已登录且界面可用。之前两次 c0000005/ntdll.dll 启动失败原记录保留，原因未定；本次成功重开不等于长期崩溃问题已修复 |
| 入口接续 | v31 的 pre-stage TCP 选择原义保持；新目录仅改引用路径、本次 10:45 截止和客户端临时 32Mbps 描述。2651＋36＝2687 绑定、57 相对依赖/语法通过，复用既有 18 选择模型及 14 实际拒绝帧模型；未重跑模型或完整 factory |
| 默认 inspect | 在启动游戏/下载前现场只读 0 游戏、0 BULK、0 pair；没有 router 配置写入。这不是负载期间的自动分类证明 |
| 正常下载 | 获用户明确许可后，Hades 选 D 盘、保持快捷方式选项不变，未购买或启动 Hades。界面见 1%/31.9Mbps，临时限速 32000Kbps；PUBG 原更新先前自然完成，Crosshair X 小更新保持已安排 |
| 游戏连接 | Defusal Group Alpha 死斗第一次被 remote host 关闭，发生在 NSS 启动前，根因未知。原守护内只再匹配一次，最后见搜索 00:01；之后未观测到实际连接结果或 jitter/loss/Miss HUD，不能标游戏正常或归因 NSS |
| 客户端期限 | 原守护 180 秒自然到期，精确自有 CS2/Steam 退出，guard/controller/CS2 零残留，未重置期限。重新打开 Steam 作设置恢复时下载自动续传，随后经 UI 暂停，最后网络/磁盘 0bps，下载量显示540.5MB/5% |

**必须区分守护退出和下载总时长。** 守护证明的是这一测试窗口的精确应用退出；手动重开 Steam 的自动续传已保留，未测累计下载秒数，因此不能写成“累计下载严格不超过180秒”。重新打开时先暂停下载，再清空本轮数字、关闭限速，视觉核实原 bit/s 显示、游戏时允许下载和下载地区保持。Hades 部分内容保留，未启动、购买或删除其它内容。

## 当前终态

10:09 的原完整只读 audit 通过，source1.60秒、native审核4 selectors，保护配置/服务epoch/五WAN健康保持，ECM关闭全零；两物理 wan/lan4 的原 mq＋四 fq_codel 所有选项及 handle 一致。没有新端点、fixture、生产配置或 NSS 会话。本轮36份资格源码、11份原始本地输入和完整守护结果已按新目录保存。

当前 Steam UI 设置已恢复，Hades 已暂停，CS2 和本轮测试守护已退出。前一轮 v31 的“原UI未恢复”仍作为当时的真实证据保存，本次新观察单独补充。

## 剩余主线

已成立的 v20 三流多WAN/五WAN队列/DOWN18共享借用/UP60每WAN12硬上限/RT prio0/FQ-CoDel硬件结果和历史CPU结果继续复用。剩余只做一次正常应用 factory：先确认 CS2 已连接，再在新的明确下载许可窗口内开启已暂停内容、独立客户端守护、真实程序三流选择、新 checkpoint下载/SHA/gzip及控制连接外恢复写前核验，随后有界NSS/恢复。下一下载窗口的许可尚待用户回答，不延长原守护或盲重试五流。夜间 heartbeat 保持暂停。

证据：[入口资格](../evidence/v32-normal-entry-qualification.json)、[客户端实际窗口](../evidence/v32-client-window.json)、[终态](../evidence/v32-normal-restoration.json)、[源码保存](../evidence/v32-normal-source-proof.json)。
