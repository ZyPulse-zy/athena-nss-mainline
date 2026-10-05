from pathlib import Path
import json,hashlib
r=Path('work/nss94')
names=['start-dallas.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','read-controlled.mjs','match-controlled.mjs','close-endpoint.mjs']
for name in names:
 p=r/name
 assert not p.exists(),f'Refuse overwrite: {p}'
 s=Path('work/nss93',name).read_text(encoding='utf-8').replace('work/nss93','work/nss94').replace('nss93','nss94').replace('NSS93','NSS94')
 p.write_text(s,encoding='utf-8')
manifest={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir()if p.is_file()and p.suffix in ['.mjs','.py','.ps1']}
(r/'diagnostic-preflight-source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'changes':'Namespace only from actual NSS93 finite controlled load','routerWrites':False,'oldInputsUntouched':True}))
