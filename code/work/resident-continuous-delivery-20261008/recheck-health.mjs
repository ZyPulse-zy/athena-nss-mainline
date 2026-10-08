import fs from 'node:fs';
import crypto from 'node:crypto';
import {startupHealth} from '../resident-continuous-dev-20261008/startup-health.mjs';
const run='work/resident-continuous-recovery-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
fs.mkdirSync(run);
fs.writeFileSync(run+'/intent.json',JSON.stringify({readonly:true,reason:'Original final audit rejected changed local fixture source before router connection; preserve failure and perform new bound read only health and physical closure',originalRun:'work/resident-continuous-integration-20261008104628-8787fb9c',at:new Date().toISOString()})+'\n',{flag:'wx'});
try { const result=await startupHealth(run); console.log(JSON.stringify({...result,runDirectory:run})); }
catch(e){fs.writeFileSync(run+'/failure-private.json',JSON.stringify({error:String(e),stack:String(e.stack)})+'\n',{flag:'wx'});console.error(String(e));process.exitCode=1;}
