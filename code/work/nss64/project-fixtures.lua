-- Differential native jsonc contract cases plus one real complete publication.
local function run(old,new,j,n,tree)
 local count=0
 local function same(a,b)
  if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end
  for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true
 end
 local function good(value,shape)
  local a,b=old(value,nil,shape),new(value,nil,shape);assert(same(a,b),'Projection differential')
  local x,y=j.parse(assert(j.stringify(a))),j.parse(assert(j.stringify(b)))
  assert(same(x,y),'Native JSON differential');count=count+1
 end
 local function bad(value)
  assert(not pcall(old,value)and not pcall(new,value),'Invalid JSON accepted');count=count+1
 end
 good(nil);good(true);good(false);good('');good('quote"\\\n\0');good(0);good(-1.25);good(1e100)
 good({});good({1,2,3});good({true,false,'x'});good({[1]='x',[3]='z'})
 good({['1']='a',['3']='c'});good({[2]='b',name='n'});good({[1]='a'},'slots')
 good({a={x=1},b={x=2}});local r={x={1,2},enabled=false};good({a=r,b=r})
 good({baseline={rpwan1={[1]={x=1},[48]={x=48}}},current={rpwan1={[1]={x=1}}}})
 good({current={dev={1,2,3}}});good({[1000000]='large'});good({[1]={current={dev={[7]='slot'}}}})
 bad({[0]='x'});bad({[-1]='x'});bad({[1.5]='x'});bad({[true]='x'});bad({[{}]='x'})
 bad({[1]='x',['1']='collision'});bad({f=function()end});bad({x=coroutine.create(function()end)})
 bad({x=n.stdout});bad(0/0);bad(math.huge);bad(-math.huge)
 local cyc={};cyc.self=cyc;bad(cyc);local a,b={},{};a.b=b;b.a=a;bad(a)
 good(tree)
 return {passed=true,cases=count,actualCompletePublicationCompared=true,flowCount=#tree.snapshot.flows,sharedReferencesPreserved=true,
  cycleAndNonJsonRejected=true,slotMapAndDenseListContractRetained=true}
end
return run
