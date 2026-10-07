import{compactSshOptions}from'./ssh-options.mjs';
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createPhaseTracker} from '../v48-ssh-phase/ssh-phase.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';

const root='work/v50-compact-handshake';
const save=(name,value)=>fs.writeFileSync(root+'/'+name+'.json',JSON.stringify(value,null,2)+'\n',{flag:'wx'});
assert.ok(!fs.existsSync(root+'/probe-once-private.json'));
const prior=JSON.parse(fs.readFileSync('work/v45-early-acquisition/active-private.json'));
assert.ok(prior.state==='RESTORED'&&prior.restorationPassed&&!fs.existsSync('work/v45-early-acquisition/active-lock'));
assert.ok(!fs.existsSync('work/v48-ssh-phase/active-private.json')&&!fs.existsSync('work/v48-ssh-phase/active-lock'));
save('probe-once-private',{at:new Date().toISOString(),readOnlyRemoteCommand:true,remoteAlarmSeconds:7,
  clientSeconds:8,probes:4,noNssOrFirewallOrEndpointWrites:true,noGlobalSshSettingsChanged:true});
const began=performance.now(),elapsed=()=> (performance.now()-began)/1000;
const quote=x=>"'"+x.replaceAll("'","'\\''")+"'";
const marker=crypto.randomBytes(8).toString('hex');
const command='python3 -B -E -s -u -c '+quote("import os,json,time,signal;signal.alarm(7);print(json.dumps({'marker':'"+marker+"','sshConnection':os.getenv('SSH_CONNECTION')}),flush=True);time.sleep(5)");
const definitions=[{slot:'tcp',kind:'default'},{slot:'tcp2',kind:'compact'},{slot:'tcp3',kind:'default'},{slot:'tcp4',kind:'compact'}];
const running=[];
const tasks=definitions.map(d=>new Promise((resolve,reject)=>{
  const options=d.kind==='compact'?[...compactSshOptions]:[];
  const child=spawn('ssh',['-v',...options,'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
    '-o','ConnectTimeout=8','-o','ServerAliveInterval=0','sub2api-dallas',command],{windowsHide:true,stdio:['ignore','pipe','pipe']});
  running.push({slot:d.slot,kind:d.kind,pid:child.pid});
  const tracker=createPhaseTracker({slot:d.slot,attempt:1,ownerPid:()=>child.pid,elapsed});
  let stdout='',stderr='',timedOut=false;
  const timer=setTimeout(()=>{timedOut=true;child.kill();},8000);
  child.stdout.on('data',b=>{stdout+=b;tracker.payload(b.length);if(Buffer.byteLength(stdout)>4096)child.kill();});
  child.stderr.on('data',b=>{stderr+=b;tracker.consume(b);if(Buffer.byteLength(stderr)>16384)child.kill();});
  child.once('error',reject);child.once('close',code=>{
    clearTimeout(timer);const x={...d,code,timedOut,seconds:elapsed(),stdout,stderr,phase:tracker.snapshot('probe-close',code)};
    save(d.slot+'-raw-private',x);resolve(x);
  });
}));
await new Promise(r=>setTimeout(r,350));
const ids=running.map(x=>x.pid).join(',');
const ps="$taskIds=@("+ids+");@(Get-NetTCPConnection -ErrorAction SilentlyContinue|Where-Object{$taskIds -contains [int]$_.OwningProcess}|Select-Object OwningProcess,LocalAddress,LocalPort,RemoteAddress,RemotePort,State)|ConvertTo-Json -Depth 4 -Compress";
const local=spawn('powershell.exe',['-NoProfile','-NonInteractive','-Command',ps],{windowsHide:true,stdio:['ignore','pipe','pipe']});let out='',err='';
local.stdout.on('data',b=>out+=b);local.stderr.on('data',b=>err+=b);
const localTimer=setTimeout(()=>local.kill(),10000);const localCode=await new Promise(r=>local.once('close',r));clearTimeout(localTimer);
save('local-sockets-private',{code:localCode,stdout:out,stderr:err,children:running});
let router;
try {
  router=await connectRouter();const e=encode('conntrack -L -p tcp --orig-src 192.168.237.207 --orig-dst 172.93.163.251 -o extended,id');
  const raw=receipt(await router.run(e.command),e);save('conntrack-raw-private',raw);assert.equal(raw.code,0);
} catch(error){save('conntrack-read-error-private',{error:String(error)});}
finally{router?.close();}
const results=await Promise.all(tasks);
const sockets=localCode===0&&out.trim()?JSON.parse(out):[];
const rows=Array.isArray(sockets)?sockets:[sockets];
const raw=fs.existsSync(root+'/conntrack-raw-private.json')?JSON.parse(fs.readFileSync(root+'/conntrack-raw-private.json')).stdout:'';
const summary=results.map(x=>{
  const socket=rows.find(y=>y.OwningProcess===x.phase.ownerPid&&y.RemotePort===22);
  const flow=socket?raw.split('\n').find(s=>s.includes('sport='+socket.LocalPort+' ')&&s.includes('dport=22 ')):null;
  const mark=flow?Number(flow.match(/\bmark=(\d+)/)?.[1]):null;
  return {slot:x.slot,kind:x.kind,code:x.code,timedOut:x.timedOut,seconds:x.seconds,
    phase:x.phase.phase,markerReturned:x.stdout.includes(marker),
    localSocketMatched:!!socket,ctMatched:!!flow,wan:mark!==null?((mark&0xff0000)>>>16):null,
    stageEvents:x.phase.events};
});
const passed=summary.some(x=>x.markerReturned);
save('summary',{passed,noNssOrFirewallOrEndpointWrites:true,sshPoliciesUnchanged:true,probes:summary,
  comparisonDoesNotProveExactPacketLossLocation:true,remainingTestProcesses:0});
console.log(JSON.stringify({passed,probes:summary,noNssOrFirewallOrEndpointWrites:true}));
