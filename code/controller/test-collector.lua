-- Real collection/parsing with mocked read-only processes and files.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));local j=require('luci.jsonc');local fs=require('nixio.fs')
local originalOpen,originalPopen,originalDir=io.open,io.popen,fs.dir
local failed,invalid,at,checks=nil,nil,100,0
local commands={}
local function check(ok)assert(ok);checks=checks+1 end
local values={neighbors={{dst='192.0.2.1',lladdr='02:00:00:00:00:01'}},addresses={}}
for w=1,5 do values.addresses[w]={ifname='rpwan'..w,addr_info={{family='inet',scope='global',['local']='198.51.100.'..w}}}end
io.open=function(path,mode)
 check(mode==nil or mode=='r')
 local text
 if path=='/proc/uptime'then text=tostring(at)..' 0'
 elseif path=='/tmp/dhcp.leases'then text='0 02:00:00:00:00:01 192.0.2.1 host *\n'
 elseif path:match('/brif/lan1/port_no$')then text='1'
 elseif path:match('/brif/phy0%-ap0/port_no$')then text='2'
 else error('Unexpected file read: '..path)end
 return{read=function()return text end,close=function()end}
end
fs.dir=function(path)
 assert(path=='/sys/class/net/br-lan/brif');local i=0
 return function()i=i+1;return({'lan1','phy0-ap0'})[i]end
end
io.popen=function(cmd)
 check(cmd:match('^/usr/bin/timeout %-k 1 1 ')~=nil)
 local name,body
 if cmd:find('neigh show',1,true)then name='neighbors';body=j.stringify(values.neighbors)
 elseif cmd:find('address show',1,true)then name='addresses';body=j.stringify(values.addresses)
 elseif cmd:find('brctl showmacs',1,true)then name='fdb';body='port no mac addr is local? ageing timer\n 1 02:00:00:00:00:01 no 5.00\n'
 elseif cmd:find('ubus call hostapd.',1,true)then name='hostapd';body=j.stringify({clients={}})
 elseif cmd:find('iw dev',1,true)then name='iw';body=''
 elseif cmd:find('/sbin/tc -j -d qdisc show dev rp',1,true)then name='cake';body=j.stringify({{kind='cake',root=true,options={bandwidth=5000000}}})
 else error('Unexpected command: '..cmd)end
 commands[name]=cmd
 if invalid==name then body='invalid JSON'end
 if failed==name then body='';at=at+1 end
 return{read=function()return body..'\nATHENA_COLLECT_EXIT_'..(failed==name and'124'or'0')..'\n'end,close=function()end}
end
local collector=dofile(root..'/collector.lua')
local good=collector.topology();check(good.complete and good.clients['192.0.2.1'].valid and good.wans.rpwan5=='198.51.100.5')
check(good.collection.failures==0 and good.collection.commands.neighbors.exitCode==0)
check(commands.neighbors:find(' 1 /sbin/ip -j ',1,true)~=nil and commands.addresses:find(' 1 /sbin/ip -j ',1,true)~=nil)
failed='neighbors';local bad=collector.topology();check(not bad.complete and bad.collection.failures==1)
check(bad.collection.commands.neighbors.exitCode==124 and bad.collection.commands.neighbors.seconds==1)
failed=nil;invalid='addresses';bad=collector.topology();check(not bad.complete and bad.collection.commands['wan-addresses'].ok)
invalid=nil;failed='hostapd';good=collector.topology();check(good.complete and good.stationSources.iwFallback==1 and good.collection.failures==1)
-- Successful empty neighbors are an actual empty observation, distinguishable
-- from the timeout above. No command status can create an identity by itself.
failed=nil;values.neighbors={};good=collector.topology();check(good.complete and next(good.clients)==nil)
local budgets=collector.software_budgets();check(budgets.complete and budgets.diagnostics.commandCount==10 and budgets.values.up[5]==40000)
failed='cake';budgets=collector.software_budgets();check(not budgets.complete and budgets.diagnostics.commandCount==1 and budgets.diagnostics.failures==1 and budgets.finishedAtUptime-budgets.startedAtUptime==1)
local resolved=collector.resolve({{dst='192.0.2.1',lladdr='02:00:00:00:00:01'}},{},{{mac='02:00:00:00:00:01',ifname='lan1',localEntry=false,age=61}},{},1)
check(not resolved['192.0.2.1'].valid and resolved['192.0.2.1'].reason=='wired-fdb-observation-expired')
io.open,io.popen,fs.dir=originalOpen,originalPopen,originalDir
print(j.stringify({passed=true,checks=checks,mockedProcesses=true,dataPlaneWrites=false,failedReadDistinctFromEmpty=true}))
