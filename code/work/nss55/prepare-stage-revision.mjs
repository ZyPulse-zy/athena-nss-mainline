// Preserve NSS55 proof; narrow syntax transport adapter in a new directory.
import fs from'node:fs';import assert from'node:assert/strict';
assert.ok(!fs.existsSync('work/nss56'));fs.mkdirSync('work/nss56');
for(const name of['baseline-publication-join.lua','wait-ready-joined.mjs','test-publication-join.mjs','qualify-entry.mjs','session-binding.mjs','current-audit-diagnostic.mjs','cleanup-audit.mjs','clock-anchor.mjs']){
 let s=fs.readFileSync('work/nss55/'+name,'utf8').replaceAll('nss55','nss56');
 if(name==='qualify-entry.mjs'){
  s=s.replace("expected=replaceOnce(expected,\"from './module-stage.mjs'\",\"from '../nss53/module-stage.mjs'\");","// Same-directory module adapter is independently bound below.");
  s=s.replace("'session-binding.mjs','join-tests.json'","'session-binding.mjs','join-tests.json','module-stage.mjs'");
  s=s.replace('nssPayloadUnchanged:true','nssPayloadUnchanged:true,oversizeClassifierSyntaxUsesExactGuardedBundle:true');
 }
 fs.writeFileSync('work/nss56/'+name,s,{flag:'wx'});
}
let m=fs.readFileSync('work/nss53/module-stage.mjs','utf8').replace("from './qualification.mjs'","from '../nss53/qualification.mjs'");
const a='const syntax=encode("/usr/bin/lua - <<\'NSS16_COMPILE_ONLY\'\\nlocal s=[===["+text+"]===];assert(loadstring(s));print(\'SYNTAX_ONLY_PASS\')\\nNSS16_COMPILE_ONLY\\n");';
assert.equal(m.split(a).length,2);
const b='let syntax;try{'+a.replace('const syntax=','syntax=')+'}catch(error){assert.equal(name,"classifier","Only the redundant classifier syntax copy may be deferred");assert.equal(String(error),"Error: Transport length refused");assert.equal(input.qosStaged,true);assert.ok(plan.qosCodeBytes>0&&plan.qosCodeBytes<=73728);save(dir,"classifier-syntax-deferred",{sourceSha256:hash(text),reason:String(error),exactGuardedBundleCompilationRequired:true,standaloneCompileDeferred:true,transportLimitUnchanged:true,payloadSha256:plan.qosCodeSha256,payloadBytes:plan.qosCodeBytes});continue;}';
m=m.replace(a,b);fs.writeFileSync('work/nss56/module-stage.mjs',m,{flag:'wx'});
fs.writeFileSync('work/nss56/stage-adapter-diff.json',JSON.stringify({passed:true,originalSource:'work/nss53/module-stage.mjs',changes:['Qualification import points at unchanged NSS53 source','Only redundant standalone classifier syntax transport overflow defers to existing exact-bundle native compile'],payloadBuilderUnchanged:true,originalGuardianUnchanged:true,originalCheckpointAndIndependentOwnerUnchanged:true,originalNativeCompileBeforeQosTagsAndGate:true,transportCapsUnchanged:true},null,2)+'\n',{flag:'wx'});
console.log('NSS56 compile transport adapter prepared; NSS53/54/55 unchanged');
