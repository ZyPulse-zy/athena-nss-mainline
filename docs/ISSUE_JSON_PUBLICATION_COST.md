# 完整 JSON 发布耗时候选

NSS64 为本地记录，没有提交上游。主线仍是单 WAN 自动游戏分类 → NSS bulk/RT leaf → 真人 CS2＋Steam；该候选只缩短完整来源的发布工作。

## 已证明的范围

- NSS63 原拒绝帧 query→完整发布时间标记 3.84 秒，提示消费结束约 5.47 秒；原完整审核再经历约 0.29 秒交接、0.35 秒哈希、0.03 秒 journal、0.51 秒 selector、0.76 秒完整解析，最终 source 7.41 秒超过原 6 秒。
- 发布时间在 JSON 投影/编码前采样；没有直接记录 rename 时点。旧提示的读耗时未独立记录，不能把标记之后全部时间归因于编码。
- 目标机真实 319 条完整连接快照，同一内存夹具交错三对：原边界平均 179.06 ms CPU，候选 136.22 ms，下降 23.92%。这是编码工作，网络没有高负载，不是整机或 NSS 收益。
- 预先投影的真实形状离线夹具，128/256/512/1024 条，仅编码 CPU 原值 29.96/64.54/156.96/422.87 ms，分块 23.77/55.39/108.93/198.18 ms。字段完整相同；不是这些条目的实际 CT/加速资格。
- 最新 36 个投影与 29 个完整编码 native 案例通过；不是独立案例总数，也没有重跑旧 99/13。完整候选 32,019 字节，目标 RAM 编译 SHA 与本地相同，没有执行 watch 或安装。

结构化证据：[本轮](../evidence/nss64-mainline.json)、[编码](../evidence/nss64-encoding.json)、[规模](../evidence/nss64-scale.json)、[历史拒绝拆分](../evidence/nss64-latency.json)、[精确编译](../evidence/nss64-compile.json)。

## 上游源码与推断

对应仓库 `openwrt/luci`，文件 [libs/luci-lib-jsonc/src/jsonc.c](https://github.com/openwrt/luci/blob/master/libs/luci-lib-jsonc/src/jsonc.c)，2026-10-04 读取。`visited()` 在每个新表上扫描之前全部指针，并按小步扩容；大量不同子表会产生随表数成对增长的比较工作。目标 `luci.jsonc.stringify` 已确认为 C 函数，规模测量趋势与此相符。

**目标安装二进制对应的精确上游 commit 尚未核验。** 所以“当前二进制就是该代码”仍是推断，不能直接作为上游缺陷报告的已证事实。也未证明该项就是高负载过期的全部根因。

## 最小复现与候选

在具有真实 `luci.jsonc` 的相同环境，运行 [encoding-scale.mjs](../code/work/nss64/encoding-scale.mjs) 中的 RAM 测量：使用一次冻结的真实形状，构造 128/256/512/1024 条，先投影到不共享的树；分别计时单次整体 `stringify` 和逐 flow 编码，解析两种完整结果并逐字段比较。现有脚本依赖本地私有只读连接桥，仓库不附凭据，不能直接当通用安装包执行。

候选 [flow-json-stream.lua](../code/work/nss64/flow-json-stream.lua) 与 [json-project-fast.lua](../code/work/nss64/json-project-fast.lua) 保留原键、有限数、循环、重复引用、稀疏/slot map 处理；未知完整字段也保留。候选 [worker](../code/work/nss64/candidate-worker.lua) 仅修改完整快照 JSON 边界，非快照发布、全部其它 worker 字节、完整解析和原审核/期限不变。不是修改 NSS driver、ECM 或系统 JSON 库。

首次 2048 条组合模拟超过原六秒 runner，返回 124，保留在本地；不提高上限，后续拆分测量。被动观察初版 runner 请求超过六秒，在执行 Lua 前返回 2；改为原六秒内的四秒窗。失败与后续通过分开。

## 下一步与提交条件

仅做 publication 边界的单变量试装，写前 checkpoint、独立超时撤销；原完整持锁审核、原 source/owner 期限以及旧流精确恢复必须通过。试装不等于重做分类器生命周期准备。再验证真实高负载完整来源/审核能在原门槛内通过，才补集中、负载可比的单 WAN A/B/A2。

提交上游前需确认精确 JSON 库版本、独立于本工程的简单输入复现、编码单项计时与语义边界，及修改前后原库证据。本轮只有本地候选，不提交 Issue/PR。
