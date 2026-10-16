# 001/002 保留现场 CN 修正与 196 字节布局的候选

观察入口已经安装，本轮不再安装或重复验收。本轮仅离线构建与只读捕获现有模块，不进行无线重载、服务/模块替换。六 WAN 和现网无线保持。

找回了原 CN ELF shim 生成脚本和模块，模块 SHA256 与现场 `8a0928ae…` 一致。新 004 是该已部署逻辑的源码移植：仅 CN、规则数不超过 64、精确 5735–5835 MHz/160 MHz 时改为 80 MHz，保留原警告；其他频率、功率、标志不变。它是兼容性保留补丁，不是新增无线调优。七组边界场景/14 断言直接测试实际源码函数，内核 I/O 为替身。

新增构建配置 `--patch-set stable-cn`：原版和修订版都保留 004；修订版只应用 001/002，不应用 003，不改变 NSS/ath11k 196 字节布局。保持现有 NSS/mesh，不把本地编译的依赖模块纳入替换集合。

```sh
python3 tools/build_wifi_modules.py --patch-set stable-cn \
  --prepared ../linux-wifi-build/prepared \
  --firmware-source ../linux-wifi-build/firmware \
  --sdk-staging ../linux-wifi-build/staging_dir \
  --host-tools ../linux-wifi-build/lua-runtime/root/usr/bin \
  --output ../linux-wifi-build/build-stable-cn-new --jobs 4
python3 tools/test_wifi_cn_shim.py --source ../linux-wifi-build/prepared/backports
python3 tools/verify_wifi_module_compatibility.py \
  --installed /private/captured-installed-modules \
  --backports ../linux-wifi-build/build-stable-cn-new/backports \
  --readelf /private/sdk/bin/aarch64-openwrt-linux-musl-readelf
```

第一次完整构建虽通过，但与现场 mac80211 的导入符号比较明确拒绝：缺少六个 LED 相关符号。原因是离线 recipe evaluation 没有复用真实 include/kernel.mk 的 `-include $(LINUX_DIR)/.config`，导致 CONFIG_LEDS_TRIGGERS 未进入配方配置。已修复读取 prepared kernel 配置，而非硬加 LED 选项。失败和修订后的结果分别保留。

现场 kernel 配置未启用 MODVERSIONS，模块没有版本 CRC 数据；不能声称 CRC 匹配。以实际 vermagic、模块参数/依赖、导入符号和导出 __kstrtab 记录比较，结合严格 modpost 和固定源码证据。原安装 ELF 已剥离部分 __ksymtab 本地符号，直接比较这些符号会产生假差异，所以读取保留的 __kstrtab 导出名称。上述检查仍不证明实际加载和运行 ABI。

003 未纳入这个候选。只读取得现场 qca-nss0-retail.bin 指纹，尚无该指纹对应的权威 wire 结构或实际消息边界证据，不能从固件版本字符串、其他分支或主机探针推定 212 字节布局。

必要驱动切换将中断无线关联；独立回退、受控 unload/load 顺序、六 WAN/source/native 保护与加载后验证仍需完成。另一个任务正在处理游戏分流，不能同时修改共享现场；既有用户部署许可继续有效，不重复询问。PR #1 草稿、不合并。

修订后原版/修订版各八个完整无线模块、四依赖严格构建通过；实际目标 Kbuild 四探针均为 196/180，12.5 宏未生效。mac80211 LED 配置已与现场对齐。ath11k 与 mac80211 实际导入/导出集合、依赖、参数和 vermagic 均匹配；CRC 不可用，未加载。

[本轮完整证据](../evidence/dorm-v2-wifi-stable-cn-candidate.json)
