-- Visibility only: retain the authenticated complete rows and their provenance.
return function(candidates,sockets)
 local flows={}
 for _,f in ipairs(candidates.flows)do
  local i,d=f.identity,f.decision;local owned=false
  if i.original.src=='192.168.237.207'and math.floor(i.mark/8192)%2==0 then
   if i.protocolNumber==6 and d.class=='BULK'then
    for _,e in ipairs(sockets.tcp)do
     if e.LocalPort==i.original.sport and e.RemoteAddress==i.original.dst and e.RemotePort==i.original.dport and(e.LocalAddress==i.original.src or e.LocalAddress=='0.0.0.0'or e.LocalAddress=='::')then owned=true end
    end
   elseif i.protocolNumber==17 and d.class=='RT'and d.budgetAdmitted==true then
    for _,e in ipairs(sockets.udp)do
     if e.LocalPort==i.original.sport and(e.LocalAddress==i.original.src or e.LocalAddress=='0.0.0.0'or e.LocalAddress=='::')then owned=true end
    end
   end
  end
  if owned then flows[#flows+1]=f;assert(#flows<=128,'Candidate count exceeds bounded reader')end
 end
 return flows
end
