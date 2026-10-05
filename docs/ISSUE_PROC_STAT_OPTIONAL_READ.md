# 可选进程stat解析：潜在兼容Issue，尚未提交

原NSS68现场在可选`/proc/<pid>/stat`格式断言125处失败，但没有记录具体PID或原始读取结果。不能直接确认现场由EOF造成，更不能称内核缺陷。

NSS69对可选枚举的空/消失/格式不完整stat跳过，guard本身仍严格读取PID/start/argv，未完整的child不准入。15目标RAM检查中旧实现9失败，新实现只有3个预期guard拒绝；完整语法和实际只读scan通过。200ms出生、HZ100、4096枚举边界不变。

对应本地 [helper](../code/work/nss69/core-guard-phase.lua) 与 [最小夹具](../code/work/nss69/stat-eof-fixtures.lua)。它是本项目helper边界；只有取得现场原始stat/身份和对应上游代码版本后，才考虑上游Issue/PR。未提交。
