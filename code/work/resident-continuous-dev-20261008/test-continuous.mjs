import fs from 'node:fs';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {root,hash,patchFast,patchGuardian,pulseLibrary} from './adapt.mjs';
import {residentLoop,servicePlan} from './policy.mjs';
import {luaSlots} from '../resident-general-dev-i-20261008/adapt-plane.mjs';
import {executeLua,luaLiteral} from '../resident-dev-20261007/lua-local.mjs';
import crypto from 'node:crypto';
import {materializeFixture,fixtureLimits,stopFixture} from './fixture-materialize.mjs';

const checks=[];const test=async(n,f)=>{await f();checks.push(n);};
const subsets=JSON.parse(fs.readFileSync(root+'/subset-model-latest.json'));
const source=fs.readFileSync(subsets.runtime+'/fast-path.lua','utf8');
await test('seven actual bundles and guardians obey unchanged byte limits',()=>{
 assert.equal(subsets.passed,true);assert.equal(subsets.shapes.length,7);
 assert.equal(source,patchFast(fs.readFileSync('work/resident-rc1-run-20261008070809-6f2bbbfe/fast-path.lua','utf8')));
 assert.equal(fs.readFileSync(subsets.runtime+'/module-stage-guardian.lua','utf8'),patchGuardian(fs.readFileSync('work/resident-rc1-run-20261008070809-6f2bbbfe/module-stage-guardian.lua','utf8'),fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko')));
 for(const s of subsets.shapes){assert.ok(s.bundleBytes<=73728);assert.ok(s.guardianExecBytes<=9000);}
});
const build=JSON.parse(fs.readFileSync(root+'/endpoint-gate/build-manifest.json'));
await test('real native control functions cross former hard deadline and reject bad CT/expiry',()=>{
 assert.equal(build.sdk_original_unchanged,true);const t=JSON.parse(build.offline_tests);
 assert.equal(t.passed,true);assert.equal(t.sourceSha256,hash(fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.c')));
 assert.match(t.stdout,/4409/);
});
async function model(o={}){
 let t=0,calls=0,reads=0;const states=[];
 const result=await residentLoop({now:()=>t,stopped:()=>t>=(o.until??86400),wait:async()=>{t+=10;},publish:s=>states.push(s),
 observe:async()=>{reads++;if(o.readFailure&&reads<5)throw Error('Temporary readonly failure');return{sourceAge:1,sourceSequence:reads,tcp:[{}],udp:[{}],pairs:[{}]};},
 verify:()=>{if(o.bindingChanged)throw Error('Different source');},
 runGeneration:async()=>{calls++;t+=o.seconds??1000;return{restorationPassed:!o.dirty,hardwareCompleted:!o.safeRefusal,nssSeconds:o.safeRefusal?0:o.seconds??1000,code:o.safeRefusal?1:0,safeCandidateDisappearedBeforeWrite:o.safeRefusal};}});
 return{result,calls,states,reads};
}
await test('healthy generation stays active well beyond former 90/120/180 limits',async()=>{const m=await model({seconds:86400});assert.equal(m.calls,1);assert.equal(m.result.nssSeconds,86400);});
await test('fresh qualified successors have no four-start window',async()=>{const m=await model({until:6000,seconds:100});assert.ok(m.calls>40);assert.ok(!m.states.some(x=>x.state==='WAITING_WINDOW'));});
await test('P0 restored-state refusal still forbids successors',async()=>assert.rejects(model({dirty:true}),/P0/));
await test('changed sources remain a pre-write refusal',async()=>{const m=await model({until:100,bindingChanged:true});assert.equal(m.calls,0);});
await test('temporary readonly errors recover without latched finite retry cap',async()=>{const m=await model({until:200,readFailure:true});assert.equal(m.calls,1);assert.ok(m.reads>=5);});
await test('fully restored no-candidate outcome permits fresh observation',async()=>{const m=await model({until:1000,seconds:100,safeRefusal:true});assert.ok(m.calls>4);assert.ok(!m.states.some(s=>s.admissionPaused));});
await test('healthy lifetime caps removed while freshness and no traffic creation remain',()=>{
 for(const k of ['maximumGenerationsPerWindow','windowSeconds','phaseSeconds','generationCutoffSeconds'])assert.equal(servicePlan[k],null);
 assert.equal(servicePlan.sourceSeconds,6);assert.equal(servicePlan.normalEntryCreatesTraffic,false);
 const entry=fs.readFileSync(root+'/normal-entry.mjs','utf8');assert.ok(entry.includes("runtimeRoot+'/pilot-supervisor.mjs',null"));
 const driver=fs.readFileSync(subsets.runtime+'/epoch-driver.mjs','utf8');assert.ok(driver.includes("fs.existsSync(observationRoot+'/stop-request.json')"));
 assert.ok(fs.readFileSync(subsets.runtime+'/module-stage.mjs','utf8').includes('waitStageUndo(ctx){ctx.stopRequested=true;'));
});
await test('finite simulation fixture has matching independent deadlines and valid generated sources',()=>{
 const runtime='work/resident-rc1-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
 const q=materializeFixture(runtime,Date.now()+600000);assert.equal(q.finiteSimulationLimits.client,360);
 for(const n of ['start-dallas.mjs','native-client.mjs','owned-load-policy.mjs','close-endpoint.mjs','check-udp-path.mjs']){
  assert.equal(hash(fs.readFileSync(runtime+'/'+n)),q.sourceManifest[runtime+'/'+n]);
  const r=spawnSync(process.execPath,['--check',runtime+'/'+n],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);
 }
 assert.ok(fs.readFileSync(runtime+'/native-client.mjs','utf8').includes('finish(),360000'));
 assert.ok(fs.readFileSync(runtime+'/check-udp-path.mjs','utf8').includes('assert.equal(config.seconds,360)'));
 assert.ok(fs.readFileSync(runtime+'/download-server.py','utf8').includes('end=time.monotonic()+360'));
 assert.ok(fs.readFileSync(runtime+'/download-server.py','utf8').includes('signal.alarm(362)'));
 assert.ok(fs.readFileSync(runtime+'/native-client.mjs','utf8').includes('stats.tcpBytes>1073741824'));
 assert.ok(fs.readFileSync(runtime+'/native-client.mjs','utf8').includes('{tcp:4,tcp2:4,tcp3:4,tcp4:4}'));
 assert.equal(fixtureLimits.offeredMbps,16);assert.ok(360*fixtureLimits.offeredMbps*1000000/8<1073741824);
 assert.ok(fs.readFileSync(runtime+'/client-watchdog.ps1','utf8').includes('WaitForExit(390000)'));
 assert.ok(fs.readFileSync(runtime+'/endpoint-firewall-guardian.py','utf8').includes("else 360"));
 assert.ok(fs.readFileSync(runtime+'/server.py','utf8').includes("c['seconds']==440"));
 const script="import ast,pathlib; [ast.parse(pathlib.Path(p).read_text()) for p in __import__('sys').argv[1:]]";
 const p=spawnSync('C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',['-c',script,...['server.py','endpoint-firewall-guardian.py','download-server.py'].map(n=>runtime+'/'+n)],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);
 const load=runtime+'/load-local-model';fs.mkdirSync(load);const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v)+'\n');
 const config={seconds:360,mbps:32,tcpRates:{tcp:4,tcp2:4,tcp3:4,tcp4:4},session:'1'.repeat(16)};
 write(runtime+'/load-latest-private.json',{dir:load,clientPid:123});write(load+'/client-config-private.json',config);write(load+'/status-private.json',{pid:123,session:config.session});
 assert.equal(stopFixture(runtime).clientControlWritten,true);assert.equal(JSON.parse(fs.readFileSync(load+'/control.json')).stop,true);
 write(load+'/status-private.json',{pid:124,session:config.session});assert.throws(()=>stopFixture(runtime));
 write(load+'/result-private.json',{});assert.equal(stopFixture(runtime).clientAlreadyEnded,true);
});

const fragment=source.slice(source.indexOf(' local function X(O)'),source.indexOf(' function out.align(deadline)'));
const observe=source.slice(source.indexOf(' local function observe()'),source.indexOf(' local function counters(raw)'));
let lua='local M=assert(loadstring('+luaLiteral(luaSlots+source)+'))();\n';
lua+=String.raw`
local function run(mode)
 local t=0;local function now()return t end;local active=true;local N=120000
 local P={owner=string.rep('1',32),selected={udp={}}};local R={adapterSourceSequence=1,tagEpochUntil=6,phases={},samples={},renewals={},deadline=180}
 local files={control={dev=1,ino=2}};local stored=0;local deadline=180;local unloaded=0
 local function read()local clock=mode=='lost'and math.min(t,200)or t;local owner=mode=='wrong-owner'and string.rep('2',32)or P.owner;local s=owner..' '..clock..' '..(mode=='stop'and t>=7200 and 'S'or 'C')..' ';return s..string.rep(' ',127-#s)..'\n'end
 local function fc()return{dev=1,ino=mode=='replaced'and 3 or 2,size=128}end
 P.residentPulse=M.control(P,'private',read,now,function()end,fc,files,R,function()stored=stored+1 end,function(d)deadline=d end)
 local function pause(s)t=t+s end
 local function stopped()assert(not active)end
 local function unload()unloaded=unloaded+1 end
 local function state()return active and 'live'or ''end
 local function S()return{uptime=t,counts={['ecm_db/connection_count']=active and 1 or 0,['ecm_nss_ipv4/accelerated_count']=active and 1 or 0}}end
 local function E(s)return s.counts['ecm_nss_ipv4/accelerated_count']==1 end
 local A={};function A.observe()return{sourceSequence=math.floor(t/3)+2,producer='fixed',startedAtUptime=t}end
 function A.compareObserved()return{action=mode=='withdraw'and t>=200 and 'END_EPOCH'or'KEEP_IMMUTABLE_EPOCH'}end
 function A.proposeRenewal()return{expectedSequence=R.adapterSourceSequence,nextSequence=math.floor(t/3)+2,untilMs=math.floor((t+6)*1000)}end
 function A.acceptRenewal(p,ack)R.adapterSourceSequence=ack.sequence end
 local pending;local function put(path,s)if path:find('front_end_ipv4_stop',1,true)then assert(s:match('^1'));return end;local a,b,c=s:match('^(%d+):(%d+):(%d+)');assert(tonumber(a)==R.adapterSourceSequence);assert(t*1000<N);pending={nextSequence=tonumber(b),untilMs=tonumber(c)}end
 local function K()return{epoch_refresh='sequence='..pending.nextSequence..' classifier_until_ms='..pending.untilMs..' session_until_ms='..math.floor((t+120)*1000),game_permit='Y',game_pinned_state='pinned=1 current_hash_matches=1',game_state='ever_opened=1 terminal=0 admit=1'}end
`;
lua+=observe+fragment;
lua+=String.raw`
 local ok,err=pcall(measure)
 if mode=='stop'then assert(ok,tostring(err));assert(t>=7200);assert(unloaded==1);assert(R.operatorStop);assert(R.phases[1].sampleCount>=14400);assert(R.totalRenewals>2300);assert(#R.samples==32 and #R.renewals==16);assert(deadline>7200);assert(stored>3000)
 elseif mode=='withdraw'then assert(ok,tostring(err));assert(t>=200 and t<201);assert(unloaded==1);assert(R.terminalInvalidation.reason=='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED')
 elseif mode=='lost'then assert(not ok);assert(t>=230 and t<231);assert(tostring(err):find('Resident control heartbeat lost',1,true))
 else assert(not ok);assert(t==0)end
end
for _,mode in ipairs{'stop','withdraw','lost','wrong-owner','replaced'}do run(mode)end
print('CONTINUOUS_LIFECYCLE_PASS')
`;
await test('actual Lua runs two virtual hours, bounded records, stop, eligibility withdrawal and heartbeat loss',()=>{
 const r=executeLua(lua,'continuous-lifecycle');fs.writeFileSync(process.argv[2]+'/lua-lifecycle-result.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);assert.equal(r.stdout.trim(),'CONTINUOUS_LIFECYCLE_PASS');
});
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,modelOnly:true,routerAccess:false,runtime:subsets.runtime,nativeControlChecks:4409}));
