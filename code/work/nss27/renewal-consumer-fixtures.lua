local function setup()
 local s,c,selected=make();s.publication='before-software-baseline';s.atUptime=100.3
 local cfg={generation=c.generation,nssPublication='classification.json',files={['worker.lua']=string.rep('b',64)},source={groupRunnerPath=c.base..'/group-runner',conntrackPath='/usr/sbin/conntrack',authorizedClient='192.168.237.0/24'}}
 c.sourceCommand=table.concat({cfg.source.groupRunnerPath,'1',cfg.source.conntrackPath,'-L','-f','ipv4','--zone','0','-s',cfg.source.authorizedClient,'-o','extended,id'},' ');s.snapshot.provenance.command=c.sourceCommand
 local ram='/tmp/router-project-game-classifier';local clock=100.4;local files={}
 files[c.base..'/config.json']=j.stringify(cfg);files['/root/router-project/game-classifier-generation']=c.base..' '..c.configSha256..'\n';files['/proc/sys/kernel/random/boot_id']=c.boot..'\n';files[ram..'/owner']=c.generation..' '..c.boot..'\n'
 local guardian={healthy=true,generation=c.generation,boot=c.boot,configSha256=c.configSha256,atUptime=clock}
 local function update()
  files[ram..'/classification.json']=j.stringify(s);files[ram..'/guardian.json']=j.stringify(guardian)
  local f={'S','1','0'};for n=4,19 do f[n]='0'end;f[20]=s.start
  files['/proc/'..s.pid..'/stat']=s.pid..' (lua) '..table.concat(f,' ')..'\n';files['/proc/'..s.pid..'/cmdline']=table.concat({'/usr/bin/lua',c.base..'/worker.lua','watch',c.base,c.configSha256},'\0')..'\0'
 end
 update();local fs={lstat=function(p)if files[p]then return{type='reg',uid=0,gid=0,nlink=1,dev=18,ino=1}end end}
 local function read(p,cap)local v=assert(files[p],p);assert(#v<=cap);return v end
 local runs=0;local function run(cmd)runs=runs+1;assert(cmd=='/usr/bin/sha256sum '..c.base..'/config.json');return c.configSha256..'  config.json\n'end
 local rec={deadline=130};local P={boot=c.boot,classifierOwner={base=c.base,configSha256=c.configSha256,workerSha256=cfg.files['worker.lua']},selected=selected}
 local step=Adapter(P,fs,j,read,function()return clock end,run,rec);step()
 local x={s=s,c=c,rec=rec,update=update,files=files,ram=ram}
 function x.time(t)clock=t;guardian.atUptime=t;update()end
 function x.fresh(seq,start)
  local p=s.snapshot.provenance;p.sequence=seq;p.startedAtUptime=start;p.finishedAtUptime=start+0.2;s.atUptime=start+0.3
  for _,f in ipairs(s.snapshot.flows)do local q=f.identity.queryProvenance;q.querySequence=seq;q.startedAtUptime=start;q.finishedAtUptime=start+0.2;f.observationStartedAtUptime=start;f.observedAtUptime=start+0.2;f.validUntilUptime=start+6 end
  x.time(start+0.4)
 end
 function x.rtGone()local f=s.snapshot.flows[2];f.decision.class='BE';f.decision.budgetAdmitted=false;f.leaf.class='BE';f.leaf.candidate=false;f.leaf.downTag=0;update()end
 return x
end
local x=setup();yes(Adapter.proposeRenewal()==nil,'unchanged sequence makes no renewal proposal')
x.fresh(5,103);local p=Adapter.proposeRenewal();yes(p.expectedSequence==4 and p.nextSequence==5 and p.untilMs==108000 and p.nssAdmissionAllowed==false,'same identity newer source proposes a bounded epoch only')
yes(x.rec.adapterSourceSequence==4 and not x.rec.adapterRenewals,'proposal does not change committed epoch')
yes(not pcall(Adapter.acceptRenewal,p,{sequence=6,classifierUntilMs=108000}),'wrong kernel sequence rejected')
yes(not pcall(Adapter.acceptRenewal,p,{sequence=5,classifierUntilMs=108001}),'wrong kernel deadline rejected')
local a=Adapter.acceptRenewal(p,{sequence=5,classifierUntilMs=108000});yes(a.sourceSequence==5 and a.epochUntil==108 and x.rec.adapterRenewals==1,'exact acknowledgement commits fresh epoch')
x.time(105.4);yes(Adapter.compareCurrentEpoch().action=='KEEP_IMMUTABLE_EPOCH','acknowledged epoch continues past original deadline')
yes(not pcall(Adapter.acceptRenewal,p,{sequence=5,classifierUntilMs=108000}),'already accepted proposal cannot replay')
x=setup();x.fresh(5,103);p=Adapter.proposeRenewal();x.rtGone();yes(not pcall(Adapter.acceptRenewal,p,{sequence=5,classifierUntilMs=108000}),'class change during native update refuses local commit')
yes(Adapter.compareCurrentEpoch().action=='RETIRE_EXACT_SELECTED_SLOTS','changed class requires exact selected retirement')
x=setup();x.fresh(5,103);x.rtGone();yes(not pcall(Adapter.proposeRenewal),'changed class cannot renew')
x=setup();x.fresh(3,103);yes(not pcall(Adapter.proposeRenewal),'regressed source sequence cannot renew')
x=setup();x.fresh(5,104.2);yes(not pcall(Adapter.proposeRenewal),'insufficient old epoch margin cannot renew')
x=setup();x.fresh(5,105);yes(not pcall(Adapter.proposeRenewal),'expired epoch cannot revive')
x=setup();x.fresh(5,103);x.s.producer='different-owner';x.update();yes(not pcall(Adapter.proposeRenewal),'restarted producer cannot renew prior epoch')
x=setup();x.fresh(5,103);x.s.status='degraded';x.s.error='source overflow';x.update();yes(not pcall(Adapter.proposeRenewal),'degraded publication withdraws renewal')
yes(Adapter.compareCurrentEpoch().clearConntrack==false,'failure retirement never requests global conntrack flush')
print(j.stringify({passed=true,checks=#cases,cases=cases,scope='Actual adapter and consumer with deterministic in-memory publications and simulated kernel acknowledgements; no live gate or firmware writes'}))
