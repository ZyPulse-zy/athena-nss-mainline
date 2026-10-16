local root=assert(arg[0]:match('^(.*)/[^/]+$'));local game=dofile(root..'/game_wan6.lua');local ctl=dofile(root..'/game_wan6_control.lua');local checks=0
local function check(v,m)checks=checks+1;assert(v,m)end
local function copy(t)if type(t)~='table'then return t end;local o={};for k,v in pairs(t)do o[k]=copy(v)end;return o end
local cfg={version=2,enabled=true,provider='steam-sdr-730',resolverIPv4='10.8.8.8',exclusionsReviewed=true,exclusionCidrs={'202.116.0.0/16','155.133.248.100/32'},sourceSha256=string.rep('a',64),sourceRevision=1,sourceFetchedAtEpoch=1000,maximumAgeSeconds=604800,refreshAfterSeconds=86400,relayGroups={{low=27015,high=27044,addresses={'155.133.248.36'}},{low=27015,high=27050,addresses={'155.133.248.37'}}},epoch=1001,ready=true,now=11,at=10}
local packet={family=4,iif='br-lan',direction='original',ctState='new',zone=0,originalPackets=1,mark=0x81000100,metaMark=256,protocol=17,ipBytes=120,sport=41000,dport=27015,dst='155.133.248.36'}
check(game.validate(cfg)==2)
check(game.decide(packet,cfg)==0x81060100)
local tests={
 {'dst','8.8.8.8'}, -- same port/size outside official relay list
 {'dst','202.116.64.144'},{'dst','10.8.8.8'},{'dst','198.18.1.1'},
 {'dst','100.64.1.1'},{'dst','192.0.2.1'},{'dst','203.0.113.1'},
 {'dport',27045},{'dport',443},{'dport',53},{'sport',51820},{'sport',41641},{'sport',1194},
 {'sport',4500},{'sport',500},{'sport',1701},{'sport',1723},{'sport',853},
 {'protocol',6},{'ipBytes',257},{'ipBytes',27},{'zone',1},{'originalPackets',2},
 {'direction','reply'},{'ctState','established'},{'fragmented',true},{'iif','tailscale0'},
 {'mark',0x81010100},{'mark',0x81002100},{'metaMark',0x2000},{'metaMark',65536},
 {'dst','155..133.248.36'},{'dst','155.133.248.999'}
}
for _,t in ipairs(tests)do local p=copy(packet);p[t[1]]=t[2];check(game.decide(p,cfg)==nil,t[1]..' exclusion')end
local p=copy(packet);p.dst='155.133.248.37';p.dport=27050;check(game.decide(p,cfg)==0x81060100,'Use each endpoint published range')
local overlap=copy(cfg);overlap.exclusionCidrs[#overlap.exclusionCidrs+1]='155.133.248.36/32';check(game.decide(packet,overlap)==nil,'Proxy/site exclusion wins over game allowlist')
for _,change in ipairs({function(c)c.enabled=false end,function(c)c.ready=false end,function(c)c.exclusionsReviewed=false end,function(c)c.sourceFetchedAtEpoch=1002 end,function(c)c.epoch=605800 end,function(c)c.now=25 end})do local c=copy(cfg);change(c);check(game.decide(packet,c)==nil,'Deny stale, future, disabled or unreviewed')end
for _,change in ipairs({function(c)c.version=1 end,function(c)c.provider='untrusted' end,function(c)c.relayGroups={}end,function(c)c.relayGroups[1].low=1 end,function(c)c.relayGroups[1].high=65535 end,function(c)c.relayGroups[1].addresses={'127.0.0.1'}end,function(c)c.relayGroups[1].addresses={'1.2.3.4; flush ruleset'}end,function(c)c.relayGroups[2].addresses={'155.133.248.36'}end,function(c)c.maximumAgeSeconds=math.huge end})do local c=copy(cfg);change(c);check(not pcall(game.validate,c),'Reject unsafe config')end
local text=game.render(cfg);check(text:find('ip daddr @athena_wan6_game_1 udp sport 1024-65535 udp dport 27015-27044',1,true)~=nil);check(text:find('ip daddr @athena_wan6_game_2',1,true)~=nil)
check(not text:find('flush ruleset',1,true) and not text:find('flush map',1,true));check(text:find('(ct mark & 0xff00ffff) | 0x00060000',1,true)~=nil)
local base={authenticated=true,healthy=true,nativeRunning=true,sourceFresh=true,wanCount=6,queuesComplete=true,policyCurrent=true}
check(game.ready_update(base):find('add element',1,true)~=nil)
for _,k in ipairs({'authenticated','healthy','nativeRunning','sourceFresh','queuesComplete','policyCurrent'})do local c=copy(base);c[k]=false;check(not game.ready_update(c):find('add element',1,true),k)end
check(ctl.cache_ready(cfg,1001,'abi=2 capacity=32 stopping=0 firmware_receipts=1 wan_max=6\n')==true)
for _,header in ipairs({'','abi=1','abi=2 capacity=32 stopping=1 wan_max=6','abi=2 capacity=32 stopping=0 wan_max=5','abi=2 capacity=32 stopping=0 wan_max=6\nslot=0 state=5 ','abi=2 capacity=32 stopping=0 wan_max=6\nslot=0 state=2 '})do check(not ctl.cache_ready(cfg,1001,header),'Observe actual kernel gate before lease')end
check(not ctl.cache_ready(cfg,605800,'abi=2 capacity=32 stopping=0 wan_max=6'))
local fresh=game.from_sdr(cfg,{success=true,revision=2,pops={one={relays={{ipv4='155.133.248.40',port_range={27015,27060}},{ipv4='155.133.248.41',port_range={27015,27044}}}},partner={partners=2}}},string.rep('b',64),2000)
check(game.validate(fresh)==2 and fresh.sourceRevision==2 and fresh.sourceFetchedAtEpoch==2000 and cfg.sourceRevision==1,'Refresh only bounded official IPv4 relay lists')
for _,data in ipairs({{success=false,revision=2,pops={}},{success=true,revision=2,pops={}},{success=true,revision=2,pops={x={relays={{ipv4='127.0.0.1',port_range={27015,27050}}}}}},{success=true,revision=2,pops={x={relays={{ipv4='155.133.248.40',port_range={1,65536}}}}}}})do check(not pcall(game.from_sdr,cfg,data,string.rep('b',64),2000),'Bad response retains original cache')end
local choose='ct mark & 0x00ff0000 == 0 numgen random mod 300 vmap @buckets # handle 31\njump athena_game_wan6 comment "athena-wan6-first-packet" # handle 90\n'
local tableText='chain choose {\nchain athena_game_wan6 {\nset athena_wan6_ready {\nset athena_wan6_excluded {\nset athena_wan6_game_1 {\nset athena_wan6_game_2 {\nset sticky_w1 {\nmap buckets {\n'
local undo=ctl.cleanup_text(choose,tableText);check(undo:find('delete rule inet rp_pbr choose handle 90',1,true)~=nil);check(not undo:find('handle 31',1,true) and not undo:find('sticky',1,true) and not undo:find('buckets',1,true),'Independent rollback owns game objects only')
check(ctl.cleanup_text('','')=='','Idempotent game rollback')
local owner={version=2,policyId='athena-wan6-game-v2',configSha='old',pendingConfigSha='new'}
check(ctl.owner_accepts(owner,'old') and ctl.owner_accepts(owner,'new'),'Register both exact snapshots across interrupted atomic updates')
check(not ctl.owner_accepts(owner,'foreign'),'Do not adopt an unregistered edit on boot or rollback')
check(not ctl.owner_accepts({version=2,policyId='foreign',configSha='old'},'old'),'Persistent namespace ownership required')
check(not pcall(ctl.cleanup_text,choose..choose,tableText),'Duplicate hooks require inspection')
check(not pcall(ctl.cleanup_text,'jump foreign comment "athena-wan6-first-packet" # handle 90',''),'Do not remove foreign target')
-- A known relay/port identifies the service endpoint, never the process or
-- payload: Steam relay probes/voice or a custom same-service tunnel can match.
local ambiguous=copy(packet);ambiguous.semanticVpn=true;check(game.decide(ambiguous,cfg)~=nil,'Residual ambiguity must remain explicit')
-- Broader first-packet heuristic, deliberately distinct from observed rate.
-- Synthetic exclusions are coverage checks, not a field false-positive rate.
local generic=copy(cfg);generic.smallUdp={enabled=true,maximumIpBytes=256,minimumPort=1024,perHostRate=4,perHostBurst=8,globalRate=16,globalBurst=32}
local unknown=copy(packet);unknown.dst='8.8.8.8';unknown.dport=30000;unknown.udpBytes=100;unknown.payloadByte1=0x55;unknown.payloadWord1=0x55667788;unknown.payloadWord2=0x99aabbcc;unknown.hostRateAllowed=true;unknown.globalRateAllowed=true
local marked,reason=game.decide(unknown,generic);check(marked==0x81060100 and reason=='small-udp-heuristic-candidate','Unknown public endpoint may qualify without a game name')
for _,t in ipairs{{'dport',443},{'dport',53},{'dport',51820},{'dport',3478},{'dport',6881},{'sport',5349},{'dport',1234},{'udpBytes',19},{'udpBytes',237},{'hostRateAllowed',false},{'globalRateAllowed',false},{'payloadWord2',0x2112a442},{'payloadWord1',0x01000000},{'payloadWord1',0x02000000},{'payloadWord1',0x03000000},{'payloadWord1',0x04000000},{'payloadByte1',0xc3},{'payloadByte1',0x21},{'ipBytes',1500},{'dst','202.116.64.144'},{'dst','198.18.1.1'},{'metaMark',0x2000},{'mark',65536},{'protocol',6}}do
 local p=copy(unknown);p[t[1]]=t[2]
 -- 1234 is intentionally an arbitrary high game port and should qualify.
 check((game.decide(p,generic)~=nil)==(t[1]=='dport'and t[2]==1234),'Generic exclusion '..t[1]..'/'..tostring(t[2]))
end
local later=copy(unknown);later.mark=marked;later.originalPackets=2;later.ctState='established';later.ipBytes=1500
check(game.decide(later,generic)==nil,'Later BULK cannot migrate an existing NAT connection')
local indistinguishable=copy(unknown);indistinguishable.semanticVpn=true;indistinguishable.futureRateKbps=100000
check(game.decide(indistinguishable,generic)~=nil,'Custom tunnel or small download handshake remains a possible false positive')
local broad=game.render(generic);check(broad:find('limit rate 4/second burst 8 packets',1,true) and broad:find('limit rate 16/second burst 32 packets',1,true),'Bound both per-host and global first-packet selection')
check(broad:find('size 1024',1,true) and broad:find('meta l4proto @athena_wan6_generic_ready',1,true),'Bounded state and independent expiring generic eligibility')
check(not broad:find(' drop',1,true),'Exclusions and rate failures fall through, never drop')
local expired=copy(base);expired.policyCurrent=false
check(game.ready_update(base,generic):find('{ udp timeout 15s }',1,true)~=nil and not game.ready_update(expired,generic):find('add element',1,true),'Both paths withdraw on stale health/cache')
local undoBroad=ctl.cleanup_text(choose,tableText..'set athena_wan6_generic_ready {\nset athena_wan6_generic_rate {\n')
check(undoBroad:find('delete set inet rp_pbr athena_wan6_generic_rate',1,true) and undoBroad:find('delete set inet rp_pbr athena_wan6_generic_ready',1,true),'Generic rollback removes only owned sets')
local refreshedBroad=game.from_sdr(generic,{success=true,revision=2,pops={x={relays={{ipv4='155.133.248.40',port_range={27015,27060}}}}}},string.rep('b',64),2000)
check(refreshedBroad.smallUdp.enabled and refreshedBroad.smallUdp.perHostRate==4,'Daily relay refresh retains reviewed generic policy')
for _,key in ipairs{'maximumIpBytes','minimumPort','perHostRate','perHostBurst','globalRate','globalBurst'}do local c=copy(generic);c.smallUdp[key]=65535;check(not pcall(game.validate,c),'Reject unbounded generic '..key)end
print(require('luci.jsonc').stringify({passed=true,checks=checks,gameEndpointScope='official-relay-IPv4-with-published-port-intersection',kernelIoMocked=true,realGameMisidentificationRateMeasured=false}))
-- Execute the real runtime in a virtual filesystem/command environment. This
-- exercises boot reconstruction, registered updates and rollback without
-- touching a router, shared nft table, source/native owner or real DNS.
cfg=copy(generic);tableText=tableText..'set athena_wan6_generic_ready {\nset athena_wan6_generic_rate {\n'
local j=require('luci.jsonc');local files={};local epoch=1001;local uptime=101;local boot='test-boot';local installed=false;local rendered='';local refreshFails=false
local oldOpen,oldPopen,oldTime=io.open,io.popen,os.time
local oldFs,oldN=package.loaded['nixio.fs'],package.loaded['nixio'];local oldFsPre,oldNPre=package.preload['nixio.fs'],package.preload['nixio']
local function put(p,t)files[p]=type(t)=='table' and j.stringify(t) or t end
put(ctl.configPath,cfg);put('/proc/sys/kernel/random/boot_id',boot..'\n');put('/proc/uptime','101.00 0.00\n')
local tags={up={wanCount=6,tags={}},down={wanCount=6,tags={}}};for w=1,6 do tags.up.tags[w]={BE=0x7e00+w*16+5,RT=0x7e00+w*16+6};tags.down.tags[w]={BE=0x7a00+w*16+5,RT=0x7a00+w*16+6}end
local nr={wanCount=6,boot=boot,phase='native-running',wans={rpwan6='198.51.100.6'},native={loaded=true,unconfirmed=0,pending=0},ingress=tags,flowState={sourceFresh=true,budgetUpdates={lastSuccessAtUptime=100}}}
put('/tmp/athena-dorm-native/status.json',nr);put('/sys/kernel/debug/athena_ecm_gate/status','abi=2 capacity=32 stopping=0 firmware_receipts=1 wan_max=6\n')
local hashIds,hashNext={},0;local function sha(p)local s=assert(files[p]);if not hashIds[s]then hashNext=hashNext+1;hashIds[s]=string.format('%064x',hashNext)end;return hashIds[s]end
io.open=function(p,mode)
 if mode==nil or mode=='r'then if files[p]==nil then return nil end;return{read=function(_,size)return type(size)=='number' and files[p]:sub(1,size) or files[p]end,close=function()return true end}end
 assert(mode=='w','Unapproved model write mode');local body='';return{write=function(_,s)body=body..s;return true end,close=function()files[p]=body;return true end}
end
local fs={lstat=function(p)if files[p]~=nil then return{type='reg',uid=0,gid=0,modedec=600,nlink=1}end end,chmod=function(p,m)assert(files[p]~=nil and m==600);return true end,rename=function(a,b)assert(files[a]~=nil);files[b]=files[a];files[a]=nil;return true end,remove=function(p)assert(files[p]~=nil);files[p]=nil;return true end}
local nixio={open=function(p,mode,permissions)assert(p=='/tmp/router-project-game-policy.lock' and mode=='w' and permissions=='600');files[p]='';return{lock=function(_,kind)assert(kind=='lock'or kind=='ulock');return true end,close=function()return true end}end}
package.loaded['nixio.fs']=fs;package.loaded['nixio']=nixio;package.preload['nixio.fs']=function()return fs end;package.preload['nixio']=function()return nixio end;os.time=function()return epoch end
io.popen=function(c)
 local body='';local rc=0
 if c:find("sha256sum '",1,true)then body=sha(assert(c:match("sha256sum '([^']+)'")))..'  model\n'
 elseif c:find('nft -a list chain inet rp_pbr choose',1,true)then body=installed and 'jump athena_game_wan6 comment "athena-wan6-first-packet" # handle 90\n' or ''
 elseif c:find('nft list table inet rp_pbr',1,true)then body=installed and tableText or 'map buckets {\nset sticky_w1 {\n'
 elseif c:find('nft -c -f ',1,true)then assert(files['/tmp/router-project-health/wan6-game-transaction.nft']);body=''
 elseif c:find('nft -f ',1,true)then
  rendered=files['/tmp/router-project-health/wan6-game-transaction.nft'];assert(not rendered:find('flush map',1,true) and not rendered:find('ruleset',1,true))
  if rendered:find('add chain inet rp_pbr athena_game_wan6',1,true)then installed=true elseif rendered:find('delete chain inet rp_pbr athena_game_wan6',1,true)then installed=false end
 elseif c:find('ubus call network.interface.campus6 status',1,true)then body=j.stringify({up=true,l3_device='rpwan6',['ipv4-address']={{address='198.51.100.6'}}})
 elseif c:find('nslookup api.steampowered.com 10.8.8.8',1,true)then if refreshFails then rc=1 else body='Server: 10.8.8.8\nName: api.steampowered.com\nAddress: 23.35.148.195\n'end
 elseif c:find('curl ',1,true)then
  assert(c:find('--resolve',1,true)and c:find('--max-filesize 1048576',1,true)and c:find("--proto '=https'",1,true)and not c:find('--insecure',1,true))
  put('/tmp/router-project-health/wan6-steam-sdr.json',{success=true,revision=2,pops={a={relays={{ipv4='155.133.248.40',port_range={27015,27060}}}}}})
 else error('Unapproved runtime command in game model: '..c)end
 return{read=function()return body..'\nGAME_RC_'..rc..'\n'end,close=function()return true end}
end
local ok,err=pcall(function()
 local runtime=ctl.runtime();check(runtime.prepare().dataPlaneWrites==false and not installed,'Prepare must not apply live rules')
 check(runtime.install().enabled and installed and files[ctl.ownerPath]~=nil,'Persist cache owner on initial activation')
 local state=runtime.tick({healthy=true});check(state.ready and rendered:find('add element',1,true)~=nil,'Initial lease')
 check(state.smallUdpEnabled and rendered:find('{ udp timeout 15s }',1,true),'Renew the generic lease from the same real runtime gate')
 -- A live scope edit must register its pending hash. The next health tick
 -- rebuilds the owned objects and updates RAM bookkeeping before renewing.
 local edited=copy(cfg);edited.smallUdp.enabled=false
 local own=j.parse(files[ctl.ownerPath]);put(ctl.configPath,edited);own.pendingConfigSha=sha(ctl.configPath);put(ctl.ownerPath,own)
 state=runtime.tick({healthy=true});check(state.ready and not state.smallUdpEnabled and j.parse(files[ctl.ownerPath]).pendingConfigSha==nil,'Registered narrow live edit replaces cache state')
 own=j.parse(files[ctl.ownerPath]);put(ctl.configPath,cfg);own.pendingConfigSha=sha(ctl.configPath);put(ctl.ownerPath,own)
 state=runtime.tick({healthy=true});check(state.ready and state.smallUdpEnabled and rendered:find('{ udp timeout 15s }',1,true),'Registered broad live edit renews both leases')
 -- A reboot/table reload loses RAM bookkeeping, but verified persistent
 -- owner/config/flag reconstruct only the game namespace and empty lease.
 installed=false;for p in pairs(files)do if p:match('^/tmp/')then files[p]=nil end end
 boot='test-boot-two';put('/proc/sys/kernel/random/boot_id',boot..'\n');nr.boot=boot;put('/tmp/athena-dorm-native/status.json',nr)
 state=runtime.tick({healthy=true});check(state.ready and installed,'Restore verified game policy after RAM/table loss without source/native restart')
 check(state.smallUdpEnabled,'Generic policy survives registered boot/table reconstruction')
 epoch=87400;state=runtime.tick({healthy=true});local owner2=j.parse(files[ctl.ownerPath]);local cached=j.parse(files[ctl.configPath])
 check(state.ready and state.sourceRevision==2 and cached.sourceFetchedAtEpoch==epoch,'Bounded real-address TLS refresh')
 check(owner2.configSha==sha(ctl.configPath) and owner2.pendingConfigSha==nil,'Finalize exact persistent owner after cache update')
 epoch=87400+604800;refreshFails=true;state=runtime.tick({healthy=true});check(not state.ready and not rendered:find('add element',1,true),'Expired cache + failed official refresh returns new flows to original pool')
 check(j.parse(files[ctl.configPath]).sourceRevision==2,'A failed download retains the last verified cache')
 local result=runtime.remove();check(result.disabled and not installed and files[ctl.flagPath]==nil,'Game-only removal keeps source/native untouched')
 check(files[ctl.configPath]~=nil and j.parse(files[ctl.ownerPath]).configSha==sha(ctl.configPath),'Retain exact ownership for later full checkpoint rollback')
end)
io.open,io.popen,os.time=oldOpen,oldPopen,oldTime;package.loaded['nixio.fs'],package.loaded['nixio']=oldFs,oldN;package.preload['nixio.fs'],package.preload['nixio']=oldFsPre,oldNPre
assert(ok,err)
print(j.stringify({passed=true,runtimeChecksCompleted=true,checks=checks,bootRestoreAndDailyRefreshModeled=true,kernelCommandsAndNetworkMocked=true}))
