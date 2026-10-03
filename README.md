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
- NSS41 已执行真实单 WAN A/B/A2：加速数 0→2→0，bulk/RT leaf +6171/+517 包，mark/NAT/WAN1 正确。原后处理和恢复调度错误保留，重新校验与恢复完整审核通过。总负载 348→380→391 Mbps 上升，没有收益结论；下一轮先修正本地验收绑定，再稳定同 WAN 对照。

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
