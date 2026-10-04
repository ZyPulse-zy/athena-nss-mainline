// One runtime variable: discover only fully validated children of the pinned guard.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function write(n,s){const p='work/nss51/'+n;assert.ok(!fs.existsSync(p),p);fs.writeFileSync(p,s,{flag:'wx'});}
const original=fs.readFileSync('work/nss49/core-guard-phase.lua','utf8');
const from="  local s=M.scan(fs,read);assert(s.guard.pid==expected.pid and s.guard.start==expected.start)\n  s.scopedIdentityRead=true;s.refreshInventory=true;return s";
const to=`  -- The guard was fully validated above. Inspect process stat for ancestry;
  -- read argv/wchan only for its direct children, then revalidate each match.
  local sleepers={};local total=0
  for pid in fs.dir('/proc')do if pid:match('^%d+$')then
   total=total+1;assert(total<=4096,'Process inventory bound')
   local ok,raw=pcall(read,'/proc/'..pid..'/stat',8192)
   if ok then local a={};for v in assert(raw:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end
    if tonumber(a[2])==g.pid then
     local p=proc(tonumber(pid))
     if p and p.ppid==g.pid and #p.argv==2 and(p.argv[1]=='sleep'or p.argv[1]=='/bin/sleep')and p.argv[2]=='5'and p.state=='S'and p.wchan=='hrtimer_nanosleep'then sleepers[#sleepers+1]=p end
    end
   end
  end end
  assert(#sleepers<=1,'Multiple core sleep children')
  local final=assert(proc(expected.pid),'Core guard absent')
  assert(final.start==g.start and final.state~='Z'and #final.argv==3 and final.argv[1]=='/bin/sh'and final.argv[2]=='/root/router-project/scripts/core-guard.sh'and final.argv[3]=='watch','Core guard identity changed')
  local p=sleepers[1];remembered=p and{guardPid=g.pid,guardStart=g.start,pid=p.pid,start=p.start}or nil
  return{guard=final,sleep=p,clockTicks=M.clockTicks(read),scopedIdentityRead=true,refreshInventory=true,parentScopedInventory=true,inventoryProcesses=total}`;
assert.equal(original.split(from).length,2);const candidate=original.replace(from,()=>to);write('core-guard-phase.lua',candidate);
write('phase-delta.json',JSON.stringify({originalSha256:hash(Buffer.from(original)),candidateSha256:hash(Buffer.from(candidate)),from,to,waitFreshByteIdentical:true,unscopedDiscoveryByteIdentical:true,sourceAndOwnerDeadlinesUnchanged:true,candidateNotYetAuthorized:true},null,2)+'\n');
console.log(JSON.stringify({created:true,waitFreshByteIdentical:true,candidateNotYetAuthorized:true}));
