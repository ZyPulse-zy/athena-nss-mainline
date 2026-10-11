-- Full identity, topology, shared budgets and conservative first-packet models.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local j=require('luci.jsonc');local core=dofile(root..'/core.lua')
local contract=dofile(root..'/wan_contract.lua');local plan=dofile(root..'/queue_plan.lua')
local game=dofile(root..'/game_wan6.lua');local tags=dofile(root..'/tag_rules.lua')
local health=dofile(root..'/health.lua');local coverage=dofile(root..'/coverage.lua')
local checks=0;local function check(v,m)checks=checks+1;assert(v,m)end
local function copy(t)if type(t)~='table'then return t end;local o={};for k,v in pairs(t)do o[k]=copy(v)end;return o end
check(contract.profile().wanCount==5)
check(contract.profile({version=1,wanCount=6}).interfaces[6]=='campus6')
for _,bad in ipairs{4,7,6.1,'6',false}do check(not pcall(contract.count,bad))end
check(not pcall(contract.profile,{version=1,wanCount=6,interfaces={'wan1','wan2','wan3','wan4','wan5','wan6'}}))
local instances={};for w=1,6 do instances['wan'..w]={running=true}end
check(contract.service_ready('router-project-minieap',instances,6))
instances.wan6=nil;instances.unrelated={running=true}
check(not contract.service_ready('router-project-minieap',instances,6))
check(contract.service_ready('router-project-autorate',instances,5))
check(contract.interface_ready(6,{up=true,l3_device='rpwan6',['ipv4-address']={{address='198.51.100.6'}}}))
check(not contract.interface_ready(6,{up=true,l3_device='wan',['ipv4-address']={{address='198.51.100.6'}}}))
local macOwner=dofile(root..'/platform/nss-macvlan-owned.lua')
local owner={boot='test',phase='native-running',wanCount=6,baseline={wanLinks={{ifname='rpwan6',address='02:00:00:00:00:66',linkinfo={info_kind='macvlan',info_data={mode='bridge'}}}}}}
check(macOwner.accept('rpwan6','02:00:00:00:00:66',owner,{allowed=true},'test'))
check(not macOwner.accept('rpwan6','02:00:00:00:00:66',owner,{allowed=false},'test'))
check(not macOwner.accept('rpwan6','02:00:00:00:00:67',owner,{allowed=true},'test'))
check(not macOwner.accept('rpwan6','02:00:00:00:00:66',owner,{allowed=true},'other'))
local oldOwner=copy(owner);oldOwner.wanCount=5;check(not macOwner.accept('rpwan6','02:00:00:00:00:66',oldOwner,{allowed=true},'test'))
local rates5={100000,100000,100000,100000,100000}
local rates6={100000,100000,100000,100000,100000,100000}
local old,up,down=plan.plan(0x7e00,rates5),plan.plan(0x7e00,rates6),plan.plan(0x7a00,rates6)
check(up.totalKbps==600000 and down.totalKbps==600000)
for w=1,5 do check(old.tags[w].RT==up.tags[w].RT and old.tags[w].BE==up.tags[w].BE)end
check(up.tags[6].RT==0x7e66 and up.tags[6].BE==0x7e65 and down.tags[6].RT==0x7a66 and down.tags[6].BE==0x7a65)
check(not pcall(plan.changes,old,up),'Topology cannot hot-change qdisc trees')
check(not pcall(plan.plan,0x7e00,{200000,200000,200000,200000,200000,200000}),'Shared physical budget')
local bad=copy(rates6);bad[3]=nil;check(not pcall(plan.plan,0x7e00,bad))
local cfg={version=1,mode='shadow',policyGeneration='six-test',wanCount=6,
 lanAddress='192.168.237.0',lanBits=24,maxTracked=64,maxCandidates=32}
local topology={clients={['192.168.237.12']={valid=true,mac='02:00:00:00:00:12',ifname='lan1'}},wans={}}
local rows={}
for w=1,6 do
 topology.wans['rpwan'..w]='198.51.100.'..w
 rows[w]={identity={connectionId=w,zone=0,wan=w,mark=0x81000000+w*65536+256,protocolNumber=17,
  original={src='192.168.237.12',sport=41000+w,dst='203.0.113.12',dport=27015},
  reply={src='203.0.113.12',sport=27015,dst='198.51.100.'..w,dport=51000+w,bytes=1000},
  instanceTagSafe=true,instanceMetadataComplete=true,
  queryProvenance={idFieldPresent=true,fullMarkFieldPresent=true,zoneSource='explicit-row-zone0',querySequence=1}},
  decision={class='RT',reason='interactive',budgetAdmitted=true,rateKbps=64},
  observationStartedAtUptime=100,validUntilUptime=106}
