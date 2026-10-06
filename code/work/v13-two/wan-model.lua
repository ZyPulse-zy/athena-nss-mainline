local lib=assert(loadstring([====[__WAN_SOURCE__]====]))()
local function trial(failure)
 local states={[1]='bridge',[2]='bridge'};local m=0;local record={};local writes=0
 local members={{w=1,pid=10,start='101',failure=0,index=11,mac='00:00:00:00:00:01',link=6,ip='192.0.2.1'},{w=2,pid=20,start='202',failure=0,index=12,mac='00:00:00:00:00:02',link=6,ip='192.0.2.2'}}
 local P={selected={tcp={wan=1,reply={dst='192.0.2.1'}},udp={wan=2,reply={dst='192.0.2.2'}}},wanPrerequisites={boot='model',members=members}}
 local function read(p)
  if p=='/proc/sys/kernel/random/boot_id'then return'model\n'end
  if p=='/proc/sys/net/ecm/mwan3_enable'then return tostring(m)end
  local pid=p:match('^/proc/(%d+)/stat$');if pid then local a={};for i=1,20 do a[i]='0'end;a[20]=pid=='10'and'101'or'202';return pid..' (model) '..table.concat(a,' ')end
  assert(p:match('^/tmp/router%-project%-logs/minieap%-wan%d.log$'));return''
 end
 local function command(s)
  local w=s:match('rpwan(%d+)')or s:match('network.interface.wan(%d+)');w=assert(tonumber(w));local e=members[w]
  if s:match('^/sbin/ip %-j %-d')then return j.stringify({{ifindex=e.index,address=e.mac,link_index=e.link,linkinfo={info_data={mode=states[w]}}}})end
  if s:match('^/bin/ubus')then return j.stringify({up=true,l3_device='rpwan'..w,['ipv4-address']={{address=e.ip}}})end
  local mode=assert(s:match(' mode (%w+)$'));writes=writes+1
  if failure and w==2 and mode=='private'then error('second mode write rejected')end
  states[w]=mode;return''
 end
 local a=lib.new(P,{},j,read,function()return 1 end,function()assert(m==0 or m==1)end,function(p,v)assert(p=='/proc/sys/net/ecm/mwan3_enable');m=assert(tonumber(v))end,command,record)
 local ok=pcall(a.setup)
 if failure then assert(not ok and states[1]=='private'and states[2]=='bridge'and m==0)else assert(ok and states[1]=='private'and states[2]=='private'and m==1);a.check()end
 a.cleanup();assert(states[1]=='bridge'and states[2]=='bridge'and m==0 and record.wanRestored)
 if not failure then assert(record.mwan3Restored and record.wanHealthAfterUndo[1]and record.wanHealthAfterUndo[2])end
 return{passed=true,partialSecondWriteFailure=failure,twoIndependentWanModesRestored=true,productionWrites=false,authenticationNotRequested=true}
end
print(j.stringify({passed=true,checks=2,cases={trial(false),trial(true)},actualTwoWanHelperExecuted=true,backendMocked=true,hardwareProof=false}))
