# 私有控制器问题候选：高负载进程发现耗时

状态：本地 backlog。未提交上游。当前证据指向本工作区控制器，尚未归因于 NSS firmware / qca-nss-ecm。

问题文件为 `code/work/nss49/core-guard-phase.lua` 的 `scan` / `waitFresh` 和 `code/work/nss49/classifier.lua` 的 `candidates` 调用路径。core guard 本身不修改。原 helper 在缓存的 `sleep 5` 子进程退出后，全机枚举最多4096个进程，读取每项stat/argv/wchan；回调还会间隔读取原完整 consumer 分类。学习前要求实际子进程换代、读取与前次间隔≤200 ms、绝对出生年龄≤200 ms。

最小复现按 [只读时序](../evidence/nss51-phase-timing.json)：固定已完整验证的 guard PID/start，执行原 candidates/readContext/Consumer.inspect，三个最长约7秒的waitFresh。每帧先后确认ECM停止且所有计数为零，保留profiler原始私有行。分别在暂停下载与真实Steam约350 Mbps时观察；不得暂停、signal、重启或编辑guard，不得为复现开放ECM。

| 观察 | 通过 | 最长回调 | 结论 |
| --- | --- | --- | --- |
| 原 helper，暂停下载 | 3/3 | 90 ms | 轻载可捕获新子进程 |
| 原 helper，实际下载 | 0/3 | 740 ms | 读取超出200 ms条件 |
| NSS51，暂停下载 | 3/3 | 50 ms | 固定 guard 子进程发现可工作 |
| NSS51，实际下载 | 1/3 | 250 ms | 缩短耗时，但仍不稳定 |

完整 consumer 路径保持，未使用的 adapter 函数和 profiler 整行注释仅为适应传输限制而省略。不同窗口没有证明 offered load完全相同，不能用此表计算整机CPU收益。

NSS51修改后只读全机stat的父进程；仅为固定guard直接子进程读完整身份，结束再次核验guard，保留缓存子进程完整核验和初始全局唯一性检查。22项目标模型、两次实际只读以及140项新入口绑定通过。但实际控制器随后在分类断言拒绝，没有新的NSS B；不能将其记为driver失败，也不能称稳定修复。

NSS52只优化父进程字段提取，旧22项模型重放与新增12项解析差分、两次轻载实际只读通过，waitFresh字节未变。10,000遍纯解析0.623336→0.050266秒，不是全机转发。见 [候选证明](../evidence/nss52-phase-qualification.json)。未安装、未绑定生产入口、未验证新的高负载窗口；下一步保持原边界完成高负载读取与同一应用对的持续性，再重新绑定候选。

第一次/第六次的Selected class is not admitted未记录具体槽位。后续连接退出或17:14下载完成只能作为后续状态，不能倒推错误帧。应另加原采样中的精确只读诊断，不增加第二份可能漂移的快照或放宽分类条件。

# 私有审核问题候选：历史服务 PID 基线

NSS50第三次原入口在任何checkpoint/暂存前拒绝：sing-box-athena core/guard在当前状态健康，命令和运行状态与NSS47安装基线一致，仅PID不同。没证明为何重启。`code/work/nss50/service-epoch.mjs`仅接纳实验前这两项PID变化，然后固定本次服务集合/命令/实例；任何实验期间变化仍拒绝。分类器继续用原生PID/start/argv/锁归属审核。

[24项本地边界案例](../evidence/nss50-service-epoch-tests.json)与目标原完整只读审核通过。新128项绑定已实际用于两次软件A暂存并完整恢复；它不是放松服务健康或忽略运行期变化。该问题也没有作为上游qca-nss-ecm缺陷提交。
