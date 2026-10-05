# auth-recover.sh：PID字段缺失导致恢复提前退出

仓库：本私有项目；目标文件 `/root/router-project/scripts/auth-recover.sh`。不是已证明的Linux/ECM/NSS上游缺陷，未提交上游。

触发：procd实例不运行，service list返回实例对象但没有pid。旧脚本在set -e下把jsonfilter结果赋给pid；字段缺失时退出1，跳过随后已有的空PID分支。

最小复现（无认证动作）：

```sh
set -eu
pid=$(printf '%s' '{"router-project-minieap":{"instances":{"wan4":{"running":false}}}}' | jsonfilter -e '@["router-project-minieap"].instances.wan4.pid')
printf 'EMPTY_BRANCH_REACHED:%s\n' "$pid"
```

实际目标shell退出1，未打印EMPTY_BRANCH_REACHED。修复只将PID查询换成原生ubus/Lua结构校验，允许pid缺失，查询/结构错误仍失败。6目标RAM案例覆盖有效PID、缺PID、缺实例、错误PID、缺instances、缺服务；不是实际认证成功证明。

实际安装有checkpoint与独立180秒撤销，保护清单只更新目标一行；单独SSH、源码SHA、其它配置和原完整native ownership审核通过后commit。未主动重启认证或接口，未测试本轮自然180秒撤销。后续watchdog一次自然恢复请求返回0；WAN4仍认证失败/down，学校账户/上游认证原因未定，不能把修脚本称为认证恢复。

证据：[修复和资格](../../evidence/nss109-auth-repair.json)、[源码](../../evidence/nss109-source-proof.json)、[终态](../../evidence/nss109-final-audit.json)。
