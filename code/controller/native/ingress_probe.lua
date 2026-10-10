-- One short architecture probe; the transaction guardian is its only writer.
-- Keep existing WAN/LAN roots and all ten software CAKE instances intact.
local M={}
function M.new(root,command,read,put,now,loaded,store,r)
 local fs=require('nixio.fs');local n=require('nixio');local j=require('luci.jsonc')
 local tc='/root/router-project/experiments/nss8-htb2-20261001/tc-nss'
 local device='athenaigs';local pref=49150
 local function receipts()
  local rows={}
  for line in (read('/sys/kernel/debug/athena_nss_receipts/igs') or ''):gmatch('[^\n]+')do
   local e={};for key,value in line:gmatch('([%w_]+)=(%d+)')do e[key]=tonumber(value)end
   if e.attempt then rows[#rows+1]=e end
  end
  return rows
 end
 local function matching(kind,after)
  local found
  for _,e in ipairs(receipts())do
   if e.interface==5 and e.type==kind and e.attempt>(after or 0) and (not found or e.attempt>found.attempt)then found=e end
  end
  return found
 end
 local function wait_pair(a,b,after)
  local deadline=now()+4
  repeat
   local x,y=matching(a,after),matching(b,after)
   if x and y and x.state==2 and y.state==2 then return {first=x,second=y}end
   assert(not x or x.state==1 or x.state==2,'First interface command was not ACKed')
   assert(not y or y.state==1 or y.state==2,'Second interface command was not ACKed')
   n.nanosleep(0,100000000)
  until now()>=deadline
  error('Interface configuration ACKs unconfirmed; IFB and modules retained')
 end
 local function counter(path)return tonumber(assert(read('/sys/class/net/'..path)))end
 local function sample()
  local text=command(tc..' -s -d qdisc show dev '..device)
  local bytes,packets=text:match('Sent (%d+) bytes (%d+) pkt')
  assert(bytes and packets,'NSS queue statistics unavailable')
  return {atUptime=now(),wanRxBytes=counter('wan/statistics/rx_bytes'),wanRxPackets=counter('wan/statistics/rx_packets'),
   igsBytes=tonumber(bytes),igsPackets=tonumber(packets),queue=text,
   driver=read('/sys/kernel/debug/qca-nss-drv/stats/igs')}
 end
 local out={}
 function out.setup()
  assert(not loaded('act_nssmirred') and not loaded('qca_nss_qdisc'))
  assert(not fs.stat('/sys/class/net/'..device))
  local baseline=command('/sbin/tc -j -d qdisc show dev wan')
  local rows=assert(j.parse(baseline));assert(#rows==5 and rows[1].kind=='mq')
  assert(command(tc..' -d filter show dev wan ingress'):match('^%s*$'))
  r.ingress={phase='prepared',baseline=baseline,device=device,temporary=true,hardwareAdmissionEnabled=false}
  store(r)
  command('/sbin/insmod /lib/modules/6.18.44/qca-nss-qdisc.ko');r.ingress.queueModule=true;store(r)
  command('/sbin/insmod '..root..'/act_nssmirred-receipts.ko');r.ingress.actionModule=true;store(r)
  command('/sbin/ip link add '..device..' type ifb');r.ingress.interface=true;store(r)
  command('/sbin/ip link set dev '..device..' up')
  -- Physical NSS roots do not expose a tcf block. clsact supplies a separate
  -- host egress block after MacVLAN/CAKE, plus the same IGS ingress hook.
  local kind=r.nativeRun and 'clsact' or 'ingress'
  command(tc..' qdisc add dev wan handle ffff: '..kind);r.ingress.ingressQdisc=true;r.ingress.hookKind=kind;store(r)
  r.ingress.filterAttempted=true;store(r)
  command(tc..' filter add dev wan ingress protocol all pref '..pref..' u32 match u32 0 0 action nssmirred redirect dev '..device..' fromdev wan')
  r.ingress.filter=true;r.ingress.bindReceipts=wait_pair(16,15,0);store(r)
  if not r.nativeRun then
   command(tc..' qdisc add dev '..device..' root handle 7a00: nssfq_codel target 5ms interval 100ms flows 1024 quantum 1514 limit 256 set_default accel_mode 0')
   r.ingress.rootQdisc=true;r.ingress.phase='sampling';r.ingress.before=sample();store(r)
  end
 end
 function out.run()
  out.setup()
  for _=1,6 do
   n.nanosleep(1);assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop'))==1)
  end
  r.ingress.after=sample();r.ingress.phase='sampled';store(r)
 end
 function out.setup_native(topology)
  out.setup()
  local plan=dofile(root..'/queue_plan.lua')
  local function rates(prefix)
   local values={}
   for w=1,5 do
    local rows=assert(j.parse(command('/sbin/tc -j -d qdisc show dev '..prefix..w)))
    for _,q in ipairs(rows)do if q.kind=='cake' then values[w]=assert(tonumber(q.options.bandwidth))*8/1000 end end
    assert(values[w],'Software account budget unavailable')
   end
   return values
  end
  local s=r.ingress;s.down=plan.plan(0x7a00,rates('rpifb'));s.up=plan.plan(0x7e00,rates('rpwan'))
  s.upBaseline=command('/sbin/tc -j -d qdisc show dev wan');store(r)
  for _,line in ipairs(s.down.commands)do
   command(tc..' '..string.format(line,device));s.rootQdisc=true;store(r)
  end
  s.uplinkAttempted=true;store(r)
  for _,line in ipairs(s.up.commands)do command(tc..' '..string.format(line,'wan'))end
  for w=1,5 do
   assert(topology.wans['rpwan'..w],'WAN address unavailable')
   command(tc..' filter add dev '..device..' parent 7a00: protocol ip pref '..(5000+w)..
    ' u32 match ip dst '..topology.wans['rpwan'..w]..'/32 flowid '..string.format('%x:',0x7a00+w*16+5))
   -- Restore the account's leaf tag after software CAKE/classification.
   -- Exact RT filters precede these account defaults. No CT/PBR/DSCP change.
   command(tc..' filter add dev wan egress protocol ip pref '..(5000+w)..
    ' u32 match ip src '..topology.wans['rpwan'..w]..'/32 action skbedit priority '..
    string.format('%x:0',0x7e00+w*16+5)..' pass')
  end
  s.phase='shared-account-queues-ready';s.before=sample();store(r)
 end
 function out.cleanup()
  local s=r.ingress;if not s then return end
  if s.filterAttempted then
   local filter=command(tc..' -d filter show dev wan ingress')
   local last=0;for _,e in ipairs(receipts())do last=math.max(last,e.attempt)end
   if filter:find('pref '..pref,1,true)then
    command(tc..' filter del dev wan ingress protocol all pref '..pref)
   else
    local binding=matching(16,0)
    if binding then
     assert(binding.state~=1,'Partial bind still awaiting firmware')
     put('/sys/kernel/debug/athena_nss_receipts/recover','5 '..binding.value..'\n')
    end
   end
   if matching(16,0)then s.unbindReceipts=wait_pair(18,17,last)end
   s.filter=false;s.filterAttempted=false;store(r)
  end
  if s.rootQdisc then command(tc..' qdisc del dev '..device..' root');s.rootQdisc=false;store(r)end
  if s.uplinkAttempted then
   local q=command(tc..' -d qdisc show dev wan')
   if q:find('nsshtb 7e00:',1,true)then command(tc..' qdisc del dev wan root')end
   s.uplinkAttempted=false;store(r)
  end
  if s.interface then command('/sbin/ip link del dev '..device);s.interface=false;store(r)end
  if s.ingressQdisc then command(tc..' qdisc del dev wan '..(s.hookKind or 'ingress'));s.ingressQdisc=false;store(r)end
  if s.actionModule then command('/sbin/rmmod act_nssmirred');s.actionModule=false;store(r)end
  if s.queueModule then command('/sbin/rmmod qca_nss_qdisc');s.queueModule=false;store(r)end
  assert(command('/sbin/tc -j -d qdisc show dev wan')==s.baseline,'Physical WAN root changed')
  assert(not fs.stat('/sys/class/net/'..device) and not loaded('act_nssmirred') and not loaded('qca_nss_qdisc'))
  s.phase='restored';s.baseline=nil;s.rollbackConfirmed=true;store(r)
 end
 return out
end
return M
