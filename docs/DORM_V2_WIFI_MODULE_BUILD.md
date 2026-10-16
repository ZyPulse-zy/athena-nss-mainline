# Linux 完整无线模块构建与 ABI 纠正（2026-10-11）

三份候选已在当前 Linux 完成原版和修订版完整模块交叉编译、严格 modpost、真实目标 Kbuild 布局核对及离线回归。未连接路由器，没有部署、重启或无线配置变化。开发过程中同步远端新增 e5f344b 六账号候选；它的工作保留，未启用。

## 必须纠正的旧结论

此前把 NSS 配方 EXTRA_CFLAGS 中的 `-DNSS_FIRMWARE_VERSION_12_5` 当作实际生效，宣称原 provider/consumer 为 212/196。这一推断撤回。Linux 6.18 的 Kbuild 不再采用该 legacy 变量；NSS 的 ccflags-y 只接收 NSS_DRV_EXTRA_INCLUDES。真实 `.nss_wifili.o.cmd` 和 `.nss.o.cmd` 重放到 AArch64 探针证实原版两端都是 196 字节。

| 实际编译案例 | NSS peer / retry offset | ath11k peer / retry offset | 结论 |
|---|---|---|---|
| 原版 | 196 / 180 | 196 / 180 | 两端一致，不能据此声称现场 ABI 错位 |
| 旧版仅修改 consumer 的 003 | 196 / 180 | 212 / 188 | 全模块可编译，但 ABI 不匹配；验证明确拒绝 |
| 本轮修订 003，两端 ccflags-y 配对 | 212 / 188 | 212 / 188 | 主机两端一致；真实 firmware 消息布局仍未知 |

003 现在同时修改 NSS Makefile 和 ath11k Makefile，使配方原意的 12.5 宏明确进入 Kbuild。必须配对使用，不能单独给 ath11k 加宏。它仍是待固件 ABI 验证的候选，宏会影响其他条件结构，不能凭编译成功上线。此前匿名 JSON 保留历史原字节；最新结论以本报告和新证据为准。无线累计重试/失败异常也不能据旧 ABI 模型归因。

001 跨 peer drop 临时累加未清零、002 HAS_TX_QUEUE 后 host queue 未初始化仍有真实完整函数定向复现；修后分别两种宏各 41 断言、160 断言通过。003 原版、仅 consumer 拒绝、两端配对三 peer 模型通过，与实际目标布局证据分开记录。

## 源码、工具链与产物

固件源码固定 `90448eeb2b8f5d172caedfe6d96ab3bacb058c09`，Backports 7.2 原归档及 299 补丁、NSS `6aa14c78e097b29c493ff2fef87e4d35906b2b5a` 和 20 补丁沿用已验证重建。四项依赖固定源提交、33 补丁及四份配方共 37 文件的 Git blob 校验记录在证据内。

本机 Ubuntu 26.04.1；交叉 SDK GCC 14.4.0（r40836-c0c50db20e），SDK 归档 SHA256 `4ae47c1c51fbc74e013c6b3a64869352cb66a618407f6eb16576bfd1161d81f8`。kernel 6.18.44 使用现有 prepared .config、Module.symvers 和 generated headers，构建前后三项哈希一致。旧 Windows 文件系统只读读取后复制到本地；85 个 WSL 链接由原 kernel tar 恢复。Linux 本地解包 Lua 5.1/cjson、bison/flex/m4，无系统安装或现网操作。SDK bison 无法启动迁移后的 m4，改用本机解包的 host tools。

原版与修订版各生成八个完整模块：compat、qmi_helpers、ath、ath11k、ath11k_ahb、ath11k_pci、mac80211、cfg80211。另编译 qca-ssdk、qca-nss-dp、qca-nss-drv、qca-nss-wifi-meshmgr，NSS/mesh 在配对补丁后重新编译。20 项最终产物记录含 SHA256、大小和 vermagic `6.18.44 SMP mod_unload aarch64`。严格 modpost 未忽略未定义符号；模块编译阶段没有 warning；host Kconfig 和外置 ABI 探针各存在一项非致命 warning，原文和阶段记录保留。

这是完整外置模块构建，不是整套 OpenWrt 软件包/固件构建，也未重现已安装二进制。没有加入现场 ath11k 的 CN 带宽 shim；未完整复用包级优化选项，不能声称按位复现。只编译无线必需的 mesh client，不代表全部 NSS clients 包构建完成。模块及原始日志留在私有 work/linux-wifi-build/build-06，不入 Git，不作为可直接替换的现网产物。

## 重现命令

在仓库根目录执行；prepared、firmware、staging_dir 是本地已校验输入，输出目录必须不存在。

```sh
python3 tools/build_wifi_modules.py \
  --prepared ../linux-wifi-build/prepared \
  --firmware-source ../linux-wifi-build/firmware \
  --sdk-staging ../linux-wifi-build/staging_dir \
  --host-tools ../linux-wifi-build/lua-runtime/root/usr/bin \
  --output ../linux-wifi-build/build-new --jobs 4
python3 tools/test_wifi_peer_drop.py --source ../linux-wifi-build/prepared/backports
python3 tools/test_wifi_tx_queue.py --source ../linux-wifi-build/prepared/backports
python3 tools/test_wifi_stat_abi.py --source ../linux-wifi-build/prepared/backports --nss-source ../linux-wifi-build/prepared/nss-drv --firmware-source ../linux-wifi-build/firmware
python3 tools/test_wifi_transport.py
```

001/002 的应用根是 backports；003 的应用根包含 backports 与 nss-drv 两个子目录，由构建工具按序处理、拒绝 fuzz/offset。构建工具复制候选源码后编译，不安装模块。

同步后的五/六账号各 13 Lua + 2 C 回归、51 Lua/12 shell 语法通过；无线模型 158 断言，传输四测试通过。nixio、内核/固件 I/O 为替身，未验证目标 nft parser。原版定向失败、旧 consumer-only ABI 失败以及前五轮构建失败均记录，未用成功覆盖失败。

## 配置与下一步依据

保持当前 NSS、五 WAN、认证/PBR/NAT、代理/Tailscale、CAKE/autorate、WMM、聚合、省电，以及两个不同 80 MHz 频块和现有功率。此前自然窗口负载方向变化，不支持按人数做固定均衡或换同频块主信道。001/002 是小范围软件修复候选；003 必须先取得实际 firmware ABI。源码显示 NSS/HAS_TX_QUEUE 路径绕过 host TXQ/AQL，仍缺同机 RT/BULK 最终 TID/AC、无线下行及客户端上行验证。

本轮未刷新现场版本或健康状态；2996d40 是此前最后核对的安装版本，不能把本轮仓库/编译版本称已安装。正式游戏验收继续延期。部署、模块替换、无线重载/参数、服务重启或主动拥塞需新的明确许可，PR #1 保持 draft、不合并。

[完整编译证据](../evidence/dorm-v2-wifi-linux-build.json) · [迁移、失败及离线验证](../evidence/dorm-v2-wifi-linux-validation.json) · [此前无线观察与发送路径](DORM_V2_WIFI_AUDIT.md)
