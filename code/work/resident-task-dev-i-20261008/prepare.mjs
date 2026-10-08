import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const generalOld='work/resident-general-dev-20261008',generalNew='work/resident-general-dev-i-20261008';
const normalOld='work/resident-normal-dev-h-20261008',normalNew='work/resident-normal-dev-i-20261008';
const serviceOld='work/resident-service-dev-h-20261008',serviceNew='work/resident-service-dev-i-20261008';
const replacements=[[generalOld,generalNew],[normalOld,normalNew],[serviceOld,serviceNew]];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const provenance=[];
for(const [from,to]of replacements){
 assert.ok(!fs.existsSync(to));fs.mkdirSync(to);
 for(const n of fs.readdirSync(from).filter(n=>/\.(mjs|py|ps1)$/.test(n))){
  const before=fs.readFileSync(from+'/'+n);let s=before.toString();for(const [a,b]of replacements){s=s.replaceAll(a,b).replaceAll(a.slice(5),b.slice(5));}
  fs.writeFileSync(to+'/'+n,s,{flag:'wx'});provenance.push({origin:from+'/'+n,originSha256:sha(before),destination:to+'/'+n,namespaceOnly:true});
 }
}
fs.mkdirSync(generalNew+'/endpoint-gate');
for(const n of fs.readdirSync(generalOld+'/endpoint-gate').filter(n=>/\.(c|h|py)$/.test(n)||n==='Makefile'||n==='build-manifest.json'||n==='rp_ecm_gate_lab_ct.runtime.ko')){
 const bytes=fs.readFileSync(generalOld+'/endpoint-gate/'+n);fs.writeFileSync(generalNew+'/endpoint-gate/'+n,bytes,{flag:'wx'});
 provenance.push({origin:generalOld+'/endpoint-gate/'+n,originSha256:sha(bytes),destination:generalNew+'/endpoint-gate/'+n,byteExact:true});
}
for(const n of ['native-source-qualified.json','runtime-elf-comparison.json'])fs.writeFileSync(generalNew+'/'+n,fs.readFileSync(generalOld+'/'+n),{flag:'wx'});
const file=generalNew+'/adapt-runtime.mjs';let s=fs.readFileSync(file,'utf8');
const before="if(n==='module-stage-guardian.lua')s=\"local function NS(t)local a={}for s,k in pairs{tcp='tcp',game='udp',tcp2='tcp2'}do if t[k]then a[#a+1]=s end end;return a end;\\n\"+s;";
assert.equal(s.split(before).length,2);
s=s.replace(before,()=>`if(n==='module-stage-guardian.lua'){
   const elf=JSON.parse(fs.readFileSync(root+'/runtime-elf-comparison.json','utf8')),bytes=fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko');
   assert.equal(elf.passed,true);assert.equal(hash(bytes),elf.runtimeSha256);
   assert.ok(bytes.length>0&&bytes.length<65536);
   s=once(s,"assert(P.moduleBytes==44616 and P.moduleSha256=='d53f5cc076f38edabbbd576b19a2fb1befed3e1acc1cb4ae7703c0e0efab12a2')","assert(P.moduleBytes=="+bytes.length+" and P.moduleSha256=='"+hash(bytes)+"','Qualified native module identity changed')");
   s="local function NS(t)local a={}for _,k in ipairs({'tcp','udp','tcp2'})do if t[k]then a[#a+1]=k=='udp'and'game'or k end end;assert(#a>0 and #a<=3);return a end;\\n"+s;
  }`);
fs.writeFileSync(file,s);
const qFile=generalNew+'/qualification.mjs';s=fs.readFileSync(qFile,'utf8');
s=s.replace("const subset=JSON.parse(fs.readFileSync(root+'/subset-model-latest.json'));", "const gp=spawnSync(process.execPath,[root+'/test-guardian-preflight.mjs'],{encoding:'utf8',windowsHide:true,timeout:120000});fs.writeFileSync(dir+'/guardian-preflight-raw.json',JSON.stringify({code:gp.status,stdout:gp.stdout,stderr:gp.stderr})+'\\n',{flag:'wx'});assert.equal(gp.status,0,gp.stderr);const guardian=JSON.parse(gp.stdout.trim());\n const subset=JSON.parse(fs.readFileSync(root+'/subset-model-latest.json'));");
s=s.replace('checks:subset.checks,syntaxSources:syntax','checks:subset.checks+guardian.checks,guardianPreflight:guardian,syntaxSources:syntax');fs.writeFileSync(qFile,s);
const output='work/resident-task-dev-i-20261008/clone-provenance-private.json';fs.writeFileSync(output,JSON.stringify({passed:true,provenance,nativeSourceAndBinaryUnchanged:true,onlyNativeGuardianBindingAndLocalRegressionChanged:true},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,namespaceSources:provenance.length,nativeSourceAndBinaryByteExact:true,oldCandidatePreserved:true}));
