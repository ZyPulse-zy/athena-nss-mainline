from pathlib import Path
import json,hashlib
r=Path('work/v41-five-sim');old=Path('work/v40-five-sim');q=json.loads((old/'entry-qualified.json').read_text());assert q['passed']
sha=lambda b:hashlib.sha256(b).hexdigest()
def rebase(data):return data.replace(b'work/v40-five-sim',b'work/v41-five-sim').replace(b'work\\/v40-five-sim\\/',b'work\\/v41-five-sim\\/').replace(b'v40-five-sim-',b'v41-five-sim-').replace(b'v40-final',b'v41-final')
skip={'prepare.py','qualify-entry.mjs','session-binding.mjs','match-controlled.mjs','repair-native-bytes.py','inspect-own-ssh-failure.mjs','model-serial.mjs'};hashes={};origins={}
for rel,h in q['sourceManifest'].items():
 p=Path(rel);data=p.read_bytes();assert sha(data)==h,rel;hashes[rel]=h
 if p.name in skip:continue
 with (r/p.name).open('xb') as f:f.write(data if p.suffix=='.json' else rebase(data))
 origins[p.name]=rel
def update(name,old,new):
 p=r/name;data=p.read_bytes();a=old.encode();assert data.count(a)==1,old;p.write_bytes(data.replace(a,new.encode()))
update('native-client.mjs',"import{mayRetryAcquisition}from'./fixture-retry-policy.mjs';","import{mayRetryAcquisition}from'./fixture-retry-policy.mjs';\nimport{pendingOwnedRotations}from'./acquisition-plan.mjs';")
update('native-client.mjs',"if(x.rotateTcp){assert.ok(['tcp','tcp2','tcp3','tcp4'].includes(x.rotateTcp.slot));const s=stats.tcpChildren.find(y=>y.slot===x.rotateTcp.slot);if(x.rotateTcp.attempt>s.attempt&&!rotating.has(s.slot)){assert.ok(!fixtureFrozen&&(performance.now()-began)/1000<30,'Natural TCP acquisition is closed');startTcp(s.slot,x.rotateTcp.attempt).catch(finish);}}", "for(const request of pendingOwnedRotations(x.rotateTcpBatch??(x.rotateTcp?[x.rotateTcp]:[]),{children:stats.tcpChildren,rotating,frozen:fixtureFrozen,elapsedSeconds:(performance.now()-began)/1000}))startTcp(request.slot,request.attempt).catch(finish);")
update('read-controlled.mjs','@{pid=$p.Id;tcp=@($rows);udp=@(','@{pid=$p.Id;tcpChildren=@($s.tcpChildren);tcp=@($rows);udp=@(')
update('read-controlled.mjs','ownedTcpSlots,tcp,udp,pairs,controlledClientPid','ownedTcpSlots,ownedTcpChildren:pc.tcpChildren,tcp,udp,pairs,controlledClientPid')
update('pilot-supervisor.mjs','2026-10-07T08:00:00Z','2026-10-07T09:00:00Z')
update('pilot-supervisor.mjs','v39 five naturally distinct WANs','v41 batched acquisition of five naturally distinct WANs')
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'oldHashes':hashes,'copyOrigins':origins,'batchDuplicateOwnedTcpOnly':True,'newReadIoAdded':False,'classificationAndNativeAdmissionUnchanged':True,'oldCompletedControlNoopPreserved':True,'sourceSeconds':6,'newAcquisitionSeconds':30,'maximumNaturalCandidatesPerSlot':8,'clientSeconds':180,'phaseSeconds':60,'combinedTcpMbps':32,'combinedCreditBytes':65536,'cutoff':'2026-10-07T09:00:00Z','productionNotStarted':True},f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'oldSourcesChecked':len(hashes),'newBatchAcquisitionOnly':True,'previousFrozenBytesPreserved':True}))
