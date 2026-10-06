from pathlib import Path
import json
r=Path(__file__).resolve().parent
(r/'prepare-v2-refusal-private.json').write_text(json.dumps({'passed':False,'phase':'local namespace generation','error':'Optional non-SSH client.py is absent in NSS152; actual test uses ssh-client.mjs','routerConnectionAttempted':False,'productionWrites':False,'priorRefusalFilenameClaimInvalid':True})+'\n',encoding='utf-8')
s=(r/'prepare.py').read_text(encoding='utf-8').replace("'client.mjs',",'').replace("'client-guard.ps1'","'client-watchdog.ps1'")
s=s.replace("assert not target.exists(), name\n    target.write_text(text, encoding='utf-8', newline='')", "if target.exists():\n        assert target.read_text(encoding='utf-8') == text, name\n        return\n    target.write_text(text, encoding='utf-8', newline='')")
required=['ssh-client.mjs','client-watchdog.ps1','server.py','upload-server.py','upload-ack.mjs','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','close-endpoint.mjs','failed-wan-owner.lua','declared-baseline.mjs','crash-read.lua']
assert all((r.parent/'nss152'/name).is_file() for name in required)
exec(compile(s,str(r/'prepare.py'),'exec'))
