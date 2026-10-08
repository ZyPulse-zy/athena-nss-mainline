-- Router-local all-LAN flow state. Pure policy: no network/configuration writes.
local M = {}
local function integer(v, low, high)
  v = tonumber(v)
  return v and v == math.floor(v) and v >= low and v <= high and v or nil
end
local function ipnumber(s)
  if type(s) ~= 'string' then return nil end
  local a,b,c,d = s:match('^(%d+)%.(%d+)%.(%d+)%.(%d+)$')
  a,b,c,d = integer(a,0,255),integer(b,0,255),integer(c,0,255),integer(d,0,255)
  if not (a and b and c and d) then return nil end
  return ((a*256+b)*256+c)*256+d
end
local function tuple(t)
  if type(t) ~= 'table' or not ipnumber(t.src) or not ipnumber(t.dst) or
     not integer(t.sport,1,65535) or not integer(t.dport,1,65535) then return nil end
  return table.concat({t.src,t.sport,t.dst,t.dport},':')
end
local function identity(f, cfg, wans)
  local i = f.identity or {}
  local o,r = tuple(i.original),tuple(i.reply)
  local id,zone,mark,wan = integer(i.connectionId,1,4294967295),integer(i.zone,0,65535),
    integer(i.mark,0,4294967295),integer(i.wan,1,5)
  if not (o and r and id and zone == 0 and mark and wan) then return nil,'identity-unverified' end
  if i.protocolNumber ~= 6 and i.protocolNumber ~= 17 then return nil,'protocol-unsupported' end
  local address = ipnumber(i.original.src)
  local size = 2^(32-cfg.lanBits)
  if math.floor(address/size) ~= math.floor(ipnumber(cfg.lanAddress)/size) then return nil,'outside-lan' end
  if math.floor(mark/8192)%2 == 1 then return nil,'proxy-software-path' end
  if math.floor(mark/65536)%256 ~= wan or wans['rpwan'..wan] ~= i.reply.dst or
     i.original.dst ~= i.reply.src or i.original.dport ~= i.reply.sport then
    return nil,'wan-or-nat-changed'
  end
  local q = i.queryProvenance or {}
  if i.instanceTagSafe ~= true or i.instanceMetadataComplete ~= true or
     q.idFieldPresent ~= true or q.fullMarkFieldPresent ~= true or
     not (q.zoneSource == 'successful-explicit-zone0-query' or q.zoneSource == 'explicit-row-zone0') then
    return nil,'conntrack-provenance-unverified'
  end
  return table.concat({'init_net',zone,id,i.protocolNumber,o,r,mark},'|')
end
local function frame_ok(p, now)
  local s = p and p.snapshot
  local q = s and s.provenance
  return p and p.status == 'running' and p.dataHealthy == true and p.nssPermit == false and
    type(p.producer) == 'string' and type(s.flows) == 'table' and type(q) == 'table' and
    q.boot == p.boot and q.queryFamily == 'ipv4' and q.queryZone == 0 and q.exitCode == 0 and
    integer(q.sequence,1,4503599627370496) and type(q.startedAtUptime) == 'number' and
    type(q.finishedAtUptime) == 'number' and q.finishedAtUptime >= q.startedAtUptime and
    q.finishedAtUptime-q.startedAtUptime <= 2 and now >= q.finishedAtUptime and
    now < q.startedAtUptime+6
end
function M.new(cfg)
  assert(cfg.version == 1 and cfg.mode == 'shadow','Only the read-only shadow backend is released')
  assert(ipnumber(cfg.lanAddress) and integer(cfg.lanBits,16,30))
  assert(integer(cfg.maxTracked,1,2048) and integer(cfg.maxCandidates,1,cfg.maxTracked))
  return {cfg=cfg,entries={},sequence=0,producer=nil,retired=0}
