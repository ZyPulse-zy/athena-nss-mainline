# 当前：运行保留，增加Loss/Miss只读诊断

2026-10-09T08:57:33.823Z（北京时间16:57）复核：NSS保持运行。当前用户报告约0.4% Loss与Miss，方向不明；尚未复现或证明根因，不能宣布已解决。

新增health.lua/diagnose.lua和手动diagnose入口，1–180秒只读、有界事件/匿名流别名、记录来源间断、活跃RT缺CREATE/绑定切换及实时队列drop/计数重置，不读取完整诊断快照、不造流量。20个模型、5文件目标解析、非法期限拒绝和真实一分钟采集通过；一分钟21样本/20个RT流进展样本全部有当前CREATE租约，RT drop增量0、来源中断0、绑定切换0，单样本最大0.04秒。该采集包括全部RT流，不能冒充游戏端到端统计。

仅安装诊断文件和入口/下次启动的复制列表；owner/guardian/reader、全部相关服务PID及启动时间、五WAN身份与保护哈希前后相同，NSS准入保持开启。没有重启控制器/路由器或改reader/writer/core、分类规则、队列速率/缓冲、游戏设置、认证/PBR/NAT、代理/Tailscale、固件/EDMA、自启/respawn。旧失败和冻结code/work保留。

已安装入口：

```sh
sh /usr/lib/athena-dorm-native/athena-qos status
sh /usr/lib/athena-dorm-native/athena-qos diagnose 60
```

诊断默认60秒，仅接受1–180秒；约每3秒读小候选投影、内核gate、两个NSS队列，不读完整快照/每station大统计。匿名事件最多128条/流别名256个，缺读和计数重置单独报告；无持续后台任务、root权限运行，私有目录记录原始资料。输出涵盖全部合格RT，CREATE回执不是每包交付确认，不能把事件为空作为零丢包证明。

现有status/start/stop/rollback语义保留，下方完整回退证据仍是此前实测，本轮没有重新stop/rollback。诊断文件备份及前后保护读回已保存；回退本轮文件不需要停止正在运行的控制器，先恢复原athena-qos/launch字节，再移除自有health/diagnose文件。

若再次自然出现Loss/Miss，关联当时游戏详细面板/时间和一次短diagnose记录；不重复旧压力/故障夹具，不默认放宽6秒租约、降全宿舍带宽或增加游戏缓冲。正式真人验收延期仍有效。

[当前状态](../../docs/STATE.md) · [证据](../../evidence/dorm-v2-native.json)

## 以下为此前记录，不代表当前运行状态

# Athena 全宿舍 v2 本机控制器

复核 2026-10-09T05:23:24.961Z：本机 native-running，实际 NSS1，来源新鲜、IPv4准入开启、未确认0；本次启动来源暂停/恢复 1/1。五WAN、原软件队列、认证/PBR/NAT、代理/Tailscale、管理与原磁盘模块核验通过，旧Windows停止，自启关闭。 用户自然游戏/舍友下载已被动观察，当前回报暂时改善；端到端丢包与长期质量未通过。见 [当前状态](../../docs/STATE.md) 与 [实际证据](../../evidence/dorm-v2-native.json)。

## 已安装服务的操作

在路由器root会话中使用：

```sh
sh /usr/lib/athena-dorm-native/athena-qos status
sh /usr/lib/athena-dorm-native/athena-qos start
sh /usr/lib/athena-dorm-native/athena-qos status
sh /usr/lib/athena-dorm-native/athena-qos stop
sh /usr/lib/athena-dorm-native/athena-qos rollback
```

**启动前从原Windows工作区停止旧continuous，确认STOPPED/restorationPassed；“当前无活跃代”不能排除下一次竞争。** 原入口为旧任务目录work/resident-continuous-dev-20261008/service.ps1 -Mode Stop/Status。回退原软件路径不会自动恢复旧 Windows 控制器；只在明确选择旧入口时使用 -Mode Start，不同时运行两套准入写入者。

start是异步procd请求，返回不代表数据面就绪；status应确认native-running、owner PID、actual accelerated与CREATE ACK。独立setsid guardian用PID/start token检查owner，退出时恢复；默认无健康固定期限。已执行一次获准重启及之后手动启动；未设置开机自启，也未enable。init service的inspect提供JSON，rc.common的status只表示进程状态。

