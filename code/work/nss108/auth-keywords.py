from pathlib import Path
import json,re
s=Path('work/nss108/wan4-auth-log-private.bin').read_text(encoding='utf-8')
allowed=['认证成功','认证失败','认证超时','用户名或密码错误','密码错误','用户不存在','已在线','已经在线','超出','上限','重复登录','被禁用','余额不足','账号已过期','已停止','退避','失败','用户名','EAP-Failure','Response Identity','Request Identity','发送 EAP']
print(json.dumps({'lastKeywords':[[x for x in allowed if x in l] for l in s.splitlines()[-45:] if any(x in l for x in allowed)]},ensure_ascii=True))
