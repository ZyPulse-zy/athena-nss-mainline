-- Runs only in the verified detached guardian. One physical port, no bridge/IFB.
local M={}
local qheaders={
 ['8f00:']='qdisc nsshtb 8f00: root r2q 10 accel_mode 0',
 ['8fff:']='qdisc nssfq_codel 8fff: parent 8f00:ff target 5ms limit 256p interval 100ms flows 1024 quantum 1514 set_default accel_mode 0',
 ['8f05:']='qdisc nssfq_codel 8f05: parent 8f00:5 target 5ms limit 256p interval 100ms flows 1024 quantum 1514 accel_mode 0',
 ['8f06:']='qdisc nssfq_codel 8f06: parent 8f00:6 target 5ms limit 128p interval 100ms flows 1024 quantum 1514 accel_mode 0'}
local cheaders={
 ['8f00:1']='burst 256Kb rate 950Mbit cburst 256Kb crate 950Mbit priority 0 quantum 1514b overhead 38b',
 ['8f00:ff']='burst 256Kb rate 950Mbit cburst 256Kb crate 950Mbit priority 0 quantum 1514b overhead 38b',
 ['8f00:50']='burst 32Kb rate 30Mbit cburst 32Kb crate 30Mbit priority 0 quantum 1514b overhead 38b',
 ['8f00:5']='burst 32Kb rate 29Mbit cburst 32Kb crate 30Mbit priority 1 quantum 1514b overhead 38b',
 ['8f00:6']='burst 8Kb rate 1Mbit cburst 32Kb crate 30Mbit priority 0 quantum 1514b overhead 38b'}
