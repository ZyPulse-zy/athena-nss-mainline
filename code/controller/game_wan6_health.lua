-- Pure gate evaluated by the existing five-second health loop. No commands.
local M={}
function M.state(r,iface,health,now,boot)
 local f=r.flowState or {};local b=f.budgetUpdates or {};local i=r.ingress or {}
 local addr=iface['ipv4-address'] and iface['ipv4-address'][1] and iface['ipv4-address'][1].address
 local fresh=type(b.lastSuccessAtUptime)=='number' and now>=b.lastSuccessAtUptime and now-b.lastSuccessAtUptime<6
 local queues=i.up and i.down and i.up.wanCount==6 and i.down.wanCount==6
 if queues then for w=1,6 do for _,d in ipairs{'up','down'}do
  local t=i[d].tags and i[d].tags[w]
  if not t or t.BE~=(d=='up' and 0x7e00 or 0x7a00)+w*16+5 or t.RT~=t.BE+1 then queues=false end
 end end end
 local state={wanCount=r.wanCount,authenticated=iface.up==true and iface.l3_device=='rpwan6' and addr~=nil and r.wans and addr==r.wans.rpwan6,
  healthy=health and health.healthy==true,sourceFresh=f.sourceFresh==true and fresh,
  nativeRunning=r.phase=='native-running' and r.boot==boot and r.native and r.native.loaded==true
   and r.native.unconfirmed==0 and r.native.pending==0,queuesComplete=queues==true}
 state.ready=state.wanCount==6 and state.authenticated and state.healthy and state.sourceFresh and state.nativeRunning and state.queuesComplete or false
 return state
end
return M
