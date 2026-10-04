// Reconstruct and compile exact candidate bytes in RAM. Never execute its watch loop.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const ctx=JSON.parse(fs.readFileSync('work/nss47/deployment-latest.json'));
const proof=JSON.parse(fs.readFileSync('work/nss64/candidate-worker-manifest.json'));
const projector=fs.readFileSync('work/nss64/json-project-fast.lua','utf8'),encoder=fs.readFileSync('work/nss64/flow-json-stream.lua','utf8');
const code=String.raw`local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc')
local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or'';f:close();assert(#x<=l);return x end
local base=[===[${ctx.base}]===];assert(read('/root/router-project/game-classifier-generation',512)==base..' ${ctx.configHash}\n')
assert(not fs.lstat('/root/router-project/active-transaction'))
for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
local raw=read(base..'/worker.lua',65536);local project=[====[${projector}]====];local encoder=[====[${encoder}]====]
local prefix='local PublicationProject=(function()\n'..project..'\nend)()\nlocal PublicationStringify=(function()\n'..encoder..'\nend)()\n'
local function once(s,a,b)local x,y=assert(s:find(a,1,true));assert(not s:find(a,y+1,true));return s:sub(1,x-1)..b..s:sub(y+1)end
local marker='local function atomic(path,value)';local oldCall='local raw=assert(j.stringify(own.jsonProject(value)));assert(#raw<=4194304)'
local newCall="local raw=assert(type(value)=='table'and type(value.snapshot)=='table'and type(value.snapshot.flows)=='table'and PublicationStringify(value,j,PublicationProject)or j.stringify(own.jsonProject(value)));assert(#raw<=4194304)"
local candidate=once(once(raw,marker,prefix..marker),oldCall,newCall);assert(loadstring(candidate,'NSS64_UNINSTALLED_CANDIDATE'))
local ar,aw=assert(n.pipe());local br,bw=assert(n.pipe());local pid=assert(n.fork())
if pid==0 then aw:close();br:close();assert(n.dup(ar,n.stdin));assert(n.dup(bw,n.stdout));ar:close();bw:close();n.exec('/usr/bin/sha256sum');os.exit(127)end
ar:close();bw:close();local at=1;while at<=#candidate do local count=assert(aw:write(candidate:sub(at)));assert(count>0);at=at+count end;assert(aw:close())
local parts,bytes={},0;while true do local x=assert(br:read(512));if #x==0 then break end;bytes=bytes+#x;assert(bytes<=512);parts[#parts+1]=x end;assert(br:close())
local id,status,exit=n.waitpid(pid);assert(id==pid and status=='exited'and exit==0)
local digest=assert(table.concat(parts):match('^(%x+) '));assert(digest=='${proof.candidateWorkerSha256}')
print(j.stringify({passed=true,compiledExactCandidateInRam=true,sha256=digest,bytes=#candidate,executed=false,installed=false,
 configurationWrites=false,nssAdmissionAllowed=false,originalWorkerBytes=#raw,originalWorkerByteRestorationVerified=once(once(candidate,prefix..marker,marker),newCall,oldCall)==raw}))`;
const body="/usr/bin/lua - <<'NSS64_COMPILE'\n"+code+'\nNSS64_COMPILE\n';
const e=encode(ctx.base+'/group-runner 6 /bin/sh -c '+"'"+body.replaceAll("'","'\\''")+"'");
const c=await connectRouter();try{
 const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss64/compile-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
 assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.equal(result.sha256,proof.candidateWorkerSha256);
 result.observedAt=new Date().toISOString();fs.writeFileSync('work/nss64/compile-qualified.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}finally{c.close()}
