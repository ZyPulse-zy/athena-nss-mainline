-- Game-only owned nft lifecycle. Never stops source/native, changes queues,
-- account routes/NAT, or the original five-account bucket/sticky objects.
local root=assert(debug.getinfo(1,'S').source:match('^@(.*)/[^/]+$'))
local game=dofile(root..'/game_wan6.lua')
local gameGate=dofile(root..'/game_wan6_health.lua')
local M={configPath='/root/router-project/policy/wan6-game.json',flagPath='/root/router-project/policy/wan6-game.enabled',ownerPath='/root/router-project/policy/wan6-game-owner.json'}
function M.cache_ready(cfg,epoch,gateHeader)
 return game.current(cfg,epoch) and type(gateHeader)=='string' and gateHeader:match('^abi=2 capacity=32 stopping=0 ')~=nil
  and gateHeader:find('wan_max=6',1,true)~=nil and not gateHeader:find('state=5 ',1,true) and not gateHeader:find('state=2 ',1,true)
end
function M.owner_accepts(owner,sha)
 return type(owner)=='table' and owner.version==2 and owner.policyId=='athena-wan6-game-v2' and type(sha)=='string' and (sha==owner.configSha or sha==owner.pendingConfigSha)
end
function M.cleanup_text(choose,tableText)
 local lines={};local hooks=0
 for line in choose:gmatch('[^\n]+')do
  if line:find('comment "athena-wan6-first-packet"',1,true)then
   assert(line:find('jump athena_game_wan6',1,true),'Foreign game hook target')
   local h=assert(line:match('# handle (%d+)'));hooks=hooks+1;assert(hooks<=1,'Duplicate game hooks')
   lines[#lines+1]='delete rule inet rp_pbr choose handle '..h
  end
 end
 if tableText:find('chain athena_game_wan6 {',1,true)then
  lines[#lines+1]='flush chain inet rp_pbr athena_game_wan6';lines[#lines+1]='delete chain inet rp_pbr athena_game_wan6'
 end
 for _,name in ipairs({'athena_wan6_ready','athena_wan6_excluded','athena_wan6_generic_ready','athena_wan6_generic_rate'})do
  if tableText:find('set '..name..' {',1,true)then lines[#lines+1]='delete set inet rp_pbr '..name end
 end
 local names={};for name in tableText:gmatch('set (athena_wan6_game_%d+) {')do names[#names+1]=name end;table.sort(names)
 for _,name in ipairs(names)do lines[#lines+1]='delete set inet rp_pbr '..name end
 return #lines>0 and table.concat(lines,'\n')..'\n' or ''
end
function M.runtime()
 local fs=require('nixio.fs');local n=require('nixio');local j=require('luci.jsonc')
 local directory='/tmp/router-project-health';local statePath=directory..'/wan6-game-control.json'
 local function read(p,cap,optional)
  local f=io.open(p);if not f then assert(optional,'Missing '..p);return nil end
  local s=f:read((cap or 262144)+1);f:close();assert(#s<=(cap or 262144),'Bounded game read exceeded');return s
 end
 local function json(p,optional)local s=read(p,262144,optional);return s and assert(j.parse(s),'Invalid policy JSON')end
 local function secure(p)
  local a=assert(fs.lstat(p));assert(a.type=='reg' and a.uid==0 and a.gid==0 and a.modedec==600 and a.nlink==1,'Unsafe game policy file')
 end
 local function quote(s)return "'"..s:gsub("'","'\\''").."'"end
 local function run(c)
  local f=assert(io.popen(c..' 2>&1; printf "\\nGAME_RC_%s\\n" "$?"'));local s=f:read(1048705);f:close();assert(#s<=1048704)
  local body,rc=s:match('^(.*)\nGAME_RC_(%d+)\n$');assert(body and rc=='0','Game-only command failed: '..c);return body
 end
 local function write(p,s)
  local tmp=p..'.new';local a=fs.lstat(tmp);if a then assert(a.type=='reg' and a.uid==0 and a.nlink==1)end
  local f=assert(io.open(tmp,'w'));assert(f:write(s));assert(f:close());assert(fs.chmod(tmp,600));assert(fs.rename(tmp,p))
 end
 local function sha(p)return assert(run('sha256sum '..quote(p)):match('^(%x+) '))end
 local function transaction(text)
  if text==''then return end
  write(directory..'/wan6-game-transaction.nft',text)
  run('nft -c -f '..directory..'/wan6-game-transaction.nft');run('nft -f '..directory..'/wan6-game-transaction.nft')
 end
 local function observed()return run('nft -a list chain inet rp_pbr choose'),run('nft list table inet rp_pbr')end
 local out={}
 function out.remove()
  local choose,tableText=observed();transaction(M.cleanup_text(choose,tableText))
  if fs.lstat(M.flagPath)then secure(M.flagPath);assert(fs.remove(M.flagPath))end
  local o=json(M.ownerPath,true);if o then secure(M.ownerPath);o.enabled=false;write(M.ownerPath,j.stringify(o))end
  write(statePath,j.stringify({enabled=false,atEpoch=os.time(),configurationRetained=true,existingCtMigration=false,configSha=o and o.configSha,pendingConfigSha=o and o.pendingConfigSha}))
  return{disabled=true,gameObjectsRemoved=true,nativeStopped=false,originalFivePoolChanged=false,existingCtMigrated=false}
 end
 function out.prepare()
  secure(M.configPath);local cfg=json(M.configPath);game.validate(cfg);assert(game.current(cfg,os.time()),'Relay snapshot already stale')
  local choose,tableText=observed();assert(M.cleanup_text(choose,tableText)=='','Game objects already exist')
  write(directory..'/wan6-game-transaction.nft',game.render(cfg));run('nft -c -f '..directory..'/wan6-game-transaction.nft')
  return{prepared=true,relayCount=game.validate(cfg),dataPlaneWrites=false,maximumSnapshotAgeDays=7}
 end
 function out.install()
  secure(M.configPath);local cfg=json(M.configPath);assert(cfg.enabled==true and game.current(cfg,os.time()))
  local choose,tableText=observed();assert(M.cleanup_text(choose,tableText)=='','Foreign or existing game objects')
  transaction(game.render(cfg));write(M.flagPath,'enabled\n')
  write(M.ownerPath,j.stringify({version=2,policyId='athena-wan6-game-v2',enabled=true,configSha=sha(M.configPath),sourceRevision=cfg.sourceRevision}))
  write(statePath,j.stringify({enabled=true,configSha=sha(M.configPath),sourceRevision=cfg.sourceRevision,sourceFetchedAtEpoch=cfg.sourceFetchedAtEpoch,installedAtEpoch=os.time(),boot=read('/proc/sys/kernel/random/boot_id',128):match('%S+')}))
  return{enabled=true,readyLeaseInitiallyEmpty=true,relayCount=game.validate(cfg),originalFivePoolChanged=false,existingCtMigration=false}
 end
 function out.tick(wan6Health)
  secure(M.configPath);local cfg=json(M.configPath);game.validate(cfg);local epoch=os.time();local s=json(statePath,true) or {}
  local choose,tableText=observed();local shaNow=sha(M.configPath);local didRefresh=false
  secure(M.ownerPath);local owner=json(M.ownerPath);assert(M.owner_accepts(owner,shaNow),'Configuration has no matching persistent owner')
  local boot=read('/proc/sys/kernel/random/boot_id',128):match('%S+')
  local bootstrapped=s.boot~=boot or not tableText:find('chain athena_game_wan6 {',1,true) or owner.pendingConfigSha~=nil
  if bootstrapped then
   -- Rebuild only our game namespace after a boot/table reload or interrupted
   -- registered cache update. Empty readiness prevents new WAN6 admissions
   -- until current authentication/source/budgets/kernel facts are checked.
   transaction(M.cleanup_text(choose,tableText)..game.render(cfg))
   owner.configSha=shaNow;owner.pendingConfigSha=nil;owner.enabled=true;write(M.ownerPath,j.stringify(owner))
   s.configSha=shaNow;s.boot=boot;choose,tableText=observed()
  end
  -- Once daily in the existing health loop, not a new process/service/schedule.
  -- Retry a failed bounded download at most hourly; keep the last verified cache.
  if epoch>=cfg.sourceFetchedAtEpoch+cfg.refreshAfterSeconds and epoch>=(s.lastRefreshAttempt or 0)+3600 then
   s.lastRefreshAttempt=epoch;write(statePath,j.stringify(s))
   local temp=directory..'/wan6-steam-sdr.json'
   local ok,fresh=pcall(function()
    -- The site's default DNS deliberately supplies proxy Fake-IP addresses.
    -- Resolve this one maintenance hostname through the reviewed campus DNS;
    -- keep global DNS/proxy unchanged and retain normal TLS hostname checks.
    local answer=run('/usr/bin/timeout -k 1 4 nslookup api.steampowered.com '..cfg.resolverIPv4)
    local addresses={};local section=false
    for line in answer:gmatch('[^\n]+')do
     if line:match('^Name:%s+api%.steampowered%.com%s*$')then section=true end
     if section then local ip=line:match('^Address:%s+(%d+%.%d+%.%d+%.%d+)%s*$');if ip then addresses[#addresses+1]=ip end end
    end
    assert(#addresses>0 and #addresses<=32,'Real official API IPv4 address missing')
    local ip=addresses[1];local parts={};for x in ip:gmatch('%d+')do assert(tonumber(x)<=255);parts[#parts+1]=x end;assert(#parts==4)
    assert(game.public_ipv4(ip),'Resolver returned a non-public API address')
    run("umask 077; curl --noproxy '*' --resolve 'api.steampowered.com:443:"..ip.."' --fail --silent --show-error --proto '=https' --connect-timeout 2 --max-time 5 --max-filesize 1048576 -o "..temp.." 'https://api.steampowered.com/ISteamApps/GetSDRConfig/v1/?appid=730'")
    local raw=assert(read(temp,1048576));local data=assert(j.parse(raw));return game.from_sdr(cfg,data,sha(temp),epoch)
   end)
   if fs.lstat(temp)then assert(fs.remove(temp))end
   if ok then
    -- Apply exact game-owned replacement atomically. Old five maps and all
    -- conntrack affinity stay intact, including already established WAN6 flows.
    local rawConfig=j.stringify(fresh);write(directory..'/wan6-game-cache-candidate.json',rawConfig)
    owner.pendingConfigSha=sha(directory..'/wan6-game-cache-candidate.json');write(M.ownerPath,j.stringify(owner))
    local text=M.cleanup_text(choose,tableText)..game.render(fresh);transaction(text)
    write(M.configPath,rawConfig);cfg=fresh;shaNow=sha(M.configPath)
    assert(shaNow==owner.pendingConfigSha);owner.configSha=shaNow;owner.pendingConfigSha=nil;owner.sourceRevision=cfg.sourceRevision;write(M.ownerPath,j.stringify(owner))
    assert(fs.remove(directory..'/wan6-game-cache-candidate.json'))
    s.lastRefreshSucceeded=true;s.refreshError=nil;didRefresh=true
   else s.lastRefreshSucceeded=false;s.refreshError='bounded-official-relay-refresh-failed' end
  end
  assert(s.configSha==shaNow or didRefresh,'Policy changed outside the owned update')
  -- Re-read readiness after a possible bounded network refresh, never renew
  -- a lease from the health loop's earlier timestamp or cached interface.
  local nr=assert(j.parse(assert(read('/tmp/athena-dorm-native/status.json',4194304))))
  local iface=assert(j.parse(run('ubus call network.interface.campus6 status')))
  local uptime=tonumber(read('/proc/uptime',128):match('^[%d.]+'))
  local boot=read('/proc/sys/kernel/random/boot_id',128):match('%S+')
  local eligible=gameGate.state(nr,iface,wan6Health,uptime,boot)
  epoch=os.time()
  eligible.policyCurrent=cfg.enabled==true and M.cache_ready(cfg,epoch,read('/sys/kernel/debug/athena_ecm_gate/status',65536,true))
  transaction(game.ready_update(eligible,cfg))
  s.enabled=true;s.configSha=shaNow;s.atEpoch=epoch;s.sourceRevision=cfg.sourceRevision;s.sourceFetchedAtEpoch=cfg.sourceFetchedAtEpoch;s.relayCount=game.validate(cfg);s.ready=eligible.ready and eligible.policyCurrent or false
  s.smallUdpEnabled=cfg.smallUdp and cfg.smallUdp.enabled==true or false
  write(statePath,j.stringify(s));return{ready=s.ready,relayCount=s.relayCount,smallUdpEnabled=s.smallUdpEnabled,sourceRevision=s.sourceRevision,snapshotAgeSeconds=epoch-cfg.sourceFetchedAtEpoch,lastRefreshSucceeded=s.lastRefreshSucceeded}
 end
 -- POSIX lock serializes activation, lease renewal, refresh and rollback.
 -- Inherited subprocesses cannot race on the shared transaction file.
 for key,fn in pairs(out)do
  local method=fn
  out[key]=function(...)
   local lockPath='/tmp/router-project-game-policy.lock';local a=fs.lstat(lockPath)
   if a then assert(a.type=='reg' and a.uid==0 and a.gid==0 and a.modedec==600 and a.nlink==1)end
   local fd=assert(n.open(lockPath,'w','600'));assert(fd:lock('lock'))
   local ok,result=pcall(method,...);assert(fd:lock('ulock'));assert(fd:close())
   if not ok then error(result)end;return result
  end
 end
 return out
end
return M
