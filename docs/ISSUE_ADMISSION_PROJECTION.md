# 私有控制器问题候选：准入投影缺失的诊断

状态：本地 backlog，未提交上游。问题属于本工作区消费者的可观测性，不是已证明的 qca-nss-ecm / NSS firmware 缺陷，也不是历史拒绝原因已知。

仓库/文件：当前NSS47常驻worker镜像 `code/work/nss46/worker.lua` 的 `projectAdmission`、`publishClassification`；`code/work/nss49/classifier.lua` 的 `ready` 仅报告通用断言。候选为 `code/work/nss53/classifier.lua` 与 `selection-diagnostic.lua`。已核验现网完整config中的worker哈希与该NSS46镜像相同，不能凭路径猜部署。

## 问题与最小复现

实际 `classification.json` 带 `admissionProjection`，范围是 bulk 和 admitted RT，而不是全部 CT 分类输入。已退出、变成非准入类、RT预算拒绝，都可能不在投影。单凭投影没有选中键，只能证明“此次准入投影不含该键”，不能证明完整CT不存在或哪个槽位为何改变。

默认ECM关闭且计数全零，使用当前已核验owner和两个合成不存在的键执行原实际ready读取，不注入流或改规则。原断言以 `Selected class is not admitted` 终态拒绝。新诊断在这个同一失败帧记录TCP/UDP投影存在性、分类、预算、计数/标签与身份比较；投影缺失标记 `NOT_IN_ADMISSION_PROJECTION`，完整存在性未知。

只有ready已经最终拒绝，才至多读一次已有完整snapshot。要求producer/generation/boot/config/PID/start和全部query sequence、started/finished uptime、method、command、boot、rawStatus、exitCode、family、zone、authorized client严格相同；原consumer.inspect再验证完整快照。来源不匹配、缺文件、投影而非完整帧、校验失败均记录unknown，不改变拒绝/重试/权限。不重新执行conntrack查询，不读取第二份准入classification。

## 修改前后证据

见 [诊断证据](../evidence/nss53-diagnostics.json)。本地完整适配器原21检查重放＋39新增断言通过，IO/时间/ACK被替代；目标原生JSON helper14项独立通过。目标实际ready路径完整保留，RAM harness只省略未用renewal等函数：轻载真实发布同源完整帧确认两个合成键不存在；真实Steam下载中query来源不同，`completeSelectionUnavailable` 明确记录 `Complete diagnostic source differs`。二者均终态拒绝，ECM仍全零，`retryable=false`。

NSS53新实验入口159项绑定，内嵌consumer及原准入、retry、来源期限、单WAN预算和独立恢复决定保持。第一诊断候选错误地将投影缺失当完整不存在，已在绑定前修正，原候选/输出仍私有保存；未安装或用它开放ECM。该修复仅避免误判诊断，不会使先前被拒的流获得权限。

本轮没有真实CS2同WAN配对、没有NSS53 B段。旧第一/第六次缺少拒绝帧，不能根据本次合成键或之后下载完成倒推历史原因。以后真实配对若被拒，应依据那次相同来源的事实定位；不为获取完整帧延长TTL或重试权限。
