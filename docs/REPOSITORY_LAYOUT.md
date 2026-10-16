# 路由器项目与配置仓库分工

2026-10-15：后续提交范围集中于 NSS 和 Athena。设备配置入口采用独立的个人仓库 [router-configs](https://github.com/ZyPulse-zy/router-configs)，初始可见性为私有；它不是使用本工程的必需依赖。

| 仓库 | 内容 |
| --- | --- |
| `athena-nss-mainline` | 控制器、平台适配、NSS/无线补丁、测试、构建记录与脱敏证据 |
| `ZyPulse-zy/nss-packages` | 上游 feed fork，保持独立、通用、可复现的贡献补丁 |
| `ZyPulse-zy/router-configs` | 设备配置模板、组件版本引用与恢复索引 |
| `ZyPulse-zy/sysu-bandwidth-aggregation` | 通用校园网多账号聚合参考方案 |

配置仓库从本工程固定 commit 的公开示例起步，记录源路径、源 SHA-256、模板 SHA-256 和脱敏变换。控制器示例为 shadow 模式；六 WAN profile 与 WAN6 autorate 参数均需要本地审查，不能直接当作完整的 native 配置或设备备份。

本工程继续保留既有源码和历史证据，不向配置仓库复制控制器或驱动实现。设备配置仓库不存放账号、密钥、代理订阅、完整备份、原始 CT/socket 记录或模块二进制；私有可见性也不改变这些提交边界。

本次仅整理配置入口与维护职责，没有读取现网私有配置、安装文件、重启服务或重新验证路由器运行状态。NSS #78 和 Athena #1 继续保持 draft。完整 ECM 模块/包构建、WAN6 真实游戏与长期验收的缺口保持原义，不以仓库整理代替。
