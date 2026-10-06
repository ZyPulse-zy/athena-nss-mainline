# Athena v1.1 单 WAN 有界试用入口

双击 `启用单WAN试用.cmd`，然后正常玩 CS2、下载已有 Steam 内容。入口在后台等候最多十分钟；检测到**同一健康 WAN 的一条 Steam TCP BULK 和一条 CS2 UDP RT**后，只执行一段约 20 秒 NSS 加速，完整恢复后退出。没有合适流就保持软件转发，不要求新下载、挂机或重复 CPU 对照。

`查看单WAN状态.cmd` 查看当前状态，`停止单WAN试用.cmd` 请求停止。停止会取消后续准入；如果已有独立实验会话，等待当前有界会话完成和恢复，不直接杀路由器守护进程。正常单段约 20 秒，失败恢复由原独立 100 秒守护负责。恢复没有获得证明时，入口保留本地准入锁、拒绝再次启动，不把关闭控制连接当作成功恢复。

| 状态 | 含义 |
|---|---|
| WAITING_FOR_NORMAL_GAME_AND_DOWNLOAD | 只读等待正常游戏和下载流 |
| ONE_BOUNDED_NSS_SESSION | 正在执行一次有界会话；新 checkpoint、分类及内核 pin |
| COMPLETED_AND_RESTORED | 本次完成，完整恢复已核验 |
| STOPPED_NO_NSS_SESSION | 启动后未开启 NSS，已停止 |
| SESSION_REFUSED_OR_FAILED_AND_RESTORED | 会话拒绝或失败，恢复已核验；原失败只留本地 |
| RESTORATION_UNCONFIRMED | 恢复未核验，禁止新准入 |
| READONLY_CHECK_FAILED | 只读检查失败，未进入实验 |

这次交付的是可启停的**有界入口**。内核 gate 仍限制 session 最长 30 秒，控制器使用 27 秒，其中有效 B 段约 20 秒；它不是常驻 NSS 或全电脑加速。一启用只执行一段，不自动轮询开启新的实验会话。

数据面直接复用 NSS157 已实际运行的 single-B 生命周期、NSS158 独立守护/QoS/完整分类、NSS160 的程序 socket 归属和原恢复审核。没有新的路由器 Lua、内核模块或固件改动。PBR、完整 ct mark、NAT、WAN affinity、原 source6/native27/owner100 秒与字节上限保持；其余连接仍是软件 fallback。

本轮验证：11 个新增 host 调度案例、真实历史应用帧 payload 与原 builder 逐字节相等、现场后台只读启动/重复启动拒绝/停止。**新的 host 入口整段 NSS 会话尚未在硬件执行**；历史数据面证据复用，不写成新入口硬件验收或长期稳定证明。不会重新打开 NSS159 gap 支线或重复 v1 CPU 门槛。

所有运行目录、完整连接身份、nonce、checkpoint、原始错误在 `runtime/` 和本地 case 目录，均不发布。仓库只保留源码及脱敏结果。三个命令依赖本工作区已有本地凭据和已验证的运行时；公开仓库不能直接带走凭据运行。

下一步仅是正常使用时执行一次新入口会话，随后将单 WAN 会话的短租约扩展成可持续试用；30 秒上限解除前，不声称完成长期启用。真人体感仍在用户正常玩游戏时确认，不额外制造负载。
