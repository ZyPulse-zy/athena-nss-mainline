-- Only the detached child creates/removes its private directory. Sender uses existing FD only.
local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local P=assert(j.parse([=[__PLAN__]=]))
local phase=assert(loadstring([=[__CORE_PHASE__]=]))()
local qosLibrary=assert(loadstring([=[__QOS_PHYSICAL__]=]))();local tagLibrary,classifierLibrary,normalizerLibrary,fastLibrary,wanLibrary,stateLibrary
assert(P.owner:match('^[a-f0-9]+$')and #P.owner==32 and P.mode=='stage'and type(P.openFrontend)=='boolean')
assert(P.moduleBytes==38480 and P.moduleSha256=='2926791b561bbc90494210f9c77335ece7779f0183bc95457e4ffd9761ca083a')
assert(not P.qosDevice or P.qosStaged);if P.qosStaged then assert(P.qosCodeBytes>0 and P.qosCodeBytes<=73728 and P.qosCodeSha256:match('^[a-f0-9]+$')and #P.qosCodeSha256==64)end
local DIR='/tmp/rp-nss25-stage-'..P.owner;local MOD='rp_ecm_gate_lab_ct';local boot
local function read(p,l)local f=assert(io.open(p));local s=f:read((l or 262144)+1)or'';f:close();assert(#s<=(l or 262144));return s end
local function now()return assert(tonumber(read('/proc/uptime',128):match('^[%d.]+')))end
local function stat(pid)if not fs.lstat('/proc/'..pid..'/stat')then return nil end;local a={};for v in assert(read('/proc/'..pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;return{pid=pid,start=a[20],state=a[1],ppid=tonumber(a[2]),pgrp=tonumber(a[3]),session=tonumber(a[4])}end
local function fd(f)return assert(tonumber(tostring(f):match('(%d+)$')))end
local function link(pid,f)return assert(fs.readlink('/proc/'..pid..'/fd/'..f))end
local function send(f,s,due)local p=1;while p<=#s and now()<due do local v={{fd=f,events=n.poll_flags('out','err','hup')}};local k,e=n.poll(v,40);if type(k)=='number'and k>0 then local z=n.poll_flags(v[1].revents);if z.err or z.hup or z.nval then return false end;if z.out then local q=f:write(s:sub(p,p+255));if not q or q==0 then return false end;p=p+q end elseif k==nil and e~=4 then return false end end;return p>#s end
local function line(f,due)local a={};while now()<due do local v={{fd=f,events=n.poll_flags('in','hup','err')}};local k,e=n.poll(v,40);if type(k)=='number'and k>0 then local z=n.poll_flags(v[1].revents);if z['in']then local s=f:read(1);if not s or s==''then return nil end;if s=='\n' then return table.concat(a)end;a[#a+1]=s;assert(#a<12000)elseif z.hup or z.err or z.nval then return nil end elseif k==nil and e~=4 then return nil end end;return nil end
local countPaths={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
local function zero()for _,p in ipairs(countPaths)do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0,'ECM count nonzero: '..p)end end
local function stopped()for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==1)end;zero()end
local function absent(p)local q,a,b=fs.lstat(p);assert(not q and(a==2 or b==2),'Unknown/existing path')end
local function command(c)local f=assert(io.popen('/usr/bin/timeout -k 1 3 '..c..' 2>&1; rc=$?;printf "\\n__NSS16_STAGE_RC__%s\\n" "$rc"'));local s=f:read(131072);f:close();local body,rc=s:match('^(.*)\n__NSS16_STAGE_RC__(%d+)\n$');assert(body and rc=='0',body or'Command receipt missing');return body end
boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','');assert(boot==P.boot);stopped();absent(DIR);absent('/sys/module/'..MOD)
local deadline=now()+100;local rr,rw=assert(n.pipe());local gr,gw=assert(n.pipe());local pid=assert(n.fork())
if pid==0 then
 rr:close();gw:close();assert(n.setsid());assert(n.signal(13,'ign'));assert(n.signal(1,'ign'));n.umask(77);local null=assert(n.open('/dev/null','r+'));assert(n.dup(null,n.stdin));assert(n.dup(null,n.stdout));assert(n.dup(null,n.stderr));null:close()
 local me=n.getpid();local ready={pid=me,stat=stat(me),boot=boot,deadline=deadline,dir=DIR,owner=P.owner,goFd=fd(gr),resultFd=fd(rw)};assert(send(rw,j.stringify(ready)..'\n',now()+3));local go=line(gr,now()+3);gr:close();if go~='G'then rw:close();os.exit(2)end
 local ownDir,ownFile,ownCode;local loaded=false;local qos;local tag;local wan;local state;local files={};local stateNode;local record={version=1,owner=P.owner,boot=boot,deadline=deadline,mode=P.mode,stageComplete=false,moduleLoaded=false,gateComplete=false,newNssPermit=false,priorityOrQueueWrites=not not P.qosDevice,qosDevice=P.qosDevice}
 local function dcheck()local a=assert(fs.lstat(DIR));assert(a.type=='dir'and a.uid==0 and a.gid==0 and a.modedec==700 and a.dev==ownDir.dev and a.ino==ownDir.ino);return a end
 local function fcheck(name,mode)local a=assert(fs.lstat(DIR..'/'..name));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1 and a.modedec==(mode or 600));return a end
 local function store()dcheck();assert(now()<deadline-1);local tmp=DIR..'/state.json.new';absent(tmp);files['state.json.new']=true;local f=assert(io.open(tmp,'w'));assert(f:write(j.stringify(record)..'\n'));assert(f:close());fcheck('state.json.new');assert(os.rename(tmp,DIR..'/state.json'));files['state.json.new']=nil;files['state.json']=fcheck('state.json')end
 local function put(p,v)local f=assert(io.open(p,'w'));assert(f:write(v));assert(f:close())end
 local function parameters()local o={};for _,name in ipairs({'registered','diagnostic_only','denied','eligible_tcp','eligible_game','allowed_tcp','allowed_game','tcp_state','game_state','tcp_pinned_state','game_pinned_state','last_decoded_info','frozen_record_sha256','classifier_until_ms','session_until_ms','classifier_sequence','epoch_refresh','renewed_epochs','tcp_permit','game_permit','expiry_tcp','expiry_game','cpu_barriers','revoke_calls','revoke_found'})do o[name]=read('/sys/module/'..MOD..'/parameters/'..name,8192):gsub('%s+$','')end;return o end
 local function undoModule()
  if not loaded then return end;put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\n');put('/sys/kernel/debug/ecm/front_end_ipv6_stop','1\n');assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop'))==1)
  if not fs.lstat('/sys/module/'..MOD)then loaded=false;stopped();return end
  assert(read('/sys/module/'..MOD..'/parameters/frozen_record_sha256',256):gsub('%s+$','')==P.frozenHash,'Module ownership changed')
  for _,slot in ipairs({'tcp','game'})do put('/sys/module/'..MOD..'/parameters/'..slot..'_close','Y\n');put('/sys/module/'..MOD..'/parameters/'..slot..'_drain','Y\n')end
  local passed=false;for z=1,50 do passed=pcall(zero);if passed then break end;n.nanosleep(0,100000000)end;assert(passed,'Scoped firmware drain failed');record.parametersBeforeUnload=parameters();command('/sbin/rmmod '..MOD);loaded=false;absent('/sys/module/'..MOD);stopped();record.moduleUnloaded=true
 end
 local function cleanup()
  undoModule();if tag then tag.cleanup()end;if qos then qos.cleanup()end;if wan then wan.cleanup()end;if state then state.cleanup()end;if not ownDir then return end;dcheck();for name in fs.dir(DIR)do assert(files[name],'Foreign private file');local pinned=name=='candidate.ko'and ownFile or name=='qos.lua'and ownCode;local a;if name=='ecm-state'then a=assert(fs.lstat(DIR..'/'..name));assert(stateNode and a.type=='chr'and a.uid==0 and a.gid==0 and a.modedec==600 and a.dev==stateNode.dev and a.ino==stateNode.ino and a.rdev==stateNode.rdev)else a=fcheck(name,pinned and pinned.modedec or 600)end;if pinned then assert(a.dev==pinned.dev and a.ino==pinned.ino)end;assert(fs.unlink(DIR..'/'..name))end;dcheck();assert(fs.rmdir(DIR));absent(DIR)
 end
 local ok,err=xpcall(function()
  stopped();assert(now()<deadline-12);absent(DIR);assert(fs.mkdir(DIR,700));ownDir=assert(fs.lstat(DIR));dcheck();put(DIR..'/owner',P.owner..' '..boot..' '..deadline..'\n');files.owner=fcheck('owner');put(DIR..'/candidate.ko','');ownFile=fcheck('candidate.ko');files['candidate.ko']=ownFile;record.moduleFileIdentity=ownFile;if P.qosStaged then put(DIR..'/qos.lua','');ownCode=fcheck('qos.lua');files['qos.lua']=ownCode;record.qosFileIdentity=ownCode end;store()
  assert(send(rw,j.stringify({success=true,ready=ready,moduleFileIdentity=ownFile,qosFileIdentity=ownCode,rollbackBeforeFirstWrite=true})..'\n',now()+2));rw:close();rw=nil
  local stageDue=math.min(deadline-12,now()+12)
  while now()<stageDue do local a=fcheck('candidate.ko');assert(a.dev==ownFile.dev and a.ino==ownFile.ino and a.size<=P.moduleBytes);if a.size==P.moduleBytes then local digest=assert(command('/usr/bin/sha256sum '..DIR..'/candidate.ko'):match('^(%x+) '));assert(digest==P.moduleSha256);record.stageComplete=true;record.stageSha256=digest;record.stageAtUptime=now();store();break end;n.nanosleep(0,50000000);stopped()end
  assert(record.stageComplete,'Module staging deadline');assert(fs.chmod(DIR..'/candidate.ko',400));ownFile=fcheck('candidate.ko',400)
  if P.qosStaged then
   while now()<stageDue do local a=fcheck('qos.lua');assert(a.dev==ownCode.dev and a.ino==ownCode.ino and a.size<=P.qosCodeBytes);if a.size==P.qosCodeBytes then local digest=assert(command('/usr/bin/sha256sum '..DIR..'/qos.lua'):match('^(%x+) '));assert(digest==P.qosCodeSha256,'QoS helper bytes changed');assert(fs.chmod(DIR..'/qos.lua',400));ownCode=fcheck('qos.lua',400);local text=read(DIR..'/qos.lua',73728);assert(#text==P.qosCodeBytes);local after=fcheck('qos.lua',400);assert(after.dev==ownCode.dev and after.ino==ownCode.ino and after.size==ownCode.size);local bundle=assert(loadstring(text))();qosLibrary=assert(bundle.qos);phase=assert(bundle.phase);tagLibrary=assert(bundle.tags);classifierLibrary=assert(bundle.classifier);normalizerLibrary=assert(bundle.normalizer);fastLibrary=assert(bundle.fast);wanLibrary=assert(bundle.wan);stateLibrary=assert(bundle.state);P.tagPlan=assert(bundle.tagPlan);record.qosCodeLoaded=true;record.qosCodeSha256=digest;store();break end;n.nanosleep(0,50000000);stopped()end
   assert(record.qosCodeLoaded,'QoS helper staging deadline')
  end
  state=stateLibrary.new(P,fs,read,now,stopped,command,record);state.setup();store()
  wan=wanLibrary.new(P,fs,j,read,now,stopped,put,command,record);wan.setup();store()
  local function load(args)
   stopped();assert(not loaded and not fs.lstat('/sys/module/'..MOD));assert(command('/usr/bin/sha256sum /lib/modules/6.18.44/ecm.ko'):match('^(%x+) ')==P.ecmSha256);assert(command('/bin/ls -A /sys/module/ecm/holders'):gsub('%s+$','')=='');loaded=true;command('/sbin/insmod '..DIR..'/candidate.ko '..args);record.moduleLoaded=true;assert(parameters().frozen_record_sha256==P.frozenHash)
  end
  local fast=fastLibrary.new(P,fs,j,read,now,stopped,put,command,record,parameters,load,undoModule,DIR,phase,classifierLibrary)
  if P.qosDevice then qos=qosLibrary.new(P,fs,j,command,now,stopped,record);qos.setup(deadline);store();if P.mode=='stage'then
   assert(P.autoClassified and P.qosDevice=='lan4')
   tag=tagLibrary.new(P,fs,j,read,now,stopped,command,record,classifierLibrary,qos,normalizerLibrary,fast);tag.run(deadline);wan.check();qos.cleanup();wan.cleanup();state.cleanup();store()
  end end
  local ending=deadline-1
  if record.automaticLifecycleEpochCompleted or record.classChangeTestCompleted or record.freshEpochRelearningCompleted then
   for _,key in ipairs({'moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'})do assert(record[key]==true,'Success teardown incomplete: '..key)end
   stopped();absent('/sys/module/'..MOD);absent('/sys/module/qca_nss_qdisc')
   record.successEarlyCompletion=true;record.successRecordGraceSeconds=5;store();ending=math.min(ending,now()+5)
  end
  while now()<ending do n.nanosleep(0,100000000);stopped()end
 end,debug.traceback)
 if not ok then record.error=tostring(err);if loaded then pcall(function()record.parametersAfterFailure=parameters()end)end;pcall(undoModule);if tag then pcall(tag.cleanup)end;if qos then pcall(qos.cleanup)end;if wan then pcall(wan.cleanup)end;if state then pcall(state.cleanup)end;pcall(store);if rw then pcall(function()send(rw,j.stringify({success=false,ready=ready,error=tostring(err)})..'\n',now()+1)end);rw:close()end;while now()<deadline-1 do n.nanosleep(0,100000000)end end
 local clean=pcall(cleanup);os.exit(clean and(ok and 0 or 4)or 3)
end
rw:close();gr:close();local ready=assert(j.parse(assert(line(rr,now()+4))));assert(ready.pid==pid and ready.boot==boot and ready.owner==P.owner and ready.deadline==deadline);local s=assert(stat(pid));assert(s.ppid==n.getpid()and s.pgrp==pid and s.session==pid and s.start==ready.stat.start);local known={};for f in fs.dir('/proc/'..pid..'/fd')do local k=tonumber(f);if k then known[k]=link(pid,k)end end;for f=0,2 do assert(known[f]=='/dev/null')end;assert(known[ready.goFd]==link(n.getpid(),fd(gw))and known[ready.resultFd]==link(n.getpid(),fd(rr)));for f in pairs(known)do assert(f<=2 or f==ready.goFd or f==ready.resultFd)end
assert(send(gw,'G\n',now()+1));gw:close();local r=assert(j.parse(assert(line(rr,now()+7))));rr:close();r.parentIdentityVerified=true;r.pipeInodesVerified=true;print(j.stringify(r))
