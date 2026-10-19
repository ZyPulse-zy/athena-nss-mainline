# Athena NSS

面向 OpenWrt 与京东云雅典娜 AX6600 的多 WAN（广域网）网络控制研究。项目围绕自动流量分类、NSS（网络子系统）硬件加速和 QoS（服务质量）调度，探索大流量传输与实时连接共存时的转发、队列和恢复机制。

本仓库保存控制器原型、代码快照和实验记录，尚未整理成通用安装包。

## 研究内容

- 结合流量分类、进程与 socket（套接字）归属、连接跟踪信息，选择可加速的连接。
- 核对连接标记、NAT（网络地址转换）和 WAN 归属，将实时流与大流量连接映射到对应队列。
- 根据带宽预算决定准入；未识别或不符合条件的流量保留软件转发路径。
- 使用租约、状态检查和独立守护处理流退出、分类变化、控制器失联及恢复。

## 已记录的能力与限制

最近一组功能记录为 **2026-10-08 的连续续租控制器**：

- 支持最多两条 TCP 大流量连接和一条已准入的 UDP 实时连接。
- 合格连接可以持续续租，连接身份、来源新鲜度与失联撤销检查持续生效。
- 已记录约 197 秒的单实时流硬件验证、65 次续租，以及主动停止后的完整恢复。

这些结果对应特定设备、固件和实验条件。长期稳定性及大下载期间的实际游戏丢包问题仍未完成验证。详见[控制器说明](docs/RESIDENT_CONTINUOUS.md)和[对应实验数据](evidence/resident-continuous.json)。

## 目录

| 路径 | 内容 |
| --- | --- |
| [code/](code/) | 分类器、控制器及各轮实验的源代码快照 |
| [docs/](docs/) | 设计说明、问题分析、状态与实验记录 |
| [evidence/](evidence/) | 结构化测量结果和验证记录 |
| [reports/](reports/) | 实验报告 |
| [tools/](tools/) | 仓库校验、离线回放和数据同步工具 |
| [source-manifest.json](source-manifest.json) | 源文件路径及内容哈希清单 |

## 阅读与离线检查

- [连续续租控制器](docs/RESIDENT_CONTINUOUS.md)：当前代码快照的行为与验证范围。
- [多 WAN 与队列调度](docs/MULTI_WAN_QOS.md)：设计及分阶段实验结果。
- [实验记录](docs/EXPERIMENT_LOG.md)与[证据索引](docs/ARTIFACT_INDEX.md)：查阅具体轮次。
- [状态记录](docs/STATE.md)与[问题记录](docs/KNOWN_FAILURES.md)：按日期查看进展及未解决问题。

使用 Python 3 校验源文件哈希、文档链接和仓库内容：

```sh
python3 tools/check_repository.py
```

使用 Lua 5.1 执行准入逻辑的离线回放：

```sh
python3 tools/replay_admission.py --lua /path/to/lua5.1
```

回放使用模拟的输入输出与时间环境，验证逻辑行为；硬件结果见相应实验记录。其它回放入口见[本地运行说明](docs/LOCAL_SETUP.md)。

## 相关独立项目

| 项目 | 用途 |
| --- | --- |
| [cake-snapshot](https://github.com/ZyPulse-zy/cake-snapshot) | 批量读取 CAKE 队列配置带宽 |
| [fenced-run](https://github.com/ZyPulse-zy/fenced-run) | 带写入互斥、超时和进程清理的命令执行工具 |
| [offload-ledger](https://github.com/ZyPulse-zy/offload-ledger) | 异步加速规则的调度、重试与恢复状态机 |
| [nss-kbuild-lab](https://github.com/ZyPulse-zy/nss-kbuild-lab) | 基于固定源码版本的 NSS 与 ath11k 编译回归 |

## 许可证

本仓库尚未设置统一的仓库级许可证。相关独立项目的许可证见各自仓库。
