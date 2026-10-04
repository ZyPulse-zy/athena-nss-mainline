# Athena NSS 主线记录

Athena AX6600 网络优化研究。唯一主线：**自动识别游戏流 → NSS RT / bulk leaf → 真人 CS2 + Steam 高负载闭环**。

这是私有研究仓库，用来跨对话保存代码、可核对证据和下一步。现场凭据、完整连接元组、路由器配置备份和模块二进制仍保存在原本的本地工作区。

## 从这里继续

1. 阅读 [当前状态](docs/STATE.md) 和 [下一步](docs/PLAN.md)。
2. 阅读 [操作约束](AGENTS.md)，核验现网，再考虑任何写入。
3. 通过 [实验记录](docs/EXPERIMENT_LOG.md) 与 [证据索引](docs/ARTIFACT_INDEX.md) 区分实测、模拟和假设。
4. 每轮更新状态、证据和代码清单，提交一个明确说明结果的 commit。

## 当前结论

- 常驻分类器已升级并保留 NSS46：三项可靠性修复逐项安装，真实 apply 过期恢复 0.80 秒、真实 crash 恢复 7.56 秒通过，配置/路由与所有期限保持。
- NSS46 新入口绑定 112 项输入、99 项离线入口检查，classification 提示后原完整现场审核通过；当前 ECM 关闭。见 [最新实装证据](evidence/nss46-mainline.json)。准备已完成，下一步集中真人 CS2＋Steam 对照。
- NSS39 历史 3 次独立自动回滚通过，最终安装核验保留。冷启动旧 producer 被拒绝的记录未隐藏；现流程先验证当前实例就绪。
- NSS38 精简准入和逐次诊断候选已绑定 NSS39 的 68 项清单，目标原生完整源码模拟、tag 往返与配置检查通过。
- **真人 WAN1 自动分类→ECM fast path→NSS bulk/RT leaf 功能已验证；现网恢复后 ECM 关闭。固定高负载 CPU 和游戏体验验收尚未通过。**
- NSS41 已执行真实单 WAN A/B/A2：加速数 0→2→0，bulk/RT leaf +6171/+517 包，mark/NAT/WAN1 正确。原失败与恢复证明保持；总负载 348→380→391 Mbps 上升，没有收益结论。
- NSS45 历史两项分类器修复分别完成短时试装、独立 180 秒自然恢复和原完整审核，当轮未长期保留，NSS 全程关闭。114 个独立本地案例、目标 RAM 重放、7 个真实 query 子进程案例通过；当轮软件过期候选未安装。见 [历史证据](evidence/nss45-mainline.json) 和 [恢复问题记录](docs/ISSUE_CLASSIFIER_RECOVERY.md)。
- NSS44 真实 WAN1 配对、写前完整发布过期拒绝、自然退出/首次恢复失败证据保持。classification 提示后原完整审核的候选未绑定新入口，准备期间无需用户挂游戏。见 [历史证据](evidence/nss44-mainline.json) 和 [发布问题记录](docs/ISSUE_CLASSIFIER_PUBLICATION.md)。
- NSS43 完成用户 Steam 只读测量：48 秒、13/13 样本，LAN4 约 278 Mbps，单 TCP 的份额限制已明确。见 [负载证据](evidence/nss43-mainline.json) 和 [验收记录](docs/SINGLE_WAN_ACCEPTANCE.md)。
- NSS42 的 102 项绑定、90 项本地＋4 项目标 RAM 检查、原完整只读审核及 600 秒自然轻载证据保持。当前 20 Mbps/流数/TTL 不变，NSS44 候选未安装、未获得新生产入口资格。

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
