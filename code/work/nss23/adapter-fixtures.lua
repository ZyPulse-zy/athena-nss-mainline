local s,c,selected=make();local cfg={generation=c.generation,files={['worker.lua']=string.rep('b',64)},source={groupRunnerPath=c.base..'/group-runner',conntrackPath='/usr/sbin/conntrack',authorizedClient='192.168.237.0/24'}}
c.sourceCommand=table.concat({cfg.source.groupRunnerPath,'1',cfg.source.conntrackPath,'-L','-f','ipv4','--zone','0','-s',cfg.source.authorizedClient,'-o','extended,id'},' ');s.snapshot.provenance.command=c.sourceCommand
local files={};files[c.base..'/config.json']=j.stringify(cfg);files['/root/router-project/game-classifier-generation']=c.base..' '..c.configSha256..'\n';files['/proc/sys/kernel/random/boot_id']=c.boot..'\n'
local ram='/tmp/router-project-game-classifier';files[ram..'/owner']=c.generation..' '..c.boot..'\n'
local clock=101;local guardian={healthy=true,generation=c.generation,boot=c.boot,configSha256=c.configSha256,atUptime=100.9}
local function update()
 files[ram..'/snapshot.json']=j.stringify(s);files[ram..'/guardian.json']=j.stringify(guardian)
 local f={'S','1','0'};for n=4,19 do f[n]='0'end;f[20]=s.start
 files['/proc/'..s.pid..'/stat']=s.pid..' (lua) '..table.concat(f,' ')..'\n';files['/proc/'..s.pid..'/cmdline']=table.concat({'/usr/bin/lua',c.base..'/worker.lua','watch',c.base,c.configSha256},'\0')..'\0'
end
update();local reads,runs=0,0;local fs={lstat=function(p)if files[p]then return{type='reg',uid=0,gid=0,nlink=1,dev=18,ino=1}end end}
local function read(p,cap)reads=reads+1;local x=assert(files[p],p);assert(#x<=cap);return x end
local function run(cmd)runs=runs+1;assert(cmd=='/usr/bin/sha256sum '..c.base..'/config.json','No private conntrack query is allowed');return c.configSha256..'  config.json\n'end
local P={boot=c.boot,classifierOwner={base=c.base,configSha256=c.configSha256,workerSha256=cfg.files['worker.lua']},selected=selected};local record={deadline=120}
local step=Adapter(P,fs,j,read,function()return clock end,run,record);local a=step()
yes(#a.flows==2 and a.flows[1].decision.class=='BULK'and a.flows[2].decision.class=='RT','existing NSS tag-owner call receives correct pair from permanent classifier')
yes(runs==1 and record.adapterPrivateObserverSpawned==false,'adapter starts no private observer or CT query')
yes(record.adapterUsesLongRunningOwner and record.adapterProducer==s.producer,'adapter records long-running process provenance')
yes(Adapter.compareCurrentEpoch().action=='KEEP_IMMUTABLE_EPOCH','live comparison retains same immutable pair')
s.snapshot.flows[2].decision={class='BE',reason='cooldown',budgetAdmitted=false};s.snapshot.flows[2].leaf.class='BE';s.snapshot.flows[2].leaf.candidate=false;s.snapshot.flows[2].leaf.downTag=0;update()
yes(Adapter.compareCurrentEpoch().affected[1]=='udp','adapter detects class change and plans exact affected-slot retirement')
yes(not pcall(step),'adapter refuses to feed a reclassified pair to ECM learning')
guardian.healthy=false;update();yes(#Adapter.compareCurrentEpoch().affected==2,'guardian failure requests retirement of controlled pair')
yes(Adapter.compareCurrentEpoch().clearConntrack==false,'failure recovery never requests CT flush')
print(j.stringify({passed=true,checks=#cases,cases=cases,scope='real adapter and consumer modules with in-memory permanent-owner files; no live hooks or firmware writes'}))
