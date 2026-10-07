import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {persistentSsh} from './persistent-ssh-candidate.mjs';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/v53-control-framing',save=(n,v)=>fs.writeFileSync(root+'/'+n+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
assert.ok(!fs.existsSync(root+'/probe-once-private.json'));save('probe-once-private',{at:new Date().toISOString(),readOnlyRemoteCommands:true,noFixtureNssOrFirewallWrites:true,originalEightSecondCommandLimit:true});
const quote=s=>"'"+s.replaceAll("'","'\\''")+"'",began=performance.now(),channels=[];
const definitions=[false,true,false,true];
try{
 for(let i=0;i<definitions.length;i++)channels.push({index:i,paced:definitions[i],channel:persistentSsh({paced:definitions[i]})});
 const results=await Promise.all(channels.map(async x=>{
  const record={index:x.index,paced:x.paced,pid:x.channel.pid,startedAt:new Date().toISOString()};
  try{record.connection=await x.channel.exec('python3 -B -E -s -u -c '+quote("import os,json;print(json.dumps({'connection':os.getenv('SSH_CONNECTION')}))"),'',{milliseconds:8000});assert.equal(record.connection.code,0);
   const input='C'.repeat(16384),digest=crypto.createHash('sha256').update(input).digest('hex');
   const command='python3 -B -E -s -u -c '+quote("import sys,json,hashlib;b=sys.stdin.buffer.read();assert len(b)==16384 and hashlib.sha256(b).hexdigest()=='"+digest+"';print(json.dumps({'passed':True,'inputBytes':len(b)}))");
   record.large=await x.channel.exec(command,input,{milliseconds:8000});record.passed=record.large.code===0&&JSON.parse(record.large.stdout).passed;
  }catch(e){record.passed=false;record.error=String(e);}record.elapsedSeconds=(performance.now()-began)/1000;save('channel-'+x.index+'-raw-private',record);return record;
 }));
 const router=await connectRouter();let raw;
 try{const e=encode('conntrack -L -p tcp --orig-src 192.168.237.207 --orig-dst 172.93.163.251 -o extended,id');raw=receipt(await router.run(e.command),e);save('conntrack-raw-private',raw);assert.equal(raw.code,0);}finally{router.close();}
 const summary=results.map(r=>{let localPort=null;if(r.connection?.code===0){const c=JSON.parse(r.connection.stdout).connection.trim().split(/\s+/);localPort=Number(c[1]);}
  const flow=localPort?raw.stdout.split('\n').find(s=>s.includes(' dport=22 ')&&s.match(new RegExp('\\bdport='+localPort+'\\b'))):null;
  const mark=flow?Number(flow.match(/\bmark=(\d+)/)?.[1]):null;return{index:r.index,paced:r.paced,passed:r.passed,connectionCompleted:r.connection?.code===0,largeInputBytes:r.passed?16384:0,elapsedSeconds:r.elapsedSeconds,ctMatched:!!flow,wan:mark!==null?((mark&0xff0000)>>>16):null,error:r.error?'Owned control input timed out or refused':null};});
 save('summary',{readOnlyRemoteCommands:true,noFixtureNssOrFirewallWrites:true,sshPoliciesUnchanged:true,probes:summary,comparisonOnly:true});console.log(JSON.stringify({probes:summary,noFixtureNssOrFirewallWrites:true}));
}finally{for(const x of channels)x.channel.close();}
