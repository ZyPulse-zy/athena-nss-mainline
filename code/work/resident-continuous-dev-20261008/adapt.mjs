import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {materializeNormal} from '../resident-normal-dev-i-20261008/materialize-normal.mjs';

export const root='work/resident-continuous-dev-20261008';
export const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function once(s,a,b){assert.equal(s.split(a).length,2,'Continuous patch anchor: '+a);return s.replace(a,()=>b);}
export const pulseLibrary=`function M.control(P,DIR,read,now,dcheck,fcheck,files,R,store,extend)
 local lastStore,lastControl=0,0
 return function(persist)
  dcheck();local a=fcheck('control');assert(a.dev==files.control.dev and a.ino==files.control.ino and a.size==128)
  local owner,t,action=read(DIR..'/control',128):match('^(%x+) ([%d.]+) ([CS]) ');t=tonumber(t)
  assert(owner==P.owner and t and t>=lastControl and t<=now()and now()-t<30,'Resident control heartbeat lost');lastControl=t
  R.controlHeartbeat=t;if action=='S'then R.operatorStop=true;return false end
  R.deadline=now()+180;extend(R.deadline);R.fixedOwnerDeadlineRemoved=true
  if persist and now()-lastStore>=2 then store();lastStore=now()end;return true
 end
end
`;

export function patchFast(s){
 s=once(s,",cpu=read('/proc/stat',16384),softnet=read('/proc/net/softnet_stat',16384),interfaces={}","");
 const telemetry="  for _,d in ipairs({'rpwan1','rpwan2','rpwan3','rpwan4','rpwan5','wan','lan4'})do r.interfaces[d]={};for _,k in ipairs({'rx_bytes','rx_packets','tx_bytes','tx_packets','rx_dropped','tx_dropped'})do r.interfaces[d][k]=tonumber(read('/sys/class/net/'..d..'/statistics/'..k,128))end end\n";
 s=once(s,telemetry,'');
 s=once(s,'function M.verifyRenewalAck(k,p,N,selected)','function M.verifyRenewalAck(k,p,N,selected,continuous)');
 s=once(s,"tonumber(sessionMs)==N,'Renewal mismatch'","(continuous and tonumber(sessionMs)>=N and tonumber(sessionMs)-p.untilMs<=120000 or not continuous and tonumber(sessionMs)==N),'Renewal mismatch'");
 s=once(s,'classifierUntilMs=tonumber(untilMs)}','classifierUntilMs=tonumber(untilMs),sessionUntilMs=tonumber(sessionMs)}');
 s=once(s,"assert(p.untilMs<=N,'ABA cannot complete within fixed session')","assert(now()*1000<N,'Cannot renew an expired session')");
 s=once(s,'M.verifyRenewalAck(k,p,N,P.selected);A.acceptRenewal(p,ack)',
  'M.verifyRenewalAck(k,p,N,P.selected,true);A.acceptRenewal(p,ack);N=ack.sessionUntilMs;R.hardSessionUntilMs=N');
 s=once(s,"R.renewals[#R.renewals+1]={atUptime=now(),previousSequence=p.expectedSequence,sequence=ack.sequence,untilMs=ack.classifierUntilMs}",
  "R.totalRenewals=(R.totalRenewals or 0)+1;R.renewals[#R.renewals+1]={atUptime=now(),previousSequence=p.expectedSequence,sequence=ack.sequence,untilMs=ack.classifierUntilMs,sessionUntilMs=N};if #R.renewals>16 then table.remove(R.renewals,1)end");
 s=once(s,"local O=observe();local s=S();s.phase=name;s.observation=O",
  "local keep=P.residentPulse(false);local O=keep and observe()or{terminalReason='RESIDENT_OPERATOR_STOP'};local s=S();s.phase=name;s.observation=O");
 s=once(s,'R.samples[#R.samples+1]=s;return s',
  'R.totalSamples=(R.totalSamples or 0)+1;R.samples[#R.samples+1]=s;if #R.samples>32 then table.remove(R.samples,1)end;P.residentPulse(true);return s');
 const from=s.indexOf(' local function measure()'),to=s.indexOf(' function out.align(deadline)',from);
 assert.ok(to>from);
 s=s.slice(0,from)+` local function measure()
  local p={name='B',cadenceSeconds=0.5,observer='continuous-qualified-renewal',sampleStart=(R.totalSamples or 0)+1,continuous=true}
  R.phases[#R.phases+1]=p;local nextAt
  repeat
   local sample=tick('B');if not sample then break end
   if not p.startedAt then p.startedAt=sample.uptime;nextAt=sample.uptime end
   p.endedAt=sample.uptime;p.seconds=p.endedAt-p.startedAt;p.sampleEnd=R.totalSamples;p.sampleCount=p.sampleEnd-p.sampleStart+1
   nextAt=nextAt+0.5;pause(math.max(0,nextAt-now()))
  until false
  p.completed=true;p.endedAt=now();p.seconds=p.startedAt and p.endedAt-p.startedAt or 0;p.sampleEnd=R.totalSamples or 0;p.sampleCount=math.max(0,p.sampleEnd-p.sampleStart+1)
  R.continuousEpochEndedSafely=true;R.continuousNssRunning=false
 end
`+s.slice(to);
 s=once(s,' session_until_ms=\'..N..\' classifier_sequence='," session_until_ms='..N..' continuous_residency=Y classifier_sequence=");
 s=once(s,"R.acceleratedState=state();R.qosAccelerated=qos.snapshot();measure()",
  "R.acceleratedState=state();R.qosAccelerated=qos.snapshot();R.continuousNssRunning=true;R.fixedSessionDeadlineRemoved=true;measure()");
 s=once(s,'R.fastPathEpochCompleted=false;R.abaCompleted=false;R.automaticLifecycleEpochCompleted=false',
  'R.fastPathEpochCompleted=true;R.abaCompleted=false;R.automaticLifecycleEpochCompleted=true');
 s=once(s,'R.fastPathMeasurement={qualified=false,terminalLifecycleOnly=true,performanceComparison=false}',
  'R.fastPathMeasurement={qualified=R.phases[1].sampleCount>0,continuousLifecycle=true,stableSeconds=R.phases[1].seconds,performanceComparison=false}');
 const tail=s.indexOf("  assert(#R.renewals>0,'B lacked a confirmed classifier renewal')");assert.ok(tail>0);
 s=s.slice(0,tail)+"  error('Continuous epoch must end through scoped retirement')\n end\n return out\nend\nreturn M\n";
 s=once(s,'function M.new(',pulseLibrary+'function M.new(');
 return s;
}

