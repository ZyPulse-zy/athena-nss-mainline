import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {selectNormalCandidates,pinNormalOwnership,verifyPinnedOwnership} from './normal-policy.mjs';
import {ownershipScript,normalReaderCode} from './normal-reader.mjs';
import {encode} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {executeLua,luaLiteral} from '../resident-dev-20261007/lua-local.mjs';
import {spawnSync} from 'node:child_process';

const root='work/resident-normal-dev-i-20261008',baseline=JSON.parse(fs.readFileSync('work/resident-rc1-run-20261007163534-ae83fa69/controlled-candidates-private.json'));
// A frozen historical frame supplies full CT/class/leaf/provenance shape. OS owners are local models only.
const flows=[...baseline.tcp,...baseline.udp],base={...baseline,flows,routerWrites:false,nssAdmissionAllowed:false};
const pc={at:'2026-10-08T00:00:00.0000000Z',ageSeconds:0.1,processes:[],tcp:[],udp:[]};
for(const [n,f] of flows.entries()){
 const pid=1000+n;pc.processes.push({pid,start:'2026-10-07T23:00:00.1234567Z',executable:'C:\\test\\client-'+n+'.exe',commandReadable:true});
 const e={LocalAddress:f.identity.original.src,LocalPort:f.identity.original.sport,OwningProcess:pid};
 if(f.identity.protocolNumber===6){Object.assign(e,{RemoteAddress:f.identity.original.dst,RemotePort:f.identity.original.dport});pc.tcp.push(e);}else pc.udp.push(e);
}
let checks=[];const test=(name,fn)=>{fn();checks.push(name);};
let frame;
test('existing BULK and admitted RT owned by arbitrary readable processes are selected',()=>{frame=selectNormalCandidates(base,pc);assert.ok(frame.pairs.length);assert.equal(frame.trafficGenerated,false);});
const selected=frame.pairs[0],pinned=pinNormalOwnership(frame,selected);
test('fresh identical process instances retain exact selection',()=>verifyPinnedOwnership(frame,selected,pinned));
function deny(name,change){test(name,()=>{const f=structuredClone(base),p=structuredClone(pc);change(f,p);let denied=false;try{const q=selectNormalCandidates(f,p).pairs;const rt=['RT process','PID reused','two UDP','RT budget'].some(k=>name.startsWith(k)),bulk=['changed TCP','unknown TCP','BE does'].some(k=>name.startsWith(k));denied=q.length===0||rt&&q.every(x=>!x.udp)||bulk&&q.every(x=>!x.tcp&&!x.tcp2);}catch{denied=true;}assert.ok(denied,name);});}
deny('no socket ownership',(_,p)=>{p.tcp=[];p.udp=[];});
test('one owned BULK is independently sufficient without another WAN or RT',()=>{const p=structuredClone(pc);p.tcp=p.tcp.slice(0,1);p.udp=[];const q=selectNormalCandidates(base,p);assert.deepEqual(Object.keys(q.pairs[0]),['tcp']);});
deny('RT process path unreadable',(_,p)=>p.processes.at(-1).executable='');
deny('RT process command unreadable',(_,p)=>p.processes.at(-1).commandReadable=false);
deny('RT process born after observation',(_,p)=>p.processes.at(-1).start='2026-10-08T00:00:01Z');
deny('PID reused or unrelated owner cannot substitute',(_,p)=>p.udp[0].OwningProcess=8888);
deny('two UDP owners are ambiguous even if second is unknown',(_,p)=>p.udp.push({...p.udp[0],OwningProcess:8888}));
deny('changed TCP remote tuple',(_,p)=>p.tcp.forEach(e=>e.RemotePort++));
deny('wrong PC source',f=>f.flows.forEach(e=>e.identity.original.src='192.168.237.208'));
deny('proxy mark stays software',f=>f.flows.forEach(e=>e.identity.mark|=0x2000));
deny('unknown TCP class stays software',f=>f.flows.filter(e=>e.identity.protocolNumber===6).forEach(e=>e.decision.class='UNKNOWN'));
deny('BE does not qualify as BULK',f=>f.flows.filter(e=>e.identity.protocolNumber===6).forEach(e=>e.decision.class='BE'));
deny('RT budget refusal stays software',f=>f.flows.filter(e=>e.identity.protocolNumber===17).forEach(e=>e.decision.budgetAdmitted=false));
deny('source6 unchanged',f=>f.sourceAge=6);
deny('OS age6 refused',(_,p)=>p.ageSeconds=6);
deny('query provenance changed',f=>f.sourceSequence++);
deny('full mark missing',f=>f.flows.forEach(e=>e.identity.queryProvenance.fullMarkFieldPresent=false));
deny('lease stale',f=>f.flows.forEach(e=>e.validUntilUptime=e.identity.queryProvenance.startedAtUptime));
deny('leaf permit cannot grant admission',f=>f.flows.forEach(e=>e.leaf.nssPermit=true));
deny('unsafe native instance',f=>f.flows.forEach(e=>e.identity.instanceTagSafe=false));
deny('duplicate classification key refused',f=>f.flows.push(structuredClone(f.flows[0])));
deny('duplicate OS process identity refused',(_,p)=>p.processes.push(structuredClone(p.processes[0])));
deny('remote reader cannot grant admission',f=>f.nssAdmissionAllowed=true);
test('scope is exact process instance plus tuple, not executable name',()=>{
 const scope={version:1,owners:pc.processes,tcp:base.flows.filter(f=>f.identity.protocolNumber===6).map(f=>f.identity.original),udp:base.flows.filter(f=>f.identity.protocolNumber===17).map(f=>f.identity.original)};
 assert.ok(selectNormalCandidates(base,pc,scope).pairs.length);
 const reused=structuredClone(scope);reused.owners=reused.owners.map(x=>({...x,start:'2026-10-07T23:00:00.1234568Z'}));assert.equal(selectNormalCandidates(base,pc,reused).pairs.length,0);
 const wrongTuple=structuredClone(scope);wrongTuple.udp[0].dport++;assert.ok(selectNormalCandidates(base,pc,wrongTuple).pairs.every(p=>!p.udp));
});
test('PID birth submillisecond precision is retained',()=>assert.equal(pinned.udp.start,'2026-10-07T23:00:00.1234567Z'));
test('selected ownership cannot switch to another process',()=>{const altered=structuredClone(frame);altered.owners[base.udp[0].key].pid++;assert.throws(()=>verifyPinnedOwnership(altered,selected,pinned));});
test('UDP wildcard with one verified owner is accepted',()=>{const p=structuredClone(pc);p.udp[0].LocalAddress='0.0.0.0';assert.ok(selectNormalCandidates(base,p).pairs.length);});
const output=root+'/tests-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(output);
const script=ownershipScript(flows);fs.writeFileSync(output+'/ownership.ps1',script,{flag:'wx'});
test('actual Windows ownership script parses',()=>{const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',"$t=$null;$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('"+output+"/ownership.ps1',[ref]$t,[ref]$e);if($e.Count){$e|ForEach-Object{$_.Message};exit 1}"],{encoding:'utf8',windowsHide:true,timeout:10000});fs.writeFileSync(output+'/powershell-parse-private.json',JSON.stringify(p)+'\n');assert.equal(p.status,0,p.stderr+p.stdout);});
const lua=normalReaderCode();
test('candidate visibility transport preserves original byte bounds',()=>{const e=encode("lua - <<'NORMAL_FLOW_READ'\n"+lua+'\nNORMAL_FLOW_READ\n');assert.ok(e.execBytes<=9000);});
test('actual Lua51 normal reader compiles',()=>{const p=executeLua('assert(loadstring('+luaLiteral(lua)+'));print("NORMAL_READER_SYNTAX_PASS")','normal-reader-syntax');assert.equal(p.stdout.trim(),'NORMAL_READER_SYNTAX_PASS');});
const result={passed:true,checks,routerAccess:false,source6Unchanged:true,processBirthPrecisionPreserved:true,unknownAndAmbiguousDefaultDeny:true,normalAppsNotStarted:true};
fs.writeFileSync(output+'/result.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
fs.writeFileSync(root+'/policy-tests-latest.json',JSON.stringify({...result,output},null,2)+'\n');console.log(JSON.stringify({passed:true,checks:checks.length,output}));
