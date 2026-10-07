from pathlib import Path
import hashlib, json

w = Path(__file__).resolve().parents[1]
old = w/'work/v44-unique-label-entry'
new = w/'work/v45-early-acquisition'
assert not new.exists()
new.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
original = {}
serial = "stamp();for(const slot of ['tcp','tcp2','tcp3','tcp4']){if(ended)break;await startTcp(slot,1);while(!ended&&!stats.tcpChildren.find(x=>x.slot===slot).connected){if((performance.now()-began)/1000>=30){finish('Finite initial TCP acquisition window ended');break;}await new Promise(r=>setTimeout(r,25));}}"
for name in ['entry.mjs', 'materialize.mjs', 'check-model.mjs', 'platform-preflight.mjs']:
    data = (old/name).read_bytes()
    original[name] = sha(data)
    text = data.decode('utf8').replace('work/v44-unique-label-entry', 'work/v45-early-acquisition').replace('v44-run-', 'v45-run-').replace('v44-other', 'v45-other')
    if name == 'materialize.mjs':
        needle = "  if(name==='pilot-supervisor.mjs'){"
        assert text.count(needle) == 1
        change = """  if(name==='native-client.mjs'){
   let s=bytes.toString('utf8');const serial=""" + json.dumps(serial) + """;
   assert.equal(s.split(serial).length,2,'Original serial initial SSH startup must match');
   s="import{launchInitialFour}from'../v45-early-acquisition/fixture-startup.mjs';\\n"+s.replace(serial,"stamp();await launchInitialFour(startTcp,()=>ended);");
   bytes=Buffer.from(s);
  }
  if(name==='wait-four-ssh.mjs'){
   let s=bytes.toString('utf8');const prior="s.tcpChildren.every(x=>x.connected&&Number.isInteger(x.ownerPid)&&x.bytes>0)&&Date.now()/1000-s.at<2";
   assert.equal(s.split(prior).length,2);
   s="import{fourOwnedPidsReady}from'../v45-early-acquisition/fixture-startup.mjs';\\n"+s.replace(prior,"fourOwnedPidsReady(s,Date.now()/1000)").replace('fourOwnedSshChildrenReady:true','fourOwnedSshPidsPublished:true,payloadAndClassificationStillRequired:true').replace('all handshakes completed','four owned child PIDs were published').replace('fixture handshakes exceeded readiness bound','fixture PID publication exceeded readiness bound');
   bytes=Buffer.from(s);
  }
"""
        text = text.replace(needle, change + needle)
        needle = "['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs']"
        assert text.count(needle) == 1
        text = text.replace(needle, "['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs']")
    if name == 'check-model.mjs':
        text = "import{launchInitialFour,fourOwnedPidsReady}from'./fixture-startup.mjs';\n" + text
        needle = 'const sourceHashes=Object.fromEntries('
        assert text.count(needle) == 1
        checks = """const childStatus={pid:999,errors:[],elapsed:1,at:100,tcpChildren:['tcp','tcp2','tcp3','tcp4'].map((slot,i)=>({slot,ownerPid:1000+i,connected:false,bytes:0}))};
test('four published PIDs permit only earlier observation before payload',()=>assert.ok(fourOwnedPidsReady(childStatus,100.5)));
test('missing or duplicate owned child PID cannot begin acquisition observation',()=>{
 for(const pid of [undefined,0,-1,1.5,1000]){const s=structuredClone(childStatus);s.tcpChildren[3].ownerPid=pid;assert.ok(!fourOwnedPidsReady(s,100.5));}
});
test('stale status or fixture errors cannot begin acquisition observation',()=>{
 assert.ok(!fourOwnedPidsReady(childStatus,102)&&!fourOwnedPidsReady(childStatus,99.9));
 assert.ok(!fourOwnedPidsReady({...childStatus,errors:['original failure']},100.5));
});
const launched=[],pending=[];
const launching=launchInitialFour((slot,attempt)=>{launched.push({slot,attempt});return new Promise(resolve=>pending.push(resolve));},()=>false);
test('a slow first initial connection does not prevent the other three spawning',()=>{
 assert.deepEqual(launched,['tcp','tcp2','tcp3','tcp4'].map(slot=>({slot,attempt:1})));assert.equal(pending.length,4);
});
for(const resolve of pending)resolve();await launching;
test('stopped fixture spawns no initial child',()=>{const calls=[];launchInitialFour(slot=>calls.push(slot),()=>true);assert.deepEqual(calls,[]);});
test('NSS selection still requires all first payloads and original full five-WAN classification',()=>{
 const s=fs.readFileSync(root+'/match-controlled.mjs','utf8');
 assert.ok(s.includes('status.tcpConnected')&&s.includes('Natural five-WAN acquisition window ended'));
 for(const name of ['match-controlled.mjs','read-controlled.mjs','fixture-retry-policy.mjs','download-server.py','guard-fixture.ps1']){
  if(!fs.existsSync(root+'/'+name))continue;
  const origin=fs.readFileSync('work/v42-counter-window/'+name,'utf8'),expected=origin.replaceAll('work\\\\/v42-counter-window\\\\/',root.replaceAll('/','\\\\/')+'\\\\/').replaceAll('work/v42-counter-window',root).replaceAll('v42-counter-window-',root.slice(5)+'-').replaceAll('v42-final',root.slice(5)+'-final');
  assert.equal(fs.readFileSync(root+'/'+name,'utf8'),expected,name);
 }
});
test('only initial startup and process readiness import the startup helper',()=>{
 assert.ok(fs.readFileSync(root+'/native-client.mjs','utf8').includes('await launchInitialFour(startTcp,()=>ended)'));
 assert.ok(fs.readFileSync(root+'/wait-four-ssh.mjs','utf8').includes('fourOwnedPidsReady(s,Date.now()/1000)'));
 assert.ok(q.sourceManifest[entryRoot+'/fixture-startup.mjs']);
});
"""
        text = text.replace(needle, checks + needle)
        text = text.replace("['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs']", "['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs','fixture-startup.mjs']")
    with (new/name).open('xb') as f:
        f.write(text.encode('utf8'))