stop/rollback等guardian关准入、逐流撤销/FW确认、回收reader、IGS RESET/CLEAR确认及还原原MACVLAN bridge/mwan/ECM/root；同时将 core guard 恢复为已校验的原始字节并单独重载，重复rollback幂等。ABI2 将经精确 tuple/generation 的原始 ENACK4/error5 NO_ENTRY 记为独立固件不存在状态；原 NACK/错误保留，不改写为 ACK。ECM 已减速时使用 observer 记录的精确 tuple 请求 DESTROY；其它未知 NACK/删除超时仍保留锁/模块/日志并报告未确认。owner 已退出时可重试 rollback，仍需真实回执，不强行释放。status.json/guardian-private.log位于root私有/tmp/athena-dorm-native；只清理明确自有文件，不拿旧全量归档覆盖新配置。

## 重启后的原服务配合

classifier_recovery.lua 只接受原 nss23 配置哈希、十个 CAKE root/全部非速率选项及已确认的 diffserv4/besteffort 差异；缺少基础规则时补原40900/41900规则，未知/部分规则不覆盖。原 worker/config 不改，autorate 的 bandwidth 继续由原服务维护。

install_core_guard.lua 只对 SHA256 已核验的原 core-guard.sh 安装 IPv4 关闭操作的条件跳过，私有目录保存原文件。core_guard_permission.lua 每次只读核对 foreground owner、独立 guardian 的 PID/start/完整命令、8秒新鲜reader发布和心跳，以及 ABI2默认拒绝gate；owner/reader失联或固件异常时由原guard关闭。它不打开 NSS，IPv6/PBR/日志操作保留。shell watch 只有重载后才使用新函数；安装器记录 PID/start 避免重复重载。回退还原原脚本和进程，未知文件变化拒绝覆盖。

## 分类来源中断与恢复

status中的flowState.admissionState为ready或waiting-source；admissionPaused只表示暂停新增/续租。分类器暂时error/degraded或快照到期时，保持可核验的本机服务和原软件路径，停止新增/续租；现有精确CT的六秒内核租约不延长。来源恢复后同一writer恢复准入，无需再次start。reader本身失联8秒、owner退出、未知固件撤销仍触发原完整回退。

flowState.sourcePauses/sourceResumes/sourceUnavailableSince/lastSourceResumedAt记录本次服务中的来源变化。原guard只读核验输出保存在私有/tmp/athena-dorm-native/core-guard-last-check.json；准入在writer外关闭时，status.coreGuardLastCheck保存最近理由，不能把外部关闭等同于人为操作。status仍需读取实际accelerated及固件CREATE回执，waiting-source不证明仍有加速流。

原分类器子进程详细stderr已丢失，底层apply失败原因尚未完全定位；未修改其冻结源码。真人游戏/下载和长期性能仍延期，现场没有造流量、杀分类器或新故障注入。

## 下载负载下的采集与预算更新

仅维护code/controller：本机reader改读较小的RT/BULK候选投影，不再解析完整诊断快照或跟踪空闲BE；新鲜hostapd关联/授权表替代每秒完整iw station统计；逐流分段JSON编码；仅变化的队列类别一次批量更新，先续精确CT租约。原分类规则和6秒租约不放宽，32槽/无按人设备配额保持。

collector.publications(false)只读原before-software-baseline候选投影；投影遗漏不当作CT退出，旧资格只存活到既有6秒期限。普通BE/UNKNOWN保持原软件路径，NSS名额优先有效RT及BULK。hostapd仅接受assoc与authorized均为true的MAC，关联表不跨轮缓存，歧义出口仍拒绝。flow_json.lua逐流使用真实jsonc，减少大对象编码开销。

flowState.reader报告topology/publication/policy/上一轮encode耗时；flowState.budgetUpdates报告批次数、本次命令数与耗时。queue_plan.changes只改变已有类的速率/上限，不重建qdisc或重置队列，writer先续租再批量更新。原autorate仍唯一维护软件CAKE速率。测试入口为test-core.lua、native/test-efficiency.lua及native/test-writer.lua，在独立模型目录运行；不启动现场数据面。

用户回报“暂时没有明显丢包/瞬移”。这是当前主观改善，不是端到端零丢包或长期稳定验收；游戏固件规则仍有撤销/重建，来源后续一次恢复、CPU0 time_squeeze增26及早先部分低速TCP RT回执混合标签保持为待查事实。诊断时大快照重编码有CPU开销，不能把捕获的超时直接归为全部游戏丢包的唯一原因。

## 数据和队列路径

