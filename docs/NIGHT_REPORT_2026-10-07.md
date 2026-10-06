# Athena NSS 夜间多 WAN / QoS 交付范围与晨间收尾

更新时间：北京时间 2026-10-07 07:44。本夜生产实验已结束，07:41最后一次只读核验全部通过。没有在晨间重新打开 fixture、NSS、Steam 或 CS2；没有生产配置写入。

## 已证明的范围

| 项目 | 实际证据 | 结论边界 |
| --- | --- | --- |
| 多 WAN 加速 | v16/v19/v20：两 TCP BULK＋一 UDP RT，自然跨两个或三个 WAN；B 60秒、ECM=3、20次续租 | 三条精确连接的有界硬件原型 |
| 双向分类和连接粘性 | 六 tag、上下行 bulk/RT leaf、完整 ct mark、NAT、WAN affinity 正确 | Linux 新连接 PBR 保持，NSS 不重新负载均衡 |
| 五 WAN QoS 映射 | v20 上下行各18 HTB class、11 FQ-CoDel leaf，RT prio0、BULK prio1 | 五 WAN 队列覆盖；不是五 WAN 同时 fast path |
| 共享下行预算 | DOWN18，每 WAN 保障3、ceil18可借用；两 bulk 6.72/8.28Mbps、合14.99Mbps，超过保障且在总预算内 | 观察到空闲份额借用；未证明长期精度或满载吞吐 |
| 上行与实时流 | UP60，每 WAN12硬上限；RT双向leaf drop0；v20 B内部自有echo2434/2434返回 | 小 UDP echo 不是 CS2 jitter/loss/Miss 或真人体感 |
| 恢复 | 实验结束恢复软件路径、原队列、模块、端点、FW和客户端；本次晨间重新只读确认 | NSS 当前关闭，尚未永久部署 |

CPU收益复用历史可比证据：NSS128约30Mbps上传，softirq 10.034%→5.246%→10.393%，原七项可比条件成立、NSS短窗相对低48.64%。本夜没有重新追CPU门槛，也不把该数值当成新多WAN、300Mbps或长期性能结论。

## 晨间实际终态

- 07:41:48完整收尾通过，原完整审核来源年龄1.29秒；五WAN健康，保护配置/auth/manifest保持，ECM关闭全零，无NSS准入。
- 两物理wan/lan4原mq＋各四fq_codel，所有默认选项和handle精确一致。
- 17个本夜自有端点单位均已退出、MainPID=0；临时FW规则0、原canonical防火墙基线一致、TCP/UDP测试端口关闭。
- 16个本机fixture namespace中，自有client/controller/guard/sender进程零残留。
- 四个实际只读步骤退出码均0。原准备记录“晨间未执行”保持历史原字节，新结果另存，不覆盖旧证明。

## 未完成与已知限制

1. 五WAN同时加速未验。五槽模块仅完成同6.18.44编译、源码/模型/RAM资格，从未加载硬件。v21..24五次负载前提失败及v27首TCP8.008秒超时全部在NSS前，原失败保留；不能归因NSS/固件，raw TCP问题根因仍未知。
2. v26正常应用入口已接Steam/CS2实际socket归属，18模型/46依赖/2586绑定通过，数据面沿用v20；现场inspect为0游戏/0下载/0pair。新整合factory未硬件验收，不能称正常应用或真人体验已通过。
3. 控制器仍为有界会话。真实BULK→BE时结束耦合旧代并恢复；连续新代、多流常驻、路由器重启恢复尚未交付。
4. 当前未覆盖全网，也没有完整CAKE公平性/diffserv/autorate/ECN复刻、Wi-Fi或300Mbps长期压力结论。
5. 常驻自动分类器仍NSS68/config581b5d46…c791d7；软件CAKE承担当前流量及fallback。

## 下一步

下一正常使用时做一次v26有限正常应用会话即可，不要求长期挂机。五流fixture的TCP前提问题先保留为独立后续事项，有新证据才继续；不盲重试、扩FW或修改学校/认证策略。长期连续代和扩大加速池另行规划。夜间自动任务在本次报告检查、提交、推送、实际Git archive验证后暂停；08:00后不自动开启新实验。

证据：[晨间真实核验](../evidence/morning-final.json)、[追加源码与保存边界](../evidence/morning-final-source-proof.json)、[v20硬件](../evidence/v20-five-hardware.json)、[v26正常入口](../evidence/v26-progress.json)、[v27原失败](../evidence/v27-raw-prerequisite.json)。
