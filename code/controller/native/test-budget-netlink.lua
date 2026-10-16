local root=assert(arg[0]:match('^(.*)/[^/]+$'));local j=require('luci.jsonc');local checks=0
local function check(v,m)checks=checks+1;assert(v,m)end
local open,popen=io.open,io.popen;local at,rows,delay,rc=100,{},.02,0;local commands=0
io.open=function(p,mode)
 check(p=='/proc/uptime'and(mode=='r'or mode==nil),'Only clock read')
 return{read=function()return tostring(at)..' 0'end,close=function()end}
end
io.popen=function(c)
 check(c:find('/cake-budget-read ',1,true)~=nil and not c:find('tc ',1,true),'One read-only binary, no formatting plugin')
 commands=commands+1;at=at+delay
 return{read=function()return(type(rows)=='string'and rows or j.stringify(rows))..'\nATHENA_COLLECT_EXIT_'..rc..'\n'end,close=function()end}
end
local c=dofile(root..'/collector.lua')
for _,count in ipairs{5,6}do
 for _,fault in ipairs{'healthy','missing','duplicate','wrong-kind','unlimited','too-large','bad-json','command-failed','late'}do
  rows={};delay=.02;rc=0;at=100;commands=0
  for w=1,count do for _,prefix in ipairs{'rpwan','rpifb'}do rows[#rows+1]={dev=prefix..w,root=true,kind='cake',options={bandwidth=4055000}}end end
  if fault=='missing'then table.remove(rows)end
  if fault=='duplicate'then rows[2]=rows[1]end
  if fault=='wrong-kind'then rows[1].kind='nsshtb'end
  if fault=='unlimited'then rows[1].options.bandwidth=0 end
  if fault=='too-large'then rows[1].options.bandwidth=25000001 end
  if fault=='bad-json'then rows='invalid'end
  if fault=='command-failed'then rc=143 end
  if fault=='late'then delay=4 end
  local progress=0;local b=c.software_budgets(count,function(p)progress=progress+1;check(p.command=='cake-roots','Exact current command stage')end)
  check(commands==1 and b.diagnostics.commandCount==1 and progress==1,'One dump per round')
  check(b.complete==(fault=='healthy'),'No partial or late budget admitted: '..fault)
  if b.complete then check(b.diagnostics.validatedRootCount==count*2 and b.values.up[count]==32440 and b.values.down[count]==32440,'All roots and exact byte rate preserved')end
  if fault=='late'then check(b.finishedAtUptime-b.startedAtUptime==4 and b.diagnostics.failureKind=='sample-time-budget','Late data never gains a new lease')end
 end
end
io.open,io.popen=open,popen
local sampler=dofile(root..'/budget_sampler.lua');local attempt=0;local published={};at=100
sampler.run({now=function()return at end,stopped=function()return attempt>=3 end,
 collect=function(w,progress)attempt=attempt+1;progress({phase='query',command='cake-roots',atUptime=at});local began=at;at=at+.02;return{version=1,source='software-cake',wanCount=w,complete=attempt~=1,startedAtUptime=began,finishedAtUptime=at,diagnostics={commandCount=1,failures=attempt==1 and 1 or 0}}end,
 publish=function(name,v)if name=='budget-sampler.json'then published[#published+1]=j.parse(j.stringify(v))end;check(name~='heartbeat','Budget worker never renews CT heartbeat')end,
 sleep=function(t)at=at+t end},6,'boot')
local last=published[#published];check(last.phase=='sampled'and last.sequence==3 and last.lastFailure.sequence==1,'Last failure survives later successful samples')
check(last.lastFailure.startedAtUptime==100 and last.lastGoodAtUptime>100,'Failure time and last-good time are distinct')
print(j.stringify({passed=true,checks=checks,oneDump=true,exactRateMapping=true,virtualTimeOnly=true}))
