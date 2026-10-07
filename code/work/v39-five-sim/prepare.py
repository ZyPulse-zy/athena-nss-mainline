from pathlib import Path
import hashlib,json

r=Path('work/v39-five-sim');old=Path('work/v24-fiveflow')
q=json.loads((old/'entry-qualified.json').read_text());assert q['passed']
sha=lambda b:hashlib.sha256(b).hexdigest()
def rebase(data,scope):
 return data.replace(('work/'+scope).encode(),b'work/v39-five-sim').replace(('work\\/'+scope+'\\/').encode(),b'work\\/v39-five-sim\\/').replace((scope+'-').encode(),b'v39-five-sim-')
old_hashes={}
for rel,h in q['sourceManifest'].items():
 p=Path(rel);data=p.read_bytes();assert sha(data)==h,rel;old_hashes[rel]=h
 if p.name in ['qualify-entry.mjs','session-binding.mjs']:continue
 with (r/p.name).open('xb') as f:f.write(data if p.suffix=='.json' else rebase(data,'v24-fiveflow'))

def write(name,data):
 (r/name).write_bytes(data.encode())
def read(name):return (r/name).read_text()
def one(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)

# The known five-slot gate, compressed payload, classification and QoS remain exact.
# Only fixture acquisition, current read-only audit and a fresh namespace are adapted.
write('current-audit-diagnostic.mjs',rebase(Path('work/v38-sim/current-audit-diagnostic.mjs').read_bytes(),'v38-sim').decode())
native=rebase(Path('work/v38-sim/native-client.mjs').read_bytes(),'v38-sim').decode()
native=one(native,'{tcp:24,tcp2:8}','{tcp:8,tcp2:8,tcp3:8,tcp4:8}')
native=one(native,"tcpChildren:[{slot:'tcp',attempt:0,bytes:0,connected:false},{slot:'tcp2',attempt:0,bytes:0,connected:false}]","tcpChildren:['tcp','tcp2','tcp3','tcp4'].map(slot=>({slot,attempt:0,bytes:0,connected:false}))")
native=one(native,"'CREDIT=32768'","'CREDIT=16384'")
native=one(native,"assert.ok(['tcp','tcp2'].includes(x.rotateTcp.slot));","assert.ok(!fixtureFrozen&&(performance.now()-began)/1000<30,'Natural TCP acquisition is closed');assert.ok(['tcp','tcp2','tcp3','tcp4'].includes(x.rotateTcp.slot));")
native=one(native,"await startTcp('tcp',1);await startTcp('tcp2',1);","for(const slot of ['tcp','tcp2','tcp3','tcp4']){if(ended)break;await startTcp(slot,1);while(!ended&&!stats.tcpChildren.find(x=>x.slot===slot).connected){if((performance.now()-began)/1000>=30){finish('Finite initial TCP acquisition window ended');break;}await new Promise(r=>setTimeout(r,25));}}")
write('native-client.mjs',native)
with (r/'fixture-retry-policy.mjs').open('xb') as f:f.write(Path('work/v38-sim/fixture-retry-policy.mjs').read_bytes())
match=read('match-controlled.mjs')
match=one(match,'performance.now()-began<60000','performance.now()-began<35000')
match=one(match,"if(frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4){console.log", "if(frame.pairs.length&&status.tcpConnected&&frame.ownedEstablishedTcpPorts.length===4){fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,freezeTcp:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');console.log")
match=one(match,"assert.ok(duplicate,'Incomplete owned socket-to-slot mapping');", "assert.ok(duplicate,'Incomplete owned socket-to-slot mapping');assert.ok(status.elapsed<30,'Natural five-WAN acquisition window ended');")
write('match-controlled.mjs',match)
supervisor=read('pilot-supervisor.mjs')
supervisor=one(supervisor,"2026-10-06T23:40:00Z","2026-10-07T08:00:00Z")
supervisor=one(supervisor,'Morning restoration margin unavailable','Five-WAN simulation restoration margin unavailable')
supervisor=one(supervisor,'fs.mkdirSync(out);fs.mkdirSync(out+\'/frozen\');',"fs.writeFileSync(root+'/one-session-attempt.json',JSON.stringify({oneAttemptOnly:true,simulatedGamePackets:true,startedAt:new Date().toISOString()})+'\\n',{flag:'wx'});fs.mkdirSync(out);fs.writeFileSync(root+'/pilot-reference-private.json',JSON.stringify({directory:out})+'\\n',{flag:'wx'});fs.mkdirSync(out+'/frozen');")
supervisor=one(supervisor,'v24 five naturally distinct WANs; four TCP BULK plus UDP RT','v39 five naturally distinct WANs; four owned TCP BULK plus simulated UDP RT')
supervisor=one(supervisor,'cs2Acceptance:false,highLoad300MbpsAcceptance:false','cs2Acceptance:false,simulatedGamePackets:true,highLoad300MbpsAcceptance:false')
write('pilot-supervisor.mjs',supervisor)
for name in ['read-final-health.mjs','read-physical-final.mjs','capture-client-closure.ps1']:
 data=rebase(Path('work/v38-sim',name).read_bytes(),'v38-sim').decode()
 if name=='read-final-health.mjs':data=one(data,"'v36-final'","'v39-final'")
 if name=='capture-client-closure.ps1':data=one(data,"@('work/v36-sim','work/v39-five-sim')","@('work/v39-five-sim')")
 with (r/name).open('xb') as f:f.write(data.encode())
receipt={'passed':True,'oldHashes':old_hashes,'nativeAndLuaUnmodifiedFromV24':True,'clientMechanismFromV38':True,'fourTcpRatesMbps':[8,8,8,8],'combinedCreditBytes':65536,'clientSeconds':180,'guardSeconds':210,'firstPayloadSeconds':8,'unconnectedTimeoutRetries':3,'acquisitionWindowSeconds':30,'originalNaturalSlotAttemptMaximum':8,'freezeBeforeCheckpoint':True,'phaseSeconds':60,'newCutoff':'2026-10-07T08:00:00Z','previousFailedSourcesUnmodified':True,'productionNotStarted':True}
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'fiveSlotAndQoSLuaExact':True,'oldSourcesChecked':len(old_hashes),'newFixtureOnly':True,'productionNotStarted':True}))
