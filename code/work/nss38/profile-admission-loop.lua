local n=require('nixio');local fs=require('nixio.fs');local realj=require('luci.jsonc');local counts={};local times={};local last
local function read(path,limit)
 local start=os.clock();local f=assert(io.open(path));local s=f:read(limit+1)or'';f:close();assert(#s<=limit)
 local k=path:find('/proc/',1,true)==1 and'proc'or path:find('/sys/',1,true)==1 and'sys'or'files';counts[k]=(counts[k]or 0)+1;times[k]=(times[k]or 0)+os.clock()-start
 return s
end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function parse(raw)local cpu=os.clock();local v=realj.parse(raw);times.json=(times.json or 0)+os.clock()-cpu;if v and v.publication=='before-software-baseline'then last=v end;return v end
local j={parse=parse,stringify=realj.stringify}
local P=assert(parse([===[__PLAN__]===]));P.boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$','')
local Phase=assert(loadstring([====[__PHASE__]====]))();local Adapter=assert(loadstring([====[__ADAPTER__]====]))()
local function run(s)assert(s:match('^/usr/bin/sha256sum /root/router%-project/classifier/nss23%-[%w%-]+/config.json$'));local f=assert(io.popen(s));local r=f:read(256);f:close();return r end
local a=Adapter.new(P,fs,j,read,now,run,{deadline=now()+40});local initial=Phase.scan(fs,read);local expected={pid=initial.guard.pid,start=initial.guard.start};local rows={};local due=now()+12
local function closed()
 for _,p in ipairs({'front_end_ipv4_stop','front_end_ipv6_stop'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==1)end
 for _,p in ipairs({'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'})do assert(tonumber(read('/sys/kernel/debug/ecm/'..p,128))==0)end
end
local function telemetry()return{uptime=now(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128))}end
local telemetryRows={telemetry()};local observerCpu=os.clock()
repeat
 counts={};times={};local start=now();local cpu=os.clock();closed();local beforeScan=now();local phaseCpu=os.clock();local phaseOk,p=pcall(Phase.scan,fs,read,expected);phaseCpu=os.clock()-phaseCpu;local phaseError;if not phaseOk then phaseError=tostring(p);p={}end;local scanned=now();local inspected=os.clock();local ready,reason,retryable=a.ready();inspected=os.clock()-inspected;local done=now();local q=last and last.snapshot and last.snapshot.provenance
 rows[#rows+1]={at=done,ready=ready,phasePassed=phaseOk,phaseError=phaseError,reason=reason,retryable=retryable,sequence=q and q.sequence,sourceAge=q and done-q.startedAtUptime,publicationDelay=q and last.atUptime-q.startedAtUptime,querySeconds=q and q.finishedAtUptime-q.startedAtUptime,phaseSeconds=scanned-beforeScan,phaseCpuSeconds=phaseCpu,adapterSeconds=done-scanned,adapterCpuSeconds=inspected,iterationSeconds=done-start,iterationCpuSeconds=os.clock()-cpu,fullInventory=p.fullInventory==true,refreshInventory=p.refreshInventory==true,counts=counts,cpuParts=times}
 n.nanosleep(0,20000000)
until now()>=due
closed();telemetryRows[2]=telemetry();print(realj.stringify({routerWrites=false,nssOpened=false,observerCpuSeconds=os.clock()-observerCpu,rows=rows,telemetry=telemetryRows}))
