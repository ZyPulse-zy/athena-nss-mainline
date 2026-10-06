local Inventory=(function()
-- Native directory/process inventory. Read-only; no signal or external ls.
local M={}
local function errno(a,b)if type(a)=='number'then return a end;if type(b)=='number'then return b end;return nil end
local function stat(fs,path,absent)local s,a,b=fs.lstat(path);if not s then assert(errno(a,b)==2,'Unknown inventory metadata error');assert(absent,'Required inventory path gone');return nil end;return s end
function M.names(fs,path)
 local a=assert(stat(fs,path,false));assert(a.type=='dir','Inventory directory changed')
 local it,e1,e2=fs.dir(path);assert(type(it)=='function','Native iterator unavailable '..tostring(errno(e1,e2)))
 local names={};while true do local name,x,y=it();if name==nil then local e=errno(x,y);assert(e==nil or e==0,'Native iterator failed');break end;assert(type(name)=='string'and not name:find('/',1,true)and not name:find('\0',1,true),'Malformed directory entry');if name~='.'and name~='..'then names[#names+1]=name end end
 local z=assert(stat(fs,path,false));assert(z.type=='dir'and a.dev==z.dev and a.ino==z.ino,'Inventory directory identity changed');return names
end
local function read(fs,io,path,processDir,limit)
 if not stat(fs,path,true)then return nil,'gone'end
 local f=io.open(path,'r');if not f then if not stat(fs,path,true)or not stat(fs,processDir,true)then return nil,'gone'end;error('Unreadable existing process entry')end
 local data,why=f:read(limit+1);local closed=f:close();assert(closed~=nil,'Process close failed');assert(data~=nil or why==nil,'Process read failed')
 if not stat(fs,processDir,true)then return nil,'gone'end
 data=data or'';assert(#data<=limit,'Process entry exceeds bound');return data
end
local function parse(pid,text)
 if not text then return nil end
 local rest=assert(text:match('^'..pid..' %(.*%) (.+)$'),'Malformed existing process stat');local a={};for x in rest:gmatch('%S+')do a[#a+1]=x end
 assert(a[20]and a[20]:match('^%d+$')and a[2]and a[2]:match('^%d+$'),'Process fields missing');return{pid=pid,start=a[20],state=a[1],parent=tonumber(a[2])}
end
function M.proc(fs,io,pid)
 assert(type(pid)=='number'and pid>=2 and pid<=2147483647 and pid==math.floor(pid),'Invalid process PID');local dir='/proc/'..pid
 if not stat(fs,dir,true)then return nil,'gone'end
 local first=parse(pid,read(fs,io,dir..'/stat',dir,8192));if not first then return nil,'gone'end
 local cmd=read(fs,io,dir..'/cmdline',dir,8192);if cmd==nil then return nil,'gone'end
 local last=parse(pid,read(fs,io,dir..'/stat',dir,8192));if not last then return nil,'gone'end
 if first.start~=last.start then return nil,'replaced'end
 last.argv=cmd;return last
end
return M

end)()
local nativefs=require("nixio.fs")
-- Read-only, kept below the verified 9000-byte SSH command limit.
local j=require('luci.jsonc')
local function read(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return s end
local function cmd(s)local f=assert(io.popen(s..'; rc=$?;printf "\n__COUNTER_READ_RC__%s\n" "$rc"'));local x=f:read('*a');f:close();local body,code=x:match('^(.*)\n__COUNTER_READ_RC__(%d+)\n$');assert(body and code=='0','Read command failed '..s);return body end
local function trim(s)return s:gsub('%s+$','')end
local function now()return tonumber(read('/proc/uptime'):match('^[%d.]+'))end
local client=assert(arg[1]);assert(client:match('^%d+%.%d+%.%d+%.%d+$'));local lite=arg[2]=='lite';local server=arg[3];local mark=arg[4];if server then assert(server:match('^%d+%.%d+%.%d+%.%d+$')and mark:match('^%d+$'))end
local o={boot=trim(read('/proc/sys/kernel/random/boot_id')),startedUptime=now(),kernel=trim(cmd('uname -r')),arch=trim(cmd('uname -m')),nftVersion=trim(cmd('nft --version')),modules=read('/proc/modules'),ecm={},addresses={},queues={},native={}}
o.nftExecutableSha256=assert(cmd('sha256sum /usr/sbin/nft'):match('^(%x+) '));assert(#o.nftExecutableSha256==64)
for key,p in pairs({stop4='front_end_ipv4_stop',stop6='front_end_ipv6_stop',db='ecm_db/connection_count',accel4='ecm_nss_ipv4/accelerated_count',accel6='ecm_nss_ipv6/accelerated_count',pending4='ecm_nss_ipv4/pending_accel_count',pending6='ecm_nss_ipv6/pending_accel_count',decel4='ecm_nss_ipv4/pending_decel_count',decel6='ecm_nss_ipv6/pending_decel_count'})do o.ecm[key]=tonumber(read('/sys/kernel/debug/ecm/'..p))end
for n=1,5 do local d='rpwan'..n;o.addresses[d]=assert(j.parse(cmd('ip -j -4 address show dev '..d)));if not lite then for _,prefix in ipairs({'rpwan','rpifb'})do local dev=prefix..n;local q=assert(j.parse(cmd('tc -j qdisc show dev '..dev)));o.queues[dev]=q;local h;for _,r in ipairs(q)do if r.root then assert(not h);h=r.handle end end;assert(h);o.native[dev]=cmd('tc -d filter show dev '..dev..' parent '..h)end end end
if not lite then o.lan4=cmd('tc -d qdisc show dev lan4');o.rules=cmd('ip -4 rule show');o.pbr=cmd('nft -s list table inet rp_pbr');o.nftRuleset=cmd('nft -s -nnn list ruleset');o.routes={};for n=1,5 do o.routes[tostring(100+n)]=cmd('ip -4 route show table '..(100+n))end;local services=assert(j.parse(cmd('ubus call service list \'{"verbose":true}\'')));o.services={};for name,s in pairs(services)do local out={};for instance,x in pairs(s.instances or{})do out[instance]={running=x.running,pid=x.pid,command=x.command}end;o.services[name]=out end;o.protectedManifestSha256=assert(cmd('sha256sum /root/router-project/experiments/nss6-install-20260930/protected.sha256'):match('^(%x+) '));cmd('sha256sum -c /root/router-project/experiments/nss6-install-20260930/protected.sha256 >/dev/null');o.protectedManifestPassed=true end
if server then o.route=assert(j.parse(cmd('ip -j -4 route get '..server..' mark '..mark)))end
o.query='conntrack -L -p udp --zone 0 --orig-src '..client..' -o extended,id';o.queryZone=0;o.queryExitCode=0;o.ctLines={};for line in cmd(o.query..' 2>/dev/null'):gmatch('[^\n]+')do o.ctLines[#o.ctLines+1]=line end;o.ctObservedAtUptime=now();o.uptime=now()
local function optional(p)local f=io.open(p);if not f then return nil end;local text=f:read('*a');f:close();return j.parse(text)end
local lab='/root/router-project/experiments/nss11-observe2-20261001'
local active=io.open('/root/router-project/active-transaction');local activeText=active and active:read('*a');if active then active:close()end
local pin=io.open(lab..'/controller-pin');if pin then
 local raw=pin:read('*a');pin:close();local h,deadline=raw:match('^([0-9a-f]+) (%d+)%s*$');assert(h and #h==64);o.actualDeadline=tonumber(deadline)
 if activeText==('nss11-observe2-20261001 '..o.boot..' '..deadline..'\n')and now()+8<tonumber(deadline)then
  assert(cmd('sha256sum '..lab..'/runtime.lua'):match('^(%x+) ')=='e4808ec8c5a079d2209d34485deafec8934894f828d4d9a4a32f22da609d251f','Runtime bytes changed; never executed')
  local R=assert(dofile(lab..'/runtime.lua'));local c=R.load(lab..'/contract.json',h);local A=assert(dofile(lab..'/auth.lua'))
  o.observerHealth=A.health(c,lab..'/contract.json',h,R,true);local snapshot=o.observerHealth.bundleSnapshot;o.observerHealth.bundleSnapshot=nil;if snapshot then o.state=snapshot.state;o.export=snapshot.export;o.bundleOwner=snapshot.owner end;o.lease=optional(c.production.leasePath);o.runner=optional(lab..'/runner.info');o.supervisor=optional(lab..'/supervisor.info')
 end
end
local nativefs=require('nixio.fs');o.ownOutputMetadata={}
for _,kind in ipairs({'bundle','lease'})do for _,suffix in ipairs({'','.new'})do local p='/tmp/nss11-observe2-20261001/'..kind..'.json'..suffix;local st,a,b=nativefs.lstat(p);if st then o.ownOutputMetadata[kind..suffix]={exists=true,type=st.type,nlink=st.nlink,uid=st.uid,gid=st.gid,modedec=st.modedec}else assert(a==2 or b==2,'Unknown output metadata');o.ownOutputMetadata[kind..suffix]={exists=false}end end end
o.ownScratch={};local ds,a,b=nativefs.lstat('/tmp/nss11-observe2-20261001');if ds then assert(ds.type=='dir'and ds.uid==0 and ds.gid==0 and ds.modedec==700);o.ownDirectoryExists=true;for _,name in ipairs(Inventory.names(nativefs,'/tmp/nss11-observe2-20261001'))do if name~='owner'and name~='bundle.json'and name~='lease.json'then o.ownScratch[#o.ownScratch+1]=name end end else assert(a==2 or b==2,'Unknown directory metadata');o.ownDirectoryExists=false end
if not lite then
 o.originalFiles={}
 for _,p in ipairs({'/root/router-project/scripts/game-qos.lua','/root/router-project/policy/game-qos.json','/etc/init.d/router-project-game-qos'})do
  local a=assert(nativefs.lstat(p));assert(a.type=='reg'and a.nlink==1 and a.uid==0 and a.gid==0,'Original file identity unknown')
  local h=assert(cmd('sha256sum '..p):match('^(%x+) '));local b=assert(nativefs.lstat(p));for _,k in ipairs({'type','nlink','uid','gid','modedec','dev','ino','size','mtime','ctime'})do assert(a[k]==b[k],'Original file hash race')end
  o.originalFiles[p]={sha256=h,mode=a.modedec,uid=a.uid,gid=a.gid}
 end
end
o.cpu=read('/proc/stat'):match('^cpu%s+([^\n]+)');o.softnet=read('/proc/net/softnet_stat');o.frequencyKHz=tonumber(read('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'))
o.links={};for n=1,5 do local dev='rpwan'..n;o.links[dev]={rxBytes=tonumber(read('/sys/class/net/'..dev..'/statistics/rx_bytes')),rxPackets=tonumber(read('/sys/class/net/'..dev..'/statistics/rx_packets'))}end
o.nftRuleset=o.nftRuleset or nil;print(j.stringify(o))
