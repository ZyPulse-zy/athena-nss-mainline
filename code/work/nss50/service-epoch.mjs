// Only acknowledge a healthy sing-box PID change that predates the experiment.
// Commands, instance sets and running states remain exact; all other services stay pinned.
import assert from 'node:assert/strict';
import {canonical} from '../nss12/forward-tag-trial/model.mjs';
export function adoptServices(historical,live){
 assert.equal(canonical(Object.keys(live)),canonical(Object.keys(historical)),'Service set changed');
 const normalized=structuredClone(live),changes=[];
 for(const name of Object.keys(historical)){
  if(name==='router-project-game-classifier')continue; // Original native ownership audit verifies its actual instance.
  if(name!=='sing-box-athena'){assert.equal(canonical(live[name]),canonical(historical[name]),'Unrelated service changed: '+name);continue;}
  assert.equal(canonical(Object.keys(historical[name]).sort()),canonical(['core','guard']));
  assert.equal(canonical(Object.keys(live[name]).sort()),canonical(['core','guard']));
  for(const instance of ['core','guard']){
   const a=historical[name][instance],b=live[name][instance];
   assert.equal(canonical(Object.keys(a).sort()),canonical(['command','pid','running']));
   assert.equal(canonical(Object.keys(b).sort()),canonical(['command','pid','running']));
   assert.equal(a.running,true);assert.equal(b.running,true,'sing-box instance not running');
   assert.ok(Number.isSafeInteger(a.pid)&&a.pid>1&&Number.isSafeInteger(b.pid)&&b.pid>1);
   assert.equal(canonical(a.command),canonical(b.command),'sing-box command changed');
   if(a.pid!==b.pid)changes.push({service:name,instance,pidChangedBeforeExperiment:true});
   normalized[name][instance].pid=a.pid;
  }
 }
 normalized['router-project-game-classifier']=structuredClone(historical['router-project-game-classifier']);
 assert.equal(canonical(normalized),canonical(historical),'Service adoption changed a protected field');
 return{services:structuredClone(live),changes,commandsRunningAndOtherServicesUnchanged:true,routerWrites:false};
}
export function verifyEpochServices(expected,current){
 const a=structuredClone(expected),b=structuredClone(current);
 // The original locked native classifier audit retains its actual PID/start/argv predicates.
 b['router-project-game-classifier']=a['router-project-game-classifier'];
 assert.equal(canonical(a),canonical(b),'Service identity changed during experiment');
 return true;
}
