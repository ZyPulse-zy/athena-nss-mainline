local j=require('luci.jsonc')
local factory=assert(loadstring([===[__CORE__]===]))()
local source=assert(loadstring([===[__CT__]===]))()
local backend=assert(loadstring([===[__BACKEND__]===]))()
local cfg=assert(j.parse([===[__POLICY__]===]))
local obs={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',groupRunnerPath='/root/router-project/classifier/nss23-fixture/group-runner',queryTimeoutSeconds=1,maxQueryAgeSeconds=2,maxSourceBytes=262144,maxSourceRows=2048}
local boot='00000000-0000-0000-0000-000000000000';local now=100;local tick=0;local port=51001;local id=101;local wan=5;local mark=327680;local exited=false;local burst=false;local burstOffset=0;local extra=0;local noReply=false;local corrupt=nil
local function row(proto,ctid,sport,w,m,upn,dn,upb,db)
 local p=proto=='udp'and'udp 17 120'or'tcp 6 120 ESTABLISHED'
 return'ipv4 2 '..p..' src=192.168.237.207 dst=192.0.2.1 sport='..sport..' dport='..(proto=='udp'and 45818 or 45817)..' packets='..upn..' bytes='..upb..' src=192.0.2.1 dst=198.51.100.'..w..' sport='..(proto=='udp'and 45818 or 45817)..' dport='..sport..' packets='..dn..' bytes='..db..' [ASSURED] mark='..m..' use=1 id='..ctid..'\n'
end
local runtime={now=function()return now end,boot=function()return boot end,query=function(cmd)
 assert(cmd:find('-s 192.168.237.0/24',1,true))
 local u=1+tick*60;local un=u*156;local t=1+tick*750;if burst then burstOffset=burstOffset+10000000 end
 local out=exited and''or row('udp',id,port,wan,mark,u,noReply and 0 or u,un+burstOffset,noReply and 0 or un+burstOffset)..row('tcp',201,51002,2,131072,1+tick*100,t,52+tick*5200,52+tick*1125000)
 for k=1,extra do local w=1+(k%5);out=out..row('udp',300+k,52000+k,w,w*65536,u,u,un,un)end
 if corrupt then out=corrupt(out)end
 local count=0;for _ in out:gmatch('\n')do count=count+1 end
 return{rawStatus=0,stdout=out,stderr='conntrack v1.4.8 (conntrack-tools): '..count..' flow entries have been shown.\n'}
end}
local function fresh()
 return factory({boot=boot,observer=obs},cfg,function(p)assert(p=='/proc/sys/net/netfilter/nf_conntrack_acct');return'1\n'end,function(cmd)
  assert(cmd=='ip -j -4 address show');local a={};for w=1,5 do a[#a+1]={ifname='rpwan'..w,addr_info={{family='inet',scope='global',['local']='198.51.100.'..w}}}end;return j.stringify(a)
 end,source,runtime)
end
local function sample(step)tick=tick+1;now=now+3;return step()end
local function find(r,ctid)for _,f in ipairs(r.flows)do if tonumber(f.identity.connectionId)==ctid then return f end end end
local checks={};local function yes(v,m)assert(v,m);checks[#checks+1]=m end
local function rejects(fn,m)local ok=pcall(fn);yes(not ok,m)end
local step=fresh();local a=sample(step);yes(find(a,id).decision.class=='UNKNOWN','cold start does not import RT');yes(find(a,201).decision.class=='UNKNOWN','cold TCP not granted')
local b=sample(step);yes(find(b,id).decision.class=='UNKNOWN','one good sample is insufficient');yes(find(b,201).decision.class=='BULK','large TCP rate maps to bulk')
local c=sample(step);yes(find(c,id).decision.class=='RT','two good UDP samples qualify RT')
local rt=backend.leaf(find(c,id));local bulk=backend.leaf(find(c,201));yes(rt.downTag==2399535104 and bulk.downTag==2399469568,'RT and bulk tags are exact NSS leaf handles');yes(not rt.nssPermit and rt.requiresKernelCTPin,'metadata alone never grants NSS')
local originalKey=find(c,id).key;port=51003;id=102;local d=sample(step);yes(find(d,id).decision.class=='UNKNOWN','new port and new CT require cold learning');yes(find(d,id).key~=originalKey,'old port identity retired');sample(step);yes(find(sample(step),id).decision.class=='RT','port change automatically follows')
local mkey=find(sample(step),id).key;mark=335872;local e=sample(step);yes(find(e,id).decision.class=='UNKNOWN'and find(e,id).key~=mkey,'full mark change cannot inherit RT');yes(find(e,id).identity.mark==335872,'low mark bits preserved')
sample(step);sample(step);wan=3;mark=196608;local f=sample(step);yes(find(f,id).decision.class=='UNKNOWN','WAN and NAT change rewarm');sample(step);yes(find(sample(step),id).decision.class=='RT','new existing WAN qualified without changing routing')
exited=true;yes(#sample(step).flows==0,'old-flow exit removes classification');exited=false;yes(find(sample(step),id).decision.class=='UNKNOWN','returning flow is cold')
sample(step);sample(step);step=fresh();yes(find(sample(step),id).decision.class=='UNKNOWN','restart and crash do not trust old metadata');sample(step);yes(find(sample(step),id).decision.class=='RT','restart relearns RT')
burst=true;yes(find(sample(step),id).decision.class=='BULK','RT flow exceeding rate becomes bulk');burst=false;yes(backend.leaf(find(sample(step),id)).candidate==false,'cooldown does not grant acceleration')
burst=false;now=now+31;sample(step);sample(step);sample(step)
noReply=true;step=fresh();sample(step);sample(step);yes(find(sample(step),id).decision.class~='RT','fresh one-way flow not classified as RT');noReply=false
extra=7;step=fresh();sample(step);sample(step);local g=sample(step);yes(g.selection.selectedCount==6 and g.selection.budgetExcluded>=2,'one global per-host slot budget across five existing WANs')
extra=0;corrupt=function(s)return s:gsub('id='..id,'id=201')end;rejects(function()sample(fresh())end,'duplicate CT ID rejects snapshot')
corrupt=function(s)return s:gsub('src=192.168.237.207','src=192.168.238.207',1)end;rejects(function()sample(fresh())end,'foreign LAN source rejects query')
corrupt=function(s)return s:gsub(' use=1',' zone=1 use=1',1)end;rejects(function()sample(fresh())end,'foreign conntrack zone rejects query')
corrupt=function(s)return s:sub(1,-2)end;rejects(function()sample(fresh())end,'truncated query rejects snapshot')
print(j.stringify({passed=true,checks=#checks,cases=checks,scope='Target Lua replay with in-memory CT and interfaces; no actual game, kernel pin, service or network mutation',actualCoreSource=true}))