end
local pub={status='running',dataHealthy=true,nssPermit=false,producer='six-source',boot='test-boot',snapshot={flows=rows,
 selection={untracked=0},provenance={boot='test-boot',queryFamily='ipv4',queryZone=0,exitCode=0,sequence=1,startedAtUptime=100,finishedAtUptime=100.2}}}
local result=core.tick(core.new(cfg),pub,pub,topology,101)
check(result.summary.wanCount==6 and result.summary.candidates==6)
check(coverage.cohort(pub,topology.wans,101,core).rows[result.flows[6].key]~=nil)
local rules={}
for _,f in ipairs(result.flows)do rules[#rules+1]={flow=f,up=up.tags[f.wan].RT*65536+6,down=down.tags[f.wan].RT*65536+6}end
local text=tags.render(rules,{up=up,down=down})
check(text:find('ct mark & 0x00ff0000 == 393216',1,true)~=nil)
check(text:find('meta priority set '..string.format('%.0f',0x7e660006),1,true)~=nil)
check(text:find('meta priority set '..string.format('%.0f',0x7a660006),1,true)~=nil)
for _,mutate in ipairs{
 function(f)f.identity.wan=7 end,function(f)f.identity.wan=0 end,
 function(f)f.identity.mark=f.identity.mark+8192 end,
 function(f)f.identity.mark=f.identity.mark+65536 end,
 function(f)f.identity.reply.dst='198.51.100.99' end,
 function(f)f.identity.zone=1 end,function(f)f.identity.queryProvenance.fullMarkFieldPresent=false end}do
 local f=copy(rows[6]);mutate(f);check(core.observationIdentity(f,cfg,topology.wans)==nil)
end
local cfg5=copy(cfg);cfg5.wanCount=5;check(core.observationIdentity(rows[6],cfg5,topology.wans)==nil)
check(#health.queues('qdisc nssfq_codel 7a66: parent 7a00:66\n Sent 100 bytes 1 pkt (dropped 2, overlimits 0 requeues 0)\n','athenaigs')==1)
for hi=0,255 do for _,low in ipairs{0,6,256,4096,32768,65535}do
 local mark=hi*16777216+low;local fresh=contract.mark(mark,6)
 check(fresh==mark+6*65536 and fresh%65536==low and math.floor(fresh/16777216)==hi)
end end
local packet={family=4,iif='br-lan',direction='original',ctState='new',zone=0,originalPackets=1,
 mark=0x81000100,metaMark=256,protocol=17,ipBytes=120,sport=41000,dport=27015,dst='203.0.113.12'}
local state={enabled=true,exclusionsComplete=true,exclusionCidrs={'203.0.113.240/28'},ready=true,at=100,now=101}
local routed=game.decide(packet,state);check(routed==contract.mark(packet.mark,6))
for k,v in pairs{protocol=6,dport=443,sport=53,ipBytes=1400,originalPackets=2,zone=1,
 ctState='established',direction='reply',iif='tailscale0',fragmented=true,mark=65536,metaMark=8192,
 dst='100.64.0.1'}do
 local p=copy(packet);p[k]=v;check(game.decide(p,state)==nil,k)
end
local p=copy(packet);p.dst='203.0.113.242';check(game.decide(p,state)==nil)
local unknownVpn=copy(packet);unknownVpn.vpn=true;check(game.decide(unknownVpn,state)~=nil,'A semantic label unavailable to nft cannot mask first-packet ambiguity')
for k,v in pairs{enabled=false,ready=false,exclusionsComplete=false,now=115}do local s=copy(state);s[k]=v;check(game.decide(packet,s)==nil,k)end
check(not pcall(game.render,{exclusionsComplete=false,exclusionCidrs={'203.0.113.240/28'}}))
local nft=game.render(state);check(nft:find('ct original packets != 1 return',1,true)~=nil and not nft:find('flush chain',1,true))
check(game.ready_update({wanCount=6}):match('^flush set') and not game.ready_update({wanCount=6}):find('add element',1,true))
local gate=dofile(root..'/game_wan6_health.lua')
local native={wanCount=6,boot='test',phase='native-running',wans={rpwan6='198.51.100.6'},native={loaded=true,unconfirmed=0,pending=0},
 ingress={up=up,down=down},flowState={sourceFresh=true,budgetUpdates={lastSuccessAtUptime=100}}}
local iface={up=true,l3_device='rpwan6',['ipv4-address']={{address='198.51.100.6'}}}
check(gate.state(native,iface,{healthy=true},101,'test').ready==true)
check(gate.state(native,iface,{healthy=true},106,'test').ready==false)
check(gate.state(native,iface,{healthy=true},99,'test').ready==false)
check(gate.state(native,iface,{healthy=true},101,'other-boot').ready==false)
for _,mutate in ipairs{function(n)n.wanCount=5 end,function(n)n.wans.rpwan6='198.51.100.7'end,
 function(n)n.native.unconfirmed=1 end,function(n)n.flowState.sourceFresh=false end,
 function(n)n.ingress.down.tags[6].RT=0 end}do local bad=copy(native);mutate(bad);check(gate.state(bad,iface,{healthy=true},101,'test').ready==false)end
check(gate.state(native,iface,{healthy=false},101,'test').ready==false)
local config=dofile(root..'/source_classifier/prepare_config.lua')
local original={version=23,queues={},policy={interval=3},source={},originalNative={},priorRules={}}
local capture={queues={},native={},boot='test',transaction='test',oldOwnerRecovered=true,nativeStopped=true,noDynamicSelectors=true,ramOwnerRetired=true,ramJournalEmpty=true}
for w=1,6 do for _,prefix in ipairs{'rpwan','rpifb'}do local dev=prefix..w
 local q={root=true,kind='cake',handle=string.format('%x:',0x8000+w*2),options={bandwidth=5000000,diffserv='diffserv4',nat=true,flowmode=prefix=='rpwan'and'dual-srchost'or'dual-dsthost'}}
 capture.queues[dev]=q;capture.native[dev]='filter protocol all pref 41900 matchall chain 0\n'
 if w<=5 then original.queues[dev]=copy(q)end
end end
local hashes={};for _,name in ipairs{'worker.lua','guardian.lua','backend.lua','owned.lua','classifier-core.lua','conntrack-source.lua','stop-worker.lua','cleanup.sh','init.sh','group-runner','process-stop','process-crash'}do hashes[name]=string.rep('a',64)end
local prepared=config.prepare(original,capture,hashes,'nss23-wan6-test')
check(prepared.wanCount==6 and prepared.policy.wanCount==6 and prepared.queues.rpifb6~=nil and original.policy.wanCount==nil)
local bad=copy(capture);bad.oldOwnerRecovered=false;check(not pcall(config.prepare,original,bad,hashes,'nss23-wan6-test'))
bad=copy(capture);bad.ramOwnerRetired=false;check(not pcall(config.prepare,original,bad,hashes,'nss23-wan6-test'))
bad=copy(capture);bad.queues.rpifb5.options.nat=false;check(not pcall(config.prepare,original,bad,hashes,'nss23-wan6-test'))
bad=copy(capture);bad.native.rpwan6='filter protocol ip pref 41001 u32 chain 0';check(not pcall(config.prepare,original,bad,hashes,'nss23-wan6-test'))
local rollout=dofile(root..'/wan6_plan.lua');local facts={rollbackVerified=true,independentGuardianReady=true,
 installedBaselineVerified=true,fiveWansStable=true,protectedFilesPinned=true,physicalMbps=1000,
 table106Free=true,rules906And1006Free=true,campus6Absent=true,rpwan6Absent=true,rpifb6Absent=true,auth6Absent=true,
 wan6OriginalProto='dhcpv6',mac='02:00:00:00:00:66',macUnused=true,gameEnabled=false,firewallZoneName='wan',firewallMasquerade=true,macMapPinned=true}
local deployment=rollout.plan(facts);check(deployment.accountInterface=='campus6' and deployment.existingNatMigration==false)
for _,c in ipairs(deployment.commands)do check(not c:find('network.wan6',1,true) and not c:find('rpwan1',1,true) and not c:find('reboot',1,true))end
facts.independentGuardianReady=false;check(not pcall(rollout.plan,facts))
local undo=rollout.rollback({checkpointOwned=true,bootMatches=true,fileHashesMatch=true})
check(undo[2].advanceOnlyWhen=='nativeStoppedAndFirmwareAbsentAndOriginalPhysicalQueuesRestored')
check(undo[4].existingNatMigration==false and undo[7].advanceOnlyWhen=='noWan6CtAndNoSnapshotTruncation')
check(not pcall(rollout.rollback,{checkpointOwned=true,bootMatches=false,fileHashesMatch=true}))
-- Deliberately include benign traffic indistinguishable from a game. These
-- synthetic counts quantify only this fixture, never a real-world error rate.
local stats={truePositive=0,falsePositive=0,falseNegative=0,trueNegative=0}
for i=1,200 do
 local p=copy(packet);local truth=i<=100
 if i<=80 then p.dport=27015+i%36
 elseif i<=100 then p.dport=30000+i -- missed games retain ordinary WAN QoS
 elseif i<=110 then p.dport=27015 -- identical-looking benign traffic
 else p.dport=443 end
 local selected=game.decide(p,state)~=nil
 local key=truth and(selected and'truePositive'or'falseNegative')or(selected and'falsePositive'or'trueNegative')
 stats[key]=stats[key]+1
end
check(stats.falsePositive==10 and stats.falseNegative==20)
print(j.stringify({passed=true,checks=checks,wanCount=6,dataPlaneWrites=false,
 modelOnly=true,gameFixture=stats,realGameAccuracyMeasured=false,gamePolicyEnabled=false}))
