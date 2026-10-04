# Athena NSS 主线记录

Athena AX6600 网络优化研究。唯一主线：**自动识别游戏流 → NSS RT / bulk leaf → 真人 CS2 + Steam 高负载闭环**。

这是私有研究仓库，用来跨对话保存代码、可核对证据和下一步。现场凭据、完整连接元组、路由器配置备份和模块二进制仍保存在原本的本地工作区。

## 从这里继续

1. 阅读 [当前状态](docs/STATE.md) 和 [下一步](docs/PLAN.md)。
2. 阅读 [操作约束](AGENTS.md)，核验现网，再考虑任何写入。
3. 通过 [实验记录](docs/EXPERIMENT_LOG.md) 与 [证据索引](docs/ARTIFACT_INDEX.md) 区分实测、模拟和假设。
4. 每轮更新状态、证据和代码清单，提交一个明确说明结果的 commit。

## 当前结论

- 常驻分类器已升级并保留 NSS39；修复 tc 超时监督与外层回收的组合，保持分类、PBR 和所有期限。
- 3 次独立自动回滚通过，最终安装核验保留。冷启动旧 producer 被拒绝的记录未隐藏；现流程先验证当前实例就绪。
- NSS38 精简准入和逐次诊断候选已绑定 NSS39 的 68 项清单，目标原生完整源码模拟、tag 往返与配置检查通过。
- **真人 WAN1 自动分类→ECM fast path→NSS bulk/RT leaf 功能已验证；现网恢复后 ECM 关闭。固定高负载 CPU 和游戏体验验收尚未通过。**
- NSS41 已执行真实单 WAN A/B/A2：加速数 0→2→0，bulk/RT leaf +6171/+517 包，mark/NAT/WAN1 正确。原失败与恢复证明保持；总负载 348→380→391 Mbps 上升，没有收益结论。
- NSS44 真实 WAN1 连接对已找到，但原入口在 checkpoint 前因完整发布过旧而拒绝。还观察到分类器自然退出、首次恢复失败；新实例与最终保护审核通过。先解决发布与恢复可靠性，再请求下一次真人窗口。见 [本轮证据](evidence/nss44-mainline.json) 和 [本地问题记录](docs/ISSUE_CLASSIFIER_PUBLICATION.md)。
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
