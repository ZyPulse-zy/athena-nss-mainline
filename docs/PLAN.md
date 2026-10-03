# 下一步：集中验证真人单 WAN 闭环

唯一主线：自动游戏分类 → NSS bulk/RT leaf → 真人 CS2＋Steam。

1. **读取当前 NSS39。** 先核验 `work/nss39/deployment-latest.json`、worker/guardian、last-error、现网保护项与 ECM 全零。新轮次用新目录；保留 NSS39 的 68 项绑定与 NSS32–38 冻结证据。
2. **检查真实身份及只读完整准入。** 用户方便时集中开一次对局与下载。核对应用 socket、CT ID/zone、双向 tuple、完整 mark、NAT 和自然 WAN affinity。没有两条持续的同 WAN 连接就不写生产；无需反复要求挂机。
3. **保留原时间条件，记录每次来源。** 使用 NSS39 已绑定的精简/带诊断 adapter。每个拒绝记录来源序号、query/publication age、phase/adapter/总循环耗时。初始采集年龄 <1 秒、预学习年龄 <2 秒、外层独立截止不改；不能缓存旧身份获得通过。当前轻负载资格未证明高负载可及时进入。
4. **单 WAN 做 A→B→A2。** checkpoint、独立恢复先行，受控 Steam TCP 与 CS2 UDP 分别进入 bulk/RT leaf；核验加速数、tag、mark/NAT/出口及精确撤销。受控子组 20 Mbps 不等于整台 Steam 300 Mbps 以上均加速。比较同负载 softirq/time_squeeze、吞吐和实际游戏 jitter/loss/Miss；没有客户端指标就明确缺失。
5. **通过才扩展。** 第二 WAN、共享预算、Wi-Fi、autorate、五 WAN 和其它 qdisc 支线等待。

分类器仍需持续观察自然故障；本轮只修复已复现的超时工具组合并补齐状态诊断，未证明 NSS38 自然 143 的所有成因。未知读取或清理状态继续终止/精确恢复，不吞错、不延长有效期。

所有现场变更继续要求检查点与独立自动回滚。后续安装须先等待当前实例的新发布和守护健康，再采样；旧实例发布不会因为 status=running 而获得资格。保留截止不足时允许恢复，不作延期。
