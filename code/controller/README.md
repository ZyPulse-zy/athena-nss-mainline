# 路由器本机的宿舍 QoS 影子控制器

复用现网 NSS68 分类发布，观察整个 LAN 的 IPv4 conntrack；读取 DHCP、邻居、桥 FDB 和 AP station，识别真实有线/Wi-Fi 出口。Windows、固定 `.207` 和固定三种槽位不参与这个控制器的候选选择。

**本目录目前只发布影子后端。** `mode` 只接受 `shadow`，实际加速数始终为零，不写 tc/nft/conntrack/ECM，也不停止旧控制器。动态表和 `revoke` 输出是观察状态与撤销意图，不能代替内核 gate、固件删除确认或无线队列验证。旧 NSS 入口仍有三槽限制。

`core.lua` 保存完整 original/reply、CT ID/zone/mark、客户端绑定及独立六秒租约；完整同序列快照缺流只撤销该流，投影缺失只停止续租。`collector.lua` 复用已安装的工具。`service.lua` 每两秒采样并发布摘要，`athena-qos` 提供统一控制。RT/BULK 类别和实际加速分开，不增加设备配额。

默认上限是 2048 个观察记录、32 个影子候选，RT 优先，其余保留软件路径；这些是控制器开销参数，不是硬件表容量证明。未知/代理/IPv6 保留现有路径。当前 IPv4 subnet 在 `config.example.json` 配置。

## 已授权的临时运行方式

将本目录的 `core.lua`、`collector.lua`、`service.lua`、`config.example.json`、`athena-qos` 放进已核对的自有 `/tmp/athena-dorm-qos-review`，然后执行：

```sh
export ATHENA_QOS_BASE=/tmp/athena-dorm-qos-review
export ATHENA_QOS_TEMPORARY=1
export ATHENA_QOS_TEST_SECONDS=120
sh "$ATHENA_QOS_BASE/athena-qos" start
sh "$ATHENA_QOS_BASE/athena-qos" status
sh "$ATHENA_QOS_BASE/athena-qos" stop
sh "$ATHENA_QOS_BASE/athena-qos" rollback
```

测试内部期限可选 1–290 秒，独立 `timeout` 强制上限 300 秒。此上限只用于临时影子试用；普通 `run` 没有健康服务固定寿命。启动必须观察到新心跳才成功；停止/回退只等待自有进程退出，失败会明确返回非零。`rollback` 也可在运行中调用，其回退范围只有影子服务。

常驻安装的候选路径为 `/usr/lib/athena-dorm-qos`，`init.sh` 是 procd 服务源；本批没有写入 `/etc/init.d`、启用自启或实际测试 procd 启停。不得将常驻安装或数据面写入视为临时试用授权。

## 验证

目标路由器已有 Lua 5.1、luci.jsonc、nixio，以及 ip/brctl/iw。模型测试可执行 `lua ./code/controller/test-core.lua`，不制造网络流量；模型不能证明游戏体验。现场结果及回退基线见 [STATE](../../docs/STATE.md) 和 [脱敏证据](../../evidence/dorm-v2-shadow.json)。
