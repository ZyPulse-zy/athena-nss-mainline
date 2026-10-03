import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
import{connectRouter}from'../nss20/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const projection=fs.readFileSync('work/nss33/admission-publication.lua','utf8');
const adapter=fs.readFileSync('work/nss32/classifier.lua','utf8');
const consumer=adapter.slice(adapter.indexOf('local Consumer=(function()')+'local Consumer=(function()'.length,adapter.indexOf('\nend)()\nlocal A={}'));
let fixtures=fs.readFileSync('work/nss23/consumer-fixtures.lua','utf8').replace('__CONSUMER__',()=>consumer);
fixtures=fixtures.slice(0,fixtures.lastIndexOf('print(j.stringify('));
// Historical fixture uses escaped separators as literal source; the native consumer uses NUL.
fixtures=fixtures.replaceAll("'\\\\0'","'\\0'");
const extra=String.raw`
local P=assert(loadstring([====[${projection}]====]))()
local s,c,w=make();local full=s.snapshot
for i=1,400 do local f=copy(full.flows[1]);f.key='noncandidate-'..i;f.decision={class='BE',reason='ordinary',budgetAdmitted=false};f.leaf.class='BE';f.leaf.candidate=false;f.leaf.downTag=0;full.flows[#full.flows+1]=f end
local before=j.stringify(full);local compact=P.project(full)
yes(#compact.flows==2 and #full.flows==402,'all and only bulk/admitted RT retained from 402 flows')
yes(j.stringify(full)==before,'full source snapshot remains byte-for-byte unchanged')
yes(compact.flows[1]==full.flows[1]and compact.flows[2]==full.flows[2],'selected identities and decisions are not reconstructed')
yes(compact.provenance==full.provenance and compact.admissionProjection.sourceSequence==4,'source sequence and timestamps unchanged')
s.snapshot=compact;local epoch=M.pair(s,c,101,w)
yes(#epoch.decisions==2 and epoch.nssAdmissionAllowed==false,'native consumer accepts compact publication without granting permission')
yes(not pcall(M.pair,s,c,102.1,w),'projection does not extend pre-learning freshness')
local f=full.flows[2];f.decision={class='BE',reason='cooldown',budgetAdmitted=false};f.leaf.class='BE';f.leaf.candidate=false;f.leaf.downTag=0;s.snapshot=P.project(full)
local changed=M.compareEpoch(epoch,s,c,101.2)
yes(changed.action=='RETIRE_EXACT_SELECTED_SLOTS'and #changed.affected==1 and changed.affected[1]=='udp','class exit omitted from projection still exactly retires UDP')
yes(changed.clearConntrack==false,'projected class exit never flushes conntrack')
local a=make();a.snapshot.flows[2]=nil;yes(#P.project(a.snapshot).flows==1,'exited UDP is absent immediately')
local a=make();a.snapshot.flows[2].decision.budgetAdmitted=false;a.snapshot.flows[2].leaf.candidate=false;a.snapshot.flows[2].leaf.downTag=0;yes(#P.project(a.snapshot).flows==1,'unadmitted RT is excluded')
yes(P.project(nil)==nil,'warming/degraded/error publications retain no snapshot')
for _,mutate in ipairs({function(s)s.flows[2].key=s.flows[1].key end,function(s)s.flows[2].leaf.nssPermit=true end,function(s)s.flows[2].leaf.downTag=0 end,function(s)s.flows[2].leaf.candidate=false end})do local a=make();mutate(a.snapshot);yes(not pcall(P.project,a.snapshot),'malformed projection input refused')end
local a=make();local projected=P.project(a.snapshot);local wire=j.stringify(projected);local roundtrip=assert(j.parse(wire));yes(#roundtrip.flows==2 and roundtrip.provenance.sequence==4,'target jsonc retains projected flows and provenance')
print(j.stringify({passed=true,checks=#cases,cases=cases,routerWrites=false,hardwareQualification=false,scope='Native Lua/jsonc, unchanged NSS32 consumer, projection and exact retirement planning'}))
`;
const c=await connectRouter();try{const code=fixtures+'\n'+extra;const e=encode("/usr/bin/lua - <<'NSS33_PROJECT_FIXTURE'\n"+code+"\nNSS33_PROJECT_FIXTURE\n");const r=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss33/projection-test-raw.json',JSON.stringify(r,null,2));assert.equal(r.code,0,r.stderr);const d=JSON.parse(r.stdout);assert.equal(d.passed,true);d.projectionSha256=crypto.createHash('sha256').update(projection).digest('hex');d.workerSha256=crypto.createHash('sha256').update(fs.readFileSync('work/nss33/worker.lua')).digest('hex');d.execBytes=e.execBytes;fs.writeFileSync('work/nss33/projection-qualified.json',JSON.stringify(d,null,2)+'\n');console.log(JSON.stringify(d));}finally{c.close()}
