
local M=assert(loadstring([====[-- Read-only scheduling hint. It cannot authorize NSS or extend any snapshot TTL.
local M={}
function M.wait(readCurrent,now,pause,due,onObservation)
 local first=readCurrent();assert(type(first)=='table','Missing full publication');local initialSequence=first.sequence;local producer=first.producer;local rows={};local started=now();local lastSequence=initialSequence
 assert(type(producer)=='string'and #producer>0,'Missing full publication producer')
 local function validate(v,t)
  assert(type(v)=='table'and v.healthy==true,'Unhealthy full publication')
  assert(v.producer==producer,'Producer changed during audit alignment')
  assert(type(v.sequence)=='number'and v.sequence==math.floor(v.sequence)and v.sequence>=1 and v.sequence>=lastSequence,'Full publication sequence regressed');lastSequence=v.sequence
  assert(type(v.queryStart)=='number'and type(v.queryFinished)=='number'and type(v.published)=='number')
  assert(v.queryStart<=v.queryFinished and v.queryFinished<=v.published and v.published<=t,'Future or unordered publication times')
  assert(v.queryFinished-v.queryStart<=2,'Query duration invalid')
 end
 validate(first,now());local v=first
 repeat
  local at=now()
  if onObservation then onObservation({at=at,sequence=v.sequence,producer=v.producer,healthy=v.healthy==true,queryStart=v.queryStart,published=v.published,sourceAge=type(v.queryStart)=='number'and at-v.queryStart or nil,publicationAge=type(v.published)=='number'and at-v.published or nil})end
  validate(v,at);rows[#rows+1]={at=at,sequence=v.sequence,sourceAge=at-v.queryStart,publicationAge=at-v.published};assert(#rows<=160,'Alignment poll bound')
  -- A newer source and the existing <2 s prelearning age form a scheduling hint.
  -- The complete locked audit keeps its original <6/<9 s predicates afterward.
  if v.sequence>initialSequence and at-v.queryStart<2 then
   return{passed=true,startedAt=started,finishedAt=at,initialSequence=initialSequence,selectedSequence=v.sequence,sourceAge=at-v.queryStart,publicationAge=at-v.published,producer=producer,rows=rows,nssAdmissionAllowed=false,auditStillRequired=true,lockHeld=false,snapshotExpiryExtended=false}
  end
  assert(at<due,'No newer fresh full publication before alignment deadline');pause();assert(now()<due,'Audit alignment deadline reached');v=readCurrent()
 until false
end
return M
]====]))();local cases={}
local function v(seq,start,finish,pub,producer,healthy)
 return{sequence=seq,queryStart=start or 99,queryFinished=finish or 99.2,published=pub or 99.4,producer=producer or 'fixture-worker',healthy=healthy~=false}
end
local function run(label,items,expected,fragment)
 local t=100;local pos=1
 local function read()local value=items[math.min(pos,#items)];pos=pos+1;if type(value)=='function'then return value()end;return value end
 local ok,r=pcall(M.wait,read,function()return t end,function()t=t+0.25 end,101)
 assert(ok==expected,label..': unexpected result '..tostring(r))
 if expected then
  assert(r.selectedSequence>r.initialSequence and r.sourceAge<2 and r.lockHeld==false and r.nssAdmissionAllowed==false and r.auditStillRequired==true and r.snapshotExpiryExtended==false)
 else assert(tostring(r):find(fragment,1,true),label..': unexpected rejection '..tostring(r))end
 cases[#cases+1]=label;print('PASS '..label)
end
run('new fresh publication schedules complete audit',{v(10),v(11)},true)
run('same sequence cannot authorize stale reuse',{v(10)},false,'deadline')
run('new sequence still too old waits for genuinely fresh source',{v(10),v(11,97,97.2,97.4),v(12,99,99.2,99.4)},true)
run('sequence below initial hard refuses',{v(10),v(9)},false,'regressed')
run('sequence regressing after a newer old publication hard refuses',{v(10),v(12,97,97.2,97.4),v(11)},false,'regressed')
run('producer change hard refuses',{v(10),v(11,99,99.2,99.4,'other-worker')},false,'Producer changed')
run('unhealthy publication hard refuses',{v(10),v(11,99,99.2,99.4,nil,false)},false,'Unhealthy')
run('future publication hard refuses',{v(10),v(11,99,99.2,101)},false,'Future')
run('unordered query hard refuses',{v(10),v(11,99.3,99.2,99.4)},false,'Future')
run('query over original two-second duration refuses',{v(10),v(11,96,99.2,99.4)},false,'Query duration')
run('exact two-second source age cannot schedule',{v(10),v(11,98.25,98.5,99)},false,'deadline')
run('fractional sequence refuses',{v(10),v(10.5)},false,'regressed')
run('read error propagates without permission',{v(10),function()error('fixture read failure')end},false,'fixture read failure')
run('missing publication refuses',{function()return nil end},false,'Missing full publication')
run('missing producer refuses',{function()local x=v(10);x.producer=nil;return x end},false,'Missing full publication producer')

local function traced(label,items,fragment,check)
 local t=100;local pos=1;local trace={}
 local ok,err=pcall(M.wait,function()local x=items[math.min(pos,#items)];pos=pos+1;if type(x)=='function'then return x()end;return x end,function()return t end,function()t=t+0.25 end,101,function(row)trace[#trace+1]=row end)
 assert(not ok and tostring(err):find(fragment,1,true),label..': refusal must remain');assert(#trace>0,label..': lost diagnostic rows');check(trace)
 cases[#cases+1]=label;print('PASS '..label)
end
traced('timeout keeps complete polled source ages',{v(10)},'deadline',function(rows)assert(#rows>=3 and rows[1].sequence==10 and rows[#rows].sourceAge>rows[1].sourceAge)end)
traced('newer but old publication refusal keeps changed sequence',{v(10),v(11,97,97.2,97.4)},'deadline',function(rows)assert(rows[#rows].sequence==11 and rows[#rows].sourceAge>=2)end)
traced('producer mismatch preserves rejecting observation',{v(10),v(11,99,99.2,99.4,'other-worker')},'Producer changed',function(rows)assert(rows[#rows].producer=='other-worker')end)
traced('unhealthy refusal preserves rejecting observation',{v(10),v(11,99,99.2,99.4,nil,false)},'Unhealthy',function(rows)assert(rows[#rows].healthy==false)end)
traced('query ordering refusal preserves source timestamps',{v(10),v(11,99.3,99.2,99.4)},'Future',function(rows)assert(rows[#rows].queryStart==99.3)end)
traced('sequence regression preserves offending sequence',{v(10),v(9)},'regressed',function(rows)assert(rows[#rows].sequence==9)end)
traced('read failure preserves previously completed observations',{v(10),function()error('fixture read failure')end},'fixture read failure',function(rows)assert(rows[#rows].sequence==10)end)
local t=100;local pos=0;local trace={};local ok=M.wait(function()pos=pos+1;return v(pos==1 and 10 or 11)end,function()return t end,function()t=t+0.25 end,101,function(row)trace[#trace+1]=row end)
assert(ok.passed and not ok.nssAdmissionAllowed and not ok.lockHeld and not ok.snapshotExpiryExtended and #trace==2)
cases[#cases+1]='successful diagnostics still cannot authorize or extend NSS';print('PASS '..cases[#cases])

print('COMPLETE '..#cases)
