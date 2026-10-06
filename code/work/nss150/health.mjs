// Report the declared auth repair and independently observed WAN4 failure.
// This is an operational closure, never an NSS admission certificate.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss27/connect-router.mjs';import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';import {render} from '../nss49/audit-renderer.mjs';
import {proveWan4Failover} from '../nss109/failover-baseline.mjs';
const root='work/nss150',h=b=>crypto.createHash('sha256').update(b).digest('hex'),q=s=>"'"+s.replaceAll("'","'\\''")+"'";
const old=JSON.parse(fs.readFileSync('work/nss68/nss107-final-20261005-baseline-private.json')),ctx=JSON.parse(fs.readFileSync('work/nss68/deployment-latest.json')),repair=JSON.parse(fs.readFileSync('work/nss108/auth-repair-latest-private.json'));
assert.ok(repair.committed&&repair.unchangedServicesAndRouting&&repair.independent180SecondRollbackVerifiedBeforeWrite);
const originalManifest=fs.readFileSync('work/nss108/protected-manifest-private.txt'),target='/root/router-project/scripts/auth-recover.sh';
const changedManifest=Buffer.from(originalManifest.toString().replace(repair.oldAuthSha256+'  '+target,repair.newAuthSha256+'  '+target));assert.equal(h(changedManifest),repair.newManifestSha256);
const version=process.argv[2]??'v1';assert.match(version,/^v[0-9]+$/);
const c=await connectRouter(),save=(n,o)=>fs.writeFileSync(root+'/'+version+'-'+n+'.json',JSON.stringify(o,null,2)+'\n',{flag:'wx'}),run=async s=>{const e=encode(s),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr||'Read-only audit failed');return r.stdout;};
try{
 const b=await readBaseline(c,root,version+'-final-baseline');assert.ok(b.protectedManifestPassed);assert.equal(b.protectedManifestSha256,repair.newManifestSha256);
 assert.equal((await run('sha256sum '+target)).split(/\s/)[0],repair.newAuthSha256);assert.equal(old.protectedManifestSha256,repair.oldManifestSha256);
 const miniOld=old.services['router-project-minieap'].wan4,miniNew=b.services['router-project-minieap'].wan4;assert.deepEqual(miniNew.command,miniOld.command);
 assert.equal((await run('sh /root/router-project/scripts/transaction.sh status')).trim(),'NO_ACTIVE_TRANSACTION');
 const body='exec 8>/tmp/router-project-transaction.lock\nflock -x 8\n/usr/bin/lua - '+ctx.base+' '+ctx.configHash+" <<'NSS109_FINAL_NATIVE'\n"+render(fs.readFileSync('work/nss23/operational-audit.lua','utf8'))+'\nNSS109_FINAL_NATIVE\n';
 const raw=JSON.parse(await run(ctx.base+'/group-runner 6 /bin/sh -c '+q(body)));save('final-native-audit-private',raw);assert.equal(raw.passed,true,raw.error);const audit=raw.result;
 assert.ok(Number.isSafeInteger(audit.pid)&&audit.pid>1);assert.equal(audit.guardianPid,17139);assert.equal(b.services['router-project-game-classifier'].classifier.pid,audit.pid);assert.equal(b.services['router-project-game-classifier'].guardian.pid,audit.guardianPid);
 const adjusted=structuredClone(b);adjusted.native=old.native;adjusted.protectedManifestSha256=old.protectedManifestSha256;
 for(const name of['classifier','guardian']){assert.deepEqual(b.services['router-project-game-classifier'][name].command,old.services['router-project-game-classifier'][name].command);assert.equal(b.services['router-project-game-classifier'][name].running,true);}
 adjusted.services['router-project-game-classifier']=structuredClone(old.services['router-project-game-classifier']);
 adjusted.services['router-project-minieap'].wan4=old.services['router-project-minieap'].wan4;adjusted.addresses.rpwan4=old.addresses.rpwan4;adjusted.routes['104']=old.routes['104'];
 const health=JSON.parse(await run('cat /tmp/router-project-health/status.json'));save('health-controller-status-private',health);
 const failover=proveWan4Failover(old,adjusted,health);save('wan4-failover-proof',failover.proof);
 const stable=auditBaseline(failover.reference,adjusted);
 const closure=String.raw`local f=require('nixio.fs');local j=require('luci.jsonc');local u=assert(require('ubus').connect());local w=assert(u:call('network.interface.wan4','status',{}));u:close();local stages,states,modules={},{},{}
for x in f.dir('/tmp')do if x:match('^rp%-nss%d+%-stage%-')then stages[#stages+1]=x end end
for x in f.dir('/root/router-project/experiments')do if x:match('^rp%-nss%d+%-state%-')then states[#states+1]=x end end
local h=assert(io.open('/proc/modules'));local s=h:read('*a');h:close();for x in s:gmatch('[^\n]+')do if x:match('^rp_ecm_gate')or x:match('^qca_nss_qdisc ')then modules[#modules+1]=x:match('^(%S+)')end end
print(j.stringify({stages=stages,states=states,modules=modules,wan4Up=w.up,wan4Ipv4Present=w['ipv4-address']and #w['ipv4-address']>0 or false}))`;
 const clean=JSON.parse(await run("lua - <<'NSS109_CLOSURE'\n"+closure+'\nNSS109_CLOSURE\n'));save('final-closure-private',clean);for(const k of['stages','states','modules'])assert.equal(clean[k].length,0,k+' remain');
 const out={passed:true,observedAt:new Date().toISOString(),readonly:true,originalFullLockedNativeAudit:true,unrelatedConfigurationMatches:stable.configurationMatches,knownExceptions:['Healthy native-audited classifier instance recovered before experiment','Auth PID-discovery source and exactly its manifest row','Naturally changed WAN4 PID/link/address/route state','Exact protected health-controller failover mapping and WAN4 DHCP rules'],exactWan4AutomaticFailoverProved:failover.proof.passed,nativeDynamicSelectorsVerifiedByOriginalOwnershipAudit:true,configSha256:ctx.configHash,workerPid:audit.pid,guardianPid:audit.guardianPid,queryAge:audit.queryAge,selectors:audit.selectors,ecmStoppedAndZero:stable.checks.ecmStoppedAndZero,noActiveTransaction:true,noStaging:true,noExperimentState:true,noExperimentalModule:true,authRepairCommitted:true,wan4Running:miniNew.running,wan4Up:clean.wan4Up,wan4Ipv4Present:clean.wan4Ipv4Present,allFiveWanHealthy:clean.wan4Up&&clean.wan4Ipv4Present,fullOriginalNssAdmissionEpochPassed:false,nssAdmissionAllowed:false,initialHealthFailurePreserved:true};
 save('final-health',out);console.log(JSON.stringify(out));
}catch(e){save('final-failure-private',{error:String(e)});console.error(String(e).split('\n')[0]);process.exitCode=1;}finally{c.close()}
