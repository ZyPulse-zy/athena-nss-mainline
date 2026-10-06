from pathlib import Path
import json
r=Path(__file__).resolve().parent
last=json.loads((r/'load-latest-private.json').read_text());p=r/'load-v2-reference-private.json';assert not p.exists();p.write_text(json.dumps(last,indent=2)+'\n',encoding='utf-8')
for a,b in [('pilot-supervisor-v2.mjs','pilot-supervisor-v3.mjs'),('epoch-driver-v2.mjs','epoch-driver-v3.mjs')]:
    p=r/b;assert not p.exists();s=(r/a).read_text(encoding='utf-8').replace('run2','run3').replace('session-binding-v2.mjs','session-binding-v3.mjs')
    if a.startswith('pilot'):
        s=s.replace('epoch-driver-v2.mjs','epoch-driver-v3.mjs').replace('frozen-qualified-inputs-v2','frozen-qualified-inputs-v3').replace('entry-source-manifest-v2.json','entry-source-manifest-v3.json')
        anchor="assert.ok(selected&&selected.tcp.wan!==4);assert.ok(read(load.dir,'udp-baseline-qualified').returned>0);";assert s.count(anchor)==1
        s=s.replace(anchor,anchor+"assert.ok(selected.tcp.original.sport<config.tcpSourcePort+7,'No reserved candidate for fresh TCP; reject before staging');")
    p.write_text(s,encoding='utf-8',newline='')
print('Reserve one of the original eight TCP candidates before any staging. Old failures/native/client/port budget preserved.')
