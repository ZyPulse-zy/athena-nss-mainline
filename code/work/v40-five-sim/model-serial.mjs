import fs from'node:fs';import assert from'node:assert/strict';import vm from'node:vm';import{EventEmitter}from'node:events';
const root='work/v40-five-sim',source=fs.readFileSync(root+'/native-client.mjs','utf8'),a=source.indexOf('async function startTcp('),b=source.indexOf('\nconst sock=',a);assert.ok(a>0&&b>a);const actual=source.slice(a,b)+';startTcp';
let checks=0;const slots=['tcp','tcp2','tcp3','tcp4'];
function fixture(failFirst=false){
 let active=0,maximum=0,pid=1000,ended=false;const children=new Map(),rotating=new Set(),calls=[],requestedTimeouts=[],errors=[];
 const stats={tcpBytes:0,tcpChildren:slots.map(slot=>({slot,attempt:0,bytes:0,connected:false}))};
 const spawn=(exe,args)=>{const p=new EventEmitter();p.pid=pid++;p.stdout=new EventEmitter();p.stderr=new EventEmitter();p.exitCode=null;p.kill=()=>{if(p.exitCode===null){p.exitCode=1;setTimeout(()=>p.emit('close',1),0)}};calls.push(args);active++;maximum=Math.max(maximum,active);if(!failFirst)setTimeout(()=>{active--;p.stdout.emit('data',Buffer.alloc(128))},5);return p};
 const finish=e=>{ended=true;errors.push(String(e));for(const p of children.values())p.kill()};
 const context={stats,children,rotating,assert,c:{tcpRates:{tcp:8,tcp2:8,tcp3:8,tcp4:8}},originalSender:fs.readFileSync(root+'/download-server.py','utf8'),sshExe:'model-owned-ssh',spawn,quote:x=>x,stamp:()=>{},finish,get ended(){return ended},setTimeout:(f,ms)=>{requestedTimeouts.push(ms);return setTimeout(f,ms===8000?30:ms)},clearTimeout};
 return{start:vm.runInNewContext(actual,context),stats,calls,errors,finish,maximum:()=>maximum,requestedTimeouts,children};
}
const f=fixture();for(const slot of slots)await f.start(slot,1);assert.equal(f.maximum(),1);assert.ok(f.stats.tcpChildren.every(x=>x.connected&&x.bytes===128&&x.attempt===1));checks++;
assert.equal(f.calls.length,4);assert.ok(f.calls.every(args=>args.at(-1).includes('RATE=8_000_000/8')&&args.at(-1).includes('CREDIT=16384')&&args.includes('ConnectTimeout=8')));assert.deepEqual(f.requestedTimeouts,[8000,8000,8000,8000]);checks++;
await f.start('tcp3',2);assert.equal(f.stats.tcpChildren[2].attempt,2);assert.ok(f.stats.tcpChildren.every(x=>x.connected));checks++;
await assert.rejects(f.start('tcp3',4));assert.equal(f.calls.length,5);checks++;
await assert.rejects(f.start('unknown',1));assert.equal(f.calls.length,5);checks++;
const failed=fixture(true);await assert.rejects(failed.start('tcp',1),/first-byte deadline/);failed.finish('model first-byte deadline');assert.equal(failed.calls.length,1);assert.equal(failed.children.get('tcp').exitCode,1);checks++;
fs.writeFileSync(root+'/serial-model-qualified.json',JSON.stringify({passed:true,checks,actualStartTcpSourceModeled:true,maximumUnauthenticatedOwnHandshakeCount:1,firstByteDeadlineMilliseconds:8000,perTcpMbps:8,combinedMbps:32,combinedCreditBytes:65536,hardwareExecuted:false,nssGateOrQosChanged:false},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks,fixtureOnly:true}));
