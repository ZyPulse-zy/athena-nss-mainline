local M=assert(loadstring([====[__HELPER__]====]))()
local checks={}
local function check(name,c)
 local tick=0;local reaped=false;local exitAt=c.exitAt or 0.02;local signaled;local calls=0
 local streams={};local number=0
 local function pipe()
  number=number+1;local stream=number==1 and'stdout'or'stderr';local delivered=false
  local fd={}
  function fd:setblocking(v)return not c.setupFail end
  function fd:close()self.closed=true;return true end
  function fd:read()
   if c.pipeError then return nil,5 end
   if tick<(c.outputAt or 0)then return nil,11 end
   if not delivered then delivered=true;return c[stream]or''end
   if c.openPipe and tick<exitAt then return nil,11 end
   return''
  end
  streams[#streams+1]=fd;return fd,{close=function()return true end}
 end
 local n={pipe=pipe,getpid=function()return 77 end,fork=function()return 88 end}
 function n.nanosleep(sec,ns)tick=tick+sec+(ns or 0)/1000000000;assert(tick<4,'Fixture loop exceeded bound')end
 function n.waitpid(pid,flag)
  calls=calls+1;assert(pid==88 and flag=='nohang'and not reaped)
  if c.waitError then return nil,10 end
  if tick>=exitAt then reaped=true;return 88,signaled and'signaled'or'exited',signaled or c.code or 0 end
  return false
 end
 function n.kill(pid,sig)
  assert(pid==88 and not reaped)
  if(sig==15 and c.termFail)or(sig==9 and c.killFail)then return false end
  if not c.neverReap and not(sig==15 and c.ignoreTerm)then exitAt=tick;signaled=sig end
  return true
 end
 local ok,result=pcall(M.run,n,function()return tick end,c.batch and{'-batch','/tmp/router-project-game-classifier/batch.77'}or{'-j','qdisc','show','dev','rpwan1'},65536)
 assert(ok==(c.ok==true),name..' '..tostring(result))
 if ok then assert(result==(c.stdout or''))else assert(tostring(result):find(c.want,1,true),name..' '..tostring(result))end
 if c.cleanup then assert(reaped and streams[1].closed and streams[2].closed,name..' child/fd cleanup')end
 checks[#checks+1]=name
end
check('successful complete output',{ok=true,stdout='[]',cleanup=true})
check('partial output and nonzero exit rejected',{stdout='[',code=7,want='code=7',cleanup=true})
check('delayed output with EAGAIN retained',{ok=true,stdout='[]',outputAt=0.1,exitAt=0.2,cleanup=true})
check('stdout overflow even after clean exit rejected',{stdout=string.rep('x',65537),want='stdout exceeded bound',cleanup=true})
check('stderr overflow rejected',{stderr=string.rep('x',4097),want='stderr exceeded bound',cleanup=true})
check('stderr warning with clean exit accepted',{ok=true,stderr='warning',cleanup=true})
check('half output cannot mask timeout',{stdout='[',openPipe=true,exitAt=10,want='2 second deadline',cleanup=true})
check('closed output cannot mask running child',{exitAt=10,want='2 second deadline',cleanup=true})
check('TERM ignoring child killed and reaped',{exitAt=10,ignoreTerm=true,want='code=9',cleanup=true})
check('pipe error terminates then reaps child',{pipeError=true,exitAt=10,want='pipe read failed',cleanup=true})
check('setup failure terminates then reaps child',{setupFail=true,exitAt=10,want='assertion failed',cleanup=true})
check('partial batch failure not retried',{batch=true,stdout='partial',code=8,want='filter-batch failed',cleanup=true})
check('wait failure remains terminal',{waitError=true,want='tc wait failed'})
check('TERM failure remains terminal',{exitAt=10,termFail=true,want='tc TERM failed'})
check('KILL failure remains terminal',{exitAt=10,ignoreTerm=true,killFail=true,want='tc KILL failed'})
check('unproved cleanup remains terminal',{exitAt=10,neverReap=true,want='child cleanup not proved'})
for _,v in ipairs(checks)do print('PASS '..v)end
print('COMPLETE '..#checks)
