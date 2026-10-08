import assert from 'node:assert/strict';
import {read} from './storage.mjs';
import {candidateUnavailableBeforeNss} from './generation-outcome.mjs';
const root='work/resident-rc1-run-20261008055107-ba4ee68e';
const pilot=read(root+'/pilot-reference-private.json').directory,dir=read(pilot+'/case-reference-private.json').dir;
const result={code:1,runtimeRoot:root,hardwareCompleted:false,restorationPassed:true,nssSeconds:0,renewals:0,samples:0,stopRequested:false,stopError:null};
const checks=[];assert.equal(candidateUnavailableBeforeNss(result),false);checks.push('old actual refusal lacks detailed witness and cannot be reclassified');
const names=['entry-result-private.json','normal-entry-supervisor-raw-private.json','normal-entry-final-audit-raw-private.json','normal-entry-physical-queues-raw-private.json','pilot-reference-private.json'];
const paths=names.map(n=>root+'/'+n).concat(pilot+'/case-reference-private.json',...['stage-undo-verified.json','last-record-private.json','selected-private.json'].map(n=>dir+'/'+n));
const data=new Map(paths.map(p=>[p,read(p)]));
const detail={diagnosticOnly:true,nssAdmissionAllowed:false,sameAdmissionFrame:true,scanTruncated:false,admissionProjectionOnly:true,sourceSequence:50,startedAtUptime:100,finishedAtUptime:100.2,slots:{}};
for(const s of Object.keys(data.get(dir+'/selected-private.json')))detail.slots[s]={selectedInputPresent:true,expectedClass:s==='udp'?'RT':'BULK',present:true,matches:1,reasonCode:'TARGET_CLASS_ADMITTED',ctMatches:true,zoneMatches:true,markMatches:true,wanMatches:true,originalMatches:true,replyMatches:true};
detail.slots.tcp={selectedInputPresent:true,expectedClass:'BULK',present:false,matches:0,reasonCode:'NOT_IN_ADMISSION_PROJECTION'};
data.get(dir+'/last-record-private.json').initialAdmissionRefusal={diagnosticOnly:true,sourceAge:1,source:{sequence:50,startedAtUptime:100,finishedAtUptime:100.2},selected:detail};
const clone=()=>new Map([...data].map(([p,v])=>[p,structuredClone(v)])),load=m=>p=>{assert.ok(m.has(p));return m.get(p);};
assert.equal(candidateUnavailableBeforeNss(result,load(data)),true);checks.push('model projection absence allows only fresh wait after full staged restoration');
for(const k of ['code','hardwareCompleted','restorationPassed','nssSeconds','renewals','samples','stopRequested','stopError']){
 const r={...result,[k]:{code:0,hardwareCompleted:true,restorationPassed:false,nssSeconds:1,renewals:1,samples:1,stopRequested:true,stopError:'unknown'}[k]};
 assert.equal(candidateUnavailableBeforeNss(r,load(data)),false);checks.push('unsafe result '+k+' remains paused');
}
for(const k of ['moduleLoaded','gateComplete','newNssPermit','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved']){
 const m=clone(),r=m.get(dir+'/last-record-private.json');r[k]=!r[k];assert.equal(candidateUnavailableBeforeNss(result,load(m)),false);checks.push('unconfirmed phase '+k+' remains paused');
}
for(const k of ['sameBoot','ownDirectoryAbsent','stateNodeDirectoryAbsent','guardianTerminated','moduleAbsent','qosModuleAbsent']){
 const m=clone();m.get(dir+'/stage-undo-verified.json')[k]=false;assert.equal(candidateUnavailableBeforeNss(result,load(m)),false);checks.push('incomplete stage undo '+k+' remains paused');
}
for(const k of ['ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches']){
 const m=clone();m.get(dir+'/last-record-private.json').initialAdmissionRefusal.selected.slots.udp[k]=false;assert.equal(candidateUnavailableBeforeNss(result,load(m)),false);checks.push('actual identity drift '+k+' remains paused');
}
for(const change of ['stale','wrongQuery','wrongTime','scanTruncated','notProjection','unknownReason','duplicate','unknownError','phaseSamples','badAudit','badPhysical','missingWitness','allAdmitted']){
 const m=clone(),r=m.get(dir+'/last-record-private.json'),p=r.initialAdmissionRefusal,d=p.selected;
 if(change==='stale')p.sourceAge=6;
 if(change==='wrongQuery')p.source.sequence++;
 if(change==='wrongTime')d.finishedAtUptime++;
 if(change==='scanTruncated')d.scanTruncated=true;
 if(change==='notProjection')d.admissionProjectionOnly=false;
 if(change==='unknownReason')d.slots.tcp.reasonCode='EXACT_KEY_ABSENT';
 if(change==='duplicate')d.slots.udp.matches=2;
 if(change==='unknownError')r.error='Unknown error';
 if(change==='phaseSamples')r.phases=[{name:'B',seconds:0.1}];
 if(change==='badAudit'){const a=m.get(root+'/normal-entry-final-audit-raw-private.json');const x=JSON.parse(a.stdout);x.ecmClosedAndZero=false;a.stdout=JSON.stringify(x);}
 if(change==='badPhysical'){const a=m.get(root+'/normal-entry-physical-queues-raw-private.json');const x=JSON.parse(a.stdout);x.defaultQueueOptionsAndHandlesExact=false;a.stdout=JSON.stringify(x);}
 if(change==='missingWitness')delete r.initialAdmissionRefusal;
 if(change==='allAdmitted')d.slots.tcp={...d.slots.udp,expectedClass:'BULK'};
 assert.equal(candidateUnavailableBeforeNss(result,load(m)),false);checks.push(change+' cannot authorize wait');
}
const full=clone(),x=full.get(dir+'/last-record-private.json').initialAdmissionRefusal.selected;
x.admissionProjectionOnly=false;x.slots.tcp={...x.slots.udp,expectedClass:'BULK',reasonCode:'TARGET_CLASS_MISMATCH'};
assert.equal(candidateUnavailableBeforeNss(result,load(full)),true);checks.push('same-identity full class mismatch ends old stage then waits without hot retag');
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,modelOnly:true,routerAccess:false,oldActualRefusalNotReclassified:true}));
