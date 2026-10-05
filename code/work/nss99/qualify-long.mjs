// Target Lua timing model; no packets, modules, sysfs writes or policy changes.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss99',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const fast=fs.readFileSync(root+'/fast-path.lua','utf8'),guard=fs.readFileSync(root+'/module-stage-guardian.lua','utf8'),native=fs.readFileSync('work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.c','utf8');
assert.ok(native.includes('session_until_ms-ms > 30000')&&native.includes('until - ms > 6000')&&native.includes('old_until - ms < 250'));
assert.ok(fast.includes('now()+27,record.deadline-28')&&fast.includes('requestedSeconds=20')&&fast.includes('p.untilMs<=session')&&fast.includes('startedAtUptime+6'));
assert.ok(guard.replace('deadline=now()+100','deadline=now()+45').replaceAll('\r\n','\n')===fs.readFileSync('work/nss49/module-stage-guardian.lua','utf8').replaceAll('\r\n','\n'),'Guardian changes exceed fixed observation deadline');
const cases=[['complete20',null],['staleSource','Classification observation stale'],['markDrift','assertion failed'],['classDrift','Selected class changed'],['flowGone','Selected flow is no longer admitted'],['wrongSessionAck','Native renewal receipt mismatch'],['beyondFixedSession','ABA cannot complete within fixed session'],['insufficientOwner','Insufficient phase/cleanup margin']];
// The unchanged tag counter contract is already qualified in NSS89. Supply a
// valid getter fixture here; execute the actual renewal and observation code.
assert.equal(hash(fs.readFileSync(root+'/tag-counter-audit.lua')),hash(fs.readFileSync('work/nss97/tag-counter-audit.lua')));
const beginAlign=fast.indexOf(' function out.align(deadline)'),endAlign=fast.indexOf(' local function alignLearning(live)');assert.ok(beginAlign>0&&endAlign>beginAlign);assert.equal(fast.match(/deadline-84/g).length,2);
const timingSource="local M={tagCounterAudit=function()return{pending=false,needsSecond=false}end}\n"+fast.slice(fast.indexOf('function M.verifyRenewalAck'),beginAlign)+fast.slice(endAlign);
const body=String.raw`
local realNixio=require('nixio');local j=require('luci.jsonc');local ticks=0
package.loaded.nixio={nanosleep=function(s,n)ticks=ticks+s+n/1000000000 end}
local M=assert(loadstring([====[${timingSource}]====]))();local results={}
local cases=assert(j.parse([====[${JSON.stringify(cases)}]====]))
for _,case in ipairs(cases)do
 ticks=0;local name=case[1];local stop4=1;local loaded=false;local nativeSession=0;local nativeUntil=0;local nativeSequence=0;local activeB=false
 local record={deadline=name=='insufficientOwner'and 70 or 100,adapterSourceSequence=1}
 local function clock()return ticks end
 local selected={};for _,slot in ipairs({'tcp','udp'})do selected[slot]={classifierKey=slot,id=slot=='tcp'and 101 or 102,mark=65536,wan=1,original={src='192.0.2.1',dst='198.51.100.1',sport=slot=='tcp'and 50001 or 50002,dport=slot=='tcp'and 22 or 45818},reply={src='198.51.100.1',dst='203.0.113.1',sport=slot=='tcp'and 22 or 45818,dport=slot=='tcp'and 50001 or 50002}}end
 local P={selected=selected,wanPrerequisites={wan=1},owner=string.rep('a',32),statePath='/root/router-project/experiments/rp-nss25-state-'..string.rep('a',32)..'/ecm-state',insmodArguments='test=1',coreGuard={}}
 local function read(p)
  if p:find('front_end_ipv4_stop',1,true)then return tostring(stop4)end
  if p:find('front_end_ipv6_stop',1,true)then return '1'end
  if p:find('/sys/kernel/debug/ecm/',1,true)then return (stop4==0 and (p:find('ecm_db/connection_count',1,true)or p:find('ecm_nss_ipv4/accelerated_count',1,true)))and '2'or '0'end
  if p=='/proc/stat'then return 'cpu 10 0 10 100 0 0 10 0\ncpu0 10 0 10 100 0 0 10 0\n'end
  if p=='/proc/net/softnet_stat'then return '00000001 00000000 00000000\n'end
  return '0'
 end
 local function stopped()assert(stop4==1)end
 local function put(p,v)
  if p:find('front_end_ipv4_stop',1,true)then stop4=tonumber(v);activeB=stop4==0
  elseif p:find('epoch_refresh',1,true)then local prev,nextSeq,untilMs=v:match('^(%d+):(%d+):(%d+)');assert(tonumber(prev)==nativeSequence);nativeSequence=tonumber(nextSeq);nativeUntil=tonumber(untilMs)end
 end
 local function parameters()
  local ackSession=name=='wrongSessionAck'and nativeSession+1 or nativeSession
  return{registered='Y',diagnostic_only='N',tcp_permit='Y',game_permit='Y',tcp_pinned_state='pinned=1 current_hash_matches=1',game_pinned_state='pinned=1 current_hash_matches=1',tcp_state='ever_opened=1 terminal=0 admit=1',game_state='ever_opened=1 terminal=0 admit=1',epoch_refresh='sequence='..nativeSequence..' classifier_until_ms='..nativeUntil..' session_until_ms='..ackSession}
 end
 local function load(args)loaded=true;nativeSession=tonumber(args:match('session_until_ms=(%d+)'));nativeUntil=tonumber(args:match('classifier_until_ms=(%d+)'));nativeSequence=tonumber(args:match('classifier_sequence=(%d+)'))end
 local function unload()loaded=false;stop4=1;activeB=false end
 local function command(_)return loaded and 'accelerated fixture'or ''end
 local function frame()
  local start=math.floor(ticks/3)*3;local flows={}
  for _,slot in ipairs({'tcp','udp'})do local w=selected[slot];local i={connectionId=w.id,zone=0,mark=w.mark,wan=w.wan,original=w.original,reply=w.reply};local c=slot=='tcp'and 'BULK'or 'RT'
   if activeB and ticks>25 and name=='markDrift'then i.mark=i.mark+1 end
   if activeB and ticks>25 and name=='classDrift'then c='BULK'end
   if not(activeB and ticks>25 and name=='flowGone'and slot=='udp')then flows[#flows+1]={key=slot,identity=i,decision={class=c},leaf={downTag=slot=='tcp'and 2399469568 or 2399535104},validUntilUptime=ticks+5}end
  end
  if activeB and ticks>25 and name=='staleSource'then start=ticks-7 end
  return{flows=flows,sourceSequence=math.floor(ticks/3)+1,producer='fixture',startedAtUptime=start,provenance={startedAtUptime=start}}
 end
 local classifier={observe=function()ticks=ticks+.01;return frame()end,diagnoseObserved=function()end,preLearningReady=function()return true end,compareCurrentEpoch=function()return{action='KEEP_IMMUTABLE_EPOCH'}end,resampleClosed=function()local f=frame();record.adapterSourceSequence=f.sourceSequence;return f end}
 function classifier.proposeRenewal()local f=frame();return{expectedSequence=record.adapterSourceSequence,nextSequence=f.sourceSequence,untilMs=name=='beyondFixedSession'and nativeSession+1 or math.floor((f.startedAtUptime+6)*1000)}end
 function classifier.acceptRenewal(p,ack)record.adapterSourceSequence=ack.sequence end
 local phase={waitFresh=function()ticks=math.ceil(ticks/3)*3;return{observedAt=ticks}end}
 local raw={nftables={}};for _,k in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do for _,suffix in ipairs({'total','expected','unexpected'})do local nz=suffix~='unexpected';raw.nftables[#raw.nftables+1]={rule={comment='fixture:'..k..'_'..suffix,expr={{counter={packets=nz and 1 or 0,bytes=nz and 60 or 0}}}}}end end;raw.nftables[#raw.nftables+1]={rule={comment='fixture:udp_post_neighbor_nonzero',expr={{counter={packets=0,bytes=0}}}}}
 local out=M.new(P,{},j,read,clock,stopped,put,command,record,parameters,load,unload,'fixture',phase,classifier)
 local ok,err=pcall(function()out.run(5,function()return raw end,{snapshot=function()return{}end},function()record.tagsRemoved=true end)end)
 if name=='complete20'then assert(ok,tostring(err));assert(#record.phases==3 and record.fastPathMeasurement.stableSeconds>=20 and #record.renewals>=6);for _,p in ipairs(record.phases)do assert(p.seconds>=20 and p.seconds<=21.5 and p.sampleCount>=38)end;assert(nativeSession>0 and record.frontendClosedAt*1000<nativeSession and ticks<record.deadline-8)
 else assert(not ok and tostring(err):find(case[2],1,true),name..':'..tostring(err));unload()end
 assert(not loaded and stop4==1);results[#results+1]={name=name,passed=true,simulated=true,elapsedSeconds=ticks,renewals=record.renewals and #record.renewals or 0}
end
package.loaded.nixio=realNixio
print(j.stringify({passed=true,checks=results,targetLuaTimingModel=true,productionExecution=false,routerWrites=false}))
`;
const c=await connectRouter();try{
 const syntax=encode("/usr/bin/lua - <<'NSS99_GUARD_SYNTAX'\nassert(loadstring([====["+guard.replace('__PLAN__','{"syntaxOnly":true}').replace('__CORE_PHASE__','return{}').replace('__QOS_PHYSICAL__','return{}')+"]====]));print('GUARD_SYNTAX_PASS')\nNSS99_GUARD_SYNTAX\n"),check=receipt(await c.run(syntax.command),syntax);assert.equal(check.code,0,check.stderr);assert.equal(check.stdout.trim(),'GUARD_SYNTAX_PASS');
 const e=encode("/usr/bin/lua - <<'NSS99_TIMING_MODEL'\n"+body+"\nNSS99_TIMING_MODEL\n"),v=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/long-window-qualification-private.json',JSON.stringify(v,null,2)+'\n');assert.equal(v.code,0,v.stderr);const result=JSON.parse(v.stdout);assert.ok(result.passed&&result.checks.length===8);fs.writeFileSync(root+'/long-window-qualification.json',JSON.stringify({...result,sourceSha256:hash(Buffer.from(fast)),guardianSha256:hash(Buffer.from(guard)),nativeSourceSha256:hash(Buffer.from(native)),nativeMaximumSessionSeconds:30,requestedNativeSessionSeconds:27,classifierMaximumLeaseSeconds:6,ownedFlows:2,oneWan:true},null,2)+'\n');console.log(JSON.stringify({passed:true,checks:result.checks.length,phaseSeconds:20,nativeSessionSeconds:27,ownerSeconds:100,routerWrites:false}));
}finally{c.close()}
