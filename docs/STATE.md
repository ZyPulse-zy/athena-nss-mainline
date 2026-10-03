# 当前状态

更新：2026-10-04，北京时间。最新现场核验见 [当前运行记录](../evidence/current-runtime.json)。

**真人 WAN1 的 CS2 UDP＋Steam TCP 已运行 software→NSS→software，ECM 稳定加速两条连接，两条 NSS bulk/RT leaf 与 mark/NAT/WAN affinity 已由冻结的实际状态验证。CPU 收益和游戏体验验收仍未完成。** 见 [NSS41 证据](../evidence/nss41-mainline.json)。

## 当前运行

- 常驻仍是 `work/nss39/deployment-latest.json`，配置 `17aaa0797d654938b654d06eaf575ba0766c845aae2a16f8e229998c5992af60`。NSS41 没有改常驻 worker、策略或有效期，同一 worker/guardian 健康。
- 本次实验先 checkpoint 下载/压缩/哈希核验，确认独立 45 秒 owner 后才临时改变一个 WAN 和物理 LAN4 队列。
- native owner 明确提前撤销，tag/队列/模块/WAN/mwan3/状态节点恢复，ECM 全零。保护配置与基线审核、闭合检查通过。独立到期已布置，本轮提前结束，未再触发到期回滚。
- 无实验残留，NSS 尚未常驻开放。认证/DHCP 身份保持；续认证没有本轮新测试。

## 已证明的真人功能路径

约 00:57:40–00:58:01，一条自然同 WAN1 的 Steam bulk TCP 与 CS2 RT UDP，zone 0、完整 mark 0x10000、同 NAT。自动分类 tag 先于 ECM 学习；B 稳定 5.17 秒，11/11 帧加速数 2，完成 1 次新序列续租。A/A2 均 11/11 帧加速数 0，队列计划和观察循环相同。

冻结硬件状态确认 TCP server-first、UDP client-first、NAT 双向元组、完整 mark、private rpwan1/物理 wan 与 LAN4/br-lan 层级、对应 bulk/RT 下行 tag 正确。B＋撤销计数窗 5.83 秒：bulk +6171 包 / 9,325,760 B，RT +517 包 / 477,890 B。RT leaf 队列丢弃增量 0，不代表端到端游戏 loss 为零。

## 性能与体验未完成

| 阶段 | 总 LAN4 Mbps | pps | busy | softirq | time_squeeze |
| --- | ---: | ---: | ---: | ---: | ---: |
| A 软件 | 347.72 | 28777 | 79.51% | 59.17% | +0 |
| B NSS | 379.98 | 31453 | 82.89% | 60.64% | +0 |
| A2 软件 | 391.11 | 32385 | 85.31% | 61.87% | +2 |

总负载上升，没有验证相同 offered load。只加速两条流，受控子组上限 20 Mbps，并非整个 380 Mbps 均加速。不能据此宣称 CPU 下降或吞吐提升。用户反馈“没注意到，无法比较”；没有客户端 jitter/loss/Miss，不能拿 RT leaf 零丢弃代替。

## 原控制器失败与重新校验

原控制器仍返回 false，该结果没有覆盖：

1. 历史后处理 `work/nss25/parse-ecm.mjs` 写死 WAN5，实际 WAN1 被误拒绝。另存通用 WAN 解析器重新检查同一份原始硬件状态，实际样本与 6 个拒绝变异通过。它不改变 native 实验，也不改冻结入口。
2. 恢复时重复使用了学习前“新 full source age <2 秒”调度，固定等待期限内未通过。随后恢复专用入口执行全部原始 <6/<9 秒持锁审核并通过，不允许 NSS 准入，不放宽审核。

83 项清单及当次身份/应用/源码已在审核前冻结；旧后处理不在该清单，新增校验源码已另行冻结。83 项不是完整依赖闭包，下一轮必须补上这个缺口。

## 本轮准备与历史

新增审核阶段诊断、按次应用封存、审核前身份与源码冻结，以及锁外等待严格更新 full publication。18 项新本地案例和 3 次最终轻载只读审核通过。初始 <1 秒、预学习 <2 秒、原始审核 <6/<9 秒、45 秒 owner 均保持。

此前普通 TCP 有限下载 27.21 秒：125.21 Mbps、最高约 3 秒 234.58 Mbps，busy 46.55%、softirq 28.35%、squeeze +136。104 帧 full age 最高 4.27 秒，3 次原完整审核通过，未复现 NSS40 原失败；观察成本包含在数据内。不能作为游戏或 NSS 收益验证。

[NSS40](../evidence/nss40-mainline.json) 的真实 323 Mbps、4/94 次只读准入与写前过期失败、72 份历史冻结证据保持。[NSS39](../evidence/nss39-mainline.json) 的实际独立到期证明保持。

下一步仅完成通用 WAN 解析器/依赖绑定与恢复审核修正，然后在同一 WAN 稳定负载与受控份额，集中验证 CPU 和游戏体验。第二 WAN、共享预算、Wi-Fi、autorate 继续等待。无需持续挂游戏或下载。
