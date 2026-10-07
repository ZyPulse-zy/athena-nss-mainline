# TCP / UDP 公网源地址假设修正与短测

更新：北京时间 2026-10-07 08:28。用户在晨间封存后要求继续；本次只做传输前提定位和一条认证 TCP 短测，未启动 NSS、五槽模块或游戏。夜间 heartbeat 保持暂停。

v27 启动器把 nonce UDP 探测到的源地址同时用于 TCP / UDP 两个规则。不同协议经过 Linux PBR 和上游 NAT 后，公网源地址不保证相同。这项源码假设需要修正；旧 v27 的具体失败连接没有相同的完整公网归属证据，因此历史精确根因仍未追认。

## 实测

| 步骤 | 实际结果 | 结论边界 |
| --- | --- | --- |
| v28 只读探测 | 一条自有 TCP 尝试、30个nonce UDP；精确 CT 为 TCP WAN1/mark65536、UDP WAN5/mark327680；VPS收到4条TCP SYN metadata和5条认证UDP metadata，公网源地址不同 | TCP只有时间关联，上游还改写源端口；不是完整TCP认证或UDP交付率证明 |
| v29 单TCP修正验证 | 分别选择TCP和UDP的实际公网源地址，仍为两个单IPv4规则；原nonce服务认证后1.391秒收到首payload，25.007秒共22960476字节，客户端无错误 | 8Mbps单TCP传输前提通过；没有证明四TCP或五WAN完整fixture |
| UDP | 全短测1025发/995返，包含防火墙启用前和结束边界 | 描述性计数，不作为丢包、CS2或NSS质量验收 |
| 恢复 | 独立180秒FW自然到期；规则0/canonical基线一致/端点关闭/客户端0；原完整router audit来源1.55秒、五WAN健康、保护配置和服务epoch保持、ECM关闭全零；两物理原mq+四fq_codel所有选项和handle一致 | 当前软件fallback保持，无NSS或router配置写入 |

每次使用新目录和nonce。端点checkpoint实际下载、SHA及gzip回读一致；原v27防火墙守护、认证server和协议字节不变，写前核验独立守护，端点250秒/客户端25秒硬截止保持。没有扩源地址范围、端口、认证期限、学校策略或修改PBR。

首次清理读取早于远端守护实际截止，按原断言拒绝。失败输出和源码保持；读取剩余时间确认自然到期后，只做一次只读重查并通过。没有提前删除规则来替代自然到期证据。

## 当前范围与下一步

v20三流跨两个或三个WAN、五WANQoS队列映射、共享DOWN18借用、UP60每WAN12硬上限、RT prio0/FQ-CoDel的硬件结论保持。本次没有新增CPU、游戏体验、五WAN同时fast path或长期常驻声明。

五流fixture必须为每条实际TCP证明其公网归属，不能继续复制UDP地址；如果原精确FW政策容纳不了实际peer，写前拒绝。本次只证明一条TCP，不能直接加载五槽模块或盲重试旧五流。下一次正常Steam/CS2条件出现时，优先用新版本/新绑定承接已冻结v26入口的一次有界正常应用会话；v26旧截止和冻结字节不改。主观真人体验仍未验。

证据：[只读诊断](../evidence/v28-peer-path.json)、[认证短测](../evidence/v29-peer-proof.json)、[完整终态](../evidence/v29-peer-restoration.json)、[源码及失败保存](../evidence/v29-peer-source-proof.json)。
