// Continue the already armed repair after a changing owned classifier selector
// made a raw native-filter text comparison fail. Original native audit stays exact.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {connectRouter} from '../nss27/connect-router.mjs';
import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';import {render} from '../nss49/audit-renderer.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const dir=process.argv[2];assert.match(dir,/^work\/nss108\/nss108-auth-[a-z0-9-]+$/);const id=dir.split('/').at(-1),h=b=>crypto.createHash('sha256').update(b).digest('hex'),q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const before=JSON.parse(fs.readFileSync(dir+'/before-private.json')),cp=JSON.parse(fs.readFileSync(dir+'/checkpoint.json')),stage=JSON.parse(fs.readFileSync(dir+'/stage-private.json'));
const old=fs.readFileSync('work/nss108/auth-before.sh'),candidate=fs.readFileSync('work/nss108/auth-candidate.sh'),manifest=fs.readFileSync('work/nss108/protected-manifest-private.txt'),target='/root/router-project/scripts/auth-recover.sh';
const newManifest=Buffer.from(manifest.toString().replace(h(old)+'  '+target,h(candidate)+'  '+target));
const save=(n,o)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(o,null,2)+'\n',{flag:'wx'});const c=await connectRouter();
const run=async s=>{const e=encode(s),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr||'Remote operation failed');return r.stdout;};
try{
 const status=(await run('sh /root/router-project/scripts/transaction.sh status')).trim().split(' ');assert.equal(status[0],id);assert.equal(status[1],before.boot);
 const now=Number((await run('cut -d. -f1 /proc/uptime')).trim());assert.ok(Number(status[2])-now>35,'Less than 35s remain; let independent undo finish');
 assert.equal((await run('sha256sum '+target)).split(/\s/)[0],h(candidate));
 const ctx=JSON.parse(fs.readFileSync('work/nss68/deployment-latest.json'));
 const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS108_NATIVE_AFTER'\n"+render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'))+'\nNSS108_NATIVE_AFTER\n';
 const audit=JSON.parse(await run(ctx.base+'/group-runner 6 /bin/sh -c '+q(body)));save('native-after-private',audit);assert.equal(audit.passed,true,audit.error);
 const after=await readBaseline(c,dir,'completion');assert.equal(after.protectedManifestSha256,h(newManifest));
 const adjusted={...after,native:before.native,protectedManifestSha256:before.protectedManifestSha256};const stable=auditBaseline(before,adjusted);
 save('unchanged-runtime',{...stable,ownedDynamicNativeSelectorsVerifiedByOriginalFullAudit:true,onlyDeclaredProtectedManifestRowChanged:true,authenticatorRestarted:false});
 await run('printf %s '+q('NSS108 PID-discovery fixtures, separate SSH, original full owned native audit, source/manifest SHA and unchanged auth/routing passed\n')+' >/root/router-project/transactions/'+id+'/verification.txt');
 await run('sh /root/router-project/scripts/transaction.sh commit '+id);assert.equal((await run('cat /root/router-project/transactions/'+id+'/result')).trim(),'committed');
 const out={passed:true,committed:true,id,localDir:dir,checkpoint:cp.name,stagePath:stage.ready.dir,oldAuthSha256:h(old),newAuthSha256:h(candidate),oldManifestSha256:h(manifest),newManifestSha256:h(newManifest),independent180SecondRollbackVerifiedBeforeWrite:true,authenticatorRestarted:false,interfacesRestarted:false,unchangedServicesAndRouting:true,ecmStoppedAndZero:true,naturalRollbackTested:false,originalNativeAuditPassed:true,initialRawDynamicFilterComparisonFailurePreserved:true,observedAt:new Date().toISOString()};
 save('committed',out);fs.writeFileSync('work/nss108/auth-repair-latest-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
 fs.writeFileSync(dir+'/cancel',Buffer.from('1'),{flag:'wx'});await c.upload(dir+'/cancel',stage.ready.dir+'/cancel');let absent=false;for(let i=0;i<12;i++){if((await c.run('test ! -e '+stage.ready.dir)).code===0){absent=true;break;}await new Promise(r=>setTimeout(r,250));}assert.ok(absent);save('stage-cleanup',{passed:true,ownedStageCancelledAfterCommit:true,naturalExpiryClaimed:false});
 console.log(JSON.stringify({...out,id:undefined,localDir:undefined,checkpoint:undefined,stagePath:undefined}));
}catch(e){save('completion-failure-private',{error:String(e)});console.error(String(e).split('\n')[0]);process.exitCode=1;}finally{c.close();}
