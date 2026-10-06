# Athena NSS mainline

最新[NSS154](evidence/nss154-mainline.json)：监督器自身被终止后，新进程从磁盘journal验证独立恢复并完成同连接新代重学。继续至20:00；先读[STATE](docs/STATE.md)。

## NSS153及更早历史

# Athena NSS mainline

最新[NSS153](evidence/nss153-mainline.json)：自有控制子进程中断后，独立恢复及同连接自动新代重学通过；单WAN有限两代，所有实验已撤销。仓库按用户最新设置要求恢复public。先读[STATE](docs/STATE.md)与[PLAN](docs/PLAN.md)。

## NSS152及更早历史

# Athena NSS mainline

最新 [NSS152](evidence/nss152-mainline.json)：真实改类自动撤销/新代重学和精确PC控制进程中断后的路由器独立恢复通过。后台自有TCP/UDP，无需游戏或下载；所有实验已恢复，长期/300Mbps/真人仍未验收。先读 [STATE](docs/STATE.md) 与 [PLAN](docs/PLAN.md)。

## NSS150及更早历史

# Athena NSS mainline

最新 [NSS150](evidence/nss150-mainline.json)：后台自有真实流完成单WAN两代自动加速、精确撤销、完整恢复、新query/checkpoint/owner/pin/CI接续，原socket/CT/mark/NAT/WAN不变。无需开游戏。有限两代已过，长期/300Mbps/真人仍未验收，最终已恢复。先读 [STATE](docs/STATE.md) 和 [PLAN](docs/PLAN.md)。

## NSS148及更早历史

# Athena NSS mainline

最新 [NSS148](evidence/nss148-mainline.json)：修复测试程序的软件段旧epoch错误，147自有后台下载单WAN完整20秒A/B/A2、ECM0/2/0、双向四tag/四FQ-CoDel leaf及恢复通过。无需启动游戏或Steam。背景负载变化使本轮严格CPU对比未通过；不称真人CS2/300Mbps/长期验收。148真人入口使用已实测147 factory，默认只读已运行；实验均撤销，常驻68不变。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)。

## NSS142及更早历史

# Athena NSS 主线

最新 [NSS142晨间终态](evidence/nss142-mainline.json)：完整保护/两物理根/七端点/客户端收尾通过，常驻68且ECM关闭；140最后真人入口1385输入未变，整合版完整A/B/A2仍待一次集中真人验收。夜间任务在发布校验后暂停，10:00后不新实验。以 [STATE](docs/STATE.md) 与 [PLAN](docs/PLAN.md) 开头为准。

# Athena NSS 主线

最新 [NSS141真人入口准备](evidence/nss141-mainline.json)：真实改类撤销与新代重学已在 [NSS139](evidence/nss139-class-lifecycle.json)通过，现已并入最后集中真人入口并完成必要离线/只读核验。常驻68、ECM关闭；140整合版本完整A/B/A2和真人验收尚未执行。以 [STATE](docs/STATE.md) 与 [PLAN](docs/PLAN.md) 开头为准，下方旧摘要仅历史。

# Athena NSS 主线

最新 [NSS92单WAN32Mbps闭环](evidence/nss92-mainline.json)：60Mbps预算下，相同32Mbps真实TCP/UDP中softirq约下降66.4%，三段UDP全部返回、ECM0→2→0与恢复通过。52Mbps回程缺包根因未定，当前NSS已撤销、常驻68未改。先读 [状态](docs/STATE.md) 和 [计划](docs/PLAN.md)。

# Athena NSS 主线

最新 [NSS82受控工程闭环](evidence/nss82-mainline.json)：两次完整单WAN A/B/A2通过；同18Mbps负载softirq约下降55%，32Mbps发送负载bulk拥塞而RT队列零丢弃。当前NSS已撤销、常驻NSS68未改。工程无需反复开Steam/CS2，下一步直接更高单WAN受控带宽，真人游戏只留最后集中验收。先读 [状态](docs/STATE.md) 和 [计划](docs/PLAN.md)。下方旧结论为历史。

# Athena NSS 主线记录

最新 [NSS78](evidence/nss78-mainline.json)：轻载准备窗口已实测存在；目前无真实游戏/下载对，未开启NSS。入口仍NSS77，下一步直接集中闭环。现网原完整审核通过。下方77及更早为历史。

最新 [NSS77](evidence/nss77-mainline.json)：真实CS2/Steam部分加速，完整闭环未通过；已定位并修正准备余量不一致，最新候选355项/目标RAM通过但未现场试用。当前ECM关闭且恢复审核通过。先读 [STATE](docs/STATE.md) 和 [PLAN](docs/PLAN.md)。下方68及更早是历史。


最新 [NSS68](evidence/nss68-mainline.json)：发布候选已实际保留，新257项入口与完整准入/恢复审核通过；ECM关闭。记录一次自然tc回收失败与自动恢复，真人同负载闭环未验收。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)，下面67及更早为历史。


最新 [NSS67](evidence/nss67-mainline.json)：发布候选在372/367/385Mbps真实Steam负载运行，高负载原完整审核3.62/4.41秒通过；独立180秒自然撤销精确恢复47，ECM关闭全零。下一步精确绑定候选实际部署再集中单WAN真人闭环；不是NSS/CPU/游戏收益验收。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)。下方65等为历史。

最新 [NSS65](evidence/nss65-mainline.json)：JSON发布候选现场试装/两次原完整审核通过，独立180秒自然撤销精确恢复；常驻47、ECM关闭全零。自然轻载不能验收高负载/整机CPU或真人收益。下一步直接高负载发布审核与正确绑定的集中单WAN A/B/A2。先读 [STATE](docs/STATE.md)、[PLAN](docs/PLAN.md)，下方NSS64为历史。

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