helper = """const slots=Object.freeze(['tcp','tcp2','tcp3','tcp4']);
export async function launchInitialFour(startTcp,shouldStop){
 if(shouldStop())return;
 await Promise.all(slots.map(slot=>shouldStop()?undefined:startTcp(slot,1)));
}
export function fourOwnedPidsReady(s,nowSeconds){
 if(!s||!Number.isInteger(s.pid)||s.pid<=0||!Array.isArray(s.errors)||s.errors.length!==0||!Array.isArray(s.tcpChildren)||s.tcpChildren.length!==4)return false;
 if(!Number.isFinite(s.elapsed)||s.elapsed<0||s.elapsed>=50||!Number.isFinite(s.at)||!Number.isFinite(nowSeconds)||nowSeconds-s.at<0||nowSeconds-s.at>=2)return false;
 if(!slots.every((slot,i)=>s.tcpChildren[i].slot===slot&&Number.isInteger(s.tcpChildren[i].ownerPid)&&s.tcpChildren[i].ownerPid>0))return false;
 return new Set(s.tcpChildren.map(x=>x.ownerPid)).size===4;
}
"""
with (new/'fixture-startup.mjs').open('xb') as f:
    f.write(helper.encode('utf8'))
assert all(sha((old/n).read_bytes()) == h for n,h in original.items())
receipt = {'prepared': True, 'originalCandidateHashes': original,
           'change': 'concurrent same four initial SSH child creation and earlier process-only readiness',
           'observedV44FirstAllPidsSeconds': 16.0071,
           'observedV44FirstAllPayloadSeconds': 18.8794,
           'original30SecondAcquisitionDeadlineNotReset': True,
           'finalPayloadIdentityClassificationAndFiveWanSelectionUnchanged': True,
           'dataPlaneAndSafetyLimitsUnchanged': True,
           'originalSourcesUnchanged': True, 'hardwareExecuted': False}
with (new/'preparation.json').open('x',encoding='utf8') as f:
    json.dump(receipt,f,indent=2); f.write('\n')
print(json.dumps({'prepared': True, 'entryRoot': 'work/v45-early-acquisition', 'hardwareExecuted': False}))
