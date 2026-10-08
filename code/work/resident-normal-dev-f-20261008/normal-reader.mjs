import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import{patchPublicationRead}from'./publication-read.mjs';
import {candidateAdapter} from '../nss143/candidate-adapter.mjs';
import {verifyDeployment} from '../resident-dev-20261007/deployment-binding.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {selectNormalCandidates} from './normal-policy.mjs';

const rootPattern=/^work\/(resident-rc1-run-\d{14}-[a-f0-9]{8}|resident-normal-observe-\d{14}-[a-f0-9]{8})$/;
const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
export function ownershipScript(flows){
 assert.ok(flows.length<=128);const ports=[...new Set(flows.map(f=>f.identity.original.sport))];
 assert.ok(ports.every(p=>Number.isInteger(p)&&p>0&&p<65536));
 return String.raw`$ErrorActionPreference='Stop';$at=(Get-Date).ToUniversalTime().ToString('o');$ports=@(${ports.join(',')});
$tcp=@(Get-NetTCPConnection -ErrorAction Stop|Where-Object{$_.State -eq 'Established' -and $_.LocalAddress -eq '192.168.237.207' -and $_.LocalPort -in $ports}|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess)
$udp=@(Get-NetUDPEndpoint -ErrorAction Stop|Where-Object{$_.LocalPort -in $ports -and $_.LocalAddress -in @('192.168.237.207','0.0.0.0','::')}|Select-Object LocalAddress,LocalPort,OwningProcess)
if($tcp.Count -gt 128 -or $udp.Count -gt 128){throw 'Normal socket inventory exceeds128'}
$ids=@(@($tcp)+@($udp)|ForEach-Object{$_.OwningProcess}|Select-Object -Unique);if($ids.Count -gt 128){throw 'Normal process inventory exceeds128'}
$rows=@();if($ids.Count){$filter=($ids|ForEach-Object{'ProcessId='+[int]$_}) -join ' OR ';foreach($p in @(Get-CimInstance Win32_Process -Filter $filter)){$rows+=@{pid=[int]$p.ProcessId;start=if($p.CreationDate){$p.CreationDate.ToUniversalTime().ToString('o')}else{''};executable=[string]$p.ExecutablePath;commandReadable=[bool]$p.CommandLine}}}
@{at=$at;processes=$rows;tcp=$tcp;udp=$udp}|ConvertTo-Json -Depth 6 -Compress`;
}
export function normalReaderCode(){
 const {deployment,config}=verifyDeployment();
 const owner={base:deployment.base,configSha256:deployment.configHash,workerSha256:config.files['worker.lua']};
 const adapter=candidateAdapter(patchPublicationRead(fs.readFileSync('work/nss49/classifier.lua','utf8'))).source;
 const lua=String.raw`local fs=require('nixio.fs');local j=require('luci.jsonc');local function read(p,l)local f=assert(io.open(p));local b=f:read(l+1)or'';f:close();assert(#b<=l);return b end;local function now()return tonumber(read('/proc/uptime',128):match('^[%d.]+'))end
local function run(s)assert(s:match('^/usr/bin/sha256sum /root/router%-project/classifier/nss23%-[%w%-]+/config.json$'));local h=assert(io.popen(s));local b=h:read(256);assert(h:close());return b end
local A=assert(loadstring([====[${adapter}]====]))();local P={boot=read('/proc/sys/kernel/random/boot_id',128):gsub('%s+$',''),classifierOwner=assert(j.parse([===[${JSON.stringify(owner)}]===])),selected={}}
local a=A.new(P,fs,j,read,now,run,{deadline=now()+10});local c=a.candidates();local flows={};for _,f in ipairs(c.flows)do local i,d=f.identity,f.decision;if i.original.src=='192.168.237.207'and math.floor(i.mark/8192)%2==0 and(i.protocolNumber==6 and d.class=='BULK'or i.protocolNumber==17 and d.class=='RT'and d.budgetAdmitted==true)then flows[#flows+1]=f;assert(#flows<=128)end end
local out=assert(j.stringify({producer=c.producer,sourceSequence=c.sourceSequence,sourceAge=now()-c.startedAtUptime,flows=flows,routerWrites=false,nssAdmissionAllowed=false}));assert(#out<=65536);print(out)`;
 return lua;
}
export async function readNormalCandidates(root,{scope}={}){
 assert.match(root,rootPattern);assert.ok(fs.statSync(root).isDirectory());
 const began=performance.now(),token=crypto.randomUUID(),lua=normalReaderCode();
 const c=await connectRouter();let raw,e;
 try{e=encode("lua - <<'NORMAL_FLOW_READ'\n"+lua+'\nNORMAL_FLOW_READ\n');raw=receipt(await c.run(e.command),e);}finally{c.close();}
 save(root+'/normal-native-'+token+'-private.json',raw);assert.equal(raw.code,0,raw.stderr);const native=JSON.parse(raw.stdout);
 let pc={at:new Date().toISOString(),processes:[],tcp:[],udp:[],ageSeconds:0};
 if(native.flows.length){
  const script=ownershipScript(native.flows);const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',script],{encoding:'utf8',windowsHide:true,timeout:Math.max(1,Math.floor(15000-(performance.now()-began))),maxBuffer:1048576});
  save(root+'/normal-pc-'+token+'-private.json',{code:p.status,stdout:p.stdout,stderr:p.stderr,error:p.error?.code??null});assert.equal(p.status,0,'Normal OS identity inventory refused');pc=JSON.parse(p.stdout.replace(/^\uFEFF/,''));pc.ageSeconds=(Date.now()-Date.parse(pc.at))/1000;
 }
 // Conservatively include the entire native + Windows read time in freshness.
 native.sourceAge+=(performance.now()-began)/1000;
 const out=selectNormalCandidates(native,pc,scope);save(root+'/normal-frame-'+token+'-private.json',out);
 fs.writeFileSync(root+'/controlled-candidates-private.json',JSON.stringify(out,null,2)+'\n');
 fs.writeFileSync(root+'/controlled-pc-raw-private.json',JSON.stringify({code:0,pc,trafficGenerated:false,normalProcessIdentityRequired:true},null,2)+'\n');
 return out;
}
export const visible=frame=>({readonly:true,sourceAge:frame.sourceAge,sourceSequence:frame.sourceSequence,tcpBulk:frame.tcp.length,udpRt:frame.udp.length,triples:frame.pairs.length,routerWrites:false,trafficGenerated:false,desktopOperated:false});
