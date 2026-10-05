local function test(kind)
 local at=10;local stop=0;local total=2;local barriers=1;local revokes=2;local terminal=false;local closed=0;local drained=0
 local active=kind~='software-class-change';if not active then stop=1;total=0 end
 local P={owner=string.rep('a',32)};P.statePath='/root/router-project/experiments/rp-nss25-state-'..P.owner..'/ecm-state'
 local B={'ecm_db/connection_count','ecm_nss_ipv4/accelerated_count','ecm_nss_ipv6/accelerated_count','ecm_nss_ipv4/pending_accel_count','ecm_nss_ipv6/pending_accel_count','ecm_nss_ipv4/pending_decel_count','ecm_nss_ipv6/pending_decel_count'}
 local R={adapterProducer='mock',tagEpochUntil=13};if kind=='expired-old-lease'then R.tagEpochUntil=10.5 end
 local M={};local retire
 __VERIFIER__
 local function now()return at end
 local function pause(s)at=at+s end
 local function read(path)
  if path=='/proc/stat'then return'cpu 0 0 0 100 0 0 0 0 0 0\n'end
  if path=='/proc/net/softnet_stat'then return'00000000 00000000 00000000\n'end
  if path:match('^/sys/class/net/[%w]+/statistics/')then return'0'end
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then return tostring(stop)end
  if path=='/sys/kernel/debug/ecm/front_end_ipv6_stop'then return'1'end
  if path:find('/sys/kernel/debug/ecm/',1,true)then
   if path:find('/connection_count',1,true)or path:find('/ecm_nss_ipv4/accelerated_count',1,true)then return tostring(total)end
   if kind=='pending-drain'and terminal and path:find('/ecm_nss_ipv4/pending_decel_count',1,true)then return'1'end
   return'0'
  end
  error('Unexpected mock read')
 end
 __SAMPLE__
 local function K()
  return{tcp_permit=terminal and'N'or'Y',game_permit='Y',tcp_state='ever_opened=1 terminal='..(terminal and'1'or'0')..' admit='..(terminal and'0'or'1'),game_state='ever_opened=1 terminal=0 admit=1',tcp_pinned_state='pinned=1 current_hash_matches=1',game_pinned_state=kind=='pin-drift'and terminal and'pinned=0 current_hash_matches=0'or'pinned=1 current_hash_matches=1',cpu_barriers=tostring(barriers),revoke_calls=tostring(revokes)}
 end
 local function put(path,value)
  if path=='/sys/kernel/debug/ecm/front_end_ipv4_stop'then stop=tonumber(value);return end
  assert(stop==1,'Target mutation before stopping new learning')
  if path:match('/tcp_close$')then terminal=true;closed=closed+1
  elseif path:match('/tcp_drain$')then drained=drained+1;barriers=barriers+1;revokes=revokes+2;total=1
  else error('Unexpected mock mutation')end
 end
 local function state()if kind=='remaining-shape'then return'conns.conn.1.protocol=6\n'end;return'conns.conn.2.protocol=17\n'end
 local A={}
 function A.observe()return{sourceSequence=2,producer='mock',startedAtUptime=at}end
 function A.compareObserved()
  if kind=='unchanged'then return{action='KEEP_IMMUTABLE_EPOCH'}end
  local C=j.parse(j.stringify(comparison))
  if kind=='no-full-frame'then C.evidence.completeSelected=nil
  elseif kind=='wrong-scope'then C.affected={'udp'}
  elseif kind=='expired-frame'then C.evidence.completeSelected.slots.tcp.validRemainingSeconds=0 end
  return C
 end
 __RETIRE__
 __OBSERVE__
 local ok,value=pcall(observe)
 if kind=='unchanged'then assert(ok and value.sequence==2 and total==2 and closed==0 and drained==0 and stop==0)
 elseif kind=='changed'then assert(not ok and tostring(value):find('REQUIRES_NEW_CHECKPOINT_AND_EPOCH',1,true));assert(R.classChangeTestCompleted and R.classTransitionHandled and R.requiresFreshEpoch and total==1 and closed==1 and drained==1 and stop==1)
 else assert(not ok and not R.classTransitionHandled);assert(stop==1);if kind=='no-full-frame'or kind=='wrong-scope'or kind=='expired-frame'or kind=='expired-old-lease'or kind=='software-class-change'then assert(closed==0 and drained==0)end end
 return{case=kind,passed=true,targetRamOnly=true,mockedClockCountersClassifierAndFirmware=true,routerWrites=false,hardwareProof=false}
end
local cases={};for _,kind in ipairs({'unchanged','changed','no-full-frame','wrong-scope','expired-frame','expired-old-lease','pending-drain','pin-drift','remaining-shape','software-class-change'})do cases[#cases+1]=test(kind)end
print(j.stringify({passed=true,checks=#cases,cases=cases,productionExecution=false}))
