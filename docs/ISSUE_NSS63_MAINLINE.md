# NSS54–63 本地主线问题与复现边界

没有向上游提交 Issue/PR。问题均先记在私有控制器/分类器；对应内核兼容缺陷尚未证明。

| 问题 | 最小实际证据 | 当前处理及剩余边界 |
|---|---|---|
| 发布读取 inode 竞态 | NSS54 path stat→open→path stat 中 snapshot 被原子替换 | NSS55 `baseline-publication-join.lua` 持文件描述符、两次fstat、最终路径inode一致；替换只作为未就绪继续原4秒等待。14 RAM案例，没有替代原审核 |
| standalone classifier 超过传输9000字节 | NSS55 syntax-only命令20246字节，在checkpoint前拒绝 | NSS56仅在已声明qos staging时交由独立守护编译原70924字节完整bundle；传输上限不变，实际56qosCodeLoaded通过 |
| nft多计数器读帧差一包 | NSS56退出ECM前A2、NSS58软件A后分别下载total比expected少1包1500B；其余方向对齐、unexpected/neighbor0 | NSS57/59限定这个见证后最多一次只读重读，仍要求原strict getter通过。原失败保留，尚没有新完整ABA证明 |
| 精简投影不包含选中TCP | NSS59第一轮最后拒绝帧与完整producer/query严格相同，完整247flow中没有选中TCP，UDP仍正确RT | 只在本次同源完整帧支持“该观察未见该CT”；没有用其它时间/投影缺失推断退出，未增加准入读/重试 |
| 提示返回结构错误 | NSS60 native完整审核通过，JS把wrapper当producer，写前拒绝 | NSS61 `publication-hint.mjs` 明确展开并核对完整producer/query，4实际parity＋10负案例，未改NSS资格 |
| 短命child /proc读取竞态 | NSS61第二轮A完成，读取先前sleep child wchan时退出，ECM尚未开 | NSS62仅候选child读取用完整读取或nil；guard读取仍strict、final stat start/parent保持。15目标RAM案例、full helper语法/只读scan通过，waitFresh字节与200ms不变。63实际尚在preaudit被拒绝，未验证新helper高负载forwarding |
| 模块依赖漏拷贝 | NSS62启动时`./payload.mjs`不存在，连接路由器前拒绝 | NSS63拷贝NSS59 payload原字节，qualifier实际导入module-stage/wait；241项绑定。不是NSS62成功执行 |
| 高负载完整发布/消费过期 | NSS63 query started1937027.91，publish1937031.75，原审核source检查1937035.32：7.41秒>6 | 当前未修完。snapshot发布3.84秒，hint再快也不授予资格；必须缩短真实worker/审核工作并保留原6/9秒条件 |

计数差帧与逐条dump/并发更新的非原子观察一致，仍只是推断。参考 Linux [v6.18 nft_counter.c](https://github.com/torvalds/linux/blob/v6.18/net/netfilter/nft_counter.c) 与 [nf_tables_api.c](https://github.com/torvalds/linux/blob/v6.18/net/netfilter/nf_tables_api.c)；参考版本不是当前供应商6.18.44源码的完整验证，不能写成已确认内核bug或据此直接提交上游。

12真实案例、所有原错误/完整输入及回滚原件留本地，脱敏见 [失败证据](../evidence/nss63-attempts.json)。NSS56只完成A+B，NSS58和NSS61第二轮只有A；5次暂存均撤销，NSS61首轮即时完整AFTER过期失败与后来暂停后通过分开保存。

离线报告投影曾对缺失wanAfter.wan使用1，错误描述四个WAN2未加速暂存。实际selected严格交叉核验已更正，v1原件私有保留；这是证据序列化错误，不是路由器WAN选择/NSS权限变化。`correct-evidence-wan.py`只读原件并生成v2，未修改任何冻结实际输入。
