from pathlib import Path
import hashlib,json

r=Path('work/v37-sim');old=Path('work/v36-sim')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
q=read(old/'entry-qualified.json');assert q['passed']
original={}
for rel,digest in q['sourceManifest'].items():
 p=Path(rel);data=p.read_bytes();assert sha(data)==digest,rel;original[rel]=digest
 if p.name in ['prepare.py','qualify-entry.mjs','session-binding.mjs']:continue
 new=r/p.name
 with new.open('xb') as f:f.write(data.replace(b'work/v36-sim',b'work/v37-sim').replace(b'v36-sim-',b'v37-sim-'))
p=r/'native-client.mjs';s=p.read_text()
s=s.replace("import fs from'node:fs';", "import{mayRetryAcquisition}from'./fixture-retry-policy.mjs';\nimport fs from'node:fs';",1)
s=s.replace('let ended=false,seq=0;', 'let ended=false,seq=0,fixtureFrozen=false;const acquisitionTimers=new Map();')
s=s.replace('ended=true;for(const t of timers)', 'ended=true;for(const t of acquisitionTimers.values())clearTimeout(t);for(const t of timers)')
needle='async function startTcp(slot,attempt)'
assert s.count(needle)==1
s=s.replace(needle,"""function retryAcquisition(slot,p,reason){
 const state=stats.tcpChildren.find(x=>x.slot===slot);if(ended||p!==children.get(slot))return;
 if(!mayRetryAcquisition({frozen:fixtureFrozen,elapsedSeconds:(performance.now()-began)/1000,attempt:state.attempt,hasPayload:state.connected,knownTimeout:true})){finish('Owned SSH '+slot+' acquisition refused: '+reason);return;}
 loadOut.write(JSON.stringify({event:'boundedAcquisitionRetry',at:Date.now()/1000,slot,attempt:state.attempt,reason,onlyBeforeNssAdmission:true})+'\\n');
 startTcp(slot,state.attempt+1).catch(finish);
}
async function startTcp(slot,attempt)""")
s=s.replace("rotating.add(slot);const old=children.get(slot);", "rotating.add(slot);clearTimeout(acquisitionTimers.get(slot));const old=children.get(slot);")
s=s.replace("let stderr='';", "let stderr='';acquisitionTimers.set(slot,setTimeout(()=>{if(p===children.get(slot)&&!s.connected&&!ended)retryAcquisition(slot,p,'No first payload within 8 seconds');},8000));")
s=s.replace('s.connected=true;s.bytes+=b.length;', 'clearTimeout(acquisitionTimers.get(slot));s.connected=true;s.bytes+=b.length;')
old_close="p.on('close',code=>{if(p===children.get(slot)&&!rotating.has(slot)&&!ended)finish(code===0||code===124?undefined:'Owned SSH '+slot+' closed '+code+': '+stderr);});"
new_close="p.on('close',code=>{if(p!==children.get(slot)||rotating.has(slot)||ended)return;clearTimeout(acquisitionTimers.get(slot));if(code===255&&!s.connected&&/Connection timed out/.test(stderr)){retryAcquisition(slot,p,'SSH timeout before first payload');return;}finish(code===0||code===124?undefined:'Owned SSH '+slot+' closed '+code+': '+stderr);});"
assert s.count(old_close)==1;s=s.replace(old_close,new_close)
s=s.replace('assert.equal(x.session,c.session);if(x.stop)', 'assert.equal(x.session,c.session);if(x.freezeTcp===true){fixtureFrozen=true;for(const t of acquisitionTimers.values())clearTimeout(t);}if(x.stop)')
p.write_text(s,encoding='utf8',newline='')
p=r/'match-controlled.mjs';s=p.read_text()
needle='  console.log(JSON.stringify({passed:true,naturalWanSet:'
assert s.count(needle)==1
s=s.replace(needle,"  fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,freezeTcp:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');\n"+needle)
p.write_text(s,encoding='utf8',newline='')
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'oldHashes':original,'priorFailureRetained':True,'onlyOwnedPreAdmissionTcpAcquisitionChanged':True,'firstPayloadTimeoutSeconds':8,'maximumAcquisitionAttempts':3,'acquisitionWindowSeconds':30,'clientSeconds':180,'cutoff':'2026-10-07T06:30:00Z','noCs2OrSteamOperations':True},f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'copied':len(original)-3,'productionNotStarted':True}))
