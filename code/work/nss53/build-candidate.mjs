// Preserve frozen NSS49/51/52 inputs. New round, diagnostics never grant permission.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss53',sha=s=>crypto.createHash('sha256').update(s).digest('hex');
function write(n,s){fs.writeFileSync(root+'/'+n,s,{flag:'wx'});}
function replace(t,a,b){assert.equal(t.split(a).length,2,a);return t.replace(a,()=>b);}
const diagnostic=fs.readFileSync(root+'/selection-diagnostic.lua','utf8');
const original=fs.readFileSync('work/nss49/classifier.lua','utf8');let adapter=original;
const edits=[];function edit(from,to){adapter=replace(adapter,from,to);edits.push({from,to});}
edit('local A={}\n','local describeSelection=(function()\n'+diagnostic+'\nend)()\nlocal A={}\n');
edit('  local ok,result=pcall(function()local s,c=readContext();local e=Consumer.pair(s,c,now(),P.selected);',
 '  local probeSnapshot,probeContext\n  local ok,result=pcall(function()local s,c=readContext();probeSnapshot=s;probeContext=c;local e=Consumer.pair(s,c,now(),P.selected);');
edit('  if ok then return result==true,nil,false end\n',
 `  if not ok and probeSnapshot then
   local diagnosed,detail=pcall(describeSelection,probeSnapshot,P.selected,done)
   record.lastAdmissionProbe.selected=diagnosed and detail or{diagnosticOnly=true,nssAdmissionAllowed=false,diagnosticError=tostring(detail)}
   if diagnosed and detail.admissionProjectionOnly and(not detail.slots.tcp.present or not detail.slots.udp.present)then
    -- Rejection is already final. Full-frame diagnostics never influence retry/permission.
    local matched,full=pcall(function()
     local x=assert(j.parse(stable(ram..'/snapshot.json',4194304)))
     for _,k in ipairs({'producer','generation','boot','configSha256','pid','start'})do assert(x[k]==probeSnapshot[k],'Complete diagnostic producer differs')end
     local a=assert(x.snapshot.provenance);local b=assert(probeSnapshot.snapshot.provenance)
     for _,k in ipairs({'sequence','startedAtUptime','finishedAtUptime','method','command','boot','rawStatus','exitCode','queryFamily','queryZone','authorizedClient'})do assert(a[k]==b[k],'Complete diagnostic source differs')end
     assert(not x.snapshot.admissionProjection,'Expected complete diagnostic input')
     Consumer.inspect(x,probeContext,now())
     local facts=describeSelection(x,P.selected,now());facts.sameSourceCompleteFrame=true;facts.afterRejectionOnly=true;return facts
    end)
    if matched then record.lastAdmissionProbe.completeSelected=full
    else record.lastAdmissionProbe.completeSelectionUnavailable=tostring(full)end
   end
  end
  if ok then return result==true,nil,false end
`);
let restored=adapter;for(const e of [...edits].reverse())restored=replace(restored,e.to,e.from);assert.equal(restored,original);
write('classifier.lua',adapter);
write('classifier-delta.json',JSON.stringify({originalSha256:sha(original),candidateSha256:sha(adapter),diagnosticSha256:sha(diagnostic),edits,embeddedConsumerByteIdentical:true,admissionDecisionAndRetryMessagesUnchanged:true,extraAdmissionSnapshotReads:0,maximumAfterRejectionDiagnosticSnapshotReads:1,completeDiagnosticRequiresIdenticalProducerAndQuery:true,diagnosticFailureCannotAuthorize:true,noRouterInstallation:true},null,2)+'\n');
const phase=fs.readFileSync('work/nss52/core-guard-phase.lua','utf8');if(!fs.existsSync(root+'/core-guard-phase.lua'))write('core-guard-phase.lua',phase);else assert.equal(fs.readFileSync(root+'/core-guard-phase.lua','utf8'),phase);
let audit=fs.readFileSync('work/nss51/current-audit-diagnostic.mjs','utf8');
audit=replace(audit,"import {verifyPreparation} from './session-binding.mjs';","import {verifyPreparation} from '../nss51/session-binding.mjs';");
audit=audit.replaceAll('work\\/nss51\\/','work\\/nss53\\/').replaceAll("'work/nss51'","'work/nss53'").replaceAll("'work/nss51/'","'work/nss53/'");write('current-audit-diagnostic.mjs',audit);
let closure=fs.readFileSync('work/nss50/cleanup-audit.mjs','utf8').replaceAll("'work/nss50/'","'work/nss53/'");write('cleanup-audit.mjs',closure);
write('candidate-summary.json',JSON.stringify({round:'NSS53',phaseSha256:sha(phase),phaseByteIdenticalToNss52:true,classifierSha256:sha(adapter),changedRuntimeDecisionPolicy:false,notInstalled:true,notProductionBound:true,highLoadQualified:false},null,2)+'\n');
console.log(JSON.stringify({created:true,embeddedConsumerByteIdentical:true,extraAdmissionSnapshotReads:0,maximumAfterRejectionDiagnosticSnapshotReads:1,notInstalled:true,notProductionBound:true}));
