-- In-place mode change for exactly one naturally selected WAN. Authentication process and DHCP lease are retained.
local M={}
function M.new(P,fs,j,read,now,stopped,put,command,record)
 local modeOwned,mwanOwned=false,false;local original=assert(P.wanPrerequisites)
 local index=assert(P.selected.tcp.wan);assert(index==P.selected.udp.wan and index==original.wan and index%1==0 and index>=1 and index<=5);local interface='rpwan'..index;local service='wan'..index
 local function health(mode)
  local link=assert(j.parse(command('/sbin/ip -j -d link show dev '..interface)))[1];local b=original.mode[1]
  assert(link.ifindex==b.ifindex and link.address==b.address and link.link_index==b.link_index and link.linkinfo.info_data.mode==mode,'WAN identity/mode drift')
  local a={};for x in assert(read('/proc/'..original.auth.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=x end;assert(a[20]==original.auth.start,'MiniEAP instance changed')
  local status=assert(j.parse(command('/bin/ubus call network.interface.'..service..' status')));assert(status.up and status.l3_device==interface and status['ipv4-address'][1].address==original.status['ipv4-address'][1].address,'WAN DHCP changed')
  local log=read('/tmp/router-project-logs/minieap-'..service..'.log',1048576);local fail=0;for _ in log:gmatch('认证失败')do fail=fail+1 end;for _ in log:gmatch('Authentication failed')do fail=fail+1 end;assert(fail==original.auth.failure,'MiniEAP reported failure')
  return{uptime=now(),mode=mode,ifindex=link.ifindex,mac=link.address,dhcpAddress=status['ipv4-address'][1].address,authPid=original.auth.pid,authStart=original.auth.start,authFailure=fail,newAuthenticationOrRenewalRequested=false}
 end
 local out={}
 function out.setup()
  stopped();assert(read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')==original.boot)
  record.wanBefore=health('bridge');assert(tonumber(read('/proc/sys/net/ecm/mwan3_enable',128))==0)
  modeOwned=true;command('/sbin/ip link set dev '..interface..' type macvlan mode private');record.wanPrivate=health('private')
  mwanOwned=true;put('/proc/sys/net/ecm/mwan3_enable','1\n');assert(tonumber(read('/proc/sys/net/ecm/mwan3_enable',128))==1);record.mwan3Set=true
 end
 function out.check()return health('private')end
 function out.cleanup()
  stopped();if mwanOwned then local v=tonumber(read('/proc/sys/net/ecm/mwan3_enable',128));assert(v==0 or v==1);if v==1 then put('/proc/sys/net/ecm/mwan3_enable','0\n')end;mwanOwned=false;record.mwan3Restored=true end
  if modeOwned then
   local x=assert(j.parse(command('/sbin/ip -j -d link show dev '..interface)))[1];local b=original.mode[1]
   assert(x.ifindex==b.ifindex and x.address==b.address and x.link_index==b.link_index,'Rollback WAN identity changed')
   local m=x.linkinfo.info_data.mode;assert(m=='private'or m=='bridge');if m=='private'then command('/sbin/ip link set dev '..interface..' type macvlan mode bridge')end
   local after=assert(j.parse(command('/sbin/ip -j -d link show dev '..interface)))[1];assert(after.ifindex==b.ifindex and after.address==b.address and after.linkinfo.info_data.mode=='bridge');modeOwned=false;record.wanRestored=true
   local ok,result=pcall(health,'bridge');record.wanHealthAfterUndo=ok;record.wanAfter=ok and result or tostring(result)
  end
 end
 return out
end
return M
