# 正常 CS2、Steam 的多 WAN 有界入口

默认执行只读检查：

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v26-normal/session.mjs' inspect
```

入口直接复用已有程序 socket 归属检查，选取两条实际分类为 BULK、出口 WAN 不同的 Steam TCP，加一条已获 RT 预算的 CS2 UDP。游戏 WAN 可以与下载相同，也可以是第三个 WAN。PBR 仍由 Linux 为新连接决定；三个已选 CT 保留完整 mark、NAT 和出口。

有符合条件的正常流时，`session` 模式执行一次 60 秒的 NSS 会话，随后完整恢复。没有符合条件的流就退出并保持软件转发，不启动游戏或制造下载。本次夜间执行授权在北京时间 2026-10-07 07:40 截止；此后 `session` 不会开启新实验。

```powershell
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/v26-normal/session.mjs' session
```

此入口使用已在硬件运行的三槽 gate 和五 WAN 队列政策：共同下行 18 Mbps、每 WAN 保障 3 Mbps并可借用至18 Mbps；共同上行60 Mbps、每WAN12 Mbps硬上限；各WAN的 RT leaf 保留1 Mbps保障、优先级0，BULK优先级1，FQ-CoDel采用target5ms、interval100ms和1024流。其余流继续软件 fallback。

数据面 Lua、native、tag builder 和 checkpoint／独立180秒恢复沿用 v20 的确切源码。新增正常程序选择器有18个离线拒绝与选择案例；46处相对依赖存在检查通过。当前现场只读检查为0游戏、0下载、0准入，没有新增NSS会话。**新的正常程序整合入口尚未完成硬件验收**，这些检查不能代替一次正常CS2和下载使用中的实际结果。

异常或旧 flow 改类会结束这三个 CT 的旧代并恢复软件路径；不能给已加速流直接换tag。这里交付的是一次有界入口，长期常驻和自动连续新代仍在后续工作中。运行记录、原始CT、nonce、checkpoint和二进制仅保存在本机。
