# 本地 backlog：无包与错误 tag 的取证应分开

尚未提交上游。这是本地控制器判定问题，不是 qca-nss driver / ECM 缺陷证明。

## 原行为和最小条件

NSS48 的 [fast-path.lua](../code/work/nss48/fast-path.lua) 在 getter 同时要求各方向 total>0、expected=total、unexpected=0。初始0.3秒循环把TCP无包也显示为 `Tag getter mismatch`。实际 WAN4 配对的 TCP up/down total/expected/unexpected 全为0，UDP up/down total为2/5、expected相同、unexpected为0。未打开ECM，精确回滚/原完整审核通过，见 [失败摘要](../evidence/nss49-failed-attempts.json)。消息不能区分空闲与错误映射，不证明硬件tag错误。

最小模型：TCP两个方向total=expected=unexpected=0；UDP total=expected>0、unexpected=0。给TCP正确计数延迟0.6秒，原初始窗拒绝。TCP持续全零必须拒绝；unexpected>0或expected!=total必须立即拒绝。

## 新候选和证据

[NSS49 fast-path.lua](../code/work/nss49/fast-path.lua) 初始允许pending，错误标签立即失败。等待最多1.2秒，并受原epoch-0.5 / owner-32剩余预算约束。全部四向正计数后再严格getter，后续学习前/阶段后不接受pending。45秒owner、原来源/epoch、20 Mbps/连接数不变。

[13个目标RAM场景](../evidence/nss49-native-aba-cases.json) 包含 delayed-tcp 0.6秒通过、idle-tcp持续空闲拒绝、wrong-tag立即拒绝、改类/NAT漂移/错误WAN/加速退出。原源码SHA c2fcf006…bb2198，新helper22bb3253…3a294，完整值见 [新入口证明](../evidence/nss49-entry-binding.json)。RAM IO/时钟/gate ACK模拟，不算硬件试验。

NSS49实际完整控制器通过，但getter0.16秒/1probe，没有使用额外余量。硬件成功支持整体功能，不能证明1.2秒等待造成成功。尚未另造真实延迟TCP场景，避免混淆模拟与观察。

资格JSON继承字段 `nssRouterPayloadsUnchanged=true` 不描述本轮helper变化。精确绑定/冻结输入已覆盖新hash，本报告明确delta；下一新轮次应修正元数据名称，原121项证明保持。这不授权扩大预算或新WAN，也不阻塞已绑定入口的主线。
