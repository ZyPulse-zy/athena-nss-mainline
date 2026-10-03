local M=dofile(arg[1]..'/address-query.lua');local P=dofile(arg[1]..'/observation-policy.lua')
local cases={};local function yes(v,name)assert(v,name);cases[#cases+1]=name end
local function run(opt)
 local at,killed,pipes=100,false,0
 local n={}
 function n.pipe()
  pipes=pipes+1;local body=pipes==1 and(opt.body or'[]')or''
  local fd={read=function(self)
   if opt.hangPipe then return nil,11 end
   if #body>0 then local out=body:sub(1,4096);body=body:sub(4097);return out end
   return''
  end,close=function()return true end,setblocking=function()return true end}
  return fd,{close=function()return true end}
 end
 function n.fork()return 7 end
 function n.waitpid(pid,mode)
  assert(pid==7 and mode=='nohang')
  if opt.waitError then return nil end
  if opt.neverReap or((opt.hangPipe or opt.hangWait)and not killed)then return false end
  return pid,opt.signaled and'signaled'or'exited',opt.signaled and 9 or(killed and 143 or(opt.code or 0))
 end
 function n.kill(pid,sig)assert(pid==7 and sig==15);if opt.killFails then return nil end;killed=true;return true end
 function n.nanosleep(a,b)at=at+a+(b or 0)/1e9 end
 local parse=function(body)if opt.parseThrows then error('invalid-json')end;return opt.parsed or{}end
 local ok,value=pcall(M.run,n,function()return at end,parse,'/fixture/group-runner')
 return ok,value,at-100,killed
end
local ok,value=run({});yes(ok and value=='[]','complete query is returned')
for _,v in ipairs({{hangPipe=true,reason='pipe-timeout'},{hangWait=true,reason='wait-timeout'}})do
 local ok,e,dt,killed=run(v);yes(not ok and P.accept(e)and e.reason==v.reason and killed and dt>=4 and dt<5.1,v.reason..' requires confirmed cancellation and reap')
end
for _,v in ipairs({{signaled=true,name='signaled runner'},{waitError=true,name='unknown child status'},
 {hangPipe=true,killFails=true,name='cancellation failed'},{hangWait=true,neverReap=true,name='cleanup deadline exceeded'},
 {code=127,name='runner exec failure'}})do
 local ok,e=run(v);yes(not ok and type(e)=='string'and not P.accept(e),v.name..' cannot enter recoverable state')
end
ok,value=run({parseThrows=true,body='['});yes(not ok and P.accept(value)and value.reason=='invalid-json','partial output never reuses previous complete inventory')
ok,value=run({parsed={bad='root-object'}});yes(not ok and P.accept(value),'malformed address root rejected')
ok,value=run({parsed={{ifname='x',addr_info={{family='inet',scope='global'}}}}});yes(not ok and P.accept(value),'missing global IPv4 address rejected')
for _,name in ipairs(cases)do print('PASS '..name)end;print('COMPLETE '..#cases)
