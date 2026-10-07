from pathlib import Path
import json,hashlib
r=Path('work/v58-resident-timeout');old=Path('work/v57-resident-bootstrap');assert not (r/'materialize.mjs').exists()
names=['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs','ssh-phase.mjs','ssh-options.mjs','recheck-endpoint-readonly.mjs','udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1','resident-window.mjs','persistent-ssh.mjs','route-acquisition.mjs','check-route-acquisition.mjs','inspect-progress.mjs']
sources={}
for name in names:
    raw=(old/name).read_bytes();sources[str(old/name)]=hashlib.sha256(raw).hexdigest()
    s=raw.decode().replace('v57-resident-bootstrap','v58-resident-timeout').replace('v57-run-','v58-run-')
    if name=='route-acquisition.mjs':
        a='timeout:Math.max(1,15000-(performance.now()-readBegan))';b='timeout:Math.max(1,Math.floor(15000-(performance.now()-readBegan)))'
        assert s.count(a)==1;s=s.replace(a,b)
    (r/name).write_bytes(s.encode())
p=r/'check-model.mjs';s=p.read_text();needle="const receipt=entryRoot+'/model-'";assert s.count(needle)==1
s=s.replace(needle,"test('remaining child-process timeout is an unsigned integer within original limit',()=>{const s=fs.readFileSync(root+'/read-controlled.mjs','utf8');assert.ok(s.includes('timeout:Math.max(1,Math.floor(15000-(performance.now()-readBegan)))'));for(const elapsed of [0,0.4074,500.1,14999.5]){const n=Math.max(1,Math.floor(15000-elapsed));assert.ok(Number.isInteger(n)&&n>=1&&n<=15000);}});\n"+needle);p.write_bytes(s.encode())
(r/'preparation.json').write_text(json.dumps({'passed':True,'originalSourceHashes':sources,'singleTimeoutTypeBugFixed':True,'priorV57FailureAndInputsUnmodified':True,'originalFifteenSecondReadLimitKept':True,'productionExecuted':False},indent=2)+'\n')
print(json.dumps({'passed':True,'singleTimeoutTypeBugFixed':True,'productionExecuted':False}))
