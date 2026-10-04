# 本地候选问题：有界观察与精确恢复

对应本私有仓库的分类器。没有证据把此问题归因于 qca-nss-ecm、NSS driver 或学校网络，未提交上游 Issue/PR。

## 2048 行边界

原 `code/deployed-classifier/conntrack-source.lua` 在第 2049 行用字符串断言退出。NSS45 开场读取到此前 11:07:30、11:08:02、11:08:10 的三次自然退出日志。原 worker/guardian 只接受其他已知有界观察错误，无法把该字符串识别为已确认回收后的观察失败。

最小离线复现是 `code/work/nss45/row-replay.lua`，合成 2049 条合法、不同实例的 UDP 记录，原上限保持 2048，全部输出小于 524288 字节。原代码返回未分类字符串错误；候选返回 `bounded-source-row-overflow`、limit 2048、observedRows 2049，且只有真实 query 结果的回收证明才能允许原地精确恢复。部分观察不能发布，未知错误仍终止。

48 个本地案例与同例目标 RAM 重放通过。另见 [真实子进程证明](../evidence/nss45-query-cleanup.json)：使用原 query helper 和真实 native fork/exec/waitpid，参数与输出为合成；7 个案例确认正常输出、2049 行新旧差异、stdout 超限、stderr 超限与未知退出均回收对应子进程。没有执行真实 conntrack 查询或生产服务溢出注入。

候选短时安装后完成冷启动、35 帧轻载观察、原完整审核和独立 180 秒自然恢复。此证据不证明高负载溢出后的完整服务恢复或连续运行。

## 初始恢复枚举重复

原 `code/work/nss45/original-backend.lua` 的 `recover()` 先 `inspect(w)`，随后 `owned.undo()` 再枚举同一初始状态。空动态规则时，共 60 次读取。候选 `code/work/nss45/candidate-backend.lua` 只复用已核验的第一次枚举；写前/写后读取仍执行，首次写后禁用缓存，不跨 WAN/调用持有缓存。

24 个实际算法案例在新旧源码均通过，覆盖接管、换端口、旧流退出、restart、四种中断、未知写入者、队列选项漂移和 boot 漂移；不能把两次执行算成 48 个新案例。未知 writer 在初始读后出现也保留。目标三对只读空日志测量 60→40 次调用，0.810→0.553 秒，见 [测量证据](../evidence/nss45-recovery-benchmark.json)。日志和 selector 投影为空、写回调始终拒绝；不是真实规则恢复或转发 CPU 对照。

backend 候选单独试装并自然回滚成功。尚未证明 NSS44 高负载 6.18 秒恢复失败已解决，亦不能归因整机 CPU 收益。

## 软件来源过期候选

NSS44 原 `snapshot stale before write`、apply 失败、首次精确恢复失败保持，见 [发布问题记录](ISSUE_CLASSIFIER_PUBLICATION.md)。NSS45 `stale-worker.lua`/`stale-guardian.lua` 是包含行数处理的独立未安装组合候选：原 6 秒软件来源/6 秒 mutation/9 秒发布界限保持。候选把已知来源过期作为绑定 apply 结果，撤回两种发布、丢弃历史、精确恢复，再接受新观察；未知 writer、未知错误、过期 producer 和恢复失败仍拒绝完成。

34 个局部案例及 8 个实际 backend/ownership 日志算法交叉场景通过本地/目标 RAM 模拟。交叉场景在第 1–5 个 WAN 的写前边界制造合成过期，验证此前已写规则和当前 intent 精确恢复、未知 writer 保留、外来 producer 拒绝和新观察接续。五 WAN 是现有软件分类器的合成日志模型，不是五 WAN NSS 实装。

应用子进程、发布与队列 IO 被替换，因此这些证明不能代替真实 apply 子进程的序列化/锁/身份/成功回收与完整服务故障恢复。候选未安装、未获得新的 NSS 准入资格。下一项补这些缺失证明，再考虑一次一变量组合与新入口绑定；不扩大预算、流数或 TTL。

原始日志、私有配置和 checkpoint 保存在工作区。潜在 Issue/PR 所需的高负载修改前后证据尚不充分；本记录仅作为 backlog。

## NSS46 实装与最小复现补充

对应仓库为本私有研究仓库 `ZyPulse-zy/athena-nss-mainline`，涉及旧 `code/work/nss39/worker.lua` 的 `R.checkFresh` / apply / watch 恢复路径、新 `code/work/nss46/worker.lua` 和 `guardian.lua`、以及 `code/work/nss45/candidate-backend.lua`。这不是已确认的上游 ECM/NSS 驱动缺陷。

最小复现：有实际被软件分类器接纳的 RT 连接时，只在测试 watch 中将一轮真实观察延迟至原六秒界限之后，再通过原带锁 apply CLI 处理；不修改 CT 身份、mark/NAT/WAN 或期限。必须先完成 checkpoint 和独立回滚。`code/work/nss46/fault-worker.lua` 是测试专用，不能常驻保留。

NSS44 原高负载自然失败记录仍为 `snapshot stale before write`、apply 失败、首次 recover 失败。NSS46 轻载受控复现实际 apply 在年龄 6.27 秒返回绑定的过期回执，实际子进程回收完成；两种发布撤回，pending intents 从 2 到 0，recover 子进程 0.80 秒，同 worker 恢复新观察。另一个真实空闲 worker crash 经 procd 在 7.56 秒恢复健康实例。两轮自然到期恢复证明及最终原完整保护审核通过，三项修复已分步保留，见 [NSS46 实装证据](../evidence/nss46-mainline.json)。

修改前自然高负载与修改后受控轻载并非同负载 A/B，不能宣称已经修复全部高负载超时。真实换端口/旧流退出、高负载稳定和客户端指标仍待集中真人窗口；未提交上游 Issue/PR。
