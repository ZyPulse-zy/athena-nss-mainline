# 本地候选问题：发布等待与有界恢复

仓库：本私有研究仓库。相关文件是现场控制器/常驻分类器，当前没有证据认定 qca-nss-ecm 或 NSS driver 存在该缺陷。未创建上游 Issue/PR。

## 已复现的入口拒绝机制

- 常驻 `code/work/nss39/worker.lua` 先发布 `classification.json`，软件规则 apply 与可能的审核后再发布完整 `snapshot.json`。
- NSS 消费者 `code/work/nss39/classifier.lua` 使用前者；NSS42 `code/work/nss42/wait-full-publication.mjs` 的学习前等待使用后者，要求来源年龄 <2 秒。
- NSS44 实际真人 WAN1 对：新鲜 Steam TCP＋CS2 UDP、zone 0、mark 0x10000、同 NAT。运行未改 NSS42 入口，完整发布延迟 2.91/3.01 秒；5.06 秒内 39 帧来源年龄 4.19–8.19 秒，全健康但全不满足时间门槛。checkpoint/暂存/生产写入均未发生。
- 复查路径：读取 [实际失败时序](../evidence/nss44-failed-admission-timing.json)，核对上述源码发布顺序及 NSS42 等待输入。真实原始归属、完整控制器失败和 102 份输入冻结留在私有工作区，不上传。

这是一个可从源码和现场时序核对的本地等待来源不匹配；没有证明所有高负载拒绝都来自这一原因。

## 未安装候选与验证边界

`code/work/nss44/wait-ready-candidate.mjs` 只把等待来源改成现有 before-software-baseline classification，并校验投影声明；提示就绪后 `candidate-audit-readonly.mjs` 仍执行原完整持锁/native 审核。调度库、学习/来源/发布时限、owner、生产 gate 均没有放宽。

30 项本地校验和一次目标只读核验通过：hint 来源年龄 0.76 秒，原完整审核来源年龄 4.28 秒，ECM 关闭、没有 NSS 许可。这是不同的自然轻载窗口，不能作为修改前后真人性能对照。候选未安装、没有绑定新生产入口，也不解决下面的 apply/recovery 失败。

## 仍需定位的生命周期问题

NSS44 同轮观察到旧 worker 因 `Classifier snapshot stale before write` 退出：apply 子进程 rawStatus 256、3.79 秒，随后首次精确 recovery rawStatus 31744、6.18 秒、`exactRecovery=false`。没有注入故障或手动重启，没有证明观察程序是该退出的原因。

procd 新实例健康，guardian 保持，最终完整规则/配置/清理审核通过。这证明最后检查时已恢复健康，不证明首次恢复成功或高负载连续稳定。相关本地源是 `code/work/nss39/worker.lua`、`code/deployed-classifier/backend.lua` 的写前年龄断言和子进程/恢复路径。

下一轮在隔离夹具内逐步复现旧快照、子进程失败/超时、锁和 crash/restart，核验旧流退出与接管。定位每个阶段后才准备最小修复与新入口绑定；现有期限保持。没有完整高负载前后证据前不提交上游，不再占用用户真人窗口重试。

## NSS45 接续

另见 [恢复问题记录](ISSUE_CLASSIFIER_RECOVERY.md)。初始枚举复用和行数溢出分别完成短时安装与独立自然恢复；软件过期候选局部/日志算法模拟通过，未安装，真实 apply 子进程与完整高负载故障恢复仍缺失。NSS44 的真实拒绝、自然失败和首次恢复失败不被这些轻载/模拟证明改写。等待来源候选没有获得新入口资格。

## NSS46 新入口

NSS46 已将 classification 提示→原完整审核方式绑定到新的当前分类器入口，112 项输入、99 项离线入口检查通过。现场等待来源年龄 0.30 秒，随后原完整 native 审核通过；等待仍是提示，不能授权 NSS。原 1/2/6/9 秒门槛、5/6 秒调度和 45 秒 owner 不变。旧 NSS42 102 项入口及 NSS44 39 次失败保持原样。

真实 apply 过期恢复与 crash 已在轻载通过，修复分步保留。当前阻塞已收敛为一次集中真人高负载验收，无需再用旧入口重复碰门槛。此轮没有真人连接对或新 fast path，见 [当前证据](../evidence/nss46-mainline.json)。
