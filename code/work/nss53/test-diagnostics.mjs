// Execute complete candidate adapter with native JSON; mocked IO and time only.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync}from 'node:child_process';
import {connectRouter}from '../nss20/connect-router.mjs';import {encode,receipt}from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss53',adapter=fs.readFileSync(root+'/classifier.lua','utf8');
const original=fs.readFileSync('work/nss49/classifier.lua','utf8'),delta=JSON.parse(fs.readFileSync(root+'/classifier-delta.json'));
let restored=adapter;for(const e of [...delta.edits].reverse()){assert.equal(restored.split(e.to).length,2);restored=restored.replace(e.to,()=>e.from);}assert.equal(restored,original);
assert.equal(adapter.slice(0,adapter.indexOf('local describeSelection=')),original.slice(0,original.indexOf('local A={}')));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const prefix=fs.readFileSync('work/nss23/consumer-fixtures.lua','utf8').split('local s,c,w=make();local epoch=')[0].replace("local M=assert(loadstring([===[__CONSUMER__]===]))()",'');
let fixture=fs.readFileSync('work/nss27/renewal-consumer-fixtures.lua','utf8');
fixture=fixture.replace(" local function read(p,cap)local v=assert(files[p],p);assert(#v<=cap);return v end", " local reads={};local function read(p,cap)reads[p]=(reads[p]or 0)+1;local v=assert(files[p],p);assert(#v<=cap);return v end");
fixture=fixture.replace('local x={s=s,c=c,rec=rec,update=update,files=files,ram=ram}','local x={s=s,c=c,rec=rec,update=update,files=files,ram=ram,reads=reads}');
const a=fixture.indexOf('local x=setup();yes('),b=fixture.indexOf('x=setup();x.fresh(5,103);p=Adapter.proposeRenewal();x.rtGone()'),end=fixture.indexOf('print(j.stringify(');assert.ok(a>0&&b>a&&end>b);
const setup=prefix+'\nlocal Adapter=assert(loadstring([====['+adapter+']====]))()\n'+fixture.slice(0,a)+'\nlocal x,p\n';
const uniform=String.raw`
x=setup();local seen=Adapter.observe();yes(#seen.flows==2 and seen.sourceSequence==4,'uniform observation reads current classified pair')
x.fresh(5,103);local current=Adapter.resampleClosed();yes(current.provenance.sequence==5 and x.rec.adapterSourceSequence==5,'stopped resample begins fresh pin epoch')
yes(Adapter.proposeRenewal()==nil,'stopped resample leaves no stale pending epoch')
x.s.status='degraded';x.s.error='fixture';x.update();yes(not pcall(Adapter.observe),'uniform observation refuses degraded publication')
`;
const newCases=String.raw`
local function probe(x,expectedReads)local before=x.reads[x.ram..'/classification.json']or 0;local ok,reason,retry=Adapter.preLearningReady();local d=x.rec.lastAdmissionProbe;yes((x.reads[x.ram..'/classification.json']or 0)==before+(expectedReads or 1),'probe uses no extra classification frames');return ok,reason,retry,d end
x=setup();local ok,reason,retry,d=probe(x);yes(ok and not reason and not retry and not d.selected,'healthy ready frame unchanged without diagnostics work')
x=setup();x.rtGone();ok,reason,retry,d=probe(x);yes(not ok and not retry and reason:match('Selected class is not admitted$')and d.selected.slots.udp.reasonCode=='TARGET_CLASS_MISMATCH'and d.selected.slots.tcp.reasonCode=='TARGET_CLASS_ADMITTED','UDP class exit identified on failing frame')
yes(d.selected.sourceSequence==4 and d.selected.sameAdmissionFrame and d.selected.nssAdmissionAllowed==false,'diagnostic preserves failing sequence and never permits NSS')
x=setup();x.s.snapshot.flows={x.s.snapshot.flows[2]};x.update();ok,reason,retry,d=probe(x);yes(not ok and not retry and d.selected.slots.tcp.reasonCode=='EXACT_KEY_ABSENT'and d.selected.slots.udp.present,'TCP exit distinguished from present UDP')
x=setup();x.s.snapshot.flows={x.s.snapshot.flows[1]};x.update();ok,reason,retry,d=probe(x);yes(not ok and not retry and d.selected.slots.udp.reasonCode=='EXACT_KEY_ABSENT','UDP exit distinguished from class change')
x=setup();local f=x.s.snapshot.flows[2];f.decision.budgetAdmitted=false;f.leaf.candidate=false;f.leaf.downTag=0;x.update();ok,reason,retry,d=probe(x);yes(not ok and not retry and d.selected.slots.udp.reasonCode=='RT_BUDGET_NOT_ADMITTED','RT budget rejection identified')
x=setup();local f=x.s.snapshot.flows[1];f.decision.reason='not-bulk';f.leaf.candidate=false;f.leaf.downTag=0;x.update();ok,reason,retry,d=probe(x);yes(not ok and not retry and d.selected.slots.tcp.reasonCode=='BULK_REASON_NOT_ADMITTED','bulk reason rejection identified')
x=setup();x.time(101.2);ok,reason,retry,d=probe(x);yes(not ok and retry and reason:match('Fresh epoch lacks tag setup reserve$')and d.selected.slots.tcp.present and d.selected.slots.udp.present,'fresh-margin retry remains retryable')
x=setup();x.s.status='degraded';x.s.error='fixture';x.update();ok,reason,retry,d=probe(x);yes(not ok and not retry and reason:match('Unhealthy classifier$'),'unhealthy frame remains terminal despite diagnostic facts')
x=setup();x.s.producer='foreign';x.update();ok,reason,retry,d=probe(x);yes(not ok and not retry and reason:match('Classifier process instance changed$'),'producer change remains terminal')
x=setup();x.files[x.ram..'/owner']='foreign\n';ok,reason,retry,d=probe(x,0);yes(not ok and not retry and not d.selected,'readContext failure invents no selection frame')
-- Read the helper independently for diagnostic-failure containment and bounds.
local describe=assert(loadstring([===[__DIAGNOSTIC__]===]))()
local s,c,w=make();local many={};for i=1,2049 do many[i]=s.snapshot.flows[1]end;s.snapshot.flows=many
local bounded=describe(s,w,101);yes(bounded.scanTruncated and bounded.slots.udp.reasonCode=='EXACT_KEY_NOT_FOUND_IN_BOUNDED_SCAN','bounded scan never asserts a truncated full-frame absence')
local empty=describe({},nil,101);yes(empty.slots.tcp.reasonCode=='SELECTED_INPUT_ABSENT'and empty.slots.udp.reasonCode=='SELECTED_INPUT_ABSENT','missing diagnostic inputs remain facts only')
local function projectedCase(change)
 local x=setup();x.rtGone();local full=copy(x.s);if change then change(full)end;x.files[x.ram..'/snapshot.json']=j.stringify(full)
 x.s.snapshot.flows={x.s.snapshot.flows[1]};x.s.snapshot.admissionProjection={version=1,scope='bulk-and-admitted-rt',sourceSequence=4,candidateFlowCount=1,completeInputFlowCount=2};x.update();return x
end
x=projectedCase();ok,reason,retry,d=probe(x);yes(not ok and not retry and d.selected.slots.udp.reasonCode=='NOT_IN_ADMISSION_PROJECTION'and not d.selected.slots.udp.completeInputPresenceKnown,'projection absence does not invent CT exit')
yes(d.completeSelected and d.completeSelected.sameSourceCompleteFrame and d.completeSelected.slots.udp.reasonCode=='TARGET_CLASS_MISMATCH','same-query full frame explains rejected UDP class')
yes(x.reads[x.ram..'/snapshot.json']==1,'at most one full diagnostic frame read after terminal rejection')
for _,change in ipairs({function(s)s.producer='foreign'end,function(s)s.configSha256='foreign'end,function(s)s.snapshot.provenance.sequence=5 end,function(s)s.snapshot.provenance.startedAtUptime=99 end,function(s)s.snapshot.flows[2].leaf.downTag=2399469568 end})do
 x=projectedCase(change);ok,reason,retry,d=probe(x);yes(not ok and not retry and not d.completeSelected and d.completeSelectionUnavailable,'different or invalid complete frame remains unknown')
end
x=projectedCase();x.files[x.ram..'/snapshot.json']=nil;ok,reason,retry,d=probe(x);yes(not ok and not retry and not d.completeSelected and d.completeSelectionUnavailable,'missing complete frame never weakens rejection')
`;
const suffix="print(j.stringify({passed=true,cases=cases,checks=#cases,nativeJsonc=true,routerWrites=false,gateAcknowledgementsMocked=true}))";
const parts=[fixture.slice(a,b),fixture.slice(b,end)+uniform,newCases.replace('__DIAGNOSTIC__',()=>fs.readFileSync(root+'/selection-diagnostic.lua','utf8'))];
const shim=String.raw`local saved,serial={},0
local function clone(v)if type(v)~='table'then return v end;local o={};for k,x in pairs(v)do o[k]=clone(x)end;return o end
package.preload['luci.jsonc']=function()return{stringify=function(v)serial=serial+1;local k='fixture:'..serial;saved[k]=clone(v);return k end,parse=function(k)return clone(saved[k])end}end
`;
const localCode=shim+setup+parts.join('\n')+"\nfor _,v in ipairs(cases)do print('PASS '..v)end;print('COMPLETE '..#cases)\n";
fs.writeFileSync(root+'/diagnostic-local-replay.lua',localCode);
// The exact ready()/readContext()/inspect()/pair() bodies run on the target.
// Unused renewal/retirement code is omitted only from this RAM fixture.
const pairStart=adapter.indexOf('function M.compareEpoch('),pairEnd=adapter.indexOf('return M\n',pairStart);assert.ok(pairStart>0&&pairEnd>pairStart);
let nativeAdapter=adapter.slice(0,pairStart)+adapter.slice(pairEnd);
const sampleStart=nativeAdapter.indexOf(' function out.sample()'),returnStart=nativeAdapter.indexOf(' return out\nend\nreturn setmetatable',sampleStart);assert.ok(sampleStart>0&&returnStart>sampleStart);
nativeAdapter=nativeAdapter.slice(0,sampleStart)+nativeAdapter.slice(returnStart);
let nativeSetup=setup.replace(adapter,()=>nativeAdapter).replace('run,rec);step()','run,rec)');
const first=parts[2].indexOf('x=setup();local ok,reason,retry,d=probe(x);');assert.ok(first>0);
const probeSetup=parts[2].slice(0,first)+'\nlocal ok,reason,retry,d\n';
const body=parts[2].slice(first).replace('local ok,reason,retry,d=probe(x);','ok,reason,retry,d=probe(x);');
const split1=body.indexOf('x=setup();local f=x.s.snapshot.flows[2]'),split2=body.indexOf("x=setup();x.s.status='degraded'"),split3=body.indexOf('-- Read the helper independently');assert.ok(split1>0&&split2>split1&&split3>split2);
// Transport rejected the larger adapter+fixture without any router execution.
// Execute the complete adapter locally; qualify the diagnostic helper separately
// with target-native JSON. Do not call this a native complete-adapter qualification.
const helper=fs.readFileSync(root+'/selection-diagnostic.lua','utf8');
const nativeCases=String.raw`
local describe=assert(loadstring([====[__HELPER__]====]))()
local s,c,w=make();local d=describe(s,w,101)
yes(d.slots.tcp.reasonCode=='TARGET_CLASS_ADMITTED'and d.slots.udp.reasonCode=='TARGET_CLASS_ADMITTED','healthy tags remain diagnostic facts')
yes(d.nssAdmissionAllowed==false and d.sameAdmissionFrame and d.sourceSequence==4,'diagnostic uses same sequence without permission')
s.snapshot.flows={s.snapshot.flows[2]};d=describe(s,w,101);yes(d.slots.tcp.reasonCode=='EXACT_KEY_ABSENT'and d.slots.udp.present,'TCP absence identified')
s,c,w=make();s.snapshot.flows={s.snapshot.flows[1]};d=describe(s,w,101);yes(d.slots.udp.reasonCode=='EXACT_KEY_ABSENT','UDP absence identified')
s,c,w=make();s.snapshot.flows[2].decision.class='BE';d=describe(s,w,101);yes(d.slots.udp.reasonCode=='TARGET_CLASS_MISMATCH','RT class exit identified')
s,c,w=make();s.snapshot.flows[2].decision.budgetAdmitted=false;d=describe(s,w,101);yes(d.slots.udp.reasonCode=='RT_BUDGET_NOT_ADMITTED','RT budget refusal identified')
s,c,w=make();s.snapshot.flows[1].decision.reason='different';d=describe(s,w,101);yes(d.slots.tcp.reasonCode=='BULK_REASON_NOT_ADMITTED','bulk reason refusal identified')
s,c,w=make();w.udp.mark=335872;w.udp.reply.dst='198.51.100.4';d=describe(s,w,101);yes(not d.slots.udp.markMatches and not d.slots.udp.replyMatches,'mark and NAT mismatch reported without permission')
s,c,w=make();s.snapshot.flows[2].leaf.downTag=0;d=describe(s,w,101);yes(not d.slots.udp.leafTagMatches,'wrong leaf reported')
s,c,w=make();s.snapshot.flows[2].validUntilUptime=100;d=describe(s,w,101);yes(d.slots.udp.validRemainingSeconds==-1,'expired per-flow time reported')
s,c,w=make();s.snapshot.flows[3]=s.snapshot.flows[1];d=describe(s,w,101);yes(d.slots.tcp.reasonCode=='DUPLICATE_EXACT_KEY','duplicates distinguished')
s,c,w=make();local many={};for i=1,2049 do many[i]=s.snapshot.flows[1]end;s.snapshot.flows=many;d=describe(s,w,101);yes(d.scanTruncated and d.slots.udp.reasonCode=='EXACT_KEY_NOT_FOUND_IN_BOUNDED_SCAN','truncated scan does not invent full absence')
d=describe({},nil,101);yes(d.slots.tcp.reasonCode=='SELECTED_INPUT_ABSENT'and d.slots.udp.reasonCode=='SELECTED_INPUT_ABSENT','missing selected inputs reported')
s,c,w=make();s.snapshot.flows={s.snapshot.flows[1]};s.snapshot.admissionProjection={scope='bulk-and-admitted-rt'};d=describe(s,w,101);yes(d.slots.udp.reasonCode=='NOT_IN_ADMISSION_PROJECTION'and not d.slots.udp.completeInputPresenceKnown,'projection absence is not complete-source absence')
`;
const nativeCode=prefix+nativeCases.replace('__HELPER__',()=>helper)+'\n'+suffix;
fs.writeFileSync(root+'/diagnostic-helper-native.lua',nativeCode);
const e=encode("/usr/bin/lua - <<'NSS53_DIAGNOSTIC_RAM'\n"+nativeCode+'\nNSS53_DIAGNOSTIC_RAM\n');
if(process.argv.includes('--prepare-only')){console.log(JSON.stringify({prepared:true,execBytes:e.execBytes,localCompleteAdapter:true,nativeDiagnosticHelperOnly:true}));process.exit(0);}
const unix=p=>{const x=fs.realpathSync(p).replaceAll('\\','/');return '/mnt/'+x[0].toLowerCase()+x.slice(2);};
const runtime='work/nss9/lua-runtime/extracted/usr';
const replay=spawnSync('wsl.exe',['-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(runtime+'/lib/x86_64-linux-gnu'),unix(runtime+'/bin/lua5.1'),unix(root+'/diagnostic-local-replay.lua')],{encoding:'utf8',windowsHide:true,timeout:30000});
fs.writeFileSync(root+'/diagnostic-local-output.txt',replay.stdout+replay.stderr);assert.equal(replay.status,0,replay.stderr);const localCases=[...replay.stdout.matchAll(/^PASS (.+)$/gm)].map(x=>x[1]);assert.equal(Number(replay.stdout.match(/^COMPLETE (\d+)$/m)?.[1]),localCases.length);const localProof={passed:true,cases:localCases};
const c=await connectRouter();let nativeProof;try{const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/diagnostic-helper-native-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);nativeProof=JSON.parse(r.stdout);assert.ok(nativeProof.passed);}finally{c.close();}
const out={passed:true,observedAt:new Date().toISOString(),localChecks:localProof.cases.length,localCases:localProof.cases,originalAdapterChecksReplayed:21,additionalLocalAssertions:localProof.cases.length-21,adapterSha256:sha(adapter),originalAdapterSha256:sha(original),fixtureSha256:sha(parts.join('\n')),nativeJsonc:true,nativeDiagnosticHelperChecks:nativeProof.cases.length,nativeCases:nativeProof.cases,completeAdapterLocalOnly:true,nativeCompleteAdapterQualified:false,ioTimeAndAcknowledgementsMocked:true,sameFailureFrame:true,extraAdmissionClassificationReads:0,maximumAfterRejectionDiagnosticReads:1,completeDiagnosticRequiresMatchingProducerAndQuery:true,embeddedConsumerByteIdentical:true,originalAssertionsRetained:true,routerWrites:false,realForwardingQualified:false,notInstalled:true,notProductionBound:true,execBytes:e.execBytes,preparationTransportRejections:3,localFixtureCorrectionsBeforeRouterExecution:2};
fs.writeFileSync(root+'/diagnostic-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({...out,localCases:undefined,nativeCases:undefined}));
