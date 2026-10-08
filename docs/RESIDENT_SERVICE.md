# dev-d：常驻异步路径错误已修复

北京时间2026-10-08 11:59。dev-c在11:49心跳后因连接初始化临时切换工作目录，异步心跳写到外部目录并发生ENOENT退出；当前进程不存在，0新NSS代。原失败、源码和空锁全部留存。路由器ECM停止且连接/加速/待处理计数全零、gate不存在，旧代恢复通过后才接续。

修复同一P2层：服务存储、心跳、锁/停止检查与进程路径固定到模块所属工作区；只读审核子进程显式cwd；启动器刷新并严格返回子进程退出码。48项服务本地回归及11 JavaScript/2 PowerShell语法通过，原异步目录错误本地复现，退出码7实际子进程检查通过。正常入口、七份数据面、分类、QoS、全部准入/期限与独立恢复保持。

当前dev-d控制器已运行并通过启动只读完整审核和两物理队列检查，源序列继续推进，准入未暂停；WAITING_FLOW，下载TCP BULK为0、游戏RT为1、新NSS代0。这是进程恢复，实际NSS仍未加速。用户下载时60–70%丢包仍为未关闭P1，不能宣称体验已修复。继续接续原正常负载，不启动游戏、制造fixture或重复数据面/CPU实验。控制入口为[dev-d service.ps1](../code/work/resident-service-dev-d-20261008/service.ps1)，[本批摘要](../evidence/resident-service-dev-d.json)。

## 以下保留历史记录

# 当前控制：dev-c 自动准入运行

原工作区执行 powershell -File work/resident-service-dev-c-20261008/service.ps1 -Mode Status / Stop / Start。任务仍Athena-NSS-Controller-Manual；只读前置接收修复，七份数据面Lua与原90秒代/20分钟四次上限不变。当前WAITING_FLOW，RT1/BULK0、新NSS0；连续/默认永久NSS及大下载游戏体验尚未验收。详见[本批事实](../evidence/resident-service-dev-c.json)。

## 以下保留历史记录

# 常驻调度 dev-b 已恢复运行；下载时游戏卡顿待核验

2026-10-08：用户报告人物回弹、延迟或丢包升高。首次自然流入口因UDP资格在下一次读取前消失，在checkpoint前退出，无生产写入；原完整恢复及两物理队列全部选项/handle检查通过。当时NSS未进入，不能把卡顿归为NSS转发故障。

修复P1调度问题：只有原入口明确证明无候选、无checkpoint、恢复通过及ECM全零，才返回等待新鲜自然流；未知失败、进入后的错误、绑定变化和P0仍停止后续准入。37项本地回归、10份JavaScript和2份PowerShell语法通过；原每20分钟四次及source6/native120/owner180/client180不变。没有新正式硬件轮次、fixture或CPU benchmark。

同名手动任务只改为dev-b启动路径，其它相关任务及触发/重启/终止设置未变。控制器已恢复运行、准入未暂停。当前控制入口为 work/resident-service-dev-b-20261008/service.ps1；进程运行与实际NSS命中分别核对，不能把等待合格流当作NSS已开启。实际状态快照见[本批记录](../evidence/resident-service-dev-b.json)。

只读18.10秒记录约405Mbps物理WAN下行、CPU忙碌84.17%、softirq62.75%、CPU0 time_squeeze增加729。游戏WAN1优先队列新增丢包0，下行排队峰值0.379ms；这证明存在软件路径处理压力，尚未证明端到端卡顿根因或体感恢复。未改学校认证、PBR、NAT/mark/affinity和十CAKE。

下一步仅观察用户原有对局和下载下的自动准入及体验；历史数据面、QoS、CPU和恢复证明复用。不启动/操作游戏，不制造新的fixture。

## 以下保留历史记录

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