export function patchGuardian(s,module){
 s=once(s,"assert(P.moduleBytes==45848 and P.moduleSha256=='49ad75f4cd30f1ae50d4a6e9a62993bc52e923b13efd8575554a8a9f48afc0be')",
  "assert(P.moduleBytes=="+module.length+" and P.moduleSha256=='"+hash(module)+"')");
 s=once(s,"files.owner=fcheck('owner');put(DIR..'/candidate.ko','');",
  "files.owner=fcheck('owner');local msg=P.owner..' '..now()..' C ';put(DIR..'/control',msg..string.rep(' ',127-#msg)..'\\n');files.control=fcheck('control');put(DIR..'/candidate.ko','');");
 s=once(s,'qosFileIdentity=ownCode,rollbackBeforeFirstWrite=true}',
  'qosFileIdentity=ownCode,controlFileIdentity=files.control,rollbackBeforeFirstWrite=true}');
 s=once(s,'  local fast=fastLibrary.new(',"  P.residentPulse=fastLibrary.control(P,DIR,read,now,dcheck,fcheck,files,record,store,function(t)deadline=t end)\n  local fast=fastLibrary.new(");
 s=once(s,'if not ok then record.error=tostring(err);',
  'if not ok then deadline=now()+8;record.deadline=deadline;record.error=tostring(err);');
 const from=s.indexOf(' local function parameters()'),to=s.indexOf(' local function undoModule()',from);assert.ok(to>from);
 s=s.slice(0,from)+` local function parameters()
  local o={};local function get(k)o[k]=read('/sys/module/'..MOD..'/parameters/'..k,8192):gsub('%s+$','')end
  for _,k in ipairs{'registered','diagnostic_only','denied','last_decoded_info','frozen_record_sha256','classifier_until_ms','session_until_ms','classifier_sequence','epoch_refresh','renewed_epochs','cpu_barriers','revoke_calls','revoke_found'}do get(k)end
  for _,slot in ipairs{'tcp','game','tcp2'}do for _,fmt in ipairs{'eligible_%s','allowed_%s','%s_state','%s_pinned_state','%s_permit','expiry_%s'}do get(fmt:format(slot))end end;return o
 end
`+s.slice(to);
 // Local identifier shortening only, preserving quoted strings and JSON fields.
 const names={record:'R',ownDir:'od',ownFile:'of',ownCode:'oc',stateNode:'sn',parameters:'params',dcheck:'dc',fcheck:'fc',countPaths:'cp',command:'cmd',undoModule:'undo',qosLibrary:'ql',tagLibrary:'tl',classifierLibrary:'cl',normalizerLibrary:'nl',fastLibrary:'fl',wanLibrary:'wl',stateLibrary:'sl'};
 s=s.replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|\b(?:record|ownDir|ownFile|ownCode|stateNode|parameters|dcheck|fcheck|countPaths|command|undoModule|qosLibrary|tagLibrary|classifierLibrary|normalizerLibrary|fastLibrary|wanLibrary|stateLibrary)\b/g,t=>names[t]??t);
 return s;
}

