import fs from'node:fs';import assert from'node:assert/strict';import crypto from'node:crypto';
const root='work/nss38',sha=s=>crypto.createHash('sha256').update(s).digest('hex');
let adapter=fs.readFileSync(root+'/candidate-classifier.lua','utf8');const adapterBaseSha=sha(adapter);
const replace=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b)};
adapter=replace(adapter,' local function readContext()',' local sourceDiagnostic\n local function readContext()');
adapter=replace(adapter,"  assert(s.publication=='before-software-baseline','Wrong classifier publication stage')",`  -- These scalar fields are diagnostic only. They never influence admission.
  local p=type(s)=='table'and type(s.snapshot)=='table'and s.snapshot.provenance
  if type(p)=='table'then
   sourceDiagnostic={}
   for _,k in ipairs({'sequence','startedAtUptime','finishedAtUptime'})do
    local v=p[k];if type(v)=='number'and v==v and math.abs(v)<1e16 then sourceDiagnostic[k]=v end
   end
   if type(s.atUptime)=='number'and s.atUptime==s.atUptime and math.abs(s.atUptime)<1e16 then sourceDiagnostic.publishedAtUptime=s.atUptime end
  end
  assert(s.publication=='before-software-baseline','Wrong classifier publication stage')`);
adapter=replace(adapter,' function out.ready()',' function out.ready()\n  sourceDiagnostic=nil;local began=now()');
adapter=replace(adapter,'  if ok then return result==true,nil,false end',`  local done=now();record.lastAdmissionProbe={startedAtUptime=began,checkedAtUptime=done,checkSeconds=done-began,diagnosticOnly=true,source=sourceDiagnostic}
  if sourceDiagnostic and sourceDiagnostic.startedAtUptime then record.lastAdmissionProbe.sourceAge=done-sourceDiagnostic.startedAtUptime end
  if ok then return result==true,nil,false end`);
let fast=fs.readFileSync(root+'/fast-path.lua','utf8');const fastBaseSha=sha(fast);
fast=replace(fast,'   stopped();phase.scan(fs,read,P.coreGuard)','   local iterationStarted=now();stopped();local phaseStarted=now();phase.scan(fs,read,P.coreGuard);local phaseDone=now()');
const append="   record.initialAlignment.probes[#record.initialAlignment.probes+1]={at,ready,reason or '',retryable==true}";
fast=replace(fast,append,append+`\n   -- Separate diagnostics preserve the historical four-field probe format.
   record.initialAlignment.diagnostics=record.initialAlignment.diagnostics or {}
   record.initialAlignment.diagnostics[#record.initialAlignment.diagnostics+1]={iterationSeconds=at-iterationStarted,phaseSeconds=phaseDone-phaseStarted,adapter=record.lastAdmissionProbe}
   record.lastAdmissionProbe=nil -- avoid repeated table references in native jsonc`);
fs.writeFileSync(root+'/candidate-traced-classifier.lua',adapter);fs.writeFileSync(root+'/candidate-traced-fast-path.lua',fast);
fs.writeFileSync(root+'/candidate-trace-manifest.json',JSON.stringify({adapterBaseSha256:adapterBaseSha,adapterSha256:sha(adapter),fastBaseSha256:fastBaseSha,fastSha256:sha(fast),diagnosticScalarsNeverAuthorize:true,historicalProbeFormatPreserved:true,routerWrites:false,operationalBindingUpdated:false},null,2)+'\n');
console.log(JSON.stringify({built:true,routerWrites:false,adapterSha256:sha(adapter),fastSha256:sha(fast)}));
