-- Called by the detached owner with acceleration stopped. One immutable epoch.
local M={}
function M.new(P,fs,j,read,now,stopped,command,record,classifier,qos,normalizer,fast)
 local T=P.tagPlan.table;assert(T:match('^rp_nss16_[a-f0-9]+$'))
 local PLAN=P.tagPlan;local expected=normalizer(PLAN.expected,PLAN)
 local owned=false;local due;local out={}
 local function nft(args,payload)
  local c='/usr/bin/timeout -k 1 3 /usr/sbin/nft '..args
  if payload then assert(not payload:find('\n',1,true));c=c.." <<'NSS19_NFT_JSON'\n"..payload..'\nNSS19_NFT_JSON\n'end
  return command(c)
 end
 local function exists()
  local n=0;for _,x in ipairs(assert(j.parse(nft('-j list tables'))).nftables)do
   if x.table and x.table.family=='inet'and x.table.name==T then n=n+1 end
  end;assert(n<=1);return n==1
 end
 local function live()
  -- Listing the exact owned table already fails if it is absent. Validate its
  -- complete native contents directly without a redundant table inventory.
  local raw=nft('-j list table inet '..T)
  assert(normalizer(assert(j.parse(raw)),PLAN)==expected,'Tag table changed')
  return assert(j.parse(raw))
 end
 function out.cleanup()
  if not owned then return end;stopped();live()
  nft('delete table inet '..T);assert(not exists());owned=false;record.tagsRemoved=true
 end
 function out.run(deadline)
  stopped();assert(not exists());assert(now()<deadline-13)
  local step=classifier(P,fs,j,read,now,command,record)
  record.classifierSnapshots={}
  assert(fast,'Long-running classifier consumer requires bounded fast-path owner')
  fast.align(deadline);stopped()
  local snapshot=step();local pair={}
  for _,f in ipairs(snapshot.flows)do for _,slot in ipairs({'tcp','udp','tcp2'})do local w=P.selected[slot];if f.key==w.classifierKey then assert(not pair[slot]);pair[slot]=f end end end
  assert(pair.tcp and pair.udp and pair.tcp2 and pair.tcp2.decision.class=='BULK'and pair.tcp.decision.class=='BULK'and pair.udp.decision.class=='RT'and pair.udp.decision.budgetAdmitted,'Current permanent classifier did not admit exact pair')
  local chosen={pair=pair,provenance=snapshot.provenance}
  record.classifierSnapshots={{flows={pair.tcp,pair.udp,pair.tcp2},selection=snapshot.selection,provenance=snapshot.provenance}}
  due=chosen.provenance.startedAtUptime+5
  assert(now()<due-3,'Classified epoch aged before tag publication')
  for _,slot in ipairs({'tcp','udp','tcp2'})do
   local f=chosen.pair[slot];local a=f.identity;local w=P.selected[slot]
   assert(a.instanceTagSafe and a.instanceMetadataComplete and tonumber(a.zone)==0 and tonumber(a.connectionId)==w.id and a.mark==w.mark and a.wan==w.wan)
   for _,d in ipairs({'original','reply'})do for _,k in ipairs({'src','dst','sport','dport'})do assert(a[d][k]==w[d][k],'Connection identity drift')end end
   assert(f.validUntilUptime>due and now()<f.validUntilUptime-1)
  end
  record.classifiedChoice=assert(j.parse(j.stringify(chosen)));record.tagEpochUntil=due
  local batch={nftables={}}
  for i,x in ipairs(PLAN.expected.nftables)do batch.nftables[i]={[i==1 and'create'or'add']=x}end
  local payload=assert(j.stringify(batch));assert(#payload<49152);nft('-c -j -f -',payload)
  assert(now()<due-2);owned=true;nft('-j -f -',payload)
  record.tagsApplied=true;record.tagsAppliedAt=now()
  record.qosBeforeTags=assert(j.parse(j.stringify(record.qosReady)));record.qosBeforeTagsIsSetupSnapshot=true
  if fast then fast.run(due,live,qos,function()record.tagsAfter=live();record.qosAfterTags=qos.snapshot();out.cleanup()end)else
   local hold=math.min(due-0.25,now()+2.5)
   while now()<hold do stopped();require('nixio').nanosleep(0,50000000)end
  end
  if owned then record.tagsAfter=live();record.qosAfterTags=qos.snapshot()end;stopped()
  out.cleanup();record.automaticPacketTagsCompleted=true
 end
 return out
end
return M
