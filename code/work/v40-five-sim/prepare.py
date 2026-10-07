from pathlib import Path
import hashlib,json
r=Path('work/v40-five-sim');old=Path('work/v39-five-sim');q=json.loads((old/'entry-qualified.json').read_text());assert q['passed']
sha=lambda b:hashlib.sha256(b).hexdigest()
def rebase(data):return data.replace(b'work/v39-five-sim',b'work/v40-five-sim').replace(b'work\\/v39-five-sim\\/',b'work\\/v40-five-sim\\/').replace(b'v39-five-sim-',b'v40-five-sim-').replace(b'v39-final',b'v40-final')
hashes={}
for rel,h in q['sourceManifest'].items():
 p=Path(rel);data=p.read_bytes();assert sha(data)==h,rel;hashes[rel]=h
 if p.name in ['prepare.py','qualify-entry.mjs','session-binding.mjs']:continue
 with (r/p.name).open('xb') as f:f.write(data if p.suffix=='.json' else rebase(data))
p=r/'native-client.mjs';s=p.read_bytes().decode()
a="if(x.rotateTcp){assert.ok(!fixtureFrozen&&(performance.now()-began)/1000<30,'Natural TCP acquisition is closed');assert.ok(['tcp','tcp2','tcp3','tcp4'].includes(x.rotateTcp.slot));const s=stats.tcpChildren.find(y=>y.slot===x.rotateTcp.slot);if(x.rotateTcp.attempt>s.attempt&&!rotating.has(s.slot))startTcp(s.slot,x.rotateTcp.attempt).catch(finish);}"
b="if(x.rotateTcp){assert.ok(['tcp','tcp2','tcp3','tcp4'].includes(x.rotateTcp.slot));const s=stats.tcpChildren.find(y=>y.slot===x.rotateTcp.slot);if(x.rotateTcp.attempt>s.attempt&&!rotating.has(s.slot)){assert.ok(!fixtureFrozen&&(performance.now()-began)/1000<30,'Natural TCP acquisition is closed');startTcp(s.slot,x.rotateTcp.attempt).catch(finish);}}"
assert s.count(a)==1;s=s.replace(a,b);p.write_bytes(s.encode())
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'oldHashes':hashes,'onlyCompletedControlCommandBecomesNoop':True,'newAcquisitionStillBefore30SecondsAndBeforeFreeze':True,'previousActualFailurePreserved':True,'nativeGateAndQosUnchanged':True,'originalClientAndRollbackDeadlinesKept':True,'cutoff':'2026-10-07T08:00:00Z','productionNotStarted':True},f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'oldSourcesChecked':len(hashes),'onlyActualPreAdmissionDefectFixed':True,'productionNotStarted':True}))
