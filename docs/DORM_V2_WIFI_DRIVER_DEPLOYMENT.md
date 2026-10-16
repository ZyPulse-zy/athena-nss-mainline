# 001/002 无线驱动修复已部署，保留原 NSS ABI 与 CN 修正

2026-10-12（UTC+8），六 WAN 和保守游戏分流任务完成后，基于远端 2a04380 串行执行本项目。沿用用户已给出的部署许可，没有重复询问。仅替换 ath11k/mac80211，包含 001 peer drop 清零、002 host queue 初始化及 004 既有 CN shim 的源码移植；不应用 003，主机统计结构仍 196 字节。

## 真实实施与失败记录

管理路径确认是有线 LAN4。新 root-only 检查点保存原四个无线模块、候选、模块参数、boot、保护文件及入口哈希。候选只 strip-debug，代码/常量/模块元数据/导出记录保持；磁盘容量足够。独立 setsid guardian 脱离 SSH，等待提交标记；失败或到期时按所有权验证恢复原模块。

七项本地执行器/guardian/持久化故障模型通过；目标独立 guardian 的模拟加载失败恢复也通过，所有内核 I/O 是替身。实际驱动切换按精确 native stop/恢复确认 → wifi down → 卸载 PCI/AHB/ath11k/mac80211 → 加载候选 mac80211/ath11k（原参数）和原 PCI/AHB → wifi up → 启动原六账号 native → 检查顺序。

首次真实 RAM 试装的验证调用遗漏 checkpoint 参数。独立 guardian 实际恢复原模块，但其最后验证也因同一遗漏报告未确认；随后带正确参数的完整人工执行检查通过，六 WAN/source/native、原磁盘模块及保护恢复已核实。这不是“模拟回退”，也没有隐去该失败。此前故障模型没覆盖真实验证调用契约，已增加目标真实 check action；修正后验证通过。

第二次使用新检查点试装，实际验证全部通过后才原子写入两个持久模块、校验哈希并再次验证，最后提交 guardian。两个 RAM source 路径、成功 insmod 过程和私有日志保留；磁盘模块哈希确认如下：

| 模块 | 持久 SHA256 |
|---|---|
| ath11k | afff499982dccf947ed3c579f7772791bfdd9dfa73dc87b7660cc17add33f3e3 |
| mac80211 | e40c564ddfeba94339a6b77f7f717405f5b118dffb126e74f4cfd9a4ea03066e |

NSS/mesh/cfg80211/总线模块保持原版，nss_offload=1、frame_mode=2 等模块参数保持。没有刷机、整机重启或改变无线参数；无线客户端确有短暂断开/重新关联，native 及其拥有的 core guard 按生命周期停止/启动，其他核验的认证、source、autorate、代理/Tailscale和健康服务没有重启。boot、五账号身份、六账号在线、保护配置、既有维护文件和原十软件队列合同保持。

## 加载后验证与口径

三个 AP 恢复，实际 5 GHz 为 36/5210MHz/80MHz、149/5775MHz/80MHz，2.4 GHz 为 6/2437MHz/20MHz，CN 5735–5835 MHz 的 80 MHz 规则通过。新 native 为 native-running/sourceFresh，pending/未确认零。source/native 重建会重置实例计数，不把前后累计数作同代差值。

被动 diagnose 30 完成，单读最大约 0.02 秒，来源间断零；本窗没有合格 RT/NSS 流，也没有真实游戏命中。因此零 mismatch、零全局字节或没有事件不能证明实际新流加速、零丢包、延迟收益或最终空口优先级。未查询硬件队列 drop、未造流量。有限内核末段日志复核不是完整 boot 审计。

实际冷启动、完整候选持久化后的回退演练、真人游戏和同机 RT/BULK 最终空口 TID/AC仍未验收。源码所示 NSS/HAS_TX_QUEUE 绕过 host TXQ/AQL 的结论未改变。

003 仍不部署：原两端实际 196，配对候选 212 不等于真实 firmware wire ABI 已确认；当前固件指纹尚无权威结构/实际消息边界证据。不会把该缺口变成猜测参数修改。自动续办在完成可安全部署范围、记录此技术阻塞后停用，避免重复切换；PR #1 保持草稿、不合并。

[匿名部署证据](../evidence/dorm-v2-wifi-driver-deployment.json) · [CN 兼容构建](DORM_V2_WIFI_STABLE_CANDIDATE.md) · [已安装观察工具与命令](DORM_V2_WIFI_OBSERVER_DEPLOYMENT.md)

运行维护入口：`/usr/lib/athena-dorm-native/athena-qos wifi-diagnose 30`。原始资料只保存在 root-only 目录，不进入 Git。驱动执行器源码是维护记录，须由已核验的私有检查点调用，不是任意路径上的通用安装器；不可直接重复执行本次 run/persist。
