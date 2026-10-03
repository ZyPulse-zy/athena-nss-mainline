# 暂存支线

这些事项不能阻塞主线，也不代表确认的上游缺陷。

- bridge B-shaper、普通 IFB/private MacVLAN 直接挂 NSS qdisc 的限制。
- ECN、tc JSON、HTB dump 兼容性。
- NSS FQ/AQM、限速精度与拥塞行为；在主线可稳定运行后验证。
- 五 WAN QoS 映射、共享下行预算、Wi-Fi、autorate。
- 原生改类后的精确撤销与重学、长期硬件过期行为，需要独立现场验收。

本地已知问题：大 JSON 发布成本；旧控制器固定 WAN5；控制器与原生 gate 的 full-mark 条件不完全一致；初始准入失败缺少逐次原因记录。已有修复或诊断不能自动提升为上游驱动 Issue。

潜在 Issue/PR 应包含仓库/文件/版本、最小复现、修改前后证据、回滚与限制。当前没有提交上游。
