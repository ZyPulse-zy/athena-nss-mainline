# 当前状态

更新：2026-10-03，北京时间。NSS37 已结束，最终现场审核约 18:15:57；详见 [current-runtime.json](../evidence/current-runtime.json) 与 [NSS37 证据](../evidence/nss37-normalizer.json)。

## 当前运行

- 常驻分类器已保留 NSS37，配置 `b053e05b74ffe5ea3871284838e7771bcebfc8aa8a80ecc042f60693d7769635`。
- 当前引用是私有工作区 `work/nss37/deployment-latest.json`。NSS35/NSS33 引用与证明保留历史，不覆盖。
- 只改变 `conntrack-source.lua` 中的属性搜索；worker、guardian、分类核心、backend、身份检查、分类策略、采集范围与全部时间边界不变。
- ECM IPv4/IPv6 关闭，连接、加速及待处理计数全零。认证/PBR/sing-box/Tailscale 与生产队列配置核验通过；没有实验事务、暂存、状态节点或 gate/qdisc 模块残留。
- 最终 producer 与重新安装后观测一致。保存的 last-error 是首次试装到期，属于另一个 producer，不能当作当前实例的新崩溃。

## 本轮证据

NSS36 的真实 WAN1 尝试未能进入 ECM：初始约 5.93 秒内 44 次时间余量拒绝，packet tag/gate 尚未安装，bulk/RT leaf 0 包，独立恢复通过。后续独立窗口测到发布时间挤占准入余量；这些历史证据保持不变。

本轮进一步定位属性提取成本，只将三次模式搜索改成字面量查找，并保留原来的空白边界、非空值和重复字段语义。

- **9,113 项新执行的本地检查**：9,087 项解析检查，26 项实际分类核心/leaf 生命周期模拟。覆盖重复/畸形/截断输入、确定性变异、换端口、旧流退出、mark/NAT/WAN 变化、冷却和 restart/crash 后重新学习。未向生产服务注入 crash。
- **16 对目标机 RAM 测量**：204 行真实采集文本，平均解析 CPU 27.043 → 15.470 ms；512 行内存合成文本，64.393 → 38.408 ms。降幅约 42.8% / 40.4%，全部输出相等。
- 以上是解析函数收益。背景约 0.639 Mbps，不是整机 CPU 降幅，不是 NSS 转发 A/B，也未证明高负载发布时间达标。
- 首次安装前 checkpoint 和独立守护核验通过；35 次观测健康。18:03:42 确认独立 180 秒到期自动恢复旧解析器、配置与健康服务。
- 18:05 重新 checkpoint、安装；35 次观测健康，18:07:55 提交保留。两次均未开启 ECM。

| 现场窗口 | 秒 | LAN4 Mbps / pps | busy | softirq | time_squeeze |
| --- | --- | --- | --- | --- | --- |
| 安装前 | 17.15 | 2.788 / 316.50 | 14.48% | 1.55% | +0 |
| 首次试装 | 17.13 | 0.793 / 134.97 | 14.43% | 4.96% | +0 |
| 重新安装、保留前 | 17.12 | 1.207 / 161.39 | 14.06% | 2.28% | +0 |

各窗口 35 次观测均健康，完整/精简快照的身份、分类、leaf 与有效期一致。不同自然轻负载，包含观测开销，不作前后收益相减。采集年龄 <1 秒的观测均为 6/35；保留窗口发布延迟约 0.25–0.29 秒。轻负载合格不能替代高负载准入验收。

## 当前主线控制器

`work/nss37/real-session.mjs` 已绑定新部署与 66 项文件/证明，目标 Lua 编译及完整 tag policy 往返检查通过，另有 10 项新执行的同 WAN 选择约束检查。未改变的 NSS36 消费者/backend 证明明确标注沿用，没有重新计数。

18:11:17 只读应用核验发现 CS2 RT 候选 1、Steam bulk 候选 0，同 WAN 连接对 0。本轮没有启动 fast path 试验，没有新的 NSS bulk/RT leaf 流量，也没有加速后的 mark/NAT/WAN affinity 或游戏 jitter/loss/Miss 数据。

历史 NSS32 仍仅证明 3 Mbps TCP + 20 pps 合成 UDP、WAN5 的加速数 0/2/0、leaf/完整 mark/NAT/续租/精确撤销正确。NSS36 真实高负载失败不能被这项低负载历史证明替代。

## 下一步与边界

先核验新部署，再在代表性负载下只读测发布时间和准入余量；必要时继续定位同一采集/分类发布路径的开销。条件成立后集中一次真实同 WAN CS2 + Steam software → NSS → software。现有受控子组仍为 20 Mbps，不代表整个 Steam 300 Mbps 以上可加速。

真人高负载完整闭环、同负载 softirq/time_squeeze 收益、CS2 jitter/loss/Miss、真实加速游戏改类撤销/重学、长期稳定性均未完成。暂不扩第二 WAN、共享预算、Wi-Fi、autorate 或五 WAN。详见 [PLAN.md](PLAN.md)。
