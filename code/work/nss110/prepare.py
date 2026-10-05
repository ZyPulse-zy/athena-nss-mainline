from pathlib import Path
import json,hashlib
r=Path('work/nss110'); checks=[]
for name in ('controlled-session.mjs','match-controlled.mjs','run.mjs'):
 s=(Path('work/nss105')/name).read_text(encoding='utf-8');v=s.replace('nss105','nss110').replace('NSS105','NSS110')
 assert v.replace('nss110','nss105').replace('NSS110','NSS105')==s
 (r/name).write_text(v,encoding='utf-8');checks.append({'file':name,'onlyNamespaceChanged':True})
for name in ('start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1'):
 s=(Path('work/nss109')/name).read_text(encoding='utf-8');v=s.replace('nss109','nss110').replace('NSS109','NSS110')
 assert v.replace('nss110','nss109').replace('NSS110','NSS109')==s
 (r/name).write_text(v,encoding='utf-8');checks.append({'file':name,'onlyNamespaceChanged':True})
(r/'prepare-receipt.json').write_text(json.dumps({'routerWrites':False,'changedVariable':'explicit committed repair and failed-WAN prewrite epoch','unchangedNssPayload':True,'checks':checks},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'files':len(checks),'productionWrites':False}))
