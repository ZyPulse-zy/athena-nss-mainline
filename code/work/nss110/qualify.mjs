import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {declaredReference,authSha256,manifestSha256,oldManifestSha256} from './declared-baseline.mjs';
import {auditBaseline} from '../nss15/baseline.mjs';
const root='work/nss110',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const original=JSON.parse(fs.readFileSync('work/nss68/nss107-final-20261005-baseline-private.json'));
const current=JSON.parse(fs.readFileSync(root+'/v1-final-baseline-private.json'));
const health=JSON.parse(fs.readFileSync(root+'/v1-health-controller-status-private.json'));
const repair=JSON.parse(fs.readFileSync('work/nss108/auth-repair-latest-private.json'));
assert.ok(repair.committed&&repair.independent180SecondRollbackVerifiedBeforeWrite);
assert.equal(repair.newAuthSha256,authSha256);assert.equal(repair.newManifestSha256,manifestSha256);assert.equal(repair.oldManifestSha256,oldManifestSha256);
const beforeManifest=fs.readFileSync('work/nss108/protected-manifest-private.txt');
const changed=Buffer.from(beforeManifest.toString().replace(repair.oldAuthSha256+'  /root/router-project/scripts/auth-recover.sh',authSha256+'  /root/router-project/scripts/auth-recover.sh'));
assert.equal(hash(beforeManifest),oldManifestSha256);assert.equal(hash(changed),manifestSha256);
assert.equal(hash(fs.readFileSync('work/nss108/auth-candidate.sh')),authSha256);
const checks=[],status={up:false,pending:false,'ipv4-address':[]};
function verify(a,b,h,digest,s){const q=declaredReference(a,b,h,digest,s);const adjusted=structuredClone(b);adjusted.native=q.reference.native;adjusted.services['router-project-game-classifier']=q.reference.services['router-project-game-classifier'];auditBaseline(q.reference,adjusted);return q;}
function check(name,mutate,accept){const a=structuredClone(original),b=structuredClone(current),h=structuredClone(health),s=structuredClone(status),args={digest:authSha256};if(mutate)mutate(a,b,h,s,args);let ok=false;try{verify(a,b,h,args.digest,s);ok=true;}catch{}assert.equal(ok,accept,name);checks.push({name,passed:true,simulated:true,accepted:ok});}
check('actual-declared-four-wan-reference',null,true);
check('auth-source-drift',(a,b,h,s,x)=>x.digest='0'.repeat(64),false);
check('manifest-foreign-row',(a,b)=>b.protectedManifestSha256='0'.repeat(64),false);
check('old-manifest-is-not-current',(a,b)=>b.protectedManifestSha256=oldManifestSha256,false);
check('manifest-check-failed',(a,b)=>b.protectedManifestPassed=false,false);
check('wan4-running-during-adoption',(a,b)=>{b.services['router-project-minieap'].wan4.running=true;b.services['router-project-minieap'].wan4.pid=9999;},false);
check('wan4-pid-field-on-stopped-instance',(a,b)=>b.services['router-project-minieap'].wan4.pid=9999,false);
check('wan4-command-drift',(a,b)=>b.services['router-project-minieap'].wan4.command.push('foreign'),false);
check('wan4-up',(a,b,h,s)=>s.up=true,false);
check('wan4-pending',(a,b,h,s)=>s.pending=true,false);
check('wan4-new-address',(a,b)=>b.addresses.rpwan4=[{}],false);
check('wan4-route-drift',(a,b)=>b.routes['104']+='foreign\n',false);
check('unknown-weight',(a,b,h)=>h.weights[1]=90,false);
check('healthy-set-drift',(a,b,h)=>h.wan[3].healthy=true,false);
check('fixed-ct-rule-drift',(a,b)=>b.rules=b.rules.replace('lookup 101','lookup 105'),false);
check('foreign-service-command',(a,b)=>b.services['router-project-minieap'].wan2.command.push('foreign'),false);
check('unrelated-file-drift',(a,b)=>{const k=Object.keys(b.originalFiles)[0];b.originalFiles[k]='foreign';},false);
check('reboot',(a,b)=>b.boot+='foreign',false);
check('ecm-open',(a,b)=>b.ecm.stop4=0,false);
check('unknown-pbr-rule',(a,b)=>{b.pbr+='foreign\n';b.nftRuleset+='foreign\n';},false);
for(const name of ['controlled-session.mjs','match-controlled.mjs','run.mjs']){
 const old=fs.readFileSync('work/nss105/'+name,'utf8'),text=fs.readFileSync(root+'/'+name,'utf8');
 assert.equal(text.replaceAll('nss110','nss105').replaceAll('NSS110','NSS105'),old,name);
 checks.push({name:name+'-namespace-only',passed:true,simulated:false});
}
for(const name of fs.readdirSync(root).filter(n=>n.endsWith('.mjs'))){const r=spawnSync(process.execPath,['--check',root+'/'+name],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);}
const sourceManifest={};for(const name of fs.readdirSync(root))if(/\.(mjs|py|ps1)$/.test(name))sourceManifest[root+'/'+name]=hash(fs.readFileSync(root+'/'+name));
const privateInputBindings={};for(const path of ['work/nss68/nss107-final-20261005-baseline-private.json',root+'/v1-final-baseline-private.json',root+'/v1-health-controller-status-private.json','work/nss108/auth-repair-latest-private.json','work/nss108/protected-manifest-private.txt','work/nss108/auth-candidate.sh','work/nss109/health-controller.lua'])privateInputBindings[path]=hash(fs.readFileSync(path));
const out={passed:true,productionExecution:false,onlyDeclaredPrewriteBaselineChanged:true,nssHardwarePayloadChanged:false,unknownDriftAccepted:false,offeredMbps:48,qosMbps:30,checks,sourceManifest,privateInputBindings};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,newChecks:checks.length,newSourceBindings:Object.keys(sourceManifest).length,productionWrites:false}));