local leaves={['8f00:ff']='8fff:',['8f00:5']='8f05:',['8f00:6']='8f06:'}
function M.validateNative(qraw,craw,complete,up)
 if up then assert(not qraw:find(" 8f%x*:")and not craw:find(" 8f%x*:"),"Downstream tag on uplink");qraw=qraw:gsub("8e","8f");craw=craw:gsub("8e","8f")end
 local seenQ,seenC={},{ };local context
 local function stats(s)
  return s:match('^Sent %d+ bytes %d+ pkt %(dropped %d+, overlimits %d+ requeues %d+%)$')or s:match('^backlog [%d.]+[KMGT]?b %d+p requeues %d+$')or s:match('^maxpacket %d+ drop_overlimit %d+ new_flow_count %d+ ecn_mark %d+$')or s:match('^new_flows_len %d+ old_flows_len %d+$')
 end
 for line in qraw:gmatch('[^\n]+')do local s=line:gsub('%s+',' '):gsub('^ ',''):gsub(' $','')
  if s:match('^qdisc ')then local h=assert(s:match('^qdisc %S+ (%S+) '));assert(qheaders[h]and not seenQ[h],'Unknown/duplicate NSS queue');s=s:gsub(' refcnt %d+','');assert(s==qheaders[h],'NSS queue option drift');seenQ[h]=true;context=h else assert(context and stats(s),'Unknown NSS queue output line')end
 end
 context=nil
 for line in craw:gmatch('[^\n]+')do local s=line:gsub('%s+',' '):gsub('^ ',''):gsub(' $','')
  if s:match('^class ')then local h=assert(s:match('^class nsshtb (%S+) root '));assert(cheaders[h]and not seenC[h],'Unknown/duplicate NSS class');local rest=s:sub(#('class nsshtb '..h..' root ')+1);local leaf=rest:match('^leaf (%S+) ');if leaf then assert(leaves[h]==leaf,'Wrong class leaf');rest=rest:sub(#('leaf '..leaf..' ')+1)end;assert(rest==cheaders[h],'NSS class option drift');seenC[h]=true;context=h else assert(context and stats(s),'Unknown NSS class output line')end
 end
 assert(seenQ['8f00:'],'No owned root');if complete then for h in pairs(qheaders)do assert(seenQ[h],'Missing NSS queue')end;for h in pairs(cheaders)do assert(seenC[h],'Missing NSS class')end end
 return{queueCount=(function()local k=0;for _ in pairs(seenQ)do k=k+1 end;return k end)(),classCount=(function()local k=0;for _ in pairs(seenC)do k=k+1 end;return k end)(),complete=not not complete,nativeOptionsValidated=true,parentDumpHasKnownStockLimitation=true}
end
function M.new(P,fs,j,command,now,stopped,record,up)
 local d=assert(up and P.uplinkDevice or P.qosDevice);assert(up and d=='wan'or not up and(d=='lan1'or d=='lan4'));local tc=assert(P.qosTc.path);assert(tc=='/root/router-project/experiments/nss8-htb2-20261001/tc-nss');local mod='/lib/modules/6.18.44/qca-nss-qdisc.ko';local ownedModule,rootAttempted=false,false
 local function trim(s)return s:gsub('%s+$','')end
 local function shape(rows)
  assert(#rows==5,'Default physical queue count changed');local out={};for _,q in ipairs(rows)do local h=q.parent or'root';assert(not out[h]);local o=q.options;if q.kind=='mq'then assert(q.root==true and q.handle=='0:'and next(o)==nil);o={}else assert(q.kind=='fq_codel'and h:match('^:[1-4]$')and q.handle=='0:')end;out[h]={kind=q.kind,handle=q.handle,root=q.root,parent=q.parent,options=o}end;assert(out.root and out[':1']and out[':2']and out[':3']and out[':4']);return out
 end
 local function canon(v)if type(v)~='table'then return j.stringify(v)end;local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys);local a={};for _,k in ipairs(keys)do a[#a+1]=j.stringify(k)..':'..canon(v[k])end;return'{'..table.concat(a,',')..'}'end
 local baseline=canon(shape(up and P.uplinkBaseline or P.qosBaseline));local function base()return canon(shape(assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)))))==baseline end
 local function checkFile(p,pin)local a=assert(fs.lstat(p));for _,k in ipairs({'dev','ino','type','nlink','uid','gid','modedec','size'})do assert(a[k]==pin.metadata[k],'Executable identity changed')end;assert(command('/usr/bin/sha256sum '..p):match('^(%x+) ')==pin.sha256,'Executable bytes changed');local b=assert(fs.lstat(p));for _,k in ipairs({'dev','ino','type','nlink','uid','gid','modedec','size','mtime','ctime'})do assert(a[k]==b[k],'Executable hash race')end end
 local function snapshot(complete)local q=command(tc..' -s -d qdisc show dev '..d);local c=command(tc..' -s -d class show dev '..d);return{qdisc=q,classes=c,validation=M.validateNative(q,c,complete,up),device=d,uptime=now()}end
 local out={}
 function out.setup(deadline)
  stopped();assert(now()<deadline-13);if up then assert(record.sharedModuleOwnedByDown==true and fs.lstat('/sys/module/qca_nss_qdisc'));assert(P.uplinkIfindex==6 and tonumber(command('/bin/cat /sys/class/net/wan/ifindex'))==6)else assert(not fs.lstat('/sys/module/qca_nss_qdisc'))end;assert(base(),'Physical default queues drifted');assert(trim(command('/sbin/tc -d filter show dev '..d..' root'))=='','Unexpected physical filter')
  if d=='lan1'then assert(trim(command('/bin/cat /sys/class/net/lan1/carrier'))=='0','Idle port became connected')end
  checkFile(tc,P.qosTc);checkFile(mod,P.qosModule);ownedModule=true;if not up then command('/sbin/insmod '..mod)end;assert(fs.lstat('/sys/module/qca_nss_qdisc'));record.qosModuleLoaded=not up
  local commands={
   'qdisc replace dev '..d..' root handle 8f00: nsshtb r2q 10 accel_mode 0',
   'class add dev '..d..' parent 8f00: classid 8f00:1 nsshtb rate 950mbit burst 256kb crate 950mbit cburst 256kb priority 0 quantum 1514 overhead 38',
   'class add dev '..d..' parent 8f00:1 classid 8f00:ff nsshtb rate 950mbit burst 256kb crate 950mbit cburst 256kb priority 0 quantum 1514 overhead 38',
   'qdisc add dev '..d..' parent 8f00:ff handle 8fff: nssfq_codel target 5ms interval 100ms flows 1024 quantum 1514 limit 256 set_default accel_mode 0',
   'class add dev '..d..' parent 8f00:1 classid 8f00:50 nsshtb rate 30mbit burst 32kb crate 30mbit cburst 32kb priority 0 quantum 1514 overhead 38',
   'class add dev '..d..' parent 8f00:50 classid 8f00:5 nsshtb rate 29mbit burst 32kb crate 30mbit cburst 32kb priority 1 quantum 1514 overhead 38',
   'qdisc add dev '..d..' parent 8f00:5 handle 8f05: nssfq_codel target 5ms interval 100ms flows 1024 quantum 1514 limit 256 accel_mode 0',
   'class add dev '..d..' parent 8f00:50 classid 8f00:6 nsshtb rate 1mbit burst 8kb crate 30mbit cburst 32kb priority 0 quantum 1514 overhead 38',
   'qdisc add dev '..d..' parent 8f00:6 handle 8f06: nssfq_codel target 5ms interval 100ms flows 1024 quantum 1514 limit 128 accel_mode 0'}
  record.qosCommandsCompleted=0;rootAttempted=true;for _,c in ipairs(commands)do assert(now()<deadline-10,'Queue construction deadline');stopped();if up then c=c:gsub('8f','8e')end;command(tc..' '..c);record.qosCommandsCompleted=record.qosCommandsCompleted+1 end
  record.qosReady=snapshot(true);record.qosConfigured=true;return record.qosReady
 end
 function out.snapshot()return snapshot(true)end
 function out.cleanup()
  if not ownedModule then return end;stopped()
  if not fs.lstat('/sys/module/qca_nss_qdisc')then assert(base(),'Default physical queues changed without module');ownedModule=false;record.qosRestored=true;record.qosModuleUnloaded=true;return end
  if rootAttempted then local raw=command(tc..' -s -d qdisc show dev '..d)
   if raw:find('qdisc nsshtb '..(up and'8e00:'or'8f00:'),1,true)then local c=command(tc..' -s -d class show dev '..d);M.validateNative(raw,c,false,up);record.qosBeforeUndo={qdisc=raw,classes=c};command(tc..' qdisc del dev '..d..' root')else assert(base(),'Unknown physical root after attempted replace')end
   assert(base(),'Physical queues not restored');rootAttempted=false
  end
  assert(trim(command('/sbin/tc -d filter show dev '..d..' root'))=='','Unexpected physical filter during undo');if up then assert(base());ownedModule=false;record.qosRestored=true;record.sharedModuleReferenceReleased=true;record.qosAfterUndo=assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)));return end;assert(trim(command('/bin/ls -A /sys/module/qca_nss_qdisc/holders'))=='','Foreign NSS qdisc holder');command('/sbin/rmmod qca_nss_qdisc');assert(not fs.lstat('/sys/module/qca_nss_qdisc'));ownedModule=false;record.qosRestored=true;record.qosModuleUnloaded=true;record.qosAfterUndo=assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)))
 end
 return out
end
local C={validateNative=M.validateNative}
function C.new(P,fs,j,command,now,stopped,record)
 assert(P.uplinkDevice=='wan'and P.uplinkIfindex==6 and P.uplinkPhysicalAeId==5)
 local down=M.new(P,fs,j,command,now,stopped,record,false)
 record.uplinkQos={};local up=M.new(P,fs,j,command,now,stopped,record.uplinkQos,true);local out={}
 function out.setup(deadline)
  local d=down.setup(deadline);record.uplinkQos.sharedModuleOwnedByDown=record.qosModuleLoaded==true
  d.uplink=assert(j.parse(j.stringify(up.setup(deadline))));record.dualPhysicalQueuesReady=true;return d
 end
 function out.snapshot()local d=down.snapshot();d.uplink=up.snapshot();return d end
 function out.cleanup()
  local a,x=pcall(up.cleanup);local b,y=pcall(down.cleanup)
  assert(a,x);assert(b,y);record.dualPhysicalQueuesRestored=record.qosRestored==true and record.uplinkQos.qosRestored==true
 end
 return out
end
return C