core.lua/collector.lua及native/reader.lua只读现网分类/DHCP/neigh/FDB/AP/完整CT，发布init_net/zone0 confirmed CT ID、full mark、original/reply NAT、MAC/出口绑定和6秒到期。native/writer.lua由独立guardian单独执行native/tc/nft；reader心跳失联8秒恢复。健康owned流不因排名波动撤销；新RT可逐条替换BE/BULK，等旧流真实 FW 删除 ACK 或精确 NO_ENTRY 回执后重用。

athena_ecm_gate.c持有独立CT/CI引用与租约，athena_nss_receipts.c转发原消息/回调，原回调完成后发布serial/tuple/generation ACK/NACK。自然DESTROY后重新CREATE重置确认周期，pending重复CREATE不覆盖旧记录。同步屏障/public decel布尔值不是FW ACK；未知/代理/IPv6保持软件。

下行物理WAN NSS IGS在LAN/AP分叉前；上行物理WAN NSS HTB，host clsact在MacVLAN/原CAKE后补实际NAT账号/精确RT标签。新NSS树跟随CAKE实时账号预算，接手主要40/70 Mbps，RT优先、BE/BULK借用账号余量。原五autorate与RT防滥用分类保持，管理/非IP/未知保留default。原CAKE再经过NSS的额外排队、全量覆盖及Wi-Fi firmware station质量未验收。

## 构建与临时试用

仅针对已验证Athena ARM64 6.18.44/MODVERSIONS-disabled及原模块ABI。在私有目录放原ecm.ko/qca-nss-drv.ko/act_nssmirred.ko，使用已有prepared kernel/toolchain：

```sh
python3 code/controller/native/build.py --kernel PREPARED_KERNEL --toolchain CROSS_BIN --ecm PRIVATE/ecm.ko --driver PRIVATE/qca-nss-drv.ko --output PRIVATE_BUILD
```

build.py不连接路由器，在私有kernel copy构建并校验导出/消息尺寸。ECM/act RAM副本executable sections相同，磁盘原kernel/NSS/ECM/act与EDMA保持；零CRC不是通用ABI保证。构建物仅私有、不提交Git。

把native运行Lua、四个构建.ko/build-result.json及父目录core.lua/collector.lua/athena-qos平铺到私有/tmp/athena-dorm-native（0700/文件0600）。停止旧控制器且保存基线后：

```sh
lua /tmp/athena-dorm-native/classifier_recovery.lua repair
lua /tmp/athena-dorm-native/install_core_guard.lua
lua /tmp/athena-dorm-native/prepare.lua
export ATHENA_QOS_BASE=/tmp/athena-dorm-native
export ATHENA_QOS_BACKEND=native
export ATHENA_QOS_NATIVE_SECONDS=120
sh "$ATHENA_QOS_BASE/athena-qos" start
sh "$ATHENA_QOS_BASE/athena-qos" status
sh "$ATHENA_QOS_BASE/athena-qos" stop
sh "$ATHENA_QOS_BASE/athena-qos" rollback
```

prepare只写自有RAM pins并核对构建/保护配置。0无固定健康期限，1–290临时期限。前提是原root/五bridge及ECM无其它owner；五private/mwan1仅候选期生效，MAC/index/IP/认证/PBR保持。已安装native/launch.sh先按已核对的原配置恢复 classifier 基础队列/规则，通过原 cleanup 完成精确恢复后才清除 terminal marker；再安装有时效只读许可钩子并确认原 core guard 重载，平铺文件、prepare并foreground 0；native/init.sh对应/etc/init.d/athena-dorm-native，无需再安装或enable。

## 验证

21策略模型（目标Lua5.1）、实际receipt C的134 mock、目标nft -c空表/prepare、6.18.44编译/加载；119秒续租/逐流FW ACK、活跃stop、reader退出、手动procd持有3条NSS时owner退出后的独立恢复。IGS部分绑定失败恢复仅mock，未现场注入。本轮17个guard权限模型、目标Lua/Shell解析、两轮22样本及活跃24条stop/full rollback/restart通过。各轮计数分别记录，详情见STATE。

影子默认ATHENA_QOS_BACKEND=shadow，原service.lua/config.example.json和同一入口，设置ATHENA_QOS_TEMPORARY=1/ATHENA_QOS_TEST_SECONDS=120后使用start/status/stop/rollback。它不写数据面，accelerated恒零。父目录init.sh是未安装影子服务，native/init.sh是已安装候选。
