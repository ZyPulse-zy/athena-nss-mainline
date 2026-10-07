// Reuse the original locked audit and exact physical-default comparison once.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const dir=process.argv[2];assert.match(dir,/^work\/v29-peer-proof\/run-\d{14}-[a-f0-9]{16}$/);
const save=(name,x)=>fs.writeFileSync(dir+'/'+name+'.json',JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const read=name=>JSON.parse(fs.readFileSync(dir+'/'+name+'.json'));
assert.ok(read('recheck-restoration').passed,'Endpoint closure must pass first');
const prePath='work/v28-peer-path/day-peer-preflight-20261007001039-b3d28a5d-process-private.json',pre=JSON.parse(fs.readFileSync(prePath));assert.equal(pre.code,0);
const label='v29-peer-final-'+Date.now(),events=[];
function run(args){const p=spawnSync(process.execPath,args,{windowsHide:true,encoding:'utf8',timeout:35000});events.push({args,code:p.status,stdout:p.stdout,stderr:p.stderr});save('audit-step-'+events.length+'-private',events.at(-1));assert.equal(p.status,0,'Saved readonly audit step failed');return JSON.parse(p.stdout.trim().split(/\r?\n/).at(-1));}
const full=run(['work/v27-raw/current-audit-diagnostic.mjs',label,'recovery',pre.caseDir]);
const original='work/nss156/read-final-physical.mjs',file='work/v29-peer-proof/read-physical-'+label+'.mjs',bytes=fs.readFileSync(original),source=bytes.toString().replace("const r='work/nss156'","const r='"+dir+"'");assert.notEqual(source,bytes.toString());fs.writeFileSync(file,source,{flag:'wx'});
const physical=run([file]);
const summary={passed:full.passed&&physical.passed&&read('recheck-restoration').passed,observedAt:new Date().toISOString(),readonly:true,productionNssWrites:false,fullAudit:full,physicalQueues:physical,endpointAndClientClosure:read('recheck-restoration'),originalPhysicalAuditSourceSha256:crypto.createHash('sha256').update(bytes).digest('hex'),physicalReaderSource:file,initialAudit:{...JSON.parse(pre.stdout),observedBeforeProbe:true}};
assert.ok(summary.passed);save('final-audit',summary);console.log(JSON.stringify(summary));
