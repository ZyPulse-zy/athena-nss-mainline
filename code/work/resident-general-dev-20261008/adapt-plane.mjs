import assert from 'node:assert/strict';
export const luaSlots="local function AS(t)local a={}for _,s in ipairs({'tcp','udp','tcp2'})do if t[s]then a[#a+1]=s end end;assert(#a>0 and #a<=3);return a end;local function NS(t)local a=AS(t);for i,s in ipairs(a)do if s=='udp'then a[i]='game'end end;return a end;";
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
export function adaptPlane(name,source){
 let s=source.replaceAll('\r\n','\n');
 if(name==='classifier.lua'){
  s=once(s,"for _,slot in ipairs({'tcp','udp','tcp2'})do\n  local w=assert(selected[slot]);","for _,slot in ipairs(AS(selected))do\n  local w=assert(selected[slot]);");
  s=once(s," assert(selected.tcp.wan~=selected.tcp2.wan,'Distinct naturally selected WANs required')",'');
  s=once(s,"for _,slot in ipairs({'tcp','udp','tcp2'})do\n  local w=type(selected)","for _,slot in ipairs(AS(selected))do\n  local w=type(selected)");
  s=once(s,"#facts.authenticatedSelectedFlows==3","#facts.authenticatedSelectedFlows==#AS(P.selected)");
  s=once(s,"detail.admissionProjectionOnly and(not detail.slots.tcp.present or not detail.slots.udp.present or not detail.slots.tcp2.present)","detail.admissionProjectionOnly and(function()for _,s in ipairs(AS(P.selected))do if not detail.slots[s].present then return true end end;return false end)()");
  s=once(s,'assert(#chosen==3);','assert(#chosen==#AS(P.selected));');
  s=once(s,"affected={'tcp','udp','tcp2'}","affected=AS(P.selected)");
 }
 else if(name==='classified-tags.lua'){
  s=s.replaceAll("ipairs({'tcp','udp','tcp2'})","ipairs(AS(P.selected))");
  s=once(s,"assert(pair.tcp and pair.udp and pair.tcp2 and pair.tcp2.decision.class=='BULK'and pair.tcp.decision.class=='BULK'and pair.udp.decision.class=='RT'and pair.udp.decision.budgetAdmitted,'Current permanent classifier did not admit exact pair')","for _,slot in ipairs(AS(P.selected))do local f=assert(pair[slot]);assert(f.decision.class==(slot=='udp'and'RT'or'BULK')and(slot~='udp'or f.decision.budgetAdmitted))end");
  s=once(s,'flows={pair.tcp,pair.udp,pair.tcp2}',"flows=(function()local a={}for _,s in ipairs(AS(P.selected))do a[#a+1]=pair[s]end;return a end)()");
 }
 else if(name==='qos-physical.lua'){
  s=s.replaceAll("ipairs({'tcp','udp','tcp2'})","ipairs(AS(P.selected))");
  s=once(s,';assert(P.selected.tcp.wan~=P.selected.tcp2.wan)','');
 }
 else if(name==='wan-scope.lua'){
  s=once(s,'#members>=2 and #members<=3','#members>=1 and #members<=3');
  s=once(s,';assert(P.selected.tcp.wan~=P.selected.tcp2.wan)','');
 }
 else if(name==='tag-normalizer.lua'){
  s=once(s,"ipairs({'tcp','udp','tcp2'})","ipairs(AS(PLAN.wanLeafAssignments))");
  s=once(s,'assert(PLAN.wanLeafAssignments.tcp.wan~=PLAN.wanLeafAssignments.tcp2.wan)','');
 }
 else if(name==='fast-path.lua'){
  s=once(s,'function M.tagCounterAudit(c,W,prior)','local function CK(t)local a={}for _,s in ipairs(AS(t))do for _,d in ipairs({"up","down"})do a[#a+1]=s.."_post_"..d end end;return a end\nfunction M.tagCounterAudit(c,W,prior,selected)');
  s=s.replaceAll("ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down','tcp2_post_up','tcp2_post_down'})","ipairs(CK(selected))");
  s=once(s,'  counter(a.udp_post_neighbor_nonzero)\n  assert(a.udp_post_neighbor_nonzero.packets==0 and a.udp_post_neighbor_nonzero.bytes==0,\'Neighbor received controlled tag\')','  if selected.udp then counter(a.udp_post_neighbor_nonzero);assert(a.udp_post_neighbor_nonzero.packets==0 and a.udp_post_neighbor_nonzero.bytes==0,\'Neighbor received controlled tag\')end');
  s=once(s,'function M.verifyRenewalAck(k,p,N)','function M.verifyRenewalAck(k,p,N,selected)');
  s=once(s," assert(k.tcp_permit=='Y'and k.game_permit=='Y'and k.tcp2_permit=='Y','Native lease not live after update')"," for _,slot in ipairs(NS(selected))do assert(k[slot..'_permit']=='Y','Native lease not live after update')end");
  s=once(s,"for _,slot in ipairs({'tcp','game','tcp2'})do\n  assert(k[slot..'_pinned_state']", "for _,slot in ipairs(NS(selected))do\n  assert(k[slot..'_pinned_state']");
  s=once(s,"assert(v and v>=0 and v<=3,'Unexpected ECM scope')","assert(v and v>=0 and v<=#AS(P.selected),'Unexpected ECM scope')");
  s=once(s,'M.tagCounterAudit(c,pending)','M.tagCounterAudit(c,pending,nil,P.selected)');
  s=once(s,'M.tagCounterAudit(next,pending,c)','M.tagCounterAudit(next,pending,c,P.selected)');
  s=s.replaceAll("~=3",'~=#AS(P.selected)');
  s=once(s,'M.verifyRenewalAck(k,p,N)','M.verifyRenewalAck(k,p,N,P.selected)');
  s=once(s,"stopped();assert(P.selected.tcp.wan~=P.selected.tcp2.wan);for _,f in ipairs({P.selected.tcp,P.selected.udp,P.selected.tcp2})do","stopped();for _,slot in ipairs(AS(P.selected))do local f=P.selected[slot];");
  s=once(s,"ipairs({'tcp','game','tcp2'})","ipairs(NS(P.selected))");
  s=once(s,'   R.lastAdmissionProbe=nil','   if not ready and retryable~=true then R.initialAdmissionRefusal=R.lastAdmissionProbe end;R.lastAdmissionProbe=nil');
 }
 else if(name==='module-stage-guardian.lua')s=once(s,"for _,slot in ipairs({'tcp','game','tcp2'})do put", "for _,slot in ipairs(NS(P.selected))do put");
 else throw Error('Unknown plane source '+name);
 return s;
}
