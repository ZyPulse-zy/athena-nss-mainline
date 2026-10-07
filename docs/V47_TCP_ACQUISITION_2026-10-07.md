# TCP 载荷取得有界定位与一次入口验收

北京时间2026-10-07 19:25。当前 v45 入口原24模型／3406绑定复用，未改分类、QoS、七份 Lua、PBR、8秒首包、30秒自然取得窗口、重试或字节上限；不操作 CS2／Steam。

## 已冻结 v46 失败的定位

原四路首次同时收到 payload 的10.71秒包括 tcp2 首次8秒无首包后的原有重试；不是四次初始握手全通过。首个 `sshd` 日志标签查询返回0行，随后只读同一45秒窗口的 SSH unit，实际得到20行 `sshd-session` 日志，其中8次公钥接受、4次认证前关闭／重置。服务器时钟读回与 PC 之间约-0.13至+2.63秒。

这些日志支持将调查范围留在 SSH 载荷取得阶段；没有证明 MaxStartups／penalty、NSS／firmware／gate／lease 是原因，也没有完成失败子进程到每一条服务器日志的精确对应。根因仍未知，不改服务器 SSH 限额、认证策略或学校策略。

## 本次唯一入口验收

用户要求继续后，新的只读检查确认原入口 RESTORED／无锁、端点端口和单位0，再执行一次同字节入口。初始四个 PID 约0.092秒齐备，四路 payload 首次齐备约2.92秒。TCP 原自然取得保留 WAN1／3／4；tcp3 轮换至第4候选后8秒没有首包，按原限制退出，13次匹配读后五 WAN pair0。

客户端实际30.36秒，TCP payload 97992704字节，软件 fixture UDP 1327发／1319返。没有 NSS checkpoint、owner、stage、模块或 ECM；没有 B 窗，不将停止边界 UDP 未返当作 NSS 丢包。**SSH 首包取得拒绝再次出现，完整可复用入口未验收；NSS 五 WAN 核心历史验收保持。** 本次不继续重开 fixture。

## 实际恢复

等待原180秒 FW 独立守护自然到期后，精确端点关闭、规则0、canonical基线通过；自有客户端／独立210秒 guard退出、残留0。最终完整审核 source1.36秒／selectors4，五 WAN 健康、保护配置不变、ECM关闭全零。两物理wan／lan4原mq＋四fq_codel全部选项／handle一致，RESTORED／锁解除。NSS68分类器不变，heartbeat保持暂停。

v42 的五流60.01秒／ECM5／20续租、2373RT全返、十tag／leaf／完整mark／NAT／affinity与恢复继续复用；DOWN18共享借用、UP60每WAN12硬上限、RT prio0／FQ-CoDel保持。当前已知限制是测试载荷的 SSH／自然WAN取得，不能把它写成已证明的 NSS 数据面故障或已解决的问题。

用户对“入口完成后尝试常驻 NSS”的授权保留；前置入口闭环尚未通过，本次没有启动常驻试用。后续只处理有证据支持的连接取得改动，不重复核心／CPU证明或为配齐WAN无条件循环。

证据：[有界定位与入口](../evidence/v47-tcp-acquisition.json)、[完整恢复](../evidence/v47-restoration.json)、[源码](../evidence/v47-source-proof.json)、[当前入口](BOUNDED_MULTIWAN_ENTRY.md)。
