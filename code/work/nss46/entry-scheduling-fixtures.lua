local cases={};local function check(name,expected,fn)local ok=pcall(fn);assert(ok==expected,name);cases[#cases+1]=name end
local function project(s)
assert(s.publication=='before-software-baseline');local p=assert(s.snapshot.provenance);local projection=assert(s.snapshot.admissionProjection);assert(projection.version==1 and projection.scope=='bulk-and-admitted-rt'and projection.sourceSequence==p.sequence and projection.candidateFlowCount==#s.snapshot.flows and projection.completeInputFlowCount>=#s.snapshot.flows)
  
return true end
local function valid()return{publication='before-software-baseline',snapshot={flows={{},{}},provenance={sequence=10},admissionProjection={version=1,scope='bulk-and-admitted-rt',sourceSequence=10,candidateFlowCount=2,completeInputFlowCount=10}}}end
check('correct projection',true,function()project(valid())end)
check('postbaseline refused',false,function()local s=valid();s.publication='after-software-baseline';project(s)end)
for _,change in ipairs({{version=2},{scope='all'},{sourceSequence=11},{candidateFlowCount=3},{completeInputFlowCount=1}})do check('changed projection '..#cases,false,function()local s=valid();for k,v in pairs(change)do s.snapshot.admissionProjection[k]=v end;project(s)end)end
check('missing projection',false,function()local s=valid();s.snapshot.admissionProjection=nil;project(s)end)
check('missing provenance',false,function()local s=valid();s.snapshot.provenance=nil;project(s)end)
for _,name in ipairs(cases)do print('PASS '..name)end;print('COMPLETE '..#cases)
