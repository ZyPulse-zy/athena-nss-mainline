from pathlib import Path
import json
r=Path(__file__).resolve().parent
(r/'prepare-refusal-private.json').write_text(json.dumps({'passed':False,'phase':'local namespace generation','error':'NSS152 has client.py/client-watchdog.ps1, not client.mjs/client-guard.ps1','routerConnectionAttempted':False,'productionWrites':False})+'\n',encoding='utf-8')
s=(r/'prepare.py').read_text(encoding='utf-8').replace("'client.mjs'","'client.py'").replace("'client-guard.ps1'","'client-watchdog.ps1'")
s=s.replace("assert not target.exists(), name\n    target.write_text(text, encoding='utf-8', newline='')", "if target.exists():\n        assert target.read_text(encoding='utf-8') == text, name\n        return\n    target.write_text(text, encoding='utf-8', newline='')")
exec(compile(s,str(r/'prepare.py'),'exec'))
