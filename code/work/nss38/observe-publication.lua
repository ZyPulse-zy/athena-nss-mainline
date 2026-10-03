local n=require('nixio');local fs=require('nixio.fs');local j=require('luci.jsonc');local S=assert(j.parse([===[__SPEC__]===]))
local function read(p,l,optional)local f=io.open(p);if not f then assert(optional);return nil end;local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local base=S.base;local f=assert(io.popen('/usr/bin/sha256sum '..base..'/config.json'));local hash=f:read(256);f:close();assert(hash:match('^(%x+) ')==S.configSha256)
local ram='/tmp/router-project-game-classifier';local cache={};local updates={classification={},snapshot={}};local reads=0;local ioCpu=0
local function publication(name)
 local path=ram..'/'..name..'.json';local stat=assert(fs.lstat(path));assert(stat.type=='reg'and stat.uid==0 and stat.nlink==1)
 local c=cache[name];if c and c.dev==stat.dev and c.ino==stat.ino then return c.value end
 local start=now();local cpu=os.clock();local raw=read(path,4194304);local after=assert(fs.lstat(path));if stat.ino~=after.ino or stat.dev~=after.dev then return nil end
 local s=assert(j.parse(raw));assert(s.configSha256==S.configSha256 and s.nssPermit==false);local p=s.snapshot and s.snapshot.provenance
 local classes={};for _,v in ipairs(s.snapshot and s.snapshot.flows or{})do local k=v.decision.class;classes[k]=(classes[k]or 0)+1 end
 local v={observed=now(),readSeconds=now()-start,bytes=#raw,status=s.status,producer=s.producer,pid=s.pid,start=s.start,published=s.atUptime,sequence=p and p.sequence,queryStart=p and p.startedAtUptime,queryFinished=p and p.finishedAtUptime,sourceRows=p and p.rawRowCount,flows=s.snapshot and #s.snapshot.flows,classes=classes}
 ioCpu=ioCpu+os.clock()-cpu;reads=reads+1;cache[name]={dev=after.dev,ino=after.ino,value=v};updates[name][#updates[name]+1]=v;return v
end
local function stat(pid)
 local raw=read('/proc/'..pid..'/stat',8192,true);if not raw then return nil end
 local values={};for v in assert(raw:match('^%d+ %b() (.*)$')):gmatch('%S+')do values[#values+1]=v end
 return{pid=tonumber(pid),state=values[1],start=values[20],cpuTicks=tonumber(values[12])+tonumber(values[13])}
end
local function children(pid)
 local pending,seen,phases={tostring(pid)},{},{};local total=0
 while #pending>0 do
  local p=table.remove(pending);assert(not seen[p]);seen[p]=true;total=total+1;assert(total<=16,'Unexpected worker subtree')
  local raw=read('/proc/'..p..'/task/'..p..'/children',2048,true)or''
  for child in raw:gmatch('%d+')do
   local cmd=read('/proc/'..child..'/cmdline',8192,true)or''
   for _,mode in ipairs({'apply','audit','recover'})do if cmd:find(base..'/worker.lua\0'..mode..'\0',1,true)then phases[mode]=true end end
   if cmd:find('/usr/sbin/conntrack\0',1,true)then phases.conntrack=true end
   if cmd:find('/sbin/ip\0',1,true)then phases.address=true end
   if cmd:find('/sbin/tc\0',1,true)then phases.tc=true end
   pending[#pending+1]=child
  end
 end
 return phases
end
local function telemetry()return{uptime=now(),cpu=read('/proc/stat',16384):match('^[^\n]+'),softnet=read('/proc/net/softnet_stat',16384),txBytes=tonumber(read('/sys/class/net/lan4/statistics/tx_bytes',128)),txPackets=tonumber(read('/sys/class/net/lan4/statistics/tx_packets',128)),stop4=tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop',128)),accel=tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count',128))}end
local a=assert(publication('classification'));local initialProducer=a.producer;local original=assert(stat(a.pid));assert(original.start==a.start)
local frames={};local telemetryRows={telemetry()};local start=now();local due=start+18;local observerCpu=os.clock()
while now()<due do
 local began=now();local c=publication('classification');local s=publication('snapshot');local p=stat(a.pid);assert(p and p.start==a.start)
 if c then assert(c.producer==initialProducer)end;if s then assert(s.producer==initialProducer)end
 local g=assert(j.parse(read(ram..'/guardian.json',8192)));local phases=children(a.pid)
 frames[#frames+1]={at=now(),classificationSequence=c and c.sequence,classificationAge=c and c.queryStart and now()-c.queryStart,snapshotSequence=s and s.sequence,snapshotAge=s and s.queryStart and now()-s.queryStart,guardianHealthy=g.healthy,workerCpuTicks=p.cpuTicks,workerState=p.state,phases=phases,observerSeconds=now()-began}
 n.nanosleep(0,200000000)
end
telemetryRows[2]=telemetry();local done=now();print(j.stringify({readonly=true,routerWrites=false,trafficGenerated=false,productionWorkerInstrumented=false,observerCpuSeconds=os.clock()-observerCpu,jsonReadCpuSeconds=ioCpu,jsonReads=reads,seconds=done-start,samplingIntervalSeconds=0.2,usesCurrentConsumerForAdmission=false,updates=updates,frames=frames,telemetry=telemetryRows}))
