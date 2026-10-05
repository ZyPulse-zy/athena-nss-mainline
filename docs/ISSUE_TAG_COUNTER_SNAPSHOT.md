# 本地控制器问题：活动流的多规则 counter dump 偏差

这是本项目的诊断记录。没有提交上游，也没有证据把它认定为 NSS firmware 误标或 Linux 内核缺陷。

真实来源见 [计数帧及修正](../evidence/nss82-tag-reader.json) 和 [五个现场案例](../evidence/nss82-trials.json)。完整带端点/owner 的 NFT JSON 保留在本地。

| 现场位置 | total | expected | unexpected | 结果 |
|---|---|---|---|---|
| NSS80 A2 末尾 TCP up | 16722 包 / 1155332 字节 | 16723 包 / 1155392 字节 | 0 包 / 0 字节 | 原严格 getter 拒绝，原失败保留 |
| NSS81 initial TCP down | 120 包 / 174200 字节 | 121 包 / 175700 字节 | 0 包 / 0 字节 | A 之前拒绝，无 ECM 开放 |
| NSS82 学习前 TCP down 第一次 | 9558 包 / 14279820 字节 | 9559 包 / 14281320 字节 | 0 包 / 0 字节 | 恰好符合一次精确重读条件 |
| NSS82 同位置第二次 | 9779 包 / 14611320 字节 | 9779 包 / 14611320 字节 | 0 包 / 0 字节 | 原严格 getter 通过 |

其它三个方向和邻居反例计数在这些帧中一致，所有错误标签计数均为零。活动 TCP 下，多规则 dump 不是所有 counter 同一时刻的快照，这与观察到的一包偏差及紧接着的一致帧相符；这是依据来源作出的解释，不是已定位的内核源码缺陷。

最小现场复现条件是：单个受控 TCP＋低速 UDP 活跃，安装精确 tuple 的 writer/total/expected/unexpected 规则，读取整个表的 JSON。总包和预期包严格相等的假设会在一包跨读取边界时误拒绝。单纯把 saved JSON 重放到 getter 只复现拒绝逻辑，不能代替活动流复现。

修正范围是本地 `code/work/nss82/fast-path.lua` 的 `checkedTags`：五个位置统一使用至多一次重读，只允许 TCP down 差一包且1500字节，或 TCP up 差一包且60字节；其它方向必须一致、所有unexpected/邻居必须为零且有真实双向包。重读本身不授予 NSS 权限，第二次仍必须通过原严格 getter，再由原 flow 身份、分类来源、native gate 和租期条件决定准入。

17项目标 RAM 案例检查 ACK 条件，包括两包偏差、错误长度、unexpected、缺少方向/真实流量、邻居和反向偏差的拒绝。NSS82现场实际用了已有 TCP-down 条件；新 ACK 条件没有现场触发证明。阶段时长、20Mbps组、六秒分类来源、12秒native session和独立45秒撤销均未改变。

若以后仍出现多包偏差，应先保存实际两帧与读取时序，再考虑改善观察方式；不要通过扩大 NSS 放行范围掩盖审计读数问题。


## NSS89–91更新：修正观察合同

见 [实际两帧和新合同](../evidence/nss92-tag-reader.json)。NSS88同一次initial读：先TCP-up expected多1包/60字节；第二次up相等而down expected又多1包/1500字节。错误tag仍0，证明一次重读后仍要求严格同瞬时相等会继续误拒绝活动流。UDPdown独立为0，不能被计数修正冒充为有双向流量。

本地文件`code/work/nss89/fast-path.lua`和`tag-counter-audit.lua`：每次live先由未改的normalizer验证完整自有NFT policy；counter数值非负整数、包/字节零状态一致，所有unexpected和neighbor包及字节0。第一帧exact equal可直接验证；skew时只再读1帧，total/expected各自单调、两帧交叉区间相交才接受观察。学习前仍需四方向正包，initial缺包仅按原1.2秒等候。native flow资格、ct identity/mark/NAT、来源/租期和默认拒绝不变。读数本身不授予加速。

30目标RAM案例覆盖实际88帧、wrong-tag byte-only、负数/缺counter/倒退/无重叠/缺方向；NSS91实际成功A2前后各一次bracket。52的两轮缺UDPdown继续拒绝，32Mbps完整A/B/A2和正确bulk/RT实际通过。这个已复现的问题属于本项目审计控制器假设，当前没有充分证据提交给Linux或NSS上游。
