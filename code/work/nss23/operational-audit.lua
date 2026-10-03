local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
local base=assert(arg[1]);local hash=assert(arg[2])
assert(base:match('^/root/router%-project/classifier/nss23%-[%w%-]+$')and hash:match('^[0-9a-f]+$')and #hash==64)
local function read(p,l)local f=assert(io.open(p));local s=f:read(l+1)or'';f:close();assert(#s<=l);return s end
local function cmd(s,l)local f=assert(io.popen(s));local x=f:read(l+1)or'';f:close();assert(#x<=l);return x end
assert(fs.readlink('/proc/'..n.getpid()..'/fd/8')=='/tmp/router-project-transaction.lock')
assert(read('/proc/'..n.getpid()..'/fdinfo/8',8192):match('FLOCK%s+ADVISORY%s+WRITE'))
assert(cmd('/usr/bin/sha256sum '..base..'/config.json',256):match('^(%x+) ')==hash)
local cfg=assert(j.parse(read(base..'/config.json',131072)))
for name,h in pairs(cfg.files)do assert(cmd('/usr/bin/sha256sum '..base..'/'..name,256):match('^(%x+) ')==h)end
local own=assert(dofile(base..'/owned.lua'));local B=assert(dofile(base..'/backend.lua'))
local J=assert(j.parse(read('/tmp/router-project-game-classifier/journal.json',4194304)))
assert(J.generation==cfg.generation and J.boot==cfg.adoptionBoot)
local out={exactOwnedNativeAudit=true,native={},selectors=0,legacyReplacedOnlyByJournalOwnedRules=true}
for w=1,5 do
 local l=assert(J.wans[tostring(w)]);assert(#l.intents==0)
 for _,dev in ipairs({'rpwan'..w,'rpifb'..w})do
  local h=cfg.queues[dev].handle;local text=cmd('/sbin/tc -d filter show dev '..dev..' parent '..h,262144)
  local p=own.parse(text,dev,h,48);assert(next(p.tableOnly)==nil)
  local clean=B.baseOnly(text,dev,h,own)
  assert(clean==B.baseOnly(cfg.originalNative[dev],dev,h,own)and clean==l.nativeBaseline[dev])
  for k,r in pairs(p.dynamic)do local e=l.current[dev][tostring(k)]or l.current[dev][k];assert(e and e.signature==r.signature,'Unknown selector');out.selectors=out.selectors+1 end
  for k,r in pairs(l.current[dev])do local e=p.dynamic[tonumber(k)];assert(e and e.signature==r.signature,'Known selector drift')end
  out.native[dev]=text
 end
end
local s=assert(j.parse(read('/tmp/router-project-game-classifier/snapshot.json',4194304)))
local g=assert(j.parse(read('/tmp/router-project-game-classifier/guardian.json',4194304)))
local now=tonumber(read('/proc/uptime',128):match('^[%d.]+'))
assert(s.status=='running'and s.boot==J.boot and s.generation==J.generation and s.configSha256==hash and s.nssPermit==false and not s.error)
assert(g.healthy==true and g.generation==J.generation and g.configSha256==hash)
assert(now-s.atUptime<9 and now-s.snapshot.provenance.startedAtUptime<6)
assert(not fs.lstat('/tmp/router-project-game-classifier/stopped'))
local expected=table.concat({'/usr/bin/lua',base..'/worker.lua','watch',base,hash},'\0')..'\0'
assert(read('/proc/'..s.pid..'/cmdline',8192)==expected)
local fields={};for v in assert(read('/proc/'..s.pid..'/stat',8192):match('^%d+ %b() (.*)$')):gmatch('%S+')do fields[#fields+1]=v end
assert(fields[20]==s.start and fields[1]~='Z')
out.pid=s.pid;out.guardianPid=g.pid;out.producer=s.producer
out.querySequence=s.snapshot.provenance.sequence;out.queryAge=now-s.snapshot.provenance.startedAtUptime
out.initHash=cmd('/usr/bin/sha256sum /etc/init.d/router-project-game-classifier',256):match('^(%x+) ')
assert(out.initHash==cfg.files['init.sh'])
assert(read('/root/router-project/game-classifier-generation',512)==base..' '..hash..'\n')
out.startup={}
for _,path in ipairs({'/etc/rc.d/S99router-project-game-qos','/etc/rc.d/K15router-project-game-qos','/etc/rc.d/S99router-project-game-classifier','/etc/rc.d/K15router-project-game-classifier'})do
 local st,a,b=fs.lstat(path);if st then assert(st.type=='lnk');out.startup[path]=fs.readlink(path)else assert(a==2 or b==2);out.startup[path]=false end
end
print(j.stringify(own.jsonProject(out)))
