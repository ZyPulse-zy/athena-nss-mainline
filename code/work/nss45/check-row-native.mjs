// Syntax and pure replay in target Lua RAM only. No service mutation or NSS permission.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from '../nss42/session-binding.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const root='work/nss45',mode=process.argv[2]??'syntax';assert.ok(['syntax','replay'].includes(mode));
const d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
let payload;const hashes={};const payloads=[];
if(mode==='syntax'){
 const policy=" if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end";
 const patches={
  'worker.lua':[[policy,policy+"\n if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end"],["return{rawStatus=0,stdout=streams[1].body,stderr=streams[2].body}","return{rawStatus=0,stdout=streams[1].body,stderr=streams[2].body,queryCleanupCompleted=true}"],["local detail={kind=snap.kind,stream=snap.stream,limit=snap.limit,reason=snap.reason,exitCode=snap.exitCode,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}","local detail={kind=snap.kind,stream=snap.stream,limit=snap.limit,observedRows=snap.observedRows,reason=snap.reason,exitCode=snap.exitCode,queryCleanupCompleted=true,attempts=overflowAttempts,baselineRecoveryComplete=overflowRecovered}"]],
  'guardian.lua':[[policy,policy+"\n if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end"]],
  'conntrack-source.lua':[["rawRows=rawRows+1;assert(rawRows<=o.maxSourceRows,'Source rows exceed bound')","rawRows=rawRows+1;if rawRows>o.maxSourceRows then error({kind='bounded-source-row-overflow',limit=o.maxSourceRows,observedRows=rawRows},0)end"],[" local rows,summary=M.normalize(o,p,answer.stdout,answer.stderr,boot,r.now())"," local normalized,rows,summary=pcall(M.normalize,o,p,answer.stdout,answer.stderr,boot,r.now())\n if not normalized then\n  -- Only the existing query implementation can attest successful child reaping.\n  if type(rows)=='table'and rows.kind=='bounded-source-row-overflow'and\n   rows.limit==o.maxSourceRows and rows.observedRows==o.maxSourceRows+1 and\n   answer.queryCleanupCompleted==true then rows.queryCleanupCompleted=true end\n  error(rows,0)\n end"]]
 };
 for(const name of Object.keys(patches)){
  const s=fs.readFileSync(root+'/'+name,'utf8');hashes[name]=sha(s);
  let code="local j=require('luci.jsonc');local f=assert(io.open('"+d.base+'/'+name+"'));local s=f:read(65537);f:close();assert(#s<=65536)\nlocal function replace(a,b)local x,y=s:find(a,1,true);assert(x and not s:find(a,y+1,true));s=s:sub(1,x-1)..b..s:sub(y+1)end\n";
  for(const [a,b]of patches[name]){assert.ok(!a.includes(']=======]')&&!b.includes(']=======]'));code+='replace([=======['+a+']=======],[=======['+b+']=======])\n'}
  code+="assert(loadstring(s));print(j.stringify({passed=true,checks=1,compiledSource=s}))";payloads.push({name,code});
 }
}else{
 const fixture=fs.readFileSync(root+'/row-replay.lua','utf8');hashes['row-replay.lua']=sha(fixture);payloads.push({name:'replay',code:fixture});
}
const capsules=payloads.map(({name,code})=>({name,e:encode(d.base+'/group-runner 6 /usr/bin/lua - <<\'NSS45_RAM_CHECK\'\n'+code+'\nNSS45_RAM_CHECK\n')}));
assert.ok(capsules.every(x=>x.e.execBytes<=9000));const c=await connectRouter();try{
 const h=await c.run('/usr/bin/sha256sum '+d.base+'/config.json '+d.base+'/group-runner');assert.equal(h.code,0);
 assert.equal(h.stdout.trim().split('\n')[0].split(/\s/)[0],d.configHash);assert.equal(h.stdout.trim().split('\n')[1].split(/\s/)[0],cfg.files['group-runner']);
 let checks=0;for(const {name,e}of capsules){const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/row-native-'+mode+'-'+name+'-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);if(mode==='syntax'){const out=JSON.parse(r.stdout);assert.equal(sha(out.compiledSource),hashes[name]);checks+=out.checks}else{checks+=r.stdout.split('\n').filter(s=>s.startsWith('PASS ')).length;assert.ok(r.stdout.includes('COMPLETE 48'))}}
 assert.equal(checks,mode==='syntax'?3:48);
 const out={passed:true,mode,checks,observedAt:new Date().toISOString(),sourceHashes:hashes,execBytes:Math.max(...capsules.map(x=>x.e.execBytes)),routerWrites:false,installed:false,realNativeLua:true,mockedNativeRecovery:mode==='replay',hardwareLifecycleQualified:false};
 fs.writeFileSync(root+'/row-native-'+mode+'-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
}finally{c.close()}