end
local function ordered(entries)
  local rows = {}; for _,e in pairs(entries) do rows[#rows+1]=e end
  table.sort(rows,function(a,b)
    if (a.class=='RT') ~= (b.class=='RT') then return a.class=='RT' end
    if a.rateKbps ~= b.rateKbps then return a.rateKbps > b.rateKbps end
    return a.key < b.key
  end)
  return rows
end
function M.tick(state, projection, full, topology, now)
  local operations, seen, cfg = {},{},state.cfg
  local function retire(key, reason)
    local e=state.entries[key]; if not e then return end
    operations[#operations+1]={op='revoke',key=key,reason=reason,hardwareWrite=false}
    state.entries[key]=nil; state.retired=state.retired+1
  end
  -- An unavailable projection only stops renewal. Its absence is not CT exit.
  local fresh=frame_ok(projection,now)
  local complete=false
  if fresh then
    local q=projection.snapshot.provenance
    if state.producer and state.producer ~= projection.producer then
      for key in pairs(state.entries) do retire(key,'classifier-instance-changed') end
      state.sequence=0
    end
    if q.sequence < state.sequence then fresh=false end
    if fresh then
      state.producer=projection.producer; state.sequence=q.sequence
      complete=frame_ok(full,now) and full.producer==projection.producer and
        full.snapshot.provenance.sequence==q.sequence and not full.snapshot.admissionProjection
      local source=complete and full or projection
      local proposed={}
      for _,f in ipairs(source.snapshot.flows) do
        local key,reason=identity(f,cfg,topology.wans or {})
        local i,d=f.identity or {},f.decision or {}
        local qp=i.queryProvenance or {}
        local expiry=tonumber(f.validUntilUptime)
        if key and qp.querySequence==q.sequence and expiry and expiry>now and
           expiry<=q.startedAtUptime+6 and f.observationStartedAtUptime==q.startedAtUptime then
          local client=(topology.clients or {})[i.original.src]
          local binding=client and client.valid and (client.mac..'|'..client.ifname) or nil
          local previous=state.entries[key]
          if previous and previous.binding~=binding then retire(key,'client-or-egress-changed'); previous=nil end
          local class=({RT=true,BULK=true,BE=true,UNKNOWN=true})[d.class] and d.class or 'UNKNOWN'
          local candidate=binding and ((class=='RT' and d.budgetAdmitted==true) or
            (class=='BULK' and d.reason=='bulk') or (cfg.includeBestEffort==true and class=='BE')) or false
          -- QoS class and actual acceleration are separate. No unverified Wi-Fi
          -- or shared-budget path is silently enabled by discovery.
          local e={key=key,connectionId=tonumber(i.connectionId),zone=0,namespace='init_net',
            client=i.original.src,mac=client and client.mac,egress=client and client.ifname,
            wireless=client and client.wireless or false,binding=binding,wan=i.wan,mark=i.mark,
            original=i.original,reply=i.reply,protocol=i.protocolNumber,class=class,
            policyGeneration=cfg.policyGeneration,validUntil=expiry,sequence=q.sequence,
            rateKbps=tonumber(d.rateKbps) or 0,budgetAdmitted=d.budgetAdmitted==true,
            candidate=candidate,accelerated=false,backend='software',
            softwareProtectionVerified=f.applied and f.applied.verified==true or false,
            reason=not binding and (client and client.reason or 'client-egress-unverified') or
              candidate and 'dynamic-nss-and-egress-qos-unverified' or reason or 'software-class',
            classificationFresh=true}
          proposed[key]=e; seen[key]=true
          operations[#operations+1]={op=previous and 'renew' or 'add',key=key,hardwareWrite=false}
        end
      end
      if complete then for key in pairs(state.entries) do if not seen[key] then retire(key,'absent-from-complete-observation') end end end
      local ranked=ordered(proposed)
      for n,e in ipairs(ranked) do
        if n<=cfg.maxTracked then state.entries[e.key]=e else retire(e.key,'software-table-capacity') end
      end
    end
  end
  for key,e in pairs(state.entries) do if now>=e.validUntil then retire(key,'classification-lease-expired') end end
  local rows=ordered(state.entries)
  -- Table capacity is about controller cost, not per-person download quotas.
  for n=#rows,cfg.maxTracked+1,-1 do retire(rows[n].key,'software-table-capacity'); table.remove(rows,n) end
  local summary={version=1,mode='shadow',running=true,atUptime=now,sourceFresh=not not fresh,
    sourceSequence=state.sequence,completeObservation=not not complete,tracked=#rows,
    retired=state.retired,candidates=0,candidateOverflow=0,accelerated=0,
    classes={RT=0,BULK=0,BE=0,UNKNOWN=0},clients=0,exits={},hardwareWrites=false,
    softwareBackend='existing-classifier-and-CAKE',softwareProtectionVerified=0,
    hardwareBackend='not-installed',perDeviceQuotas=false}
  local clients={}
  for _,e in ipairs(rows) do
    summary.classes[e.class]=summary.classes[e.class]+1;clients[e.client]=true
    if e.egress then summary.exits[e.egress]=(summary.exits[e.egress] or 0)+1 end
    if e.softwareProtectionVerified then summary.softwareProtectionVerified=summary.softwareProtectionVerified+1 end
    if e.candidate then
      if summary.candidates<cfg.maxCandidates then summary.candidates=summary.candidates+1
      else e.candidate=false;e.reason='candidate-capacity-software-fallback';summary.candidateOverflow=summary.candidateOverflow+1 end
    end
  end
  for _ in pairs(clients) do summary.clients=summary.clients+1 end
  return {summary=summary,flows=rows,operations=operations}
end
M.ipnumber=ipnumber
return M
