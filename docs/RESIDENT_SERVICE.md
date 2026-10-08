# 手动常驻试用进程已部署

北京时间2026-10-08 10:35，常驻进程已保留运行，当前为WAITING_FLOW。18项本地回归、8份JavaScript和2份PowerShell语法通过；真实启动、分类源推进、正常停止/锁解除、重新启动通过。四个已有相关任务的XML指纹未变，新任务无登录触发、无故障自动重启，使用普通用户权限。

进程每30秒观察已有流量，合格时调用原正常入口，每代90秒；每20分钟最多开始四代，每代新checkpoint下载/SHA/gzip和控制连接外独立恢复，恢复审核通过后才进入下一代。source6/native120/owner180/client180与全部原字节限制保持。原四代900秒控制器/360秒累计NSS、五WAN/QoS/CPU证明复用，不重跑数据面。

当前实际合格组合0、新NSS代0。两次启动前完整只读审核及两物理队列选项/handle通过，ECM关闭全零、五WAN健康、保护配置不变。这次证明的是常驻进程和正常停止/重启；真实普通负载的首次自动准入与更长soak尚待自然出现，不声称连续永久NSS或默认开机常驻。实际[部署结果](../evidence/resident-service-runtime.json)。

## 控制

原工作区执行 `powershell -File work/resident-service-dev-20261008/service.ps1 -Mode Status` 查看实际进程身份、心跳、源序列和代数。`Stop`停止新准入，当前代按原独立期限恢复后退出；`Start`重新启动手动试用，`Uninstall`只在进程停止和恢复确认后移除本任务。任务名`Athena-NSS-Controller-Manual`；[控制脚本](../code/work/resident-service-dev-20261008/service.ps1)、[调度器](../code/work/resident-service-dev-20261008/daemon.mjs)、[调度策略](../code/work/resident-service-dev-20261008/policy.mjs)。私有连接、当前部署输入和模块仍只在原工作区。

## 限制与后续

- 仅本机两TCP BULK＋一UDP RT组合，两个TCP使用已有不同自然WAN；其它/未知流保留软件路径。
- 常驻进程持续等待，数据面仍是有限代。登录自启和长期默认运行尚未验收。
- 连续三次源读取拒绝、绑定改变、入口拒绝后暂停准入；不盲重试。P0保留锁并停止后续写入，先确认恢复。
- 常态只轮转本进程的新操作性观察缓存，保留最近16组；硬件代、失败和冻结历史证据不删除。
- Wi-Fi、autorate、ECN、新类型、新QoS、新CPU与极端故障模型不扩展。

本批两处P2报告/模型错误均在本地修正，原失败留存，未因此开硬件实验。[原错误摘要](../evidence/resident-service-development-failures.json)、[白名单源码](../evidence/resident-service-source-proof.json)。
