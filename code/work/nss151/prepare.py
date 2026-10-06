"""Explicit new orchestration namespace; both deployed native factories stay unchanged."""
from pathlib import Path
import json,hashlib
w=Path(__file__).resolve().parents[2];r=w/'work/nss151'
def write(name,text):
    p=r/name
    assert not p.exists(),name
    p.write_text(text,encoding='utf-8',newline='')
def copy(old,name,namespace=None):
    p=w/old
    if namespace is None:
        q=r/name;assert not q.exists();q.write_bytes(p.read_bytes())
    else:write(name,p.read_text(encoding='utf-8').replace(namespace,'work/nss151'))
for name in ['health.mjs','read-final-physical.mjs','read-controlled.mjs','match-controlled.mjs','close-endpoint.mjs','discover-peer.py']:
    copy('work/nss150/'+name,name,'work/nss150')
for name in ['client-watchdog.ps1','server.py','probe-peer.py','endpoint-firewall-guardian.py']:
    copy('work/nss150/'+name,name)
for name in ['ssh-client.mjs','upload-server.py','upload-ack.mjs','bounded-pacer.mjs','watcher-read.lua']:
    copy('work/nss138/'+name,name)
for name in ['declared-baseline.mjs','service-epoch.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','failed-wan-owner.lua']:
    copy('work/nss140/'+name,name)
copy('work/nss138/pause-control.mjs','pause-control.mjs','work/nss138')
start=(w/'work/nss150/start-dallas-v5.mjs').read_text().replace('work/nss150','work/nss151').replace('NSS150_PASSIVE_READY','NSS151_PASSIVE_READY').replace("config.bulkDirection='download'","config.bulkDirection='upload'")
write('start-dallas.mjs',start)
p=r/'discover-peer.py';p.write_text(p.read_text().replace('NSS150_PASSIVE_READY','NSS151_PASSIVE_READY'),encoding='utf-8',newline='')
audit=(w/'work/nss150/current-audit-diagnostic-v5.mjs').read_text().replace('work/nss150','work/nss151').replace('./session-binding-v5.mjs','./session-binding.mjs').replace(r'automatic-epoch-\d+',r'(?:automatic-epoch|controlled-class)-\d+')
write('current-audit-diagnostic.mjs',audit)
change=(w/'work/nss138/controlled-session.mjs').read_text().replace('work/nss138','work/nss151').replace("from './module-stage.mjs'","from '../nss138/module-stage.mjs'")
needle=' const preauditSelected=pair[0];let selected;'
assert change.count(needle)==1
change=change.replace(needle,needle+"\n const continuityPath=process.argv[3];assert.equal(continuityPath,'work/nss151/run/continuity-private.json');\n const continuity=JSON.parse(fs.readFileSync(continuityPath));assert.deepEqual(preauditSelected,continuity.selected,'Original controlled pair changed before class-change stage');")
write('class-session.mjs',change)
normal=(w/'work/nss150/controlled-session-v5.mjs').read_text().replace('work/nss150','work/nss151').replace('./session-binding-v5.mjs','./session-binding.mjs').replace('current-audit-diagnostic-v5.mjs','current-audit-diagnostic.mjs').replace('work/nss151/run-v5/continuity-private.json','work/nss151/run/continuity-private.json')
write('epoch-session.mjs',normal)
first_inputs=json.loads((w/'work/nss138/entry-qualified.json').read_text())['sourceManifest']
assert all((w/f).is_file() and hashlib.sha256((w/f).read_bytes()).hexdigest()==v for f,v in first_inputs.items())
write('preparation-private.json',json.dumps({'passed':True,'bothExistingFactoriesUnchanged':True,'firstFactory':'work/nss138/module-stage.mjs','successorFactory':'work/nss149/module-stage.mjs','currentNamespaceDependenciesExplicit':True},indent=2)+'\n')
print(json.dumps({'passed':True,'newNamespace':'NSS151','unchangedNativeFactories':[138,149],'noRouterWrites':True}))
