import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {declaredReference,auditScopedBaseline,authSha256} from './declared-baseline.mjs';
const root='work/nss111',h=b=>crypto.createHash('sha256').update(b).digest('hex');
const historical=JSON.parse(fs.readFileSync('work/nss68/nss107-final-20261005-baseline-private.json'));
const current=JSON.parse(fs.readFileSync('work/nss110/v1-final-baseline-private.json'));
const health=JSON.parse(fs.readFileSync('work/nss110/v1-health-controller-status-private.json'));
const checks=[];
function run(name,fn,expected){let ok=false;try{fn();ok=true;}catch{}assert.equal(ok,expected,name);checks.push({name,passed:true,simulated:true,accepted:ok});}
function fixture(running){const b=structuredClone(current),s={up:false,pending:false,'ipv4-address':[]};if(running){b.services['router-project-minieap'].wan4.running=true;b.services['router-project-minieap'].wan4.pid=20931;}
 const seal=running?{running:true,commandMatches:true,pid:20931,start:'203985809',ppid:1,sameProcessBeforeAfter:true}:{running:false,commandMatches:true,instanceStillNotRunning:true};return {b,s,seal};}
function verify(f){const q=declaredReference(historical,f.b,health,authSha256,f.s,f.seal);return auditScopedBaseline(q.reference,f.b);}
for(const running of [false,true])run(running?'failed-wan-running-owned':'failed-wan-stopped',()=>verify(fixture(running)),true);
for(const [name,change]of [
 ['up',f=>f.s.up=true],['pending',f=>f.s.pending=true],['ipv4',f=>f.s['ipv4-address']=[{}]],['address',f=>f.b.addresses.rpwan4=[{}]],['route',f=>f.b.routes['104']+='foreign'],
 ['pid-mismatch',f=>f.seal.pid++],['parent-not-procd',f=>f.seal.ppid=20931],['cmdline-drift',f=>f.seal.commandMatches=false],['process-race',f=>f.seal.sameProcessBeforeAfter=false],['start-invalid',f=>f.seal.start='invalid'],['not-running-seal',f=>f.seal.running=false],
 ['zero-pid',f=>f.b.services['router-project-minieap'].wan4.pid=0],['fractional-pid',f=>f.b.services['router-project-minieap'].wan4.pid=2.5],['unknown-key',f=>f.b.services['router-project-minieap'].wan4.foreign=true],['command-drift',f=>f.b.services['router-project-minieap'].wan4.command.push('foreign')]
])run(name,()=>{const f=fixture(true);change(f);verify(f);},false);
for(const [name,change]of [
 ['foreign-service',b=>b.services['router-project-minieap'].wan2.pid++],['selected-route',b=>b.routes['105']+='foreign'],['pbr-map',b=>b.pbr+='foreign'],['nft-policy',b=>b.nftRuleset+='foreign'],['fixed-mark-rule',b=>b.rules=b.rules.replace('lookup 105','lookup 101')],['manifest',b=>b.protectedManifestSha256='0'.repeat(64)],['ecm-open',b=>b.ecm.stop4=0],['reboot',b=>b.boot+='foreign']
])run(name,()=>{const f=fixture(false),b=structuredClone(f.b);change(b);auditScopedBaseline(f.b,b);},false);
run('exact-known-runtime-process-transition',()=>{const a=fixture(false).b,b=fixture(true).b;auditScopedBaseline(a,b);},true);
run('stopped-seal-still-running',()=>{const f=fixture(false);f.seal.instanceStillNotRunning=false;verify(f);},false);
run('stopped-instance-extra-pid',()=>{const f=fixture(false);f.b.services['router-project-minieap'].wan4.pid=20931;verify(f);},false);
for(const file of fs.readdirSync(root).filter(x=>x.endsWith('.mjs'))){const p=spawnSync(process.execPath,['--check',root+'/'+file],{windowsHide:true,encoding:'utf8'});assert.equal(p.status,0,p.stderr);}
const sourceManifest={};for(const file of fs.readdirSync(root))if(/\.(mjs|lua|py|ps1)$/.test(file))sourceManifest[root+'/'+file]=h(fs.readFileSync(root+'/'+file));
const out={passed:true,onlyFailedUnselectedWan4ProcessEpochChanged:true,routingChangesAllowed:false,nssHardwarePayloadChanged:false,productionExecution:false,checks,sourceManifest};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,newChecks:checks.length,sourceBindings:Object.keys(sourceManifest).length,productionWrites:false}));
