# 本地测试程序：20秒软件对照误用6秒准入epoch

范围：本私有仓库的实验harness，尚不是qca-nss-ecm或固件缺陷，未提交上游。

最小复现：原140 fast-path的A段要求20秒，Consumer.compareEpoch每帧同时核验当前完整分类和初始6秒epoch截止。即使分类源持续刷新、CT/class/PBR未变，A约4.5秒/10帧后仍拒绝，ECM从未开放。145实测失败；146内层增closed参数，但A.compareObserved顶facade未转发，实测rejectedComparison.reason仍为epoch expired，影响TCP和UDP。

修改：147 classifier.lua的Consumer.compareEpoch只在显式closed时略过旧初始epoch截止，out.compareObserved及顶facade完整转发closed。fast-path.observe只在未active时先stopped核验双方frontend与全部计数0；当前完整source/class/CT/producer检查继续严格，活动NSS native截止和续租不变。记录拒绝比较结果供定位。真实BULK→BE精准撤销逻辑保持，不能以该开关重新开放terminal gate。

证据：8个完整Consumer及9个实际phase/compare/facade目标RAM分项通过，明确mock inspector，不称整个factory RAM验证；147完整硬件三段20.01秒/123帧、ECM0→2→0、7续租和精确恢复通过。对应 [失败](../evidence/nss148-failures.json)、[轮次](../evidence/nss148-trial.json)、[实际源码](../code/work/nss147/classifier.lua) 和 [fast-path](../code/work/nss147/fast-path.lua)。148仅接回同一已实测factory；真人wrapper完整ABA尚未跑过。

相关独立问题：143候选读取命令9311>9000，只精简visibility reader且保持原policy token；144漏本地审核依赖；146立即恢复审核instance断言失败，后来完整终态通过。它们和原失败分开保留，不以147成功覆盖。
