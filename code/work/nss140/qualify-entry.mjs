// RAM/model qualification is separate from current-flow authorization.
import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
import{verifyPreparation as previous}from'../nss138/session-binding.mjs';import{verifyPreparation as previousReal}from'../nss77/session-binding.mjs';
import{applicationSockets,filterApplications}from'./application-ownership.mjs';import{mapClassifiedPair}from'../nss127/class-leaf-map.mjs';import{canonicalSelection}from'../nss27/flow-selection.mjs';
import{buildPayload}from'./payload.mjs';import{packetTemplate}from'./uplink-tag-plan.mjs';import{packGuardian}from'./pack-guardian.mjs';
import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss140',h=b=>crypto.createHash('sha256').update(b).digest('hex'),checks=[],inherited=previous(),real=previousReal();
for(const[f,x]of Object.entries(real.sourceManifest))assert.equal(inherited.sourceManifest[f],x);
checks.push({name:'all-original-real-entry-355-bindings-retained',passed:true,bindings:Object.keys(real.sourceManifest).length});
const old='work/nss128/controlled-matched-aba-20261005205520-95105879',frame=JSON.parse(fs.readFileSync(old+'/post-checkpoint-controlled-receipt-private.json'));
const tcp=frame.flows.find(f=>f.identity.protocolNumber===6),udp=frame.flows.find(f=>f.identity.protocolNumber===17);assert.ok(tcp&&udp);
const pc={processes:[{pid:11,name:'steam'},{pid:12,name:'cs2'},{pid:13,name:'unrelated'}],tcp:[{LocalAddress:tcp.identity.original.src,LocalPort:tcp.identity.original.sport,RemoteAddress:tcp.identity.original.dst,RemotePort:tcp.identity.original.dport,OwningProcess:11}],udp:[{LocalAddress:'0.0.0.0',LocalPort:udp.identity.original.sport,OwningProcess:12}]};
const sockets=applicationSockets(pc),owned=filterApplications(frame.flows,sockets);assert.equal(owned.bulk[0],tcp);assert.equal(owned.game[0],udp);
const selected={tcp:canonicalSelection(tcp),udp:canonicalSelection(udp)},actualMap=mapClassifiedPair({...frame,...owned},selected);assert.deepEqual(actualMap.decisions.map(d=>[d.class,d.upTag,d.downTag]),[['BULK',0x8e050000,0x8f050000],['RT',0x8e060000,0x8f060000]]);
checks.push({name:'historical-authenticated-full-rows-preserved-and-class-mapper-accepts',passed:true,historicalActualFrameOnly:true,pcOwnershipModeled:true,currentNssAuthorization:false});
const wrongOwner=structuredClone(pc);wrongOwner.tcp[0].OwningProcess=13;assert.equal(filterApplications(frame.flows,applicationSockets(wrongOwner)).bulk.length,0);
const wrongTuple=structuredClone(pc);wrongTuple.tcp[0].RemotePort=tcp.identity.original.dport===65535?65534:tcp.identity.original.dport+1;assert.equal(filterApplications(frame.flows,applicationSockets(wrongTuple)).bulk.length,0);
const wrongUdp=structuredClone(pc);wrongUdp.udp[0].LocalPort=udp.identity.original.sport===65535?65534:udp.identity.original.sport+1;assert.equal(filterApplications(frame.flows,applicationSockets(wrongUdp)).game.length,0);
const unknown=structuredClone(frame.flows);unknown[0].decision.class='UNKNOWN';unknown[1].decision.budgetAdmitted=false;assert.deepEqual(filterApplications(unknown,sockets),{game:[],bulk:[]});
const foreign=structuredClone(frame.flows);for(const f of foreign)f.identity.original.src='192.168.237.208';assert.deepEqual(filterApplications(foreign,sockets),{game:[],bulk:[]});
const proxy=structuredClone(frame.flows);for(const f of proxy)f.identity.mark|=0x2000;assert.deepEqual(filterApplications(proxy,sockets),{game:[],bulk:[]});
const stripped={...frame,flows:frame.flows.map(({identity,decision,key})=>({identity,decision,key}))};assert.throws(()=>mapClassifiedPair(stripped,selected));
const overflow=structuredClone(pc);overflow.tcp=Array.from({length:129},()=>pc.tcp[0]);assert.throws(()=>applicationSockets(overflow));
checks.push({name:'ownership-tuple-class-proxy-full-provenance-and-budget-rejections',passed:true,checks:8,nodeModelsOnly:true});
const filter=fs.readFileSync(root+'/application-filter.lua','utf8');
const models=String.raw`local j=require('luci.jsonc');local owned=assert(loadstring([====[${filter}]====]))();local cases=0;local function check(x)assert(x);cases=cases+1 end
local function inputs()return{flows={{key='tcp',identity={original={src='192.168.237.207',dst='192.0.2.1',sport=32101,dport=443},mark=65536,protocolNumber=6,queryProvenance={sequence=17}},decision={class='BULK'},leaf={requiresKernelCTPin=true}},{key='udp',identity={original={src='192.168.237.207',dst='192.0.2.2',sport=32102,dport=27015},mark=65536,protocolNumber=17,queryProvenance={sequence=17}},decision={class='RT',budgetAdmitted=true},leaf={requiresKernelCTPin=true}}}},{tcp={{LocalAddress='192.168.237.207',LocalPort=32101,RemoteAddress='192.0.2.1',RemotePort=443}},udp={{LocalAddress='0.0.0.0',LocalPort=32102}}}end
local a,b=inputs();local f=owned(a,b);check(#f==2 and f[1]==a.flows[1]and f[2]==a.flows[2]);check(f[1].leaf.requiresKernelCTPin and f[1].identity.queryProvenance.sequence==17)
a,b=inputs();b.tcp[1].RemoteAddress='192.0.2.3';check(#owned(a,b)==1)
a,b=inputs();b.tcp[1].RemotePort=80;check(#owned(a,b)==1)
a,b=inputs();b.udp[1].LocalPort=32103;check(#owned(a,b)==1)
a,b=inputs();a.flows[2].decision.budgetAdmitted=false;check(#owned(a,b)==1)
a,b=inputs();a.flows[1].decision.class='UNKNOWN';check(#owned(a,b)==1)
a,b=inputs();a.flows[1].identity.mark=73728;check(#owned(a,b)==1)
a,b=inputs();a.flows[1].identity.original.src='192.168.237.208';check(#owned(a,b)==1)
a,b=inputs();a.flows={};check(#owned(a,b)==0)
print(j.stringify({passed=true,checks=cases,ramOnly=true,mockedSocketsAndRows=true,routerWrites=false,nssAuthorization=false}))`;
const c=await connectRouter();let native;
try{const e=encode("lua - <<'NSS140_APPLICATION_FILTER_MODELS'\n"+models+"\nNSS140_APPLICATION_FILTER_MODELS\n"),raw=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/application-model-v2-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);native=JSON.parse(raw.stdout);assert.ok(native.passed&&native.checks===10);checks.push({name:'actual-application-Lua-filter-in-target-RAM',passed:true,checks:native.checks,execBytes:e.execBytes});}finally{c.close()}
const template=packetTemplate(actualMap,'a'.repeat(32),59999);template.expected.nftables=template.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const helpers={qos:fs.readFileSync(root+'/qos-physical.lua','utf8'),phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:fs.readFileSync(root+'/classifier.lua','utf8'),tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync(root+'/tag-normalizer.lua','utf8')};
const payload=buildPayload({tagPlan:{table:template.expected.nftables[0].table.name,owner:'a'.repeat(32),mode:'rt',expected:template.expected}},helpers);const payloadBytes=Buffer.byteLength(payload.stagedCode);assert.ok(payloadBytes<=73728);
const plan=JSON.parse(fs.readFileSync('work/nss138/controlled-class-20261005222654-399b3465/stage-plan-private.json'));for(const k of['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete plan[k];
const rendered=packGuardian(fs.readFileSync(root+'/module-stage-guardian.lua','utf8')).replace('__PLAN__',()=>JSON.stringify(plan)).replace('__CORE_PHASE__',()=> 'return{}').replace('__QOS_PHYSICAL__',()=> 'return{}'),guardian=encode("/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+rendered+"\nNSS20_STAGE_BEGIN\n");assert.ok(guardian.execBytes<=9000);
checks.push({name:'complete-original-transport-budgets',passed:true,payloadBytes,maximumPayloadBytes:73728,guardianExecBytes:guardian.execBytes,maximumExecBytes:9000,historicalActualPlansOnly:true});
const entry=fs.readFileSync(root+'/real-session.mjs','utf8');assert.ok(entry.includes("const mode=process.argv[2]??'inspect'")&&entry.includes('mapClassifiedPair(selectionFrame,selected)')&&entry.includes('chooseAfterCheckpoint')&&entry.includes("p.seconds>=20&&p.seconds<=21.5")&&entry.includes('auditScopedBaseline')&&entry.includes('validateAcceleratedState'));
checks.push({name:'read-only-default-fresh-post-checkpoint-map-and-no-partial-ABA-success',passed:true});
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|lua|ps1)$/.test(name)&&!name.includes('private')){const f=root+'/'+name;sourceManifest[f]=h(fs.readFileSync(f));if(name.endsWith('.mjs')){const p=spawnSync(process.execPath,['--check',f],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}}
const p={passed:true,integratedRealEntry:true,partialClassChangeIsNotCompletedAba:true,productionExecution:false,productionPairStillRestrictedToTcpBulkUdpRt:true,fullRowsRetainedForClassMapping:true,currentNssAuthorization:false,actualHardwareAbaThisVersion:false,wholeFactoryAbaNotExecutedThisRound:true,fastQualificationSha256:h(fs.readFileSync(root+'/fast-qualified.json')),classifierMaximumLeaseSeconds:6,nativeSessionSeconds:27,independentOwnerSeconds:100,payloadBytes,guardianExecBytes:guardian.execBytes,inheritedBoundInputs:Object.keys(inherited.sourceManifest).length,sourceManifest,checks,nativeModels:native};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(p,null,2)+'\n',{flag:'wx'});const verified=(await import('./session-binding.mjs')).verifyPreparation();console.log(JSON.stringify({passed:true,checks:checks.length,newBindings:Object.keys(sourceManifest).length,allBindings:Object.keys(verified.sourceManifest).length,payloadBytes,guardianExecBytes:guardian.execBytes,productionExecution:false}));
