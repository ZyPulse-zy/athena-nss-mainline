import fs from 'node:fs';import assert from 'node:assert/strict';import net from 'node:net';import {spawn} from 'node:child_process';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss94',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),chosen=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')).pairs[0];assert.ok(chosen);const f=chosen.udp;
for(const v of [f.original.src,f.original.dst,f.reply.src,f.reply.dst])assert.equal(net.isIP(v),4);for(const p of [f.original.sport,f.original.dport])assert.ok(Number.isInteger(p)&&p>0&&p<=65535);assert.ok(Number.isInteger(f.wan)&&f.wan>=1&&f.wan<=5);
const quote=x=>"'"+x.replaceAll("'","'\\''")+"'";const capture=`import socket,struct,json,time
c=${JSON.stringify({token:config.token,port:config.udpPort})}
token=bytes.fromhex(c['token']);s=socket.socket(socket.AF_PACKET,socket.SOCK_DGRAM,socket.htons(0x0003));s.settimeout(.2);due=time.monotonic()+55;rows=[]
while time.monotonic()<due:
 try:data,address=s.recvfrom(2048)
 except socket.timeout:continue
 if len(data)<28 or data[0]>>4!=4 or data[9]!=17:continue
 h=(data[0]&15)*4
 if len(data)<h+136:continue
 sp,dp=struct.unpack('!HH',data[h:h+4])
 if sp!=c['port'] and dp!=c['port']:continue
 if data[h+8:h+40]!=token:continue
 rows.append({'at':time.time(),'sequence':struct.unpack('!Q',data[h+40:h+48])[0],'direction':'out' if sp==c['port'] else 'in','interface':address[0],'packetType':address[2]})
print(json.dumps({'passed':True,'rows':rows,'readonly':True}))
`;
const cap=spawn('ssh',['-o','BatchMode=yes','-o','ConnectTimeout=8','sub2api-dallas','timeout -k 1 60 python3 -B -E -s -u -c '+quote(capture)],{windowsHide:true,stdio:['ignore','pipe','pipe']});let stdout='',stderr='';cap.stdout.on('data',b=>stdout+=b);cap.stderr.on('data',b=>stderr+=b);const done=new Promise(r=>cap.once('close',code=>r(code)));const hard=setTimeout(()=>cap.kill(),67000);
const query='/usr/bin/timeout -k 1 1 /usr/sbin/conntrack -L -f ipv4 --zone 0 -p udp -s '+f.original.src+' -d '+f.original.dst+' --sport '+f.original.sport+' --dport '+f.original.dport+' -o extended,id';
const c=await connectRouter();const chunks=[];let firstBoot;
try{
 const clocks=[];for(let i=0;i<3;i++){const t0=Date.now()/1000;const r=await c.run("/usr/bin/lua -e 'local h=assert(io.open(\"/proc/uptime\"));local u=tonumber(h:read(128):match(\"^[%d.]+\"));h:close();print(u)' ");const t1=Date.now()/1000;assert.equal(r.code,0);const u=Number(r.stdout.trim());assert.ok(u>0);clocks.push({routerUptime:u,midpointOffset:(t0+t1)/2-u,uncertaintySeconds:(t1-t0)/2,t0,t1})}fs.writeFileSync(load.dir+'/queue-clock-private.json',JSON.stringify({samples:clocks,chosen:clocks.toSorted((a,b)=>a.uncertaintySeconds-b.uncertaintySeconds)[0]},null,2));
 for(let batch=0;batch<8;batch++){
 const script=`local j=require('luci.jsonc');local n=require('nixio');local function read(p)local h=assert(io.open(p));local x=h:read('*a');h:close();return x end;local function now()return tonumber(read('/proc/uptime'):match('^[%d.]+'))end
local function run(cmd)local h=assert(io.popen(cmd));local raw=h:read(16385)or'';local ok=h:close();assert(ok and #raw<=16384);return assert(j.parse(raw))end
local function cake()local rows=run('/usr/bin/timeout -k 1 1 /sbin/tc -j -s -d qdisc show dev rpifb${f.wan}');assert(#rows==1 and rows[1].kind=='cake' and #rows[1].tins==4);local q=rows[1];return {packets=q.packets,bytes=q.bytes,drops=q.drops,overlimits=q.overlimits,backlog=q.backlog,qlen=q.qlen,bandwidth=q.options.bandwidth,tins=q.tins}end
local function redirect()local rows=run('/usr/bin/timeout -k 1 1 /sbin/tc -j -s filter show dev rpwan${f.wan} ingress');local a={};for _,r in ipairs(rows)do if r.options and r.options.actions then for _,x in ipairs(r.options.actions)do assert(x.kind=='mirred' and x.to_dev=='rpifb${f.wan}');a[#a+1]=x.stats end end end;assert(#a==1);return a[1]end
local function nic()local o={};for _,dev in ipairs({'wan','rpwan${f.wan}','rpifb${f.wan}','lan4'})do local s={};for _,k in ipairs({'rx_packets','rx_bytes','rx_dropped','rx_errors','tx_packets','tx_bytes','tx_dropped','tx_errors'})do s[k]=assert(tonumber(read('/sys/class/net/'..dev..'/statistics/'..k)))end;o[dev]=s end;return o end
local function softnet()local o={};for line in read('/proc/net/softnet_stat'):gmatch('[^\\n]+')do local a={};for v in line:gmatch('%S+')do a[#a+1]=tonumber(v,16)end;o[#o+1]={processed=a[1],dropped=a[2],squeeze=a[3]}end;return o end
local o={boot=read('/proc/sys/kernel/random/boot_id'):gsub('%s+$',''),samples={}};local untilAt=now()+6
repeat local at=now();assert(tonumber(read('/sys/kernel/debug/ecm/front_end_ipv4_stop'))==1 and tonumber(read('/sys/kernel/debug/ecm/front_end_ipv6_stop'))==1 and tonumber(read('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count'))==0)
local h=assert(io.popen([=[${query}]=]));local raw=h:read(4097)or'';local rc=h:close();assert(#raw<=4096,'Exact CT output overflow');local ctEnd=now();local q=cake();local red=redirect();local s={startedAt=at,ctEndedAt=ctEnd,endedAt=now(),raw=raw,status=rc,cake=q,redirect=red,nic=nic(),softnet=softnet(),cpu=read('/proc/stat'):match('[^\\n]+')};o.samples[#o.samples+1]=s;n.nanosleep(0,800000000)
until now()>=untilAt
print(j.stringify(o))`;
 const enc=encode("/usr/bin/timeout -k 1 8 /usr/bin/lua - <<'NSS94_READ_ONLY_QUEUES'\n"+script+"\nNSS94_READ_ONLY_QUEUES\n"),t0=Date.now()/1000;const raw=receipt(await c.run(enc.command),enc);const t1=Date.now()/1000;fs.writeFileSync(load.dir+'/router-queues-'+batch+'-private.json',JSON.stringify({t0,t1,...raw},null,2));assert.equal(raw.code,0,raw.stderr);const chunk=JSON.parse(raw.stdout);firstBoot??=chunk.boot;assert.equal(chunk.boot,firstBoot);chunks.push({...chunk,t0,t1});console.log(JSON.stringify({batch:batch+1,routerSamples:chunk.samples.length,routerWrites:false,nssOpened:false}));
 }
 const code=await done;clearTimeout(hard);fs.writeFileSync(load.dir+'/server-queues-private.json',JSON.stringify({code,stdout,stderr},null,2));assert.equal(code,0,stderr);fs.writeFileSync(load.dir+'/queue-observation-private.json',JSON.stringify({passed:true,query,chosen,router:chunks,server:JSON.parse(stdout),routerWrites:false,nssOpened:false},null,2));console.log(JSON.stringify({passed:true,routerSamples:chunks.reduce((a,b)=>a+b.samples.length,0),serverPackets:JSON.parse(stdout).rows.length,wan:f.wan,routerWrites:false,nssOpened:false}));
}finally{clearTimeout(hard);cap.kill();c.close()}
