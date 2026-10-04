# Athena NSS 主线记录

最新 [NSS64](evidence/nss64-mainline.json)：完整JSON发布候选、319条真实快照编码CPU约23.92%改善、目标精确编译；尚未安装，整机/高负载收益未验证。现网仍47、ECM关闭全零，原完整审核/清理通过。下一步直接单项checkpoint/独立撤销发布测试，再补可比单WAN A/B/A2；不重复准备或继续装新游戏。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md) 和 [候选](docs/ISSUE_JSON_PUBLICATION_COST.md)。下方NSS63为历史。

最新 [NSS63](evidence/nss63-mainline.json)：再次验证真实单WAN CS2 UDP＋Steam TCP进入NSS bulk/RT leaf，实际取得A/B HUD；A2被计数检查拒绝。304→262 Mbps负载不匹配，softirq下降不能作为收益。常驻仍47，五次临时暂存均撤销，最终ECM关闭/完整审核与清理通过、游戏HUD恢复。最新241项入口在高负载完整来源过期时写前拒绝；下一步只解决真实发布/审核延迟，随后补同负载完整A/B/A2，不重装/重放旧准备或扩WAN。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)、[问题定位](docs/ISSUE_NSS63_MAINLINE.md)。

Athena AX6600 网络优化研究。唯一主线：**自动识别游戏流 → NSS RT / bulk leaf → 真人 CS2 + Steam 高负载闭环**。

这是私有研究仓库，用来跨对话保存代码、可核对证据和下一步。现场凭据、完整连接元组、路由器配置备份和模块二进制仍保存在原本的本地工作区。

## 从这里继续

1. 阅读 [当前状态](docs/STATE.md) 和 [下一步](docs/PLAN.md)。
2. 阅读 [操作约束](AGENTS.md)，核验现网，再考虑任何写入。
3. 通过 [实验记录](docs/EXPERIMENT_LOG.md) 与 [证据索引](docs/ARTIFACT_INDEX.md) 区分实测、模拟和假设。
4. 每轮更新状态、证据和代码清单，提交一个明确说明结果的 commit。

## 当前结论

- 当前常驻 NSS47：NSS46 三项可靠性修复继续保留，仅加每观察重置、各1024项的纯地址缓存。目标解析CPU约下降26.4%，不能写成整机收益；独立180秒自然恢复/保留安装/完整审核通过。
- NSS49 完整单WAN控制器成功：真实在线CS2＋Steam，ECM0→2→0，bulk/RT leaf、mark/NAT/WAN affinity正确，续租和精确恢复通过。绑定121项输入、99项本地入口检查、13项目标RAM模拟。见 [最新实装证据](evidence/nss49-mainline.json)。当前ECM关闭，剩余同负载客户端验收；不重复准备。
- NSS39 历史 3 次独立自动回滚通过，最终安装核验保留。冷启动旧 producer 被拒绝的记录未隐藏；现流程先验证当前实例就绪。
- NSS38 精简准入和逐次诊断候选已绑定 NSS39 的 68 项清单，目标原生完整源码模拟、tag 往返与配置检查通过。
- **NSS49 助手在线观战功能闭环已完成；真人WAN1历史证明保留。NSS49三段总下载168/194/171 Mbps不匹配，B段HUD缺失，不能宣称CPU/真人游戏收益；第二轮下载完成、写前等待。**
- NSS41 已执行真实单 WAN A/B/A2：加速数 0→2→0，bulk/RT leaf +6171/+517 包，mark/NAT/WAN1 正确。原失败与恢复证明保持；总负载 348→380→391 Mbps 上升，没有收益结论。
- NSS45 历史两项分类器修复分别完成短时试装、独立 180 秒自然恢复和原完整审核，当轮未长期保留，NSS 全程关闭。114 个独立本地案例、目标 RAM 重放、7 个真实 query 子进程案例通过；当轮软件过期候选未安装。见 [历史证据](evidence/nss45-mainline.json) 和 [恢复问题记录](docs/ISSUE_CLASSIFIER_RECOVERY.md)。
- NSS44 真实 WAN1配对、写前过期拒绝、自然退出/首次恢复失败保持；当时未绑定的等待候选已由后续新轮次另行验证。见 [历史证据](evidence/nss44-mainline.json) 和 [发布问题记录](docs/ISSUE_CLASSIFIER_PUBLICATION.md)。
- NSS43 完成用户 Steam 只读测量：48 秒、13/13 样本，LAN4 约 278 Mbps，单 TCP 的份额限制已明确。见 [负载证据](evidence/nss43-mainline.json) 和 [验收记录](docs/SINGLE_WAN_ACCEPTANCE.md)。
- NSS42 102项绑定、90项本地＋4项目标RAM/600秒轻载保持。当前20 Mbps/流数/owner TTL不变，旧只读候选不作为新的生产准入资格。

最新证据见 [STATE.md](docs/STATE.md)、[实验记录](docs/EXPERIMENT_LOG.md) 和 [本地 Issue 候选](docs/ISSUE_TC_SUPERVISION.md)。代码镜像不是可直接安装的发布包。

## 目录

| 路径 | 用途 |
| --- | --- |
| `docs/` | 状态、计划、决策、逐轮记录与接续说明 |
| `evidence/` | 脱敏的结构化观测与结论边界 |
| `code/` | 精确保存的部署源文件与实验代码，原相对路径保留 |
| `tools/` | 从私有工作区按白名单同步、检查仓库内容 |
| `source-manifest.json` | 来源路径、内容哈希与部署匹配关系 |

代码镜像不是通用安装包，未附带运行所需的私有状态文件。不要直接运行现场控制器，也不要从旧的 `deployment-latest.json` 推断当前部署。详见 [本地接续](docs/LOCAL_SETUP.md)。
