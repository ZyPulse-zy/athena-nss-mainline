# 可独立贡献的上游工作：2026-10-10 复查

本轮仅进行源码查重、离线编译和独立组件测试。开发分支复查基线为
`951d023fb75d6d6423408f7e6380057b7b73eb27`；已安装控制器仍为
`2996d405c9a96ec4d891887358f02f28de4e340c`，这份文档和测试更新不改变部署版本。
没有连接或操作现网，没有重复部署、启动正式游戏/Wi-Fi 验收或制造故障/拥塞。

| 候选 | 合适的上游 | 当前证据与建议 |
| --- | --- | --- |
| ECM 保留双向显式 UDP QoS 优先级 | qosmio/nss-packages；后续由维护者决定 CodeLinaro/Julius feed 同步 | 已有 [草稿 #78](https://github.com/qosmio/nss-packages/pull/78)。两套源码的前后回归，以及完整分类器文件的真实头文件编译已完成；继续保留 draft，待完整包/固件验证。 |
| nftables concat typeof 元数据超过 4 字段被截断，以及长 concat 读取字段数问题 | Netfilter nftables 官方开发流程 | 最新源码真实库 API 测试确认 5/6/11 字段都只保留前 4 字段；另一个解码器模型由 6 字段修复为 11 字段。可准备具体 bug report/RFC；完整修复需原生 Linux 的元数据与文本/JSON 回读验证。 |
| ECM/NSS CREATE/DESTROY/FLUSH 与被动同步统计观察接口、方向测试说明 | ECM/NSS feed 维护者与 CodeLinaro | 已有接口 RFC 和通用方向/CREATE 回归，可作为文档/测试讨论贡献。接口尚未实现，不能宣布稳定 ABI。 |
| ECM 在 Linux 6.18 的编译兼容 | 采用该内核版本的 NSS feed | 找到旧 timer API 和外部编译参数传递问题。独立小改动后 41 个对象编译并链接 `ecm.o`；缺匹配 NSS 内核导出，尚未生成 `.ko`。需完整匹配环境后再决定单独 PR。 |

## ECM：已经有具体可审查的贡献

qosmio `NSS-12.5-K6.x` 最新远端仍为
`0d970dbf0185e3f53709bd803e8a466598023c57`；Julius `edma-nss` 为
`c3bc04aa2f7bba688309b7b0356b558fe1fdad34`；CodeLinaro 所核对的 QSDK 14.0
`win.nss.1.0.r39` 为 `7894b769eeb64f1c44fde547a107a8b866997590`。
各自现有补丁序列之后，所提 UDP 修复均可无 fuzz 应用。

IGS 关闭时每套源码 1,838 项断言，开启时 3,182 项；未修复各有 196 项失败，
修复后均为 0。回归使用实际源代码语句和四条 NSS CREATE 字段传播路径，外围 CT/skb
为模拟。新增 Kbuild 编译对整个修改后的 `ecm_classifier_dscp.c` 使用真实内核/NSS
头文件，IGS 开、关都通过。见 [源码与复现](../upstream/ecm/README.md)、
[完整分类器编译](../upstream/ecm/CLASSIFIER_BUILD.md)和
[结构化构建结果](../upstream/ecm/classifier-build.json)。

补丁只在 UDP 的两方向 PRIO 标志均有效时采用显式值，合法零值保留；不加入宿舍、
WAN、客户端、控制器租约或二进制替换逻辑。CREATE 赋值本身正确，问题在分类器
选择值。Julius client 补丁 0044 针对 forward-chain IGS 标签生产，解决的是另一条
路径。本轮针对两 feed 的 QoS/DSCP/IGS/UDP Issue/PR 查重未找到另一份相同补丁，
这不代表所有外部讨论或邮件列表均已排除。已有草稿无需重复开第二份相同 PR。

完整模块/包、固件回执和最终空口队列仍是不同层次的验证；完整分类器编译通过
不能代替它们。未把 Linux 6.18 兼容实验混入 #78。

## Netfilter：复现更具体，但不能发布历史崩溃修复结论

官方 nftables `91373de3ec389004c30ae5465d1bb34dcaf690dd` 和 libnftnl
`6b3bded9a9e86f327b00e26391ac72076368a487` 已在私有目录构建。
真实库的 concat userdata 构建器与解析器使用了值为 4 的 `NFT_REG32_SIZE`
作为字段上限。它表示每个寄存器的字节数；寄存器个数为 16。实际调用方还忽略
构建器的失败返回，最终保留部分元数据。

独立测试使用生产相同的 256 字节缓冲；1、4 字段通过，5、6、11 字段均只解析出
4 个字段。直接 API 和真实源码 key-wrapper 各测一次，共 10 个用例、6 个预期失败。
它不安装表、创建 hook 或打开 Netlink socket。见
[复现脚本](../upstream/nftables/test_concat_udata.py)、
[结果](../upstream/nftables/udata-results.json)和
[完整调查/提交准备](../upstream/nftables/REPORT.md)；另有
[尚未发送的 bug report 草稿](../upstream/nftables/BUG_REPORT_DRAFT.md)。

另一个 decoder RFC 对人工构造的 11 字段完整表达式，将读回由 6 改为 11；
该修复单独不能解决真实元数据的四字段上限和容量约束。简单将上限 4 改成 16
也不是完整修复，因为完整 set/map 元数据会受到 256 字节与嵌套长度限制。
历史厂商构建的 `mergesort` 断言与官方同版本源码不完全一致，不能把它直接归因
于这两个组件问题或 libnftnl。

本机 WSL1 缺少 NFNETLINK/隔离网络命名空间，WSL2 又受虚拟化支持不可用限制，
尚不能完成最新版原生无 hook 文本/JSON 回读。Netfilter 采用官方仓库和邮件流程；
本轮未给 GitHub 镜像开 PR，也未发送邮件。已有无 hook 虚构地址 fixture 和组件
结果可供继续验证。若后续查到已有修复，应准备对应 OpenWrt 回移植。

## 适合留在本仓库的改动和证据

恢复表 32 项限额的 bug 属于自己的 `writer.lua`，其修复与回归保留在开发分支，
不构成 ECM 上游补丁。专用 ELF 符号替换适配器、宿舍准入策略和设备识别同样不
适合整体推给通用上游。Wi-Fi 最后一级 TID/AC、同设备游戏/下载、完整固件恢复、
无通知规则失踪、FDB 长连接和长期覆盖率仍缺验收，不能先包装成上游已证实故障。

可先推进通用 [观察接口 RFC](../upstream/ecm/OBSERVATION_API_RFC.md)的方向、
事件、计数、遗漏和生命周期约定，再按维护者反馈实现源代码观察点；它必须保持
原有 callback/accounting 行为，不重复计数、不替换 SYNC_MANY 所有者，也不携带
现网配置或未授权的流量信息。
