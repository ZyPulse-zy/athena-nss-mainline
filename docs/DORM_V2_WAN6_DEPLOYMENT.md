最新游戏优先策略已经启用，详见 [游戏规则与风险核验](DORM_V2_GAME_WAN6.md)。下文保留为六账号部署时记录。

# WAN6 双向 NSS 已部署并实测

当前六个校园账号均在线，六账号 source/native 已成套安装，NSS 为 `native-running`、`sourceFresh`，pending/未确认均为 0。第六账号使用 `campus6/rpwan6/rpifb6`、表 106 和原完整 WAN mark 掩码；既有 DHCPv6 `network.wan6` 保留。新上行/下行 NSS 标签为 BE `7e65/7a65`、RT `7e66/7a66`。46 个控制器/平台文件及 12 个 source/helper 文件哈希核对通过，来源和预算覆盖十二个软件根。

## 真实连接证明

使用一条新 LAN TCP/TLS 连接进行小流量验证，临时规则仅匹配这条原始首包，不迁移已有连接。64.39 秒、32 样本中，18 个采样同时确认精确 CT/NAT/full mark/zone 身份、CREATE ACK、双向标签和 IGS 方向；标签 mismatch 为 0。16 个相同 generation/serial 的硬件 RX 同步区间，上行归属增量 **15,996 字节**，下行 **26,846 字节**。这是逐流进展，未使用全局字节冒充 WAN6。

连接正常关闭后，同一绑定到达 firmware-absent 状态 6，响应 ENACK 4/error 5（条目已不存在）；这不是成功 REMOVE ACK。临时验证规则已移除。HTTPS 服务返回 400，只证明本次 TCP/TLS/NAT 通路，不代表游戏或该服务功能验收。

## 保护与实际修正

五个原账号的地址/MAC 身份、认证与 autorate PID、代理/Tailscale 及其他核验保护服务身份保持；原网络/防火墙段、物理 DHCPv6 接口、无线配置和十个软件根句柄/固定选项保持。NSS owner、所拥有 core guard、source、必要 shaper/health/auth watcher 按已授权窗口切换。原磁盘 ECM/NSS/ingress 模块不变，receipt 副本仅按原 RAM 生命周期加载；没有重启路由器、刷机、改 EDMA 或部署无线候选。

首次安装把 Python 的 POSIX 权限数值 384 传给需要 600 形式的 nixio API，在首个候选文件完成安装前失败。独立 guardian 已实际恢复原五 WAN，并逐项复核；失败记录保留。修正后先在目标私有目录验证全部 46 文件的权限、内容和原子安装，再建立新的私有检查点完成当前窗口部署。目标没有 stat 工具，新增认证入口改用已有 Lua/nixio 严格验证 root:root/0600/普通单链接文件。校园凭据只用于路由器私有认证配置，未写入提交、测试、命令参数、报告或 PR。

现场修正持久 PBR 文件遗漏的 NAT/forward，并使它与运行时计划完全相同。原 fw4 `accept_to_wan` 中的设备集合只有原五账号，不能简单跳入该别名链就认为新设备已放行；现仅为 rpwan6 在此链内追加 invalid-drop 与 accept，保持原五账号别名。新增规则都有独占注释，便于精确回退。第六软件退路的冷启动句柄固定为 8061/8062，与 source 捕获合同一致；现有队列未改动。

## 测试、回退及限制

最终五/六账号各 13 Lua + 2 C 回归、51 Lua/12 shell 语法通过；目标原 Lua/jsonc 上四套虚拟 I/O 模型通过。新增一致性检查覆盖运行时/持久 PBR、NAT、LAN forward、NAT 泄漏保护、回退对象标签及第六冷启动句柄。已应用的新增 nft 事务均先通过目标 check-only。6.18.44 gate/receipts 交叉构建沿用已验证产物；本次后续修正没有改变 native 模块输入。

新的 root-only 检查点保留原文件、source 指针、按 inode/boot 退休的原 RAM owner、候选哈希和“原不存在”记录。部署 guardian 在已验证提交标记后正常退出；native 自身的独立 guardian 和有界恢复继续运行。完整回退顺序为撤新流入口 → 精确 native 恢复 → 候选十二根 source owned 清理 → 停止第六账号/隔离 table106 → 按候选哈希恢复文件/原 RAM 与指针 → 恢复原五 source/native → 两次完整新鲜 CT 读确认无 WAN6 mark 后移除 route fence。不会全局清 CT 或迁移既有 NAT。

首次失败后的原五恢复是真实执行；完成六账号后的全平台回退没有为了演练而再切换。冷启动逻辑已有静态/模型检查，**未重启实测**。未进行拥塞/故障注入、校园共享端口容量或六账号并发 100 Mbps 测量，也未读 NSS 队列 drop 统计或完成长期/真人游戏验收。

**游戏首包分流仍关闭，普通连接池仍是 WAN1–5。** 第六账号与 NSS 通路已可用；游戏策略需排除清单与首包误识别风险单独评估后再启用。

[结构化部署证据](../evidence/dorm-v2-wan6-deployment.json)
