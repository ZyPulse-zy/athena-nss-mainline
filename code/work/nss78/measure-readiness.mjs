import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyPreparation} from '../nss77/session-binding.mjs';
import {verifyDeployment} from '../nss68/deployment-binding.mjs';

// Diagnostic only. Reads publication timing and core sleep witnesses without
// selecting, tagging, staging, generating traffic, or granting NSS admission.
const root='work/nss78';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const binding=verifyPreparation();
const {deployment}=verifyDeployment();
const phase=fs.readFileSync('work/nss69/core-guard-phase.lua','utf8');
const health=JSON.parse(fs.readFileSync('work/nss68/nss78-start-20261005-health.json'));
assert.equal(health.passed,true);
assert.equal(health.configSha256,deployment.configHash);
const expected={base:deployment.base,hash:deployment.configHash,pid:health.workerPid,guardianPid:health.guardianPid};
const code=String.raw`
local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local E=assert(j.parse([===[${JSON.stringify(expected)}]===]))
local function read(p,cap)local f=assert(io.open(p));local b=f:read(cap+1)or'';f:close();assert(#b<=cap);return b end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local function stable(p,cap)local a=assert(fs.lstat(p));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1);local b=read(p,cap);local z=assert(fs.lstat(p));assert(a.dev==z.dev and a.ino==z.ino);return b end
local function zero()
 for _,x in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..x,128))==1)end
 for _,x in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..x,128))==0)end
end
local boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')
assert(read('/root/router-project/game-classifier-generation',512)==E.base..' '..E.hash..'\n')
local phase=assert(loadstring([====[${phase}]====]))()
local initial=phase.scan(fs,read);local guard={pid=initial.guard.pid,start=initial.guard.start}
local ram='/tmp/router-project-game-classifier';local samples={};local started=now();local stop=started+16
local guardText=read('/root/router-project/scripts/core-guard.sh',65536)
repeat
 zero();local began=now();local s=assert(j.parse(stable(ram..'/classification.json',4194304)));local g=assert(j.parse(stable(ram..'/guardian.json',4194304)));local got=now()
 assert(s.pid==E.pid and s.configSha256==E.hash and s.boot==boot and s.status=='running'and not s.error and s.nssPermit==false)
 assert(s.publication=='before-software-baseline'and g.pid==E.guardianPid and g.healthy and g.boot==boot and g.configSha256==E.hash)
 local p=assert(s.snapshot.provenance);assert(p.boot==boot and p.rawStatus==0 and p.exitCode==0 and p.queryFamily=='ipv4'and p.queryZone==0)
 assert(p.startedAtUptime<=p.finishedAtUptime and p.finishedAtUptime<=got)
 local c=phase.scan(fs,read,guard);local done=now();local age=done-p.startedAtUptime
 local sleepAge=c.sleep and done-tonumber(c.sleep.start)/c.clockTicks or nil
 samples[#samples+1]={at=done,sequence=p.sequence,queryStarted=p.startedAtUptime,queryFinished=p.finishedAtUptime,published=s.atUptime,queryAge=age,publishDelay=s.atUptime-p.startedAtUptime,sourceReadSeconds=got-began,coreReadSeconds=done-got,initialAgeEligible=age<1.65,originalTagAgeEligible=age<2,learningAgeEligible=age<2.75,sleepPid=c.sleep and c.sleep.pid or nil,sleepAge=sleepAge,freshCoreBirthEligible=sleepAge and sleepAge>=0 and sleepAge<=0.2 or false,flowCount=#s.snapshot.flows}
 assert(#samples<=200)
 if now()>=stop then break end;n.nanosleep(0,100000000)
until false
zero();print(j.stringify({started=started,ended=now(),samples=samples,guardText=guardText,guard=guard,workerPid=E.pid,guardianPid=E.guardianPid,configSha256=E.hash,ecmStoppedAndZero=true,readonly=true,nssAdmissionAllowed=false,actualPairReadinessNotTested=true}))
`;
const c=await connectRouter();
try {
 const e=encode("/usr/bin/lua - <<'NSS78_READINESS_TIMING'\n"+code+"\nNSS78_READINESS_TIMING\n");
 const r=receipt(await c.run(e.command),e);
 fs.writeFileSync(root+'/readiness-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});
 assert.equal(r.code,0,r.stderr);
 const result=JSON.parse(r.stdout);
 const {guardText,...timing}=result;
 fs.writeFileSync(root+'/core-guard-source-private.sh',guardText,{flag:'wx'});
 fs.writeFileSync(root+'/readiness-timing-private.json',JSON.stringify(timing,null,2)+'\n',{flag:'wx'});
 const samples=result.samples;
 const unique=[...new Map(samples.map(s=>[s.sequence,s])).values()];
 const range=k=>({min:Math.min(...samples.map(s=>s[k])),max:Math.max(...samples.map(s=>s[k]))});
 const out={observedAt:new Date().toISOString(),readonly:true,seconds:result.ended-result.started,samples:samples.length,publications:unique.length,
  initialAgeEligible:samples.filter(s=>s.initialAgeEligible).length,originalTagAgeEligible:samples.filter(s=>s.originalTagAgeEligible).length,
  freshCoreBirthEligible:samples.filter(s=>s.freshCoreBirthEligible).length,jointFreshSamples:samples.filter(s=>s.initialAgeEligible&&s.freshCoreBirthEligible).length,
  queryAge:range('queryAge'),publicationDelay:range('publishDelay'),sourceReadSeconds:range('sourceReadSeconds'),coreReadSeconds:range('coreReadSeconds'),
  workerPid:result.workerPid,guardianPid:result.guardianPid,configSha256:result.configSha256,ecmStoppedAndZero:true,
  realFlowAdmissionNotTested:true,highLoadNotTested:true,cpuBenefitNotTested:true,nssPermissionGranted:false,
  sourceManifest:{'work/nss78/measure-readiness.mjs':hash(fs.readFileSync(root+'/measure-readiness.mjs')),'work/nss69/core-guard-phase.lua':hash(phase)},
  originalEntryBindingCount:Object.keys(binding.sourceManifest).length,privateCoreGuardSha256:hash(guardText)};
 fs.writeFileSync(root+'/readiness-summary.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(out));
} finally {c.close();}
