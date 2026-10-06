-- Two immutable natural WAN identities. Never alter PBR or request authentication.
local M={}
function M.new(P,fs,j,read,now,stopped,put,command,record)
 local p=assert(P.wanPrerequisites);local members=assert(p.members);assert(#members==2)
 local own,mwan={},false
 for i,f in ipairs({P.selected.tcp,P.selected.udp})do local e=members[i];assert(e.w==f.wan and e.ip==f.reply.dst and e.w%1==0 and e.w>=1 and e.w<=5)end
 assert(members[1].w~=members[2].w)
 local function link(e)local x=assert(j.parse(command('/sbin/ip -j -d link show dev rpwan'..e.w)))[1];assert(x.ifindex==e.index and x.address==e.mac and x.link_index==e.link,'WAN identity drift');return x end
 local function health(e,mode)
  local x=link(e);assert(x.linkinfo.info_data.mode==mode,'WAN mode drift')
  local a={};for x in assert(read('/proc/'..e.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=x end;assert(a[20]==e.start,'MiniEAP instance changed')
  local status=assert(j.parse(command('/bin/ubus call network.interface.wan'..e.w..' status')));assert(status.up and status.l3_device=='rpwan'..e.w and status['ipv4-address'][1].address==e.ip,'WAN DHCP changed')
  local text=read('/tmp/router-project-logs/minieap-wan'..e.w..'.log',1048576);local fail=0;for _ in text:gmatch('认证失败')do fail=fail+1 end;for _ in text:gmatch('Authentication failed')do fail=fail+1 end;assert(fail==e.failure,'MiniEAP reported failure')
  return{wan=e.w,uptime=now(),mode=mode,ifindex=x.ifindex,dhcpAddress=e.ip,authPid=e.pid,authStart=e.start,authFailure=fail,newAuthenticationOrRenewalRequested=false}
 end
 local out={}
 function out.setup()
  stopped();assert(read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')==p.boot);assert(tonumber(read('/proc/sys/net/ecm/mwan3_enable',128))==0)
  record.wanBefore={};for i,e in ipairs(members)do record.wanBefore[i]=health(e,'bridge')end
  record.wanPrivate={};for i,e in ipairs(members)do own[i]=true;command('/sbin/ip link set dev rpwan'..e.w..' type macvlan mode private');record.wanPrivate[i]=health(e,'private')end
  mwan=true;put('/proc/sys/net/ecm/mwan3_enable','1\n');assert(tonumber(read('/proc/sys/net/ecm/mwan3_enable',128))==1);record.mwan3Set=true
 end
 function out.check()local t={};for i,e in ipairs(members)do t[i]=health(e,'private')end;return t end
 function out.cleanup()
  stopped();local errors={}
  if mwan then local ok,err=pcall(function()local v=tonumber(read('/proc/sys/net/ecm/mwan3_enable',128));assert(v==0 or v==1);if v==1 then put('/proc/sys/net/ecm/mwan3_enable','0\n')end;mwan=false;record.mwan3Restored=true end);if not ok then errors[#errors+1]=tostring(err)end end
  record.wanAfter=record.wanAfter or{};record.wanHealthAfterUndo=record.wanHealthAfterUndo or{}
  for i,e in ipairs(members)do if own[i]then local ok,err=pcall(function()
   local x=link(e);local mode=x.linkinfo.info_data.mode;assert(mode=='private'or mode=='bridge');if mode=='private'then command('/sbin/ip link set dev rpwan'..e.w..' type macvlan mode bridge')end
   assert(link(e).linkinfo.info_data.mode=='bridge');own[i]=false
   local good,result=pcall(health,e,'bridge');record.wanHealthAfterUndo[i]=good;record.wanAfter[i]=good and result or tostring(result)
  end);if not ok then errors[#errors+1]=tostring(err)end end end
  record.wanRestored=not own[1]and not own[2];assert(#errors==0,table.concat(errors,'; '))
 end
 return out
end
return M
