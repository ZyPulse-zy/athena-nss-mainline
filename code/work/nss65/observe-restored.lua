-- Passive four-second pipeline timing under the existing six-second runner.
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local base,hash=assert(arg[1]),assert(arg[2]);local ram='/tmp/router-project-game-classifier/'
local function read(p,l)local f=assert(io.open(p));local x=f:read(l+1)or'';f:close();assert(#x<=l);return x end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function closed()
 for _,k in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==1)end
 for _,k in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..k,128))==0)end
end
local function telemetry()return{at=now(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),
 txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128))}end
closed();assert(not fs.lstat('/root/router-project/active-transaction'))
assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n')
local initial=assert(j.parse(read(ram..'snapshot.json',4194304)));local producer=assert(initial.producer)
local cache,rows={},{};local replaced=0;local cpu=os.clock();local started=now();local first=telemetry()
local function sample(name)
 local path=ram..name..'.json';local at=now();local st=assert(fs.lstat(path));local prior=cache[name]
 assert(st.type=='reg'and st.uid==0 and st.gid==0 and st.nlink==1)
 if prior and st.dev==prior.dev and st.ino==prior.ino then prior.lastSamePathAt=now();return end
 local f=assert(n.open(path,'r'));local a=assert(f:stat());local parts,bytes={},0
 while true do local s=assert(f:read(65536));if #s==0 then break end;bytes=bytes+#s;assert(bytes<=4194304);parts[#parts+1]=s end
 local z=assert(f:stat());assert(f:close());for _,k in ipairs({'dev','ino','size','mtime','ctime'})do assert(a[k]==z[k],'Publication changed in place')end
 local b=assert(fs.lstat(path));if st.dev~=a.dev or st.ino~=a.ino or a.dev~=b.dev or a.ino~=b.ino then replaced=replaced+1;return end
 local stableAt=now();local value=assert(j.parse(table.concat(parts)));local parsedAt=now()
 assert(value.producer==producer,'Worker producer changed during passive window')
 local p=value.snapshot and value.snapshot.provenance
 local seq=p and p.sequence or value.querySequence;assert(type(seq)=='number')
 rows[#rows+1]={name=name,sequence=seq,readStartedAt=at,heldReadCompletedAt=stableAt,parsedAt=parsedAt,
  previousSamePathAt=prior and prior.lastSamePathAt,bytes=bytes,publishedAt=value.atUptime,
  queryStarted=p and p.startedAtUptime,queryFinished=p and p.finishedAtUptime,flows=value.snapshot and #value.snapshot.flows,
  dataHealthy=value.dataHealthy,error=value.error}
 cache[name]={dev=a.dev,ino=a.ino,lastSamePathAt=stableAt}
end
repeat
 closed();for _,name in ipairs({'classification','request','apply-result','snapshot'})do sample(name)end
 n.nanosleep(0,50000000)
until now()>=started+4
closed();local last=telemetry();print(j.stringify({passed=true,readonly=true,nssAdmissionAllowed=false,productionInstrumentation=false,
 trafficGenerated=false,originalClassifierUnchanged=true,startedAt=started,finishedAt=now(),observerCpuSeconds=os.clock()-cpu,
 publicationReplacementsSkipped=replaced,rows=rows,telemetry={first,last},visibilityTimesAreObservationBounds=true}))
