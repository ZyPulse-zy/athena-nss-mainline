-- Five WAN queue mappings; only five exact kernel-pinned flows are permitted.
local M={}
local function specs(P,up)
 local wans={1,2,3,4,5};for _,slot in ipairs({'tcp','udp','tcp2','tcp3','tcp4'})do local w=P.selected[slot].wan;assert(w%1==0 and w>=1 and w<=5)end;assert(P.selected.tcp.wan~=P.selected.tcp2.wan)
 local base=up and 0x8e00 or 0x8f00;local root=string.format('%x:',base);local shared=up and 60 or 18;local each=up and shared/#wans or math.floor(shared/#wans);local ceiling=up and each or shared
 local commands,qs,cs,leaves={},{},{},{}
 local function cid(n)return root..string.format('%x',n)end
 local function cl(n,parent,rate,ceil,prio,burst)
  local options='burst '..burst..'Kb rate '..rate..'Mbit cburst '..burst..'Kb crate '..ceil..'Mbit priority '..prio..' quantum 1514b overhead 38b';cs[cid(n)]=options
  commands[#commands+1]='class add dev %s parent '..(parent and cid(parent)or root)..' classid '..cid(n)..' nsshtb rate '..rate..'mbit burst '..burst..'kb crate '..ceil..'mbit cburst '..burst..'kb priority '..prio..' quantum 1514 overhead 38'
 end
 local function queue(n,handle,limit,default)
  leaves[cid(n)]=handle;qs[handle]='qdisc nssfq_codel '..handle..' parent '..cid(n)..' target 5ms limit '..limit..'p interval 100ms flows 1024 quantum 1514'..(default and' set_default'or'')..' accel_mode 0'
  commands[#commands+1]='qdisc add dev %s parent '..cid(n)..' handle '..handle..' nssfq_codel target 5ms interval 100ms flows 1024 quantum 1514 limit '..limit..(default and' set_default'or'')..' accel_mode 0'
 end
 qs[root]='qdisc nsshtb '..root..' root r2q 10 accel_mode 0';commands[1]='qdisc replace dev %s root handle '..root..' nsshtb r2q 10 accel_mode 0'
 cl(1,nil,950,950,0,256);cl(255,1,950,950,0,256);queue(255,string.format('%x:',base+255),256,true);cl(80,1,shared,shared,0,32)
 for _,w in ipairs(wans)do
  assert(type(w)=='number'and w%1==0 and w>=1 and w<=5);local parent=256+w;cl(parent,80,each,ceiling,0,32)
  for _,low in ipairs({5,6})do local n=w*16+low;cl(n,parent,low==5 and each-1 or 1,ceiling,low==5 and 1 or 0,low==5 and 32 or 8);queue(n,string.format('%x:',base+n),low==5 and 256 or 128,false)end
 end
 for slot,d in pairs(assert(P.tagPlan.wanLeafAssignments))do
  local f=assert(P.selected[slot]);local low=slot=='udp'and 6 or 5;assert(d.wan==f.wan and d.class==(slot=='udp'and'RT'or'BULK'))
  assert(d.upTag==(0x8e00+f.wan*16+low)*65536 and d.downTag==(0x8f00+f.wan*16+low)*65536)
 end
 return{commands=commands,qs=qs,cs=cs,leaves=leaves,root=root,wans=wans,shared=shared,perWan=ceiling,perWanGuarantee=each}
end
local function validate(qraw,craw,complete,s)
 local seenQ,seenC={},{};local context
 local function stats(x)return x:match('^Sent %d+ bytes %d+ pkt %(dropped %d+, overlimits %d+ requeues %d+%)$')or x:match('^backlog [%d.]+[KMGT]?b %d+p requeues %d+$')or x:match('^maxpacket %d+ drop_overlimit %d+ new_flow_count %d+ ecn_mark %d+$')or x:match('^new_flows_len %d+ old_flows_len %d+$')end
 for line in qraw:gmatch('[^\n]+')do local x=line:gsub('%s+',' '):gsub('^ ',''):gsub(' $','')
  if x:match('^qdisc ')then local h=assert(x:match('^qdisc %S+ (%S+) '));assert(s.qs[h]and not seenQ[h]);assert(x:gsub(' refcnt %d+','')==s.qs[h],'NSS queue options changed');seenQ[h]=true;context=h else assert(context and stats(x),'Unknown NSS queue statistics')end
 end
 context=nil
 for line in craw:gmatch('[^\n]+')do local x=line:gsub('%s+',' '):gsub('^ ',''):gsub(' $','')
  if x:match('^class ')then local h=assert(x:match('^class nsshtb (%S+) root '));assert(s.cs[h]and not seenC[h]);local rest=x:sub(#('class nsshtb '..h..' root ')+1);local leaf=rest:match('^leaf (%S+) ');if leaf then assert(s.leaves[h]==leaf);rest=rest:sub(#('leaf '..leaf..' ')+1)end;assert(rest==s.cs[h],'NSS class options changed');seenC[h]=true;context=h else assert(context and stats(x),'Unknown NSS class statistics')end
 end
 assert(seenQ[s.root]);if complete then for h in pairs(s.qs)do assert(seenQ[h])end;for h in pairs(s.cs)do assert(seenC[h])end end
 return{complete=not not complete,nativeOptionsValidated=true,parentDumpHasKnownStockLimitation=true,wanNumbers=s.wans,sharedMbps=s.shared,perWanCeilingMbps=s.perWan,perWanGuaranteedMbps=s.perWanGuarantee}
end
function M.new(P,fs,j,command,now,stopped,R,up)
 local d=up and P.uplinkDevice or P.qosDevice;assert(up and d=='wan'or not up and d=='lan4');local tc=P.qosTc.path;assert(tc=='/root/router-project/experiments/nss8-htb2-20261001/tc-nss');local mod='/lib/modules/6.18.44/qca-nss-qdisc.ko';local own,attempted=false,false;local spec=specs(P,up)
 local function trim(s)return s:gsub('%s+$','')end
 local function shape(rows)
  assert(#rows==5);local a={};for _,q in ipairs(rows)do local h=q.parent or'root';assert(not a[h]);if q.kind=='mq'then assert(q.root and q.handle=='0:'and next(q.options)==nil)else assert(q.kind=='fq_codel'and h:match('^:[1-4]$')and q.handle=='0:')end;a[h]={kind=q.kind,handle=q.handle,root=q.root,parent=q.parent,options=q.options}end;assert(a.root and a[':1']and a[':2']and a[':3']and a[':4']);return a
 end
 local function canon(x)if type(x)~='table'then return j.stringify(x)end;local ks={};for k in pairs(x)do ks[#ks+1]=k end;table.sort(ks);local a={};for _,k in ipairs(ks)do a[#a+1]=j.stringify(k)..':'..canon(x[k])end;return'{'..table.concat(a,',')..'}'end
 local baseline=canon(shape(up and P.uplinkBaseline or P.qosBaseline));local function base()return canon(shape(assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)))))==baseline end
 local function check(p,pin)local a=assert(fs.lstat(p));for _,k in ipairs({'dev','ino','type','nlink','uid','gid','modedec','size'})do assert(a[k]==pin.metadata[k])end;assert(command('/usr/bin/sha256sum '..p):match('^(%x+) ')==pin.sha256);local b=assert(fs.lstat(p));for _,k in ipairs({'dev','ino','type','nlink','uid','gid','modedec','size','mtime','ctime'})do assert(a[k]==b[k])end end
 local function snap(complete)local q=command(tc..' -s -d qdisc show dev '..d);local c=command(tc..' -s -d class show dev '..d);return{qdisc=q,classes=c,validation=validate(q,c,complete,spec),device=d,uptime=now()}end
 local out={}
 function out.setup(deadline)
  stopped();assert(now()<deadline-13);if up then assert(R.sharedModuleOwnedByDown and fs.lstat('/sys/module/qca_nss_qdisc'));assert(P.uplinkIfindex==6 and tonumber(command('/bin/cat /sys/class/net/wan/ifindex'))==6)else assert(not fs.lstat('/sys/module/qca_nss_qdisc'))end
  assert(base());assert(trim(command('/sbin/tc -d filter show dev '..d..' root'))=='');check(tc,P.qosTc);check(mod,P.qosModule);own=true;if not up then command('/sbin/insmod '..mod)end;assert(fs.lstat('/sys/module/qca_nss_qdisc'));R.qosModuleLoaded=not up
  attempted=true;R.qosCommandsCompleted=0;for _,c in ipairs(spec.commands)do stopped();assert(now()<deadline-10);command(tc..' '..string.format(c,d));R.qosCommandsCompleted=R.qosCommandsCompleted+1 end
  R.qosReady=snap(true);R.qosConfigured=true;R.wanBudgetHierarchyCommandsAccepted=true;return R.qosReady
 end
 function out.snapshot()return snap(true)end
 function out.cleanup()
  if not own then return end;stopped();if not fs.lstat('/sys/module/qca_nss_qdisc')then assert(base());own=false;R.qosRestored=true;R.qosModuleUnloaded=true;return end
  if attempted then local q=command(tc..' -s -d qdisc show dev '..d);if q:find('qdisc nsshtb '..spec.root,1,true)then local c=command(tc..' -s -d class show dev '..d);validate(q,c,false,spec);R.qosBeforeUndo={qdisc=q,classes=c};command(tc..' qdisc del dev '..d..' root')else assert(base())end;assert(base());attempted=false end
  assert(trim(command('/sbin/tc -d filter show dev '..d..' root'))=='');if up then own=false;R.qosRestored=true;R.sharedModuleReferenceReleased=true;R.qosAfterUndo=assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)));return end
  assert(trim(command('/bin/ls -A /sys/module/qca_nss_qdisc/holders'))=='');command('/sbin/rmmod qca_nss_qdisc');assert(not fs.lstat('/sys/module/qca_nss_qdisc'));own=false;R.qosRestored=true;R.qosModuleUnloaded=true;R.qosAfterUndo=assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)))
 end
 return out
end
local C={}
function C.new(P,fs,j,command,now,stopped,R)
 assert(P.uplinkDevice=='wan'and P.uplinkIfindex==6 and P.uplinkPhysicalAeId==5)
 local down=M.new(P,fs,j,command,now,stopped,R,false);R.uplinkQos={};local up=M.new(P,fs,j,command,now,stopped,R.uplinkQos,true);local out={}
 function out.setup(deadline)local d=down.setup(deadline);R.uplinkQos.sharedModuleOwnedByDown=R.qosModuleLoaded;d.uplink=assert(j.parse(j.stringify(up.setup(deadline))));R.dualPhysicalQueuesReady=true;return d end
 function out.snapshot()local d=down.snapshot();d.uplink=up.snapshot();return d end
 function out.cleanup()local a,x=pcall(up.cleanup);local b,y=pcall(down.cleanup);assert(a,x);assert(b,y);R.dualPhysicalQueuesRestored=R.qosRestored and R.uplinkQos.qosRestored end
 return out
end
return C
