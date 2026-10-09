-- Restore the classifier's existing diffserv4 queue contract after a boot.
-- This does not replace the classifier, its configuration, or the autorater.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
assert(root=='/tmp/athena-dorm-native' or root=='/usr/lib/athena-dorm-native')
local mode=arg[1] or 'inspect';assert(mode=='inspect' or mode=='repair')
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
assert(not fs.stat('/sys/module/athena_ecm_gate') and not fs.stat('/tmp/athena-dorm-native/lock'))
local function run(cmd)
 local f=assert(io.popen(cmd..' 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'))
 local s=f:read('*a');f:close();local body,code=s:match('^(.*)\nATHENA_EXIT_(%d+)\n$')
 assert(body and code=='0',s);return body
end
local function read(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return s end
local function same(a,b)
 if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not same(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local function options(q)
 local o={};for k,v in pairs(assert(q.options))do if k~='bandwidth' and k~='diffserv'then o[k]=v end end;return o
end
local base,hash=read('/root/router-project/game-classifier-generation'):match('^(%S+)%s+(%x+)%s*$')
assert(base and base:match('^/root/router%-project/classifier/nss23%-%w+%-[%w%-]+$') and #hash==64)
assert(run('sha256sum '..base..'/config.json'):match('^(%x+) ')==hash,'Classifier config changed')
local cfg=assert(j.parse(read(base..'/config.json')));assert(cfg.version==23)
assert(run('sha256sum '..base..'/owned.lua'):match('^(%x+) ')==cfg.files['owned.lua'],'Classifier filter parser changed')
local owned=dofile(base..'/owned.lua')
local function queue(dev)
 local qs=assert(j.parse(run('tc -j -d qdisc show dev '..dev)));local result
 for _,q in ipairs(qs)do if q.root then assert(not result);result=q end end;return assert(result)
end
local function check(dev,q)
 local expected=assert(cfg.queues[dev]);assert(q.kind=='cake' and q.root and q.handle==expected.handle,'Queue root changed '..dev)
 assert(q.options.bandwidth and q.options.bandwidth>0 and expected.options.diffserv=='diffserv4')
 assert(same(options(q),options(expected)),'Queue option drift '..dev)
 assert(q.options.diffserv=='diffserv4' or q.options.diffserv=='besteffort','Unexpected queue class mode '..dev)
end
local function classifierRunning()
 local services=assert(j.parse(run('ubus call service list')))
 local instances=((services['router-project-game-classifier'] or {}).instances or {})
 return instances.classifier and instances.classifier.running==true and instances.guardian and instances.guardian.running==true
end
local function publicationFresh()
 local f=io.open('/tmp/router-project-game-classifier/classification.json');if not f then return false end
 local p=j.parse(f:read('*a'));f:close();local now=tonumber(read('/proc/uptime'):match('^[%d.]+'))
 return p and p.status=='running' and not p.error and p.generation==cfg.generation and
  p.boot==read('/proc/sys/kernel/random/boot_id'):match('%S+') and type(p.atUptime)=='number' and now-p.atUptime<9
end
local function filters(dev,h)
 local text=run('tc -d filter show dev '..dev..' parent '..h);local present={}
 for pref in text:gmatch('filter protocol %w+ pref (%d+) ')do
  pref=tonumber(pref)
  if pref==40900 or pref==41900 or pref>=41000 and pref<=41099 then present[pref]=true end
 end
 if present[40900] or present[41900]then
  assert(present[40900] and present[41900],'Partial classifier baseline '..dev)
  owned.parse(text,dev,h,48);return false
 end
 assert(next(present)==nil,'Dynamic selectors without baseline '..dev)
 return true
end
local before,needed,missingBase={},{},{}
for w=1,5 do for _,prefix in ipairs{'rpwan','rpifb'}do
 local dev=prefix..w;local q=queue(dev);check(dev,q);before[dev]=q
 if q.options.diffserv~='diffserv4' then needed[#needed+1]=dev end
 if filters(dev,q.handle)then missingBase[#missingBase+1]=dev end
end end
local wasRunning=classifierRunning() and publicationFresh()
local report={mode=mode,queueRepairsNeeded=#needed,filterPairsNeeded=#missingBase,classifierWasRunning=wasRunning,queueRepairs=0,filterPairsRestored=0,classifierRestarted=false,configUnchanged=true}
if mode=='repair' then
 -- Validate every queue before the first write; change only the known mode.
 for _,dev in ipairs(needed)do
  local fresh=queue(dev);check(dev,fresh)
  assert(fresh.handle==before[dev].handle and same(options(fresh),options(before[dev])),'Queue changed before repair')
  if fresh.options.diffserv~='diffserv4' then
   run('tc qdisc change dev '..dev..' root cake diffserv4')
   local after=queue(dev);check(dev,after)
   assert(after.handle==fresh.handle and same(options(after),options(fresh)) and after.options.diffserv=='diffserv4','Queue repair readback failed')
   report.queueRepairs=report.queueRepairs+1
  end
 end
 for _,dev in ipairs(missingBase)do
  local q=queue(dev);check(dev,q);assert(q.handle==before[dev].handle)
  assert(filters(dev,q.handle),'Classifier filters appeared before restoration')
  local prefix='tc filter add dev '..dev..' parent '..q.handle
  run(prefix..' protocol ip pref 40900 u32 match u8 0x45 0xff at 0 match ip protocol 6 0xff match u16 0x400 0xfc00 at 2 action skbedit priority '..q.handle..'2 pass')
  run(prefix..' protocol all pref 41900 matchall action skbedit priority '..q.handle..'2 pass')
  assert(not filters(dev,q.handle),'Classifier filter restoration unconfirmed')
  report.filterPairsRestored=report.filterPairsRestored+1
 end
 if not wasRunning then
  run('/etc/init.d/router-project-game-classifier stop')
  -- Its terminal marker intentionally survives a normal service restart.
  -- Perform the original exact recovery first, then allow a fresh watch.
  local result=run('/usr/bin/timeout -k 2 25 /bin/sh '..base..'/cleanup.sh '..base..' '..hash..' rollback')
  local recovered=assert(j.parse(assert(result:match('([^\n]+)\n*$'))))
  assert(recovered.exactRecovery==true,'Original classifier recovery unconfirmed')
  assert(not classifierRunning(),'Classifier did not stop for recovery')
  local ram='/tmp/router-project-game-classifier'
  if fs.stat(ram..'/stopped')then
   assert(read(ram..'/stopped')=='rollback\n','Unexpected terminal marker after recovery')
   local snapshot=assert(j.parse(read(ram..'/snapshot.json')))
   assert(snapshot.status=='stopped' and snapshot.generation==cfg.generation and snapshot.boot==read('/proc/sys/kernel/random/boot_id'):match('%S+'))
   assert(os.remove(ram..'/stopped'))
   report.terminalMarkerClearedAfterExactRecovery=true
  end
  run('/etc/init.d/router-project-game-classifier start')
  report.classifierRestarted=true
 end
 local deadline=tonumber(read('/proc/uptime'):match('^[%d.]+'))+12
 repeat
  if classifierRunning() and publicationFresh()then break end
  assert(tonumber(read('/proc/uptime'):match('^[%d.]+'))<deadline,'Original classifier did not restart')
  n.nanosleep(0,250000000)
 until false
 assert(run('sha256sum '..base..'/config.json'):match('^(%x+) ')==hash,'Classifier config changed during recovery')
 report.classifierRunning=true
 report.classifierPublicationFresh=true
end
print(j.stringify(report))
