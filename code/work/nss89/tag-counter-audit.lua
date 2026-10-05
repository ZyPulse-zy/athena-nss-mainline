function M.tagCounterAudit(c,allowPending,prior)
 local function value(v)
  assert(type(v)=='number'and v>=0 and v%1==0 and v<=9007199254740991,'Invalid tag counter')
 end
 local function counter(v)
  assert(type(v)=='table','Tag counter missing');value(v.packets);value(v.bytes)
  assert((v.packets==0)==(v.bytes==0),'Inconsistent tag counter')
 end
 local function safe(a)
  for _,k in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do
   counter(a[k..'_total']);counter(a[k..'_expected']);counter(a[k..'_unexpected'])
   assert(a[k..'_unexpected'].packets==0 and a[k..'_unexpected'].bytes==0,'Unexpected tag observed')
  end
  counter(a.udp_post_neighbor_nonzero)
  assert(a.udp_post_neighbor_nonzero.packets==0 and a.udp_post_neighbor_nonzero.bytes==0,'Neighbor received controlled tag')
 end
 safe(c);if prior then safe(prior)end
 local pending,skew=false,false
 for _,k in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do
  local t,e=c[k..'_total'],c[k..'_expected']
  for _,unit in ipairs({'packets','bytes'})do
   if t[unit]~=e[unit]then skew=true end
   if prior then
    local a,b=prior[k..'_total'],prior[k..'_expected']
    assert(t[unit]>=a[unit]and e[unit]>=b[unit],'Tag counter regressed')
    assert(a[unit]<=e[unit]and b[unit]<=t[unit],'Tag counter snapshots do not overlap')
   end
  end
  if t.packets==0 or e.packets==0 then
   if prior or not skew then
    assert(allowPending==true and t.packets==0 and e.packets==0,'Tag getter lacks bidirectional traffic')
   end
   pending=true
  end
 end
 return{pending=pending,needsSecond=skew and not prior,bracketValidated=prior~=nil}
end
