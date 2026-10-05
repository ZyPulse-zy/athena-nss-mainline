import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {packetTemplate} from './uplink-tag-plan.mjs';import {validateAcceleratedState} from './parse-ecm-any-wan.mjs';import {buildPayload} from './payload.mjs';
import{packLua}from'./pack-lua.mjs';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss112',h=b=>crypto.createHash('sha256').update(b).digest('hex'),checks=[];
assert.equal(packLua("  -- comment\n  local s='-- preserved';\n\n  return s\n"),"local s='-- preserved';\nreturn s");checks.push({name:'format-only-single-line-code-and-string-preserved',passed:true,simulated:true});
for(const [name,s]of [['long-string','return [[content]]'],['long-equals-string','return [=[content]=]'],['long-comment','--[[content]]'],['continued-string',"local s='a\\\nb'"],['continued-crlf-string',"local s='a\\\r\nb'"]]){assert.throws(()=>packLua(s));checks.push({name:'format-packer-rejects-'+name,passed:true,simulated:true});}
const casePath='work/nss111/controlled-matched-aba-20261005180738-532c1641';const selected=JSON.parse(fs.readFileSync(casePath+'/selected-private.json'));
const oldRecord=JSON.parse(fs.readFileSync(casePath+'/last-record-private.json'));const owner='1234567890abcdef1234567890abcdef';
const decision={decisions:[{slot:'tcp',protocol:6,downTag:0x8f050000,flow:selected.tcp,validUntilUptime:1},{slot:'udp',protocol:17,downTag:0x8f060000,flow:selected.udp,validUntilUptime:1}]};
const template=packetTemplate(decision,owner,59999);let writers=0,getters=0,neighbors=0;
for(const x of template.expected.nftables){const r=x.rule;if(!r)continue;const name=r.comment.slice(owner.length+1),tag=name.startsWith('tcp_')?0x8e050000:0x8e060000;
 for(const e of r.expr){if(name.includes('neighbor')){if(e.match?.left.meta?.key==='priority'){assert.equal(e.match.right,0);neighbors++;}continue;}
  if(!name.includes('_up'))continue;if(e.mangle?.key.meta?.key==='priority'){assert.equal(e.mangle.value,tag);writers++;}if(e.match?.left.meta?.key==='priority'){assert.equal(e.match.right,tag);getters++;}}
}
assert.equal(writers,2);assert.equal(getters,8);assert.equal(neighbors,4);checks.push({name:'two-uplink-writers-eight-getters-neighbors-zero',passed:true,simulated:true});
let raw=oldRecord.acceleratedState;
for(const slot of ['tcp','udp']){
 const old=JSON.parse(fs.readFileSync(casePath+'/actual-accelerated-state-proof.json')).proof[slot];const up=slot==='tcp'?0x8e050000:0x8e060000;const key='conns.conn.'+old.serial+'.classifiers.dscp.pr.'+(old.ecmOrientation==='client-first'?'flow':'return')+'_qos_tag';
 const find=key+'=0';assert.ok(raw.split('\n').includes(find));raw=raw.replace(find,key+'='+up);
}
assert.equal(validateAcceleratedState(raw,selected).passed,true);checks.push({name:'recorded-identity-uplink-tags-simulated',passed:true,simulated:true});
assert.throws(()=>validateAcceleratedState(oldRecord.acceleratedState,selected));checks.push({name:'original-zero-uplink-tags-rejected',passed:true,simulated:true});
const source=fs.readFileSync(root+'/qos-physical.lua','utf8');const saved=JSON.parse(fs.readFileSync('work/nss8/nss8-htb2-20261001-run.json')).stdout;
const split=saved.indexOf('qdisc '),classes=saved.slice(0,split).replaceAll('20Mbit','30Mbit').replaceAll('19Mbit','29Mbit'),queues=saved.slice(split).replace(/IDLE_PHYSICAL_SHAPER_ATTACHED\n$/,'');
const fixtures=[];
for(const up of [false,true]){const q=up?queues.replaceAll('8f','8e'):queues,c=up?classes.replaceAll('8f','8e'):classes;const label=up?'uplink':'downlink';
 for(const f of [{name:'full-recorded-layout',q,c,complete:true,pass:true},{name:'target-drift',q:q.replaceAll('target 5ms','target 6ms'),c,complete:true,pass:false},{name:'priority-drift',q,c:c.replaceAll('priority 1','priority 2'),complete:true,pass:false},{name:'unknown-line',q:q+'unknown\n',c,complete:true,pass:false},{name:'duplicate',q:q+q,c,complete:false,pass:false},{name:'missing-rt',q:q.slice(0,q.indexOf(up?'qdisc nssfq_codel 8e06:':'qdisc nssfq_codel 8f06:')),c,complete:true,pass:false},{name:'partial-undo',q:q.slice(0,q.indexOf('qdisc nssfq_codel ')),c:'',complete:false,pass:true}])fixtures.push({...f,name:label+'-'+f.name,up});
}
fixtures.push({name:'downlink-tag-not-valid-uplink-layout',q:queues,c:classes,complete:true,pass:false,up:true});
const cap=JSON.parse(fs.readFileSync(root+'/uplink-capacity-private.json')),pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));
assert.equal(cap.boot,pin.boot.trim());const config={qosDevice:'lan4',qosTc:pin.tc,qosModule:pin.qdiscModule,qosBaseline:pin.interfaces.lan4.qdiscs,uplinkDevice:'wan',uplinkIfindex:6,uplinkPhysicalAeId:5,uplinkBaseline:cap.defaultQueues};
const simulator=fs.readFileSync(root+'/qos-lifecycle-fixtures.lua','utf8');const body=`local j=require('luci.jsonc');local M=assert(loadstring([====[${source}]====]))();local f=assert(j.parse([====[${JSON.stringify(fixtures)}]====]));local checks={};for _,v in ipairs(f)do local ok,out=pcall(M.validateNative,v.q,v.c,v.complete,v.up);assert(ok==v.pass,v.name..':'..tostring(out));checks[#checks+1]={name=v.name,passed=true,simulated=true}end;local test=assert(loadstring([====[${simulator}]====]))();for _,v in ipairs(test(M,j,assert(j.parse([====[${JSON.stringify(config)}]====])),[====[${queues}]====],[====[${classes}]====]))do checks[#checks+1]=v end;print(j.stringify({passed=true,checks=checks,configurationWrites=false,hardwareQueueExecution=false}))`;
// Preserve the refused single-message preparation. The transport bounds remain
// unchanged; independent native-parser and command-model checks travel separately.
const originalCommand="lua - <<'NSS112_QOS_RAM'\n"+body+"\nNSS112_QOS_RAM\n";
let refused;try{encode(originalCommand);}catch(e){refused=String(e);}
assert.equal(refused,'Error: Transport length refused');
if(!fs.existsSync(root+'/transport-preparation-refused.json')){
 fs.writeFileSync(root+'/transport-preparation-refused.json',JSON.stringify({passed:false,reason:refused,rawBytes:Buffer.byteLength(originalCommand),sourceSha256:h(originalCommand),routerExecution:false,limitsUnchanged:true},null,2)+'\n',{flag:'wx'});
 fs.writeFileSync(root+'/transport-preparation-refused-private.lua',body,{flag:'wx'});
}
const descriptors=fixtures.map(v=>({name:v.name,up:v.up,complete:v.complete,pass:v.pass,kind:v.name==='downlink-tag-not-valid-uplink-layout'?v.name:v.name.replace(/^(uplink|downlink)-/,'')}));
const nativeBody=`local j=require('luci.jsonc');local M=assert(loadstring([====[${source}]====]))();local baseQ=[====[${queues}]====];local baseC=[====[${classes}]====];local f=assert(j.parse([====[${JSON.stringify(descriptors)}]====]));local checks={};for _,v in ipairs(f)do local q,c=baseQ,baseC;if v.up and v.kind~='downlink-tag-not-valid-uplink-layout'then q=q:gsub('8f','8e');c=c:gsub('8f','8e')end;if v.kind=='target-drift'then q=q:gsub('target 5ms','target 6ms')elseif v.kind=='priority-drift'then c=c:gsub('priority 1','priority 2')elseif v.kind=='unknown-line'then q=q..'unknown\\n'elseif v.kind=='duplicate'then q=q..q elseif v.kind=='missing-rt'then q=q:sub(1,assert(q:find(v.up and'qdisc nssfq_codel 8e06:'or'qdisc nssfq_codel 8f06:',1,true))-1)elseif v.kind=='partial-undo'then q=q:sub(1,assert(q:find('qdisc nssfq_codel ',1,true))-1);c=''end;local ok,out=pcall(M.validateNative,q,c,v.complete,v.up);assert(ok==v.pass,v.name..':'..tostring(out));checks[#checks+1]={name=v.name,passed=true,simulated=true}end;print(j.stringify({passed=true,checks=checks,configurationWrites=false,hardwareQueueExecution=false}))`;
const lifecycleBody=`local j=require('luci.jsonc');local M=assert(loadstring([====[${source}]====]))();local test=assert(loadstring([====[${simulator}]====]))();local checks=test(M,j,assert(j.parse([====[${JSON.stringify(config)}]====])),[====[${queues}]====],[====[${classes}]====]);print(j.stringify({passed=true,checks=checks,configurationWrites=false,hardwareQueueExecution=false}))`;
const cases=[['native',nativeBody,15],['lifecycle',lifecycleBody,5]],ramChecks=[];
const c=await connectRouter();try{for(const [label,text,count]of cases){const e=encode("lua - <<'NSS112_QOS_RAM'\n"+text+"\nNSS112_QOS_RAM\n"),r=receipt(await c.run(e.command),e);const prefix=root+'/qos-'+label+'-qualification-',n=fs.readdirSync(root).filter(x=>x.startsWith('qos-'+label+'-qualification-')&&x.endsWith('raw-private.json')).length+1;fs.writeFileSync(prefix+'attempt'+n+'-raw-private.json',JSON.stringify({...r,transportRawBytes:e.bytes??e.execBytes,transportExecBytes:e.execBytes},null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const q=JSON.parse(r.stdout);assert.ok(q.passed&&q.checks.length===count);ramChecks.push(...q.checks);}}
finally{c.close()}
assert.equal(ramChecks.length,20);checks.push(...ramChecks);const nativeProof={passed:true,checks:ramChecks,configurationWrites:false,hardwareQueueExecution:false,sourceSha256:h(fs.readFileSync(root+'/qos-physical.lua'))};if(fs.existsSync(root+'/qos-native-qualification.json'))assert.deepEqual(JSON.parse(fs.readFileSync(root+'/qos-native-qualification.json')),nativeProof);else fs.writeFileSync(root+'/qos-native-qualification.json',JSON.stringify(nativeProof,null,2)+'\n',{flag:'wx'});
const input={tagPlan:{table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected}};
input.tagPlan.expected.nftables=input.tagPlan.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const payload=buildPayload(input,{qos:source,phase:fs.readFileSync('work/nss69/core-guard-phase.lua','utf8'),classifier:fs.readFileSync('work/nss73/classifier.lua','utf8'),tags:fs.readFileSync('work/nss49/classified-tags.lua','utf8'),normalizer:fs.readFileSync('work/nss49/tag-normalizer.lua','utf8')});
assert.ok(Buffer.byteLength(payload.stagedCode)<=73728);checks.push({name:'complete-payload-within-original-73728-byte-cap',passed:true,bytes:Buffer.byteLength(payload.stagedCode),simulated:false});
fs.writeFileSync(root+'/payload-syntax-private.lua',payload.stagedCode,{flag:'wx'});
for(const file of fs.readdirSync(root).filter(x=>x.endsWith('.mjs'))){const p=spawnSync(process.execPath,['--check',root+'/'+file],{encoding:'utf8',windowsHide:true});assert.equal(p.status,0,p.stderr);}
for(const name of ['fast-path.lua','module-stage-guardian.lua'])assert.equal(h(fs.readFileSync(root+'/'+name)),h(fs.readFileSync('work/nss105/'+name)));
const sourceManifest={};for(const file of fs.readdirSync(root))if(/\.(mjs|py|lua|ps1)$/.test(file)&&!file.includes('private'))sourceManifest[root+'/'+file]=h(fs.readFileSync(root+'/'+file));
const out={passed:true,onlyPhysicalUplinkQosAdded:true,productionExecution:false,nativeGateBinaryChanged:false,maximumStagedBytes:73728,payloadBytes:Buffer.byteLength(payload.stagedCode),guardedWholeBundleCompilationBeforeAnyQueueOrWanWriteStillRequired:true,permanentClassifierPublicationUpTagZeroRetained:true,controlledUplinkTagsDerivedFromCurrentBulkRtClass:true,uplinkCapacitySha256:h(fs.readFileSync(root+'/uplink-capacity-private.json')),checks,sourceManifest};
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks:checks.length,payloadBytes:out.payloadBytes,hardwareExecution:false}));
