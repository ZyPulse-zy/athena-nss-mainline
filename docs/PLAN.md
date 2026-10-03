# 下一步：完成写前审核诊断，再集中一次真人验收

唯一主线：自动游戏分类 → NSS bulk/RT leaf → 真人 CS2＋Steam 单 WAN。

1. **核验 NSS39。** 常驻引用 `work/nss39/deployment-latest.json`，68 项绑定保持；新轮次用新目录，不覆盖 NSS40 的 72 份失败证据。先核对实例、守护、旧错误归属、保护配置与 ECM 全零。
2. **接入已完成的取证入口。** 复制并绑定 NSS40 的 `current-audit-diagnostic.mjs` / `audit-renderer.mjs`，替代仅输出断言行号的本地审核入口；按次使用 `record-candidates.mjs` 保存 socket/候选/原始响应，再保存 selected pair，不能只覆盖 latest。所有原审核断言和外层截止保持。不要直接重跑 NSS40 冻结的实际尝试。
3. **先定位完整快照过期。** NSS40 在约 323 Mbps 时 compact 准入 4/94 次通过，但随后的 full snapshot 写前审核失败，具体年龄未记录。源码发布顺序已知，根因未证明；先比较审核分段、来源/发布年龄、producer/sequence 和负载。不能拿之后 0.29 秒的轻载审核解释高负载根因，不能持锁等待新发布或放宽 TTL。
4. **条件具备后集中短测。** 用户无需常驻游戏/反复下载。真实 socket → CT ID/zone/元组/完整 mark/NAT/自然 WAN affinity 均匹配，完整只读审核通过，才创建 checkpoint 并验证独立恢复。仍是一个 WAN、一条 bulk TCP＋一条 RT UDP，初始年龄 <1 秒、预学习 <2 秒、45 秒独立期限不变。
5. **完成 software→NSS→software。** 核验 tag getter、两条加速 flow、bulk/RT FQ-CoDel leaf 与精确撤销。受控子组上限 20 Mbps，不等于整台 Steam 300 Mbps 均加速。重点比较相同实际负载下 softirq/time_squeeze、吞吐和 CS2 jitter/loss/Miss；计入观察成本，没有客户端遥测就写未测到。
6. **闭环通过才扩展。** 第二 WAN、共享预算、Wi-Fi、autorate、五 WAN 及其它 qdisc 支线继续等待。

本轮未生产写入，未产生新的回滚验证。NSS39 历史独立回滚证明继续保留，每次新写入仍须建立本次 checkpoint 和独立自动恢复。未知读取/清理状态拒绝，不吞错、不扩大改动碰运气。