export function patchStage(s){
 s=s.replaceAll('work/resident-general-dev-i-20261008/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko',root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko')
  .replaceAll('work/resident-general-dev-i-20261008/runtime-elf-comparison.json',root+'/runtime-elf-comparison.json');
 const a="local q=read('${dir}/state.json',1048576);o.record=assert(j.parse(q))end;print(j.stringify(o))";
 const b="local q=read('${dir}/state.json',1048576);o.record=assert(j.parse(q));if o.identity and o.identity.start=='${ctx.receipt.ready.stat.start}'and o.identity.pgrp==${pid} and o.identity.session==${pid} and o.identity.state~='Z'then local f=assert(n.open('${dir}/control','r+'));local st=assert(f:stat());assert(st.dev==${ctx.receipt.controlFileIdentity.dev} and st.ino==${ctx.receipt.controlFileIdentity.ino} and st.type=='reg'and st.uid==0 and st.gid==0 and st.modedec==600 and st.nlink==1 and st.size==128);assert(f:seek(0,'set')==0);local message='${ctx.plan.owner} '..o.uptime..' ${ctx.stopRequested?'S':'C'} ';message=message..string.rep(' ',127-#message)..'\\n';assert(f:write(message)==128);assert(f:close());o.residentControlUpdated=true end end;print(j.stringify(o))";
 s=once(s,a,b);return once(s,'export async function waitStageUndo(ctx){','export async function waitStageUndo(ctx){ctx.stopRequested=true;');
}

export function patchDriver(s,runtime){
 s=once(s,'for(let i=0;i<115;i++){const s=await readStage(c,context);',
  "for(let i=0;;i++){context.stopRequested=fs.existsSync(observationRoot+'/stop-request.json');const s=await readStage(c,context);");
 s=once(s,"assert.ok(p.completed&&p.seconds>=90&&p.seconds<=91.5&&p.sampleCount>=178);for(const t of latest.samples.slice(p.sampleStart-1,p.sampleEnd))",
  "assert.ok(p.completed&&p.continuous&&p.seconds>=0&&p.sampleCount>0);for(const t of latest.samples.filter(t=>t.phase===p.name))");
 s=once(s,"assert.equal(latest.error,undefined,latest.error);",
  "assert.equal(latest.error,undefined,latest.error);assert.equal(latest.continuousEpochEndedSafely,true);assert.equal(latest.fixedSessionDeadlineRemoved,true);assert.equal(latest.fixedOwnerDeadlineRemoved,true);");
 return s;
}

export function materializeContinuous(runtime,cutoff=Date.now()+600000){
 const q=materializeNormal(runtime,cutoff);
 const build=JSON.parse(fs.readFileSync(root+'/endpoint-gate/build-manifest.json'));
 const elf=JSON.parse(fs.readFileSync(root+'/runtime-elf-comparison.json'));
 const module=fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko');
 assert.equal(build.status,'built-classifier-epoch-offline; no runtime qualification');assert.equal(build.sdk_original_unchanged,true);
 assert.equal(elf.passed,true);assert.equal(hash(module),elf.runtimeSha256);assert.equal(hash(fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.c')),build.source_hashes['rp_ecm_gate_lab_ct.c']);
 for(const [name,patch] of Object.entries({'fast-path.lua':patchFast,'module-stage-guardian.lua':s=>patchGuardian(s,module),'module-stage.mjs':patchStage,'epoch-driver.mjs':s=>patchDriver(s,runtime)})){
  const file=runtime+'/'+name,s=patch(fs.readFileSync(file,'utf8'));fs.writeFileSync(file,s);q.sourceManifest[file]=hash(Buffer.from(s));
 }
 for(const name of ['adapt.mjs','policy.mjs','normal-entry.mjs','run-generation.mjs','qualification.mjs','endpoint-gate/rp_ecm_gate_lab_ct.c','endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko','endpoint-gate/build-manifest.json','runtime-elf-comparison.json'])q.sourceManifest[root+'/'+name]=hash(fs.readFileSync(root+'/'+name));
 q.continuousQualifiedResidency=true;q.fixedSessionLimitSeconds=null;q.fixedOwnerLimitSeconds=null;
 q.qualifiedRenewalRequired=true;q.controlHeartbeatSeconds=30;q.newNativeRollingSession=true;
 fs.writeFileSync(runtime+'/entry-qualified.json',JSON.stringify(q,null,2)+'\n');return q;
}
