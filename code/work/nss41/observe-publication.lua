local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local S=assert(j.parse([===[__SPEC__]===]))
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local ram='/tmp/router-project-game-classifier';local cache={};local updates={classification={},snapshot={}};local frames={};local cpuStart=os.clock()
local function publication(name)
 local path=ram..'/'..name..'.json';local st=assert(fs.lstat(path));assert(st.type=='reg'and st.uid==0 and st.gid==0 and st.nlink==1)
 local old=cache[name];if old and st.dev==old.dev and st.ino==old.ino then return old.value end
 local start=now();local s=assert(j.parse(read(path,4194304)));local after=assert(fs.lstat(path));if after.dev~=st.dev or after.ino~=st.ino then return nil end
 assert(s.configSha256==S.configSha256 and s.nssPermit==false and s.status=='running')
 local p=assert(s.snapshot.provenance);local v={observed=now(),readSeconds=now()-start,sequence=p.sequence,producer=s.producer,pid=s.pid,start=s.start,published=s.atUptime,queryStart=p.startedAtUptime,queryFinished=p.finishedAtUptime,flows=#s.snapshot.flows,bytes=st.size}
 cache[name]={dev=st.dev,ino=st.ino,value=v};updates[name][#updates[name]+1]=v;return v
end
local function telemetry()return{uptime=now(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128))}end
local function closed()
 for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
 for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end
end
local first=assert(publication('classification'));local start=now();local due=start+27;local samples={telemetry()}
repeat
 closed();local c=publication('classification');local s=publication('snapshot');local g=assert(j.parse(read(ram..'/guardian.json',8192)))
 assert(g.healthy==true and g.producer==first.producer)
 if c then assert(c.producer==first.producer)end;if s then assert(s.producer==first.producer)end
 local at=now();frames[#frames+1]={at=at,compactSequence=c and c.sequence,compactAge=c and at-c.queryStart,fullSequence=s and s.sequence,fullAge=s and at-s.queryStart,guardianHealthy=g.healthy,telemetry=telemetry()}
 n.nanosleep(0,250000000)
until now()>=due
closed();samples[2]=telemetry();print(j.stringify({readonly=true,routerConfigurationWrites=false,nssOpened=false,seconds=now()-start,observerCpuSeconds=os.clock()-cpuStart,frames=frames,updates=updates,telemetry=samples,workerPhaseNotInstrumented=true}))
