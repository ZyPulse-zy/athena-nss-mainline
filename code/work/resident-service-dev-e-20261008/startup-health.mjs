import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawn} from 'node:child_process';
import {materializeNormal} from '../resident-normal-dev-e-20261008/materialize-normal.mjs';
import {save,resolveLocal,workspaceRoot} from './storage.mjs';
export async function startupHealth(run){
 const root='work/resident-rc1-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
 const q=materializeNormal(root,Date.now()+600000);assert.equal(q.allSevenDataPlaneLuaByteExactWithRc1,true);
 save(run+'/startup-health-reference-private.json',{root,readonly:true,createsTraffic:false});
 for(const [name,seconds]of [['read-final-health.mjs',95],['read-physical-final.mjs',35]]){
  const p=spawn(process.execPath,[resolveLocal(root+'/'+name)],{cwd:workspaceRoot,windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);
  const timer=setTimeout(()=>p.kill(),seconds*1000);let code;try{code=await new Promise((resolve,reject)=>{p.once('error',reject);p.once('close',resolve);});}finally{clearTimeout(timer);}
  save(run+'/startup-'+name+'-raw-private.json',{code,stdout,stderr});assert.equal(code,0,'Startup readonly health refused; original output retained: '+name);
 }
 const proof={passed:true,readonly:true,healthAndOriginalPhysicalQueuesPassed:true,routerWrites:false,trafficGenerated:false};save(run+'/startup-health.json',proof);return proof;
}
