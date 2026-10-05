# 本地 Issue 候选：BusyBox timeout 与 mutation subreaper 的回收等待

状态：可复现的本项目兼容问题；NSS39 已局部修复。没有提交上游，不判定 BusyBox/NSS/内核自身有缺陷。

## 对应代码和环境

- 仓库：ZyPulse-zy/athena-nss-mainline。
- 旧 worker：`code/work/nss39/original-worker.lua` 的 bounded()/direct()；外层 `code/work/nss11/group-runner.c` 使用 PR_SET_CHILD_SUBREAPER、进程组 TERM/KILL、waitpid(-1)。
- 新 worker/helper：`code/work/nss39/worker.lua`、`tc-command.lua`。
- 目标 BusyBox 1.38.0。官方 [发布源码](https://busybox.net/downloads/busybox-1.38.0.tar.bz2) 的 coreutils/timeout.c 与 libbb/vfork_daemon_rexec.c 显示独立会话监视进程及一秒轮询。下载校验已验证，但固件补丁未逐项比较。

## 最小复现与前后证据

使用已构建且核验哈希的本项目 group-runner 运行：外层 6 秒；内层旧 timeout -k 1 2；leaf 为立即退出或睡眠 4 秒的隔离 Lua。命令只属于 fixture，不向生产 worker 注入故障。

- 正常 leaf：旧完整 wrapper 约 1.02 秒；内层超时可返回 143、外层 1；外层独立缩短到 1 秒的 fixture 返回 124，旧清理约 3.02 秒。
- 新 helper：正常约 0.18 秒；超时确认 signal 15，忽略 TERM 时确认 signal 9；外层 1 秒 fixture 约 1.18 秒、124，全部 fixture 子进程消失。
- 真实只读队列/过滤器 4/20 次各四对：完整 wrapper 1037.5→215 / 1150→395 ms。子命令本身略慢，改进来自回收等待。

原生复现入口 `test-timeout-path.mjs`、`test-tc-native.mjs`、`benchmark-tc-readonly.mjs` 依赖私有连接封装，不能直接当安装包。仓库内安全离线入口为 `tools/replay_tc_supervision.py`。结构化证据见 [NSS39](../evidence/nss39-mainline.json)。

## 修改和边界

直接 fork/exec 同步 tc，维持在外层原进程组中；不再派生 timeout 独立监视进程。只允许既有参数，非阻塞有界双管道、2 秒终止、确认回收。6 秒外层组清理、失效关闭、原精确恢复不变。补充 outer raw status/耗时，不用返回 143 猜信号来源。

16 模型、13 参数、8 原生隔离案例和三次真实独立到期恢复通过。未对生产批量写入注入故障；未知清理继续终止。没有原自然故障的阻塞栈或信号证据，不能说修复了那次故障的所有成因。没有高负载长期稳定性或 NSS 性能结论。

潜在 PR 仅应围绕本项目 worker 的监督组合与诊断，继续保留明确默认拒绝；向 BusyBox/NSS 上游提交前还需要各自最小复现与归因。

## NSS68自然故障补充（非新最小复现）

2026-10-05 10:32:50，保留发布候选worker17138的apply子进程在TCCommand.run中触发“tc child cleanup not proved; outer mutation must terminate”；10:32:52外层rawStatus256/4.35秒。原代码2秒命令、0.15秒TERM和0.85秒KILL回收仍未得到reaped证明，因此原逻辑拒绝并退出，procd随后恢复23634，guardian17139连续。配置和所有保护/ECM终态审核通过。

该次发生在10:34恢复下载之前。NSS68候选与47的整个TCCommand监督片段字节相同，47在08:37也有另一次apply256，但后者是另一断言，不能合并为同根因。publication JSON成本优化不能据此判定为故障原因，也没有证据指向NSS或内核缺陷。

当前缺失具体tc argv/child PID、waitpid中间状态及阻塞栈，不能给出新的可靠最小复现或提交上游。下一次若自然复现，应在既有边界内保留这些诊断，而不是放宽2/6秒或清理证明。该发现不授权新生产改动。见 [实际证据](../evidence/nss68-mainline.json)。
