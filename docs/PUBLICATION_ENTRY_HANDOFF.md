# 发布候选接入 NSS 的下一步

NSS67 已在真实 Steam 下载的 372 / 367 / 385 Mbps 窗口运行发布候选。高负载期间两次原完整审核 source 3.62 / 4.41 秒通过，原 6 秒限制保留。候选自动恢复后未留驻；目前常驻仍47，NSS63入口241项未变。见 [实测](../evidence/nss67-mainline.json)。

下一次应先建立受独立回滚保护的候选保留部署和精确绑定，再集中使用现有暂停下载、真实 CS2 做可比 A/B/A2。不能把过期或 `committed:false` 的 publication trial 私有引用传给旧 NSS 入口，也不能只改一个 config SHA 让检查通过。

已核对当前调用位置，需统一接收同一个经过验证的实际部署：

| 位置 | 当前来源及作用 | 接续要求 |
| --- | --- | --- |
| [读取真实候选](../code/work/nss49/read-real-candidates.mjs) | 只接受49旧引用，从 config 构造 base/config/worker hash | 新入口明确声明候选部署来源；核验实际配置和 worker，不能依赖旧别名 |
| [原完整审核](../code/work/nss63/current-audit-diagnostic.mjs) | 读取47部署引用，持锁执行完整原审核 | 审核同一实际候选 config/worker/producer；保留全部原断言和 source 期限 |
| [NSS 暂存](../code/work/nss63/module-stage.mjs) | 要求 committed 部署，构造 `classifierOwner` 的三项来源 | 使用已受保护保留且精确绑定的候选部署，不能伪造 committed 或覆盖旧资格 |

保留原241项输入及其已有证明；需要变更的消费者/入口在新轮次创建、单独核验并绑定。原来源 1/2/6/9 秒、200ms child、45 秒 owner、20 Mbps、一 TCP＋一 UDP保持。发布试装的180秒事务和 NSS gate 的45秒 owner不可混为一个证明。

NSS66/67 的晚到审核均在独立生产期限过后，用候选 config 对已恢复原配置审核，于配置 SHA 断言拒绝。原失败保留，恢复后原审核通过；这说明来源检查生效，不是新的 source 超时证据。新入口必须正确选择当前有效部署，而非复用已到期 context。

本轮没有进入 NSS fast path，没有新的 leaf/ct mark/NAT/WAN affinity 验证，没有真实 CS2、HUD 或真人体验。JSON 编码改动的离线 CPU收益和这次高负载发布验证不能代替整机 NSS收益。无需重装整套分类器、重放旧99/13及36/29、开新游戏长期准备或扩第二WAN。
