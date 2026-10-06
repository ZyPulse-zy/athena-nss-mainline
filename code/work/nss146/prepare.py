"""Keep native leases strict; closed software phases compare fresh identities."""
from pathlib import Path
import hashlib, json

r=Path('work/nss146')
proof=json.loads(Path('work/nss145/entry-qualified.json').read_text())
assert len(proof['sourceManifest'])==23
for file,digest in proof['sourceManifest'].items():
    src=Path(file); data=src.read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest
    if src.name in ['prepare.py','qualify.mjs','session-binding.mjs']:
        continue
    changed=data.replace(b'nss145',b'nss146').replace(b'NSS145',b'NSS146')
    assert changed.replace(b'nss146',b'nss145').replace(b'NSS146',b'NSS145')==data
    if src.name=='controlled-session.mjs':
        needle=b"from '../nss140/module-stage.mjs'"
        assert changed.count(needle)==1
        changed=changed.replace(needle,b"from './module-stage.mjs'")
    with (r/src.name).open('xb') as f:f.write(changed)

same=['qos-physical.lua','tag-normalizer.lua','module-stage-guardian.lua','pack-lua.mjs',
      'pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','service-epoch.mjs']
for name in same:
    with (r/name).open('xb') as f:f.write((Path('work/nss140')/name).read_bytes())
for name in ['normalizer-qualification.json','qos-native-qualification.json']:
    with (r/name).open('xb') as f:f.write((Path('work/nss140')/name).read_bytes())

for name in ['module-stage.mjs','payload.mjs']:
    data=(Path('work/nss140')/name).read_bytes()
    changed=data.replace(b'nss140',b'nss146').replace(b'NSS140',b'NSS146')
    assert changed.replace(b'nss146',b'nss140').replace(b'NSS146',b'NSS140')==data
    with (r/name).open('xb') as f:f.write(changed)

consumer=(Path('work/nss140')/'classifier.lua').read_bytes()
def once(data,a,b):
    assert data.count(a)==1,a
    return data.replace(a,b)
consumer=once(consumer,b'function M.compareEpoch(epoch,s,c,now)',b'function M.compareEpoch(epoch,s,c,now,closed)')
consumer=once(consumer,b'or now>=epoch.epochUntil then',b'or(not closed and now>=epoch.epochUntil)then')
consumer=once(consumer,b'function out.compareObserved()',b'function out.compareObserved(closed)')
consumer=once(consumer,b'Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now())',b'Consumer.compareEpoch(epoch,out.lastObservedSnapshot,out.lastObservedContext,now(),closed)')
with (r/'classifier.lua').open('xb') as f:f.write(consumer)
fast=(Path('work/nss140')/'fast-path.lua').read_bytes()
fast=once(fast,b'local frame=A.observe();local C=A.compareObserved()',b'if not active then stopped()end\n  local frame=A.observe();local C=A.compareObserved(not active)')
fast=once(fast,b"if C.action~='KEEP_IMMUTABLE_EPOCH'then",b"if C.action~='KEEP_IMMUTABLE_EPOCH'then\n   R.rejectedComparison=C")
with (r/'fast-path.lua').open('xb') as f:f.write(fast)
print(json.dumps({'prepared':True,'singleBehaviorChange':'Software-only comparison does not use expired native epoch',
    'activeNativeExpiryUnchanged':True,'closedEcmStoppedAndZeroRequired':True,'classAndIdentityDriftStillRejected':True,
    'sourceSeconds':6,'nativeSeconds':27,'ownerSeconds':100,'routerWrites':False,'old140And145FrozenSourcesUnchanged':True}))
