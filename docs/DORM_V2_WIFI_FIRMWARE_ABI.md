# 003：精确固件 ABI 核查与 ath11k 消费端修复

## 固件身份与现场消息证据

现场 NSS 固件与固定 firmware 源码 `90448eeb2b8f5d172caedfe6d96ab3bacb058c09` 的发行包解出的 IPQ6018 `NSS.FW.12.5-210-CP.R` retail_router0.bin 逐字节相同。发行包 SHA256、recipe blob 与固件 SHA256 见匿名证据。发行包未提供固件 C 源码或调试符号；没有假称已取得厂商实现。

20 秒独立有界观察转发原回调，最多64行，仅保存长度、peer数量及两种步长的匹配布尔值。已有统计消息保持原样，不打开额外统计、不存 MAC/peer ID/消息内容。64条消息含2和5个peer，212步长全部对应当前peer且无重复，196步长全部失败。原回调恢复，观察模块已卸载，ownership_lost=0。源函数模型25项通过；内核真实并发不是离线模型模拟出来的结论。

`cm.len=216` 是固定模板长度，不能除以peer数。目标 AArch64 探针：旧peer196/模板200；新peer212/模板216；两者整体 nss_wifili_msg 上限均2096。实际 skb 长度未由该观察器记录。

## 生产、转发、消费三层

真实生产端为固件。固定 NSS 源码 `nss_wifili.c:nss_wifili_handler` 只对SOC统计进行本地解析；peer统计仅检查公共头和消息上限，然后将原指针交给注册回调。`nss_wifili_log.c` 明确不记录该类payload；全树 wpcs/peer_ctrl_stats 引用只在导出头声明中。

因此 NSS 主机头的196声明不等于固件输出196。此前以主机头生成“provider”消息的模型只能证明两份主机定义一致，不能证明真实 wire ABI；原196/196、历史配对212/212编译记录保留。此次用实际固件消息校正模型，003缩小为仅 ath11k 的 `NSS_FIRMWARE_VERSION_12_5`，不更换 NSS 驱动。

固件 → nss_core 状态消息公共校验 → nss_wifili_handler 原指针转发 → ath11k_nss_wifili_event_receive → peer数组索引/统计更新。修复错误步长和条件字段偏移；不更改 DSCP/TID/WMM/AQL策略。

## 构建、验证与部署

`build-firmware-212-cn-02` 使用固定 Linux6.18.44/GCC14.4真实Kbuild，全套原版/候选模块严格modpost通过。保留001/002/004；候选ath11k212，NSS196。01因native m4工具不可用而失败，未作为候选；02使用已验证native工具目录。

```sh
python3 tools/build_wifi_modules.py --prepared ../linux-wifi-build/prepared --firmware-source ../linux-wifi-build/firmware --sdk-staging ../linux-wifi-build/staging_dir --host-tools ../linux-wifi-build/lua-runtime/root/usr/bin --patch-set firmware-212-cn --output ../linux-wifi-build/build-firmware-212-cn-new
python3 tools/test_wifi_stat_abi.py --source ../linux-wifi-build/prepared/backports --nss-source ../linux-wifi-build/prepared/nss-drv --firmware-source ../linux-wifi-build/firmware
python3 tools/test_wifi_driver_runtime.py
```

已完成RAM试装及持久部署。最终ath11k SHA256 `6d21891e207dc7b80bf17fef99101e62422a8db943bf57c71aa50b08b16d24fa`；部署进展和其余哈希见匿名证据，二进制/检查点/日志仅保留私有目录。仅ath11k替换，mac80211/NSS/mesh/cfg80211不变。vermagic、依赖、参数、导入/导出集合比较通过；现场未启用MODVERSIONS，CRC不支持，不能声称CRC匹配。

部署前发现native因reader心跳超时已回退；原生命周期恢复后来源新鲜。首次RAM试装遇到异步native启动期间core guard暂时恢复原版，保护哈希检查过早触发真实独立回退。原模块、保护、六WAN/source确认恢复。核验修正为有界等待来源新鲜且所有保护哈希精确一致，不放宽合同；新检查点重试，结果单独记录。

## 保留与未验证边界

保留CN、现有信道/带宽/功率、WMM、聚合、省电、六WAN、认证/PBR/NAT、代理/Tailscale、CAKE/autorate和保守游戏WAN6策略。没有按人数调负载、没有给UDP统一提权、没有主动拥塞或游戏验收。

多peer实测证明记录步长；完整字段含义依赖与精确版本一致的头定义，未逐项对比固件计数器。统计开关当前未提升，修复不保证 iw 能直接读到全部NSS统计。最终空口TID/AC、RT/BULK真实队列、NSS路径AQL效果、双5GHz长期负载、冷启动与正式游戏验收仍缺。003修复统计消费，不能据此声称游戏延迟改善。

加载后精确候选回调地址匹配成功；32条四peer消息再次仅212步长正确，32条单peer按规则不可判别。30秒被动观察11样本，sourceGaps0、未确认0；17个RT创建/进展样本、29个标签核验样本、标签不匹配0。实际NSS数量0–5；这些来自正常现场流量，没有主动造流。标签和NSS字节进展不等于最终无线AC、零丢包或游戏收益。

有界观察器源码 `code/controller/native/wifi-abi-observer.c` 与实际源码函数模型均提交；`tools/build_wifi_abi_observer.py` 从已有真实 .cmd 重放目标编译旗标，仅离线构建，绝不自动加载。该模块仅适用于核验的精确目标布局，动态回调/peer查找地址仅在私有目录解析，装载前还需精确匹配检查与独立清理守护。它不接入日常六秒循环。

观察器重现构建命令：

```sh
python3 tools/build_wifi_abi_observer.py --build ../linux-wifi-build/build-firmware-212-cn-02 --kernel ../linux-wifi-build/prepared/kernel --output ../private/abi-observer-new
python3 tools/test_wifi_abi_observer.py
```

重现构建工具最初两次分别缺NSS data-plane绝对include和fixdep依赖文件，被拒绝；修复后03严格modpost/完整链接通过，仅离线产物，未加载。
