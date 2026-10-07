# 有界入口整合：准入前退出，恢复已确认

北京时间2026-10-07 17:36。用户恢复执行权限后，原v43提交`b0a3c47965ba7d0113b592f4049a2893005ee946`已推送并实际Git archive校验，4553源SHA / 5209文件 / 1442链接通过；原3290份v1/v1.1 code/evidence保持。没有修改凭据或Git配置。

v43恢复后的首次入口因本地命名空间替换漏掉尾部分隔符，在SSH和负载前拒绝。原失败保留；v44只修复该分隔符并增加两项回归检查，15模型通过。一次只读确认健康和物理默认队列后才解除原锁。

## 唯一一次实际流量窗口

v44自有四TCP＋模拟UDP运行31.96秒，TCP客户端payload 75546624字节、客户端错误0。最后实际分类source age 0.71秒：

| 槽 | 自动分类 | WAN |
|---|---|---|
| TCP1 | BULK | 1 |
| TCP2 | BULK | 1 |
| TCP3 | BULK | 2 |
| TCP4 | BULK | 4 |
| UDP | RT | 3 |

五WAN要求没有满足，原30秒自然取得窗口结束即拒绝，未调用NSS checkpoint、owner、stage或ECM；没有NSS B段。这是取得前提的失败，不能归为NSS/firmware或分类失效。没有改PBR、分类门槛、期限或再开fixture。全fixture UDP 1370发 / 1361返只作软件窗口记录；停止边界待返回包不归因NSS，不代替v42内部B窗口2373/2373。

## 恢复与已证实的本地修复

端点关闭、精确规则0/FW基线和客户端退出已通过。原最终审核在共享`nss122`输出的固定`v44-final`名称处遇到EEXIST；先前只读确认已使用这个名字。原错误和RESTORATION_UNCONFIRMED结果原字节保留。

随后只在新目录补一次失败的只读健康及两物理队列步骤，使用唯一label：source 1.22秒 / selectors 6，五WAN健康、保护配置不变、ECM关闭全零；wan/lan4原mq＋四fq_codel所有选项与handle一致，自有入口进程0。已通过的端点/客户端证据复用，未重开流量。只有证明齐全后才将可变入口ledger标RESTORED并解除锁；原失败结果未改写为通过。

`work/v44-unique-label-entry`已把最后审核label绑定完整新runtime命名空间，增加两项实际生成输出隔离回归，17模型和默认inspect通过。七Lua数据面、分类/QoS/期限/字节上限保持。**这是软件候选，未运行新硬件会话；完整可复用入口现场验收仍未通过。** 本轮完成封存，不因自然WAN分布继续盲重试。

v42的五WAN五流60.01秒、121次ECM5、20续租、2373模拟UDP全部回包、完整十tag/leaf/CT/mark/NAT/affinity及恢复仍成立。v41计数差异仍known limitation；旧CPU和v1证据复用，本次不新增CPU、CS2/Steam、永久/全网/长期声明。heartbeat保持暂停。

已知限制：自然PBR在30秒内可能配不齐五WAN；偶发SSH取得超时；v41分类计数差异根因未知；普通应用factory和最新输出隔离候选尚未现场验收。连续新代、长期/永久/全网、WiFi/autorate/ECN留v1.1/v2，不自动新增实验。

证据：[实际入口](../evidence/v44-bounded-entry.json)、[完整恢复](../evidence/v44-restoration.json)、[修订候选](../evidence/v44-unique-label-candidate.json)、[源与冻结](../evidence/v44-source-proof.json)、[v43原本地拒绝](../evidence/v43-resumed-local-refusal.json)、[v42验收](FIVE_WAN_SIMULATED_ACCEPTANCE_2026-10-07.md)。
