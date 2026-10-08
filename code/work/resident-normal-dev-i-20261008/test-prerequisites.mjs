import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {prerequisiteLua,prerequisiteShell,prerequisiteCommand,readPrerequisites} from './read-prerequisites.mjs';
import {executeLua,luaLiteral} from '../resident-dev-20261007/lua-local.mjs';
import {encode} from '../nss11/v7-observe-repair/observe2/transport.mjs';

const source=fs.readFileSync('work/nss49/read-prerequisites.lua','utf8');
const checks=[];
const root='work/resident-rc1-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
fs.mkdirSync(root);
const modelDirectory=name=>{const p=root+'/session-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(p);fs.writeFileSync(p+'/model-only.json',JSON.stringify({name,routerAccess:false}));return p;};
async function test(name,fn){await fn();checks.push(name);}
const ip=wan=>'192.0.2.'+wan;
const row=wan=>({wan,auth:{pid:10,start:'456'},status:{up:true,l3_device:'rpwan'+wan,'ipv4-address':[{address:ip(wan)}]},mode:[{linkinfo:{info_data:{mode:'bridge'}}}],stateMajor:242});
const selected={tcp:{protocol:6,zone:0,id:1,wan:3,reply:{dst:ip(3)}},udp:{protocol:17,zone:0,id:2,wan:3,reply:{dst:ip(3)}},tcp2:{protocol:6,zone:0,id:3,wan:5,reply:{dst:ip(5)}}};
const options={base:'/owned',source};
const mock=calls=>({async run(command){calls.push(command);const wan=command.includes('rpwan3')?3:5;return{code:0,stdout:JSON.stringify(row(wan))+'\n',stderr:''};}});

await test('original prerequisite assertions retained and Lua popen removed',()=>{
 const adapted=prerequisiteLua(source);
 assert.ok(!adapted.includes('io.popen'));
 assert.equal(adapted.split('\n').at(-3),source.replaceAll('\r\n','\n').split('\n').at(-3));
 assert.ok(adapted.includes("o.mode[1].linkinfo.info_data.mode=='bridge' and o.status.up and o.mwan3==0 and o.dscp==1 and o.delay==1"));
 assert.ok(adapted.includes("o.devices:find('\\n'..o.stateMajor..' ecm_state\\n',1,true)"));
 assert.throws(()=>prerequisiteLua(source.replace('local function cmd(c)','local function changed(c)')));
});
await test('all WAN commands retain 3s deadline within a single 6s process group',()=>{
 for(let wan=1;wan<=5;wan++){
  const shell=prerequisiteShell(wan,source),command=prerequisiteCommand(wan,source,'/owned');
  assert.equal(shell.split('/usr/bin/timeout -k 1 3 ').length-1,5);
  assert.ok(shell.startsWith('set -eu\n'));assert.ok(command.startsWith('/owned/group-runner 6 /bin/sh -c '));
  assert.ok(shell.includes('show dev rpwan'+wan)&&shell.includes('network.interface.wan'+wan+' status'));
  assert.ok(!/nft |insmod |rmmod |tc .*replace|conntrack .*delete/.test(shell));
  const e=encode(command);assert.ok(e.execBytes<=9000);
 }
 for(const bad of [0,6,1.1,'3; true'])assert.throws(()=>prerequisiteShell(bad,source));
 assert.throws(()=>prerequisiteCommand(3,source,'/owned; true'));
});
await test('shell parses in local Linux without executing any command',()=>{
 const file=root+'/prerequisites.sh';fs.writeFileSync(file,prerequisiteShell(3,source));
 const absolute=path.resolve(file).replaceAll('\\','/'),unix='/mnt/'+absolute[0].toLowerCase()+absolute.slice(2);
 const r=spawnSync('wsl.exe',['-d','Athena-Cake-Build','--exec','/bin/sh','-n',unix],{encoding:'utf8',windowsHide:true,timeout:15000});
 fs.writeFileSync(root+'/shell-syntax-private.json',JSON.stringify({code:r.status,stdout:r.stdout,stderr:r.stderr,error:r.error?.code??null}));assert.equal(r.status,0,r.stderr);
});
const model=row(3),sha='a'.repeat(64),stat=Array(20).fill('0');stat[19]='456';
const files={'/proc/10/stat':'10 (minieap) '+stat.join(' '),'/tmp/router-project-logs/minieap-wan3.log':'Authentication failed\nAuthentication succeeded\n','/proc/sys/kernel/random/boot_id':'model-boot\n','/proc/uptime':'10.0 0.0','/proc/sys/net/ecm/mwan3_enable':'0','/sys/kernel/debug/ecm/ecm_classifier_dscp/enabled':'1','/sys/kernel/debug/ecm/ecm_classifier_default/accel_delay_pkts':'1','/sys/kernel/debug/ecm/ecm_state/state_dev_major':'242','/proc/devices':'Character devices:\n242 ecm_state\n'};
const prelude=`local paths=${luaLiteral(files)};local originalIo=io;local pops=0;local got
arg={'3','__MODE__','__STATUS__','${sha}  eap-header','${sha}  core-guard.sh','${sha}  prepare-macvlans.sh'}
io={open=function(p)return {read=function(self,n)return assert(paths[p],p)end,close=function()end}end,popen=function()pops=pops+1;return {read=function()return nil,'Interrupted system call',4 end,close=function()end}end}
require=function(name)if name=='ubus' then return {connect=function()return {call=function()return {['router-project-minieap']={instances={wan3={running=true,pid=10}}}}end,close=function()end}end}end;if name=='nixio.fs' then return {} end;assert(name=='luci.jsonc');return {parse=function(s)if s=='__MODE__' then return ${luaLiteral(model.mode)} end;if s=='__STATUS__' then return ${luaLiteral(model.status)} end;error('malformed JSON')end,stringify=function(o)got=o;return 'MODEL_ONLY' end}end
print=function()end
`;
await test('actual nil-read failure reproduced locally; adapted reader succeeds without popen',()=>{
 const code=prelude+"\nlocal original=assert(loadstring("+luaLiteral(source)+"));local ok,err=pcall(original);assert(not ok and tostring(err):find('nil value',1,true));assert(pops==1);pops=0\n"+prerequisiteLua(source)+`\nassert(pops==0);assert(got.wan==3 and got.status.l3_device=='rpwan3');assert(got.auth.start=='456' and got.auth.failure==1 and got.auth.success==1);assert(got.eapHeaderSha=='${sha}' and got.coreSha=='${sha}' and got.prepareSha=='${sha}');originalIo.write('PASS\\n')`;
 const r=executeLua(code,'prerequisite-nil-read');fs.writeFileSync(root+'/lua-nil-replay-private.json',JSON.stringify(r));assert.equal(r.code,0,r.stderr);assert.equal(r.stdout.trim(),'PASS');
});
await test('empty input and malformed JSON refuse in local Lua',()=>{
 for(const [name,mutation] of [['empty',"arg[2]=''"],['json',"arg[2]='malformed'"]]){
  const code=prelude+'\n'+mutation+'\nlocal ok=pcall(assert(loadstring('+luaLiteral(prerequisiteLua(source))+")));assert(not ok);originalIo.write('PASS\\n')";
  const r=executeLua(code,'prerequisite-'+name);fs.writeFileSync(root+'/lua-'+name+'-private.json',JSON.stringify(r));assert.equal(r.code,0,r.stderr);assert.equal(r.stdout.trim(),'PASS');
 }
});
await test('same WAN reused while both distinct WANs retain exact status identity',async()=>{
 const calls=[],dir=modelDirectory('success'),rows=await readPrerequisites(mock(calls),dir,selected,options);
 assert.deepEqual(rows.map(q=>q.wan),[3,5]);assert.equal(calls.length,2);
 assert.ok(fs.existsSync(dir+'/prerequisites-tcp-raw-private.json')&&fs.existsSync(dir+'/prerequisites-tcp2-raw-private.json'));
 assert.ok(!fs.existsSync(dir+'/prerequisites-udp-private.json'));
});
await test('command timeout is retained before refusal and cannot execute the next WAN',async()=>{
 const dir=modelDirectory('timeout'),calls=[];
 await assert.rejects(readPrerequisites({async run(c){calls.push(c);return{code:124,stdout:'',stderr:'model timeout'};}},dir,selected,options),/raw receipt retained/);
 assert.equal(calls.length,1);assert.equal(JSON.parse(fs.readFileSync(dir+'/prerequisites-tcp-raw-private.json')).code,124);
 assert.ok(!fs.existsSync(dir+'/prerequisites-tcp-private.json'));
});
await test('foreign NAT address, wrong WAN and malformed or oversized response refuse',async()=>{
 for(const invalid of [{...row(3),wan:5},{...row(3),status:{...row(3).status,'ipv4-address':[{address:ip(4)}]}},'{',' '.repeat(65537)]){
  const dir=modelDirectory('invalid'),stdout=typeof invalid==='string'?invalid:JSON.stringify(invalid);
  await assert.rejects(readPrerequisites({async run(){return{code:0,stdout,stderr:''};}},dir,selected,options));
  assert.ok(fs.existsSync(dir+'/prerequisites-tcp-raw-private.json'));assert.ok(!fs.existsSync(dir+'/prerequisites-tcp-private.json'));
 }
});
console.log(JSON.stringify({passed:true,checks:checks.length,names:checks,modelOnly:true,routerAccess:false,dir:root}));
