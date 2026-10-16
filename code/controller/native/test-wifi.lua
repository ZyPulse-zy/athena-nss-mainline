-- All interface names and addresses below are synthetic fixtures.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local m=dofile(root..'/wifi.lua');local c=dofile(root..'/wifi_collect.lua');local checks=0
local function check(ok,label)assert(ok,label or('check '..(checks+1)));checks=checks+1 end
local function copy(v)if type(v)~='table'then return v end;local out={};for k,x in pairs(v)do out[k]=copy(x)end;return out end
local dev=[[phy#8
 Interface wlan-high
  ifindex 12
  wdev 0x900
  addr 02:00:00:00:00:08
  type AP
  channel 149 (5745 MHz), width: 80 MHz, center1: 5775 MHz
  txpower 20.00 dBm
phy#1
 Interface radio8-ap
  ifindex 22
  wdev 0x200
  addr 02:00:00:00:00:01
  type AP
  channel 36 (5180 MHz), width: 80 MHz, center1: 5210 MHz
  txpower 19.50 dBm
]]
local station=[[Station 02:11:22:33:44:55 (on wlan-high)
 inactive time: 10 ms
 rx bytes: 1000
 rx packets: 0
 tx bytes: 2000
 tx packets: 100
 tx retries: 0
 tx failed: 0
 signal: -55 [-55, -57] dBm
 signal avg: -56 dBm
 tx bitrate: 960.7 MBit/s HE-MCS 9 HE-NSS 2
 rx bitrate: 432.3 MBit/s HE-MCS 5
 authorized: yes
 authenticated: no
 associated: yes
 connected time: 100 seconds
 tid 6
  rx msdu: 0
  tx msdu: 12
  tx msdu retries: 1
  tx msdu failed: 0
]]
local survey=[[Survey data from wlan-high
 frequency: 5745 MHz [in use]
 noise: -95 dBm
 channel active time: 1000 ms
 channel busy time: 100 ms
 channel receive time: 50 ms
 channel transmit time: 20 ms
]]
local ap=m.interfaces(dev);check(#ap==2);check(ap[1].name=='radio8-ap'and ap[1].phy=='phy1','No radio/phy name inference')
check(ap[2].center1MHz==5775 and ap[2].txpowerDbm==20)
local reg=m.regions('global\ncountry US: DFS-FCC\nphy#8 (self-managed)\ncountry CN: DFS-UNSET\n')
check(reg.global=='US'and reg.phy8=='CN')
local st=m.stations(station)[1];check(st.mac=='02:11:22:33:44:55'and st.ap=='wlan-high')
check(st.authenticated==false and st.authorized==true)
check(st.counters.txRetries==0 and st.counters.txFailed==0);check(st.signalDbm==-55 and st.txRateMbps==960.7)
check(st.tids[6].txMsduFailed==0)
local sv=m.survey(survey)[5745];check(sv.activeMs==1000 and sv.busyMs==100 and sv.inUse)
check(m.query_state(95,'command failed: Operation not supported (-95)')=='unsupported')
check(m.query_state(1,'No such file or directory')=='missing')
check(m.query_state(143,'')=='timeout');check(m.query_state(0,'',true)=='oversize');check(m.query_state(1,'permission denied')=='failed')
check(m.delta(10,10,'ok','ok',true).value==0)
check(m.delta(10,nil,'ok','ok',true).state=='missing')
check(m.delta(10,1,'ok','ok',true).state=='reset')
check(m.delta(10,10,'ok','timeout',true).state=='timeout')
check(m.delta(10,10,'ok','unsupported',true).state=='unsupported')
check(m.delta(10,10,'ok','ok','epoch-unverified').state=='epoch-unverified')
check(m.number('9007199254740992')==nil and m.number('1.1')==nil)
local nextsv=copy(sv);nextsv.activeMs=2000;nextsv.busyMs=300
local sd=m.survey_delta(sv,nextsv,'ok','ok',true);check(sd.busyFraction.value==0.2)
check(sd.externalInterferenceMeasured==false)
check(m.survey_delta(sv,sv,'ok','ok',true).busyFraction.state=='no-exposure')
nextsv.busyMs=2000;check(m.survey_delta(sv,nextsv,'ok','ok',true).busyFraction.state=='inconsistent')
check(m.survey_delta(sv,nextsv,'ok','ok',false).busyFraction.state=='epoch-changed')
check(m.survey_delta(nil,nextsv,'unsupported','ok',true).busyFraction.state=='unsupported')
local t=0;local commands={};local sleeps=0;local endpoint=1
local adapter={now=function()return t end,sleep=function(seconds)t=t+seconds;sleeps=sleeps+1;endpoint=2 end}
function adapter.query(command,timeout,cap)
 commands[#commands+1]=command;check(timeout==1 and cap>=1 and cap<=262144)
 check(command=='iw dev'or command=='iw reg get'or command:match('^iw phy phy%d+ info$')or command:match('^iw dev [%w_.%-]+ survey dump$')or command:match('^iw dev [%w_.%-]+ station dump$')or command:match('^cat /proc/sys/kernel/random/boot_id$')or command:match('^cat /sys/kernel/debug/ieee80211/[%w_./:%-]+$'),'Read-only whitelist')
 t=t+0.01
 if command=='cat /proc/sys/kernel/random/boot_id'then return{code=0,text='boot-one'}end
 if command=='iw dev'then return{code=0,text=dev}end
 if command=='iw reg get'then return{code=0,text='global\ncountry CN: DFS-UNSET\n'}end
 if command:match('^iw phy')then return{code=0,text='Supported extended features:\n * [ AQL ]: Airtime Queue Limit\n'}end
 if command=='iw dev wlan-high station dump'then return{code=0,text=endpoint==1 and station or station:gsub('tx bytes: 2000','tx bytes: 3000'):gsub('connected time: 100','connected time: 130')}end
 if command:match('station dump$')then return{code=0,text=''}end
 if command:match('survey dump$')then return{code=0,text=endpoint==1 and survey or survey:gsub('1000 ms','31000 ms'):gsub('100 ms','2100 ms')}end
 if command:match('/nss_stats$')then return{code=0,text=endpoint==1 and'tx_packets 3\ntx_failed 450280\n'or'tx_packets 3\ntx_failed 450300\n'}end
 if command:match('/aqm$')then return{code=0,text='tid ac backlog-bytes drops\n6 VO 0 4\n0 BE 10 0\n'}end
 if command:match('/aql_enable$')then return{code=0,text='1\n'}end
 return{code=1,text='cat: No such file or directory'}
end
local report,raw=c.run(adapter,m,30)
check(sleeps==1 and report.samples==2,'Exactly two endpoint captures')
check(report.stations[1].counters.txBytes.value==1000)
check(report.stations[1].counters.txFailed.value==0,'Measured zero retained')
check(report.stations[1].debug.nss_stats.counters.tx_failed.value==20,'NSS basis separate')
check(report.counterRatiosCalculated==false and report.finalAirTidAcVerified==false)
check(report.radios[1].hostAql.featureAdvertisement.state=='advertised')
check(report.radios[1].hwFlags.values.SUPPORTS_AQL==nil,'AQL is an nl80211 extended feature, not a hwflag')
check(report.stations[1].debug.airtime.state=='missing')
check(report.stations[1].debug.aqm.statistics.rows[1].ac=='VO')
local text=require('luci.jsonc').stringify(report)
check(not text:find('02:11:22:33:44:55',1,true)and not text:find('02:00:',1,true),'No MAC in public report')
check(not text:find('wlan-high',1,true)and not text:find('No such file',1,true),'No private names, commands or logs')
local changed=copy(raw.last);changed.interfaces[2].center1MHz=5795
local r=m.report(raw.first,changed);check(r.stations[1].counters.txBytes.state=='epoch-changed')
changed=copy(raw.last);changed.boot='another';check(m.report(raw.first,changed).stations[1].counters.txBytes.state=='epoch-changed')
changed=copy(raw.last);changed.stations[1].connectedSeconds=1
check(m.report(raw.first,changed).stations[1].counters.txBytes.state=='association-reset')
changed=copy(raw.last);changed.stations[1].connectedSeconds=nil
check(m.report(raw.first,changed).stations[1].counters.txBytes.state=='epoch-unverified')
changed=copy(raw.last);changed.stations[1].connectedSeconds=110
check(m.report(raw.first,changed).stations[1].counters.txBytes.state=='association-discontinuous','Reconnect timer must track the measured interval')
changed=copy(raw.last);changed.stations[1].counters.txBytes=1
check(m.report(raw.first,changed).stations[1].counters.txBytes.state=='reset')
changed=copy(raw.last);changed.queries['stations:wlan-high'].state='failed';changed.stations={}
check(m.report(raw.first,changed).departedStations==0 and m.report(raw.first,changed).unobservedStations==1)
local at=m.airtime('RX: 1 us\nTX: 2 us\nDeficit: VO: -3 us VI: 256 us BE: 0 us BK: 1 us')
check(at.txUs==2 and at.rxUs==1 and at.deficitUs.VO==-3)
check(m.table_stats('AC\tAQL limit low\tAQL limit high\nVO\t5000\t12000').rows[1].limitHighUs==12000)
check(m.table_stats('tid ac drops\n').state=='empty','Successful header-only query is not zero or failure')
check(m.table_stats('tid ac drops\n6 1 4').rows[1].acName=='VI')
local aqmd=m.aqm_delta('tid ac drops marks tx-bytes\n6 1 4 0 100','tid ac drops marks tx-bytes\n6 1 6 0 120','ok','ok',true)
check(aqmd[1].counters.drops.value==2 and aqmd[1].counters.marks.value==0)
check(aqmd[1].counters['tx-bytes'].value==20 and aqmd[1].counters.collisions.state=='missing')
check(m.aqm_delta('tid ac drops\n6 1 4','tid ac drops\n6 1 1','ok','ok',true)[1].counters.drops.state=='reset')
local originalLimits=copy(c.limits);c.limits.endpointSeconds=0.005
local bounded=c.capture(adapter,m,30);check(bounded.queries.interfaces.state=='budget-exhausted')
check(#bounded.interfaces==0)
c.limits=originalLimits
local calls=0;local limited={now=function()return 0 end,query=function(_,timeout,cap)
 calls=calls+1;check(timeout==1 and cap==15);return{code=0,text=string.rep('x',15)}end}
c.limits=copy(originalLimits);c.limits.totalBytesPerEndpoint=15
bounded=c.capture(limited,m,30);check(calls==1 and bounded.queries.interfaces.state=='budget-exhausted','Aggregate output cap stops further I/O')
c.limits=copy(originalLimits);c.limits.queriesPerEndpoint=1
bounded=c.capture(adapter,m,30);check(bounded.queries.interfaces.state=='budget-exhausted'and #bounded.costs==2,'Query count budget retains a missing endpoint record')
c.limits=originalLimits
for _,bad in ipairs{0,4,121,5.5}do check(not pcall(c.run,adapter,m,bad),'Duration rejected before I/O')end
print('Wireless observer assertions passed: '..checks)
