local root=assert(arg[0]:match('^(.*)/[^/]+$'));local m=dofile(root..'/coverage.lua');local checks=0
local function check(v)assert(v);checks=checks+1 end
local function cohort(seq,start,rt,be,producer)
 return{producer=producer or'one',boot='boot',sequence=seq,started=start,finished=start+0.1,
 rows={a={class='RT',bytes=rt},b={class='BE',bytes=be}}}
end
local function hw(n,gen)return{a={serial=1,generation=gen or 1,down=n}}end
local s=m.new();m.tick(s,100,cohort(1,99,100,100),hw(50));check(not m.report(s).measured)
m.tick(s,103,cohort(2,102,200,200),hw(150));check(s.pending and s.windows==0)
m.tick(s,106,cohort(3,105,300,400),hw(250));local r=m.report(s)
check(r.measured and r.hardwareBytes==100 and r.totalBytes==500 and r.ratioLowerBound==0.2)
check(r.includesBestEffort and r.classes.BE.bytes==300 and r.classes.BE.hardware==0 and not r.fullLanCoverage)
check(r.lastWindow.ctStart<r.lastWindow.hardwareStart and r.lastWindow.ctEnd>r.lastWindow.hardwareEnd)
m.tick(s,109,cohort(4,108,400,450),hw(300,2));m.tick(s,112,cohort(5,111,500,500),hw(400,2))
check(s.excluded==1 and s.classes.RT.bytes==200 and s.classes.BE.bytes==400)
m.tick(s,115,nil,{});check(not s.base and not s.pending)
m.tick(s,118,cohort(6,117,600,600,'two'),hw(1));check(s.base and not s.pending)
local core=dofile(root..'/core.lua');local publication={status='running',dataHealthy=true,nssPermit=false,producer='one',boot='boot',
 snapshot={flows={},selection={untracked=0},provenance={boot='boot',queryFamily='ipv4',queryZone=0,exitCode=0,sequence=1,startedAtUptime=99,finishedAtUptime=99.1}}}
check(m.cohort(publication,{},100,core)~=nil)
publication.snapshot.selection.untracked=1;check(not m.cohort(publication,{},100,core));publication.snapshot.selection.untracked=0
publication.snapshot.provenance.queryZone=1;check(not m.cohort(publication,{},100,core))
print(require('luci.jsonc').stringify({passed=true,checks=checks,dataPlaneWrites=false,modelOnly=true}))
