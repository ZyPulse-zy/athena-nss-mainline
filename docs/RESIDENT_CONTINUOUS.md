# 连续合格NSS常驻

2026-10-08，取消健康代90秒退出和20分钟四次启动限制。合格流持续自动续租；分类/socket6秒新鲜度、native滚动120秒、guardian滚动180秒及失联撤销保持。实际RT mask2连续NSS 196.75秒／393采样校验／65续租，跨原90/120/180秒后主动Stop和完整恢复通过。

控制器一直运行，合格的原有流保持当前epoch并滚动续租。取消的是固定健康会话寿命与启动次数窗口；6秒来源新鲜度、30秒控制失联、CT/NAT/mark/affinity身份和停止/异常恢复仍生效。它们用于撤销失去证据的权限。

`work/resident-continuous-dev-20261008/service.ps1 Status / Stop / Start` 控制已有手动任务。现有Windows任务没有执行时长上限；本次只换其启动参数，不改其它任务或电源计划，不增加登录触发。

每个实时tick验证精确ECM、分类和身份。记录保留32采样与16续租尾部以及累计数量，1MiB记录/73728 bundle/9000 exec上限不放宽。新的native ACK实际延长会话期限；健康owner同步延长守护窗，PC失联或资格丢失结束旧代并恢复软件路径。

本地27项回归、4409 native控制/109CT/134匹配、七子集语法/尺寸及2虚拟小时通过。硬件仅RT mask2，测试流量是有限16Mbps背景模拟下载和50pps UDP echo；软件控制器本身不造流量。跨期限后主动Stop、完整保护与物理队列恢复、精确端点/FW与独立客户端守护关闭通过。

前两次夹具失败保留；初次未进NSS，第二次182秒发送器闹钟使模拟客户端提前结束，对应NSS安全撤销。未把这个P2当成固件故障。有限硬件窗口不证明长期soak或永不撤销；最多2BULK/1RT直接归属IPv4流，其它/未知走软件。实际游戏大下载丢包P1仍未关闭。

[源码适配器](../code/work/resident-continuous-dev-20261008/adapt.mjs) · [控制器](../code/work/resident-continuous-dev-20261008/daemon.mjs) · [脱敏事实](../evidence/resident-continuous.json)
