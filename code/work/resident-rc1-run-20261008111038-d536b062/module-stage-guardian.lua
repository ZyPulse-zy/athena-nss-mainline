local function NS(t)local a={}for _,s in ipairs{'tcp','game','tcp2'}do if t[s=='game'and'udp'or s]then a[#a+1]=s end end;return a end;
-- Only the detached child creates/removes its private directory. Sender uses existing FD only.
local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local P=assert(j.parse([=[__PLAN__]=]))
local phase=assert(loadstring([=[__CORE_PHASE__]=]))()
local ql=assert(loadstring([=[__QOS_PHYSICAL__]=]))();local tl,cl,nl,fl,wl,sl
assert(P.owner:match('^[a-f0-9]+$')and #P.owner==32 and P.mode=='stage'and type(P.openFrontend)=='boolean')
assert(P.moduleBytes==46280 and P.moduleSha256=='79566ffd7f24ca3be3a4e39a1b7a4d0e1193f7419f26db127b2dd4e077bc4091')
assert(not P.qosDevice or P.qosStaged);if P.qosStaged then assert(P.qosCodeBytes>0 and P.qosCodeBytes<=73728 and P.qosCodeSha256:match('^[a-f0-9]+$')and #P.qosCodeSha256==64)end
assert(P.qosStaged and P.selected==nil,'Selection must be SHA-pinned in bundle')
local DIR='/tmp/rp-nss25-stage-'..P.owner;local MOD='rp_ecm_gate_lab_ct';local boot
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 262144)+1)or'';f:close();assert(#s<=(l or 262144));return s end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local function stat(pid)if not fs.lstat('/proc/'..pid..'/stat')then return nil end;local a={};for v in assert(read('/proc/'..pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;return{pid=pid,start=a[20],state=a[1],ppid=tonumber(a[2]),pgrp=tonumber(a[3]),session=tonumber(a[4])}end
local function fd(f)return assert(tonumber(tostring(f):match('(%d+)$')))end
local function link(pid,f)return assert(fs.readlink('/proc/'..pid..'/fd/'..f))end
local function send(f,s,due)local p=1;while p<=#s and now()<due do local v={{fd=f,events=n.poll_flags('out','err','hup')}};local k,e=n.poll(v,40);if type(k)=='number'and k>0 then local z=n.poll_flags(v[1].revents);if z.err or z.hup or z.nval then return false end;if z.out then local q=f:write(s:sub(p,p+255));if not q or q==0 then return false end;p=p+q end elseif k==nil and e~=4 then return false end end;return p>#s end
local function line(f,due)local a={};while now()<due do local v={{fd=f,events=n.poll_flags('in','hup','err')}};local k,e=n.poll(v,40);if type(k)=='number'and k>0 then local z=n.poll_flags(v[1].revents);if z['in']then local s=f:read(1);if not s or s==''then return nil end;if s=='\n' then return table.concat(a)end;a[#a+1]=s;assert(#a<12000)elseif z.hup or z.err or z.nval then return nil end elseif k==nil and e~=4 then return nil end end;return nil end
local cp={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
local function zero()for _,p in ipairs(cp)do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0,'ECM count nonzero: '..p)end end
local function stopped()for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==1)end;zero()end
local function absent(p)local q,a,b=fs.lstat(p);assert(not q and(a==2 or b==2),'Unknown/existing path')end
local function cmd(c)local f=assert(io.popen('/usr/bin/timeout -k 1 3 '..c..' 2>&1; rc=$?;printf "\\n__NSS16_STAGE_RC__%s\\n" "$rc"'));local s=f:read(131072);f:close();local body,rc=s:match('^(.*)\n__NSS16_STAGE_RC__(%d+)\n$');assert(body and rc=='0',body or'Command receipt missing');return body end
boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','');assert(boot==P.boot);stopped();absent(DIR);absent('/sys/module/'..MOD)
local deadline=now()+180;local rr,rw=assert(n.pipe());local gr,gw=assert(n.pipe());local pid=assert(n.fork())
if pid==0 then
 rr:close();gw:close();assert(n.setsid());assert(n.signal(13,'ign'));assert(n.signal(1,'ign'));n.umask(77);local null=assert(n.open('/dev/null','r+'));assert(n.dup(null,n.stdin));assert(n.dup(null,n.stdout));assert(n.dup(null,n.stderr));null:close()
 local me=n.getpid();local ready={pid=me,stat=stat(me),boot=boot,deadline=deadline,dir=DIR,owner=P.owner,goFd=fd(gr),resultFd=fd(rw)};assert(send(rw,j.stringify(ready)..'\n',now()+3));local go=line(gr,now()+3);gr:close();if go~='G'then rw:close();os.exit(2)end
 local od,of,oc;local loaded=false;local qos;local tag;local wan;local state;local files={};local sn;local R={version=1,owner=P.owner,boot=boot,deadline=deadline,mode=P.mode,stageComplete=false,moduleLoaded=false,gateComplete=false,newNssPermit=false,priorityOrQueueWrites=not not P.qosDevice,qosDevice=P.qosDevice}
 local function dc()local a=assert(fs.lstat(DIR));assert(a.type=='dir'and a.uid==0 and a.gid==0 and a.modedec==700 and a.dev==od.dev and a.ino==od.ino);return a end
 local function fc(name,mode)local a=assert(fs.lstat(DIR..'/'..name));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1 and a.modedec==(mode or 600));return a end
 local function store()dc();assert(now()<deadline-1);local tmp=DIR..'/state.json.new';absent(tmp);files['state.json.new']=true;local f=assert(io.open(tmp,'w'));assert(f:write(j.stringify(R)..'\n'));assert(f:close());fc('state.json.new');assert(os.rename(tmp,DIR..'/state.json'));files['state.json.new']=nil;files['state.json']=fc('state.json')end
 local function put(p,v)local f=assert(io.open(p,'w'));assert(f:write(v));assert(f:close())end
 local function params()
  local o={};local function get(k)o[k]=read('/sys/module/'..MOD..'/parameters/'..k,8192):gsub('%s+$','')end
  for _,k in ipairs{'registered','diagnostic_only','denied','last_decoded_info','frozen_record_sha256','classifier_until_ms','session_until_ms','classifier_sequence','epoch_refresh','renewed_epochs','cpu_barriers','revoke_calls','revoke_found'}do get(k)end
  for _,slot in ipairs{'tcp','game','tcp2'}do for _,fmt in ipairs{'eligible_%s','allowed_%s','%s_state','%s_pinned_state','%s_permit','expiry_%s'}do get(fmt:format(slot))end end;return o
 end
 local function undo()
  if not loaded then return end;put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');put('/sys/kernel/debug/ecm/front_end_ipv6_stop','1\n');assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop'))==1)
  if not fs.lstat('/sys/module/'..MOD)then loaded=false;stopped();return end
  assert(read('/sys/module/'..MOD..'/parameters/frozen_record_sha256',256):gsub('%s+$','')==P.frozenHash,'Module ownership changed')
  for _,slot in ipairs(NS(P.selected))do put('/sys/module/'..MOD..'/parameters/'..slot..'_close','Y\n');put('/sys/module/'..MOD..'/parameters/'..slot..'_drain','Y\n')end
  local passed=false;for z=1,50 do passed=pcall(zero);if passed then break end;n.nanosleep(0,100000000)end;assert(passed,'Scoped firmware drain failed');R.parametersBeforeUnload=params();cmd('/sbin/rmmod '..MOD);loaded=false;absent('/sys/module/'..MOD);stopped();R.moduleUnloaded=true
 end
 local function cleanup()
  undo();if tag then tag.cleanup()end;if qos then qos.cleanup()end;if wan then wan.cleanup()end;if state then state.cleanup()end;if not od then return end;dc();for name in fs.dir(DIR)do assert(files[name],'Foreign private file');local pinned=name=='candidate.ko'and of or name=='qos.lua'and oc;local a;if name=='ecm-state'then a=assert(fs.lstat(DIR..'/'..name));assert(sn and a.type=='chr'and a.uid==0 and a.gid==0 and a.modedec==600 and a.dev==sn.dev and a.ino==sn.ino and a.rdev==sn.rdev)else a=fc(name,pinned and pinned.modedec or 600)end;if pinned then assert(a.dev==pinned.dev and a.ino==pinned.ino)end;assert(fs.unlink(DIR..'/'..name))end;dc();assert(fs.rmdir(DIR));absent(DIR)
 end
 local ok,err=xpcall(function()
  stopped();assert(now()<deadline-12);absent(DIR);assert(fs.mkdir(DIR,700));od=assert(fs.lstat(DIR));dc();put(DIR..'/owner',P.owner..' '..boot..' '..deadline..'\n');files.owner=fc('owner');local msg=P.owner..' '..now()..' C ';put(DIR..'/control',msg..string.rep(' ',127-#msg)..'\n');files.control=fc('control');put(DIR..'/candidate.ko','');of=fc('candidate.ko');files['candidate.ko']=of;R.moduleFileIdentity=of;if P.qosStaged then put(DIR..'/qos.lua','');oc=fc('qos.lua');files['qos.lua']=oc;R.qosFileIdentity=oc end;store()
  assert(send(rw,j.stringify({success=true,ready=ready,moduleFileIdentity=of,qosFileIdentity=oc,controlFileIdentity=files.control,rollbackBeforeFirstWrite=true})..'\n',now()+2));rw:close();rw=nil
  local stageDue=math.min(deadline-12,now()+12)
  while now()<stageDue do local a=fc('candidate.ko');assert(a.dev==of.dev and a.ino==of.ino and a.size<=P.moduleBytes);if a.size==P.moduleBytes then local digest=assert(cmd('/usr/bin/sha256sum '..DIR..'/candidate.ko'):match('^(%x+) '));assert(digest==P.moduleSha256);R.stageComplete=true;R.stageSha256=digest;R.stageAtUptime=now();store();break end;n.nanosleep(0,50000000);stopped()end
  assert(R.stageComplete,'Module staging deadline');assert(fs.chmod(DIR..'/candidate.ko',400));of=fc('candidate.ko',400)
  if P.qosStaged then
   while now()<stageDue do local a=fc('qos.lua');assert(a.dev==oc.dev and a.ino==oc.ino and a.size<=P.qosCodeBytes);if a.size==P.qosCodeBytes then local digest=assert(cmd('/usr/bin/sha256sum '..DIR..'/qos.lua'):match('^(%x+) '));assert(digest==P.qosCodeSha256,'QoS helper bytes changed');assert(fs.chmod(DIR..'/qos.lua',400));oc=fc('qos.lua',400);local text=read(DIR..'/qos.lua',73728);assert(#text==P.qosCodeBytes);local after=fc('qos.lua',400);assert(after.dev==oc.dev and after.ino==oc.ino and after.size==oc.size);local bundle=assert(loadstring(text))();ql=assert(bundle.qos);phase=assert(bundle.phase);tl=assert(bundle.tags);cl=assert(bundle.classifier);nl=assert(bundle.normalizer);fl=assert(bundle.fast);wl=assert(bundle.wan);sl=assert(bundle.state);P.tagPlan=assert(bundle.tagPlan);assert(P.selected==nil);P.selected=assert(bundle.selected);R.selectionFromPinnedBundle=true;R.qosCodeLoaded=true;R.qosCodeSha256=digest;store();break end;n.nanosleep(0,50000000);stopped()end
   assert(R.qosCodeLoaded,'QoS helper staging deadline')
  end
  state=sl.new(P,fs,read,now,stopped,cmd,R);state.setup();store()
  wan=wl.new(P,fs,j,read,now,stopped,put,cmd,R);wan.setup();store()
  local function load(args)
   stopped();assert(not loaded and not fs.lstat('/sys/module/'..MOD));assert(cmd('/usr/bin/sha256sum /lib/modules/6.18.44/ecm.ko'):match('^(%x+) ')==P.ecmSha256);assert(cmd('/bin/ls -A /sys/module/ecm/holders'):gsub('%s+$','')=='');loaded=true;cmd('/sbin/insmod '..DIR..'/candidate.ko '..args);R.moduleLoaded=true;assert(params().frozen_record_sha256==P.frozenHash)
  end
  P.residentPulse=fl.control(P,DIR,read,now,dc,fc,files,R,store,function(t)deadline=t end)
  local fast=fl.new(P,fs,j,read,now,stopped,put,cmd,R,params,load,undo,DIR,phase,cl)
  if P.qosDevice then qos=ql.new(P,fs,j,cmd,now,stopped,R);qos.setup(deadline);store();if P.mode=='stage'then
   assert(P.autoClassified and P.qosDevice=='lan4')
   tag=tl.new(P,fs,j,read,now,stopped,cmd,R,cl,qos,nl,fast);tag.run(deadline);wan.check();qos.cleanup();wan.cleanup();state.cleanup();store()
  end end
  local ending=deadline-1
  if R.abaCompleted or R.automaticLifecycleEpochCompleted or R.classChangeTestCompleted or R.freshEpochRelearningCompleted or R.flowEligibilityExitCompleted then
   for _,key in ipairs({'moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'})do assert(R[key]==true,'Success teardown incomplete: '..key)end
   stopped();absent('/sys/module/'..MOD);absent('/sys/module/qca_nss_qdisc')
   R.successEarlyCompletion=true;R.successRecordGraceSeconds=5;store();ending=math.min(ending,now()+5)
  end
  while now()<ending do n.nanosleep(0,100000000);stopped()end
 end,debug.traceback)
 if not ok then deadline=now()+8;R.deadline=deadline;R.error=tostring(err);if loaded then pcall(function()R.parametersAfterFailure=params()end)end;pcall(undo);if tag then pcall(tag.cleanup)end;if qos then pcall(qos.cleanup)end;if wan then pcall(wan.cleanup)end;if state then pcall(state.cleanup)end;pcall(store);if rw then pcall(function()send(rw,j.stringify({success=false,ready=ready,error=tostring(err)})..'\n',now()+1)end);rw:close()end;while now()<deadline-1 do n.nanosleep(0,100000000)end end
 local clean=pcall(cleanup);os.exit(clean and(ok and 0 or 4)or 3)
end
rw:close();gr:close();local ready=assert(j.parse(assert(line(rr,now()+4))));assert(ready.pid==pid and ready.boot==boot and ready.owner==P.owner and ready.deadline==deadline);local s=assert(stat(pid));assert(s.ppid==n.getpid()and s.pgrp==pid and s.session==pid and s.start==ready.stat.start);local known={};for f in fs.dir('/proc/'..pid..'/fd')do local k=tonumber(f);if k then known[k]=link(pid,k)end end;for f=0,2 do assert(known[f]=='/dev/null')end;assert(known[ready.goFd]==link(n.getpid(),fd(gw))and known[ready.resultFd]==link(n.getpid(),fd(rr)));for f in pairs(known)do assert(f<=2 or f==ready.goFd or f==ready.resultFd)end
assert(send(gw,'G\n',now()+1));gw:close();local r=assert(j.parse(assert(line(rr,now()+7))));rr:close();r.parentIdentityVerified=true;r.pipeInodesVerified=true;print(j.stringify(r))
