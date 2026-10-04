import fs from 'node:fs';import assert from 'node:assert/strict';
assert.ok(!fs.existsSync('work/nss62'));fs.mkdirSync('work/nss62');
for(const n of ['real-session.mjs','current-audit-diagnostic.mjs','cleanup-audit.mjs','clock-anchor.mjs','wait-publication-metadata.mjs']){
 let s=fs.readFileSync('work/nss61/'+n,'utf8').replaceAll('nss61','nss62');
 if(n==='real-session.mjs')s=s.replace("from '../nss59/module-stage.mjs'","from './module-stage.mjs'");
 if(n==='wait-publication-metadata.mjs')s=s.replace("from './publication-hint.mjs'","from '../nss61/publication-hint.mjs'");
 fs.writeFileSync('work/nss62/'+n,s,{flag:'wx'});
}
let stage=fs.readFileSync('work/nss59/module-stage.mjs','utf8');
stage=stage.replace("from './payload.mjs'","from '../nss59/payload.mjs'").replace("'work/nss53/core-guard-phase.lua'","'work/nss62/core-guard-phase.lua'").replace("'work/nss53/phase-qualified.json'","'work/nss62/phase-qualified.json'");
fs.writeFileSync('work/nss62/module-stage.mjs',stage,{flag:'wx'});
let phase=fs.readFileSync('work/nss53/core-guard-phase.lua','utf8');
const old="   local argv={};for v in read('/proc/'..pid..'/cmdline',2048):gmatch('([^%z]+)')do argv[#argv+1]=v end\n   return{pid=pid,start=a[20],state=a[1],ppid=tonumber(a[2]),argv=argv,wchan=read('/proc/'..pid..'/wchan',256)}";
const replacement="   local cmd,wchan\n   if pid==expected.pid then\n    cmd=read('/proc/'..pid..'/cmdline',2048);wchan=read('/proc/'..pid..'/wchan',256)\n   else\n    -- A short-lived child may exit between proc files. Incomplete identity is\n    -- never a sleep witness; rediscover through the same bounded parent scan.\n    local okCmd,c=pcall(read,'/proc/'..pid..'/cmdline',2048);if not okCmd then return nil end\n    local okW,w=pcall(read,'/proc/'..pid..'/wchan',256);if not okW then return nil end\n    local okEnd,last=pcall(read,'/proc/'..pid..'/stat',8192);if not okEnd then return nil end\n    local z={};for v in assert(last:match('^%d+ %b() (.*)$')):gmatch('%S+')do z[#z+1]=v end\n    if z[20]~=a[20]or z[2]~=a[2]then return nil end\n    a=z;cmd=c;wchan=w\n   end\n   local argv={};for v in cmd:gmatch('([^%z]+)')do argv[#argv+1]=v end\n   return{pid=pid,start=a[20],state=a[1],ppid=tonumber(a[2]),argv=argv,wchan=wchan}";
assert.equal(phase.split(old).length,2);phase=phase.replace(old,()=>replacement);
assert.equal(phase.slice(phase.indexOf('function M.waitFresh')),fs.readFileSync('work/nss53/core-guard-phase.lua','utf8').slice(fs.readFileSync('work/nss53/core-guard-phase.lua','utf8').indexOf('function M.waitFresh')));
fs.writeFileSync('work/nss62/core-guard-phase.lua',phase,{flag:'wx'});
console.log('NSS62 process-read race candidate; guard reads and waitFresh unchanged');
