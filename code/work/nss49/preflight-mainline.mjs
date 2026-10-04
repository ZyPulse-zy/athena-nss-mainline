import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {buildPayload} from './payload.mjs';
import {packetTemplate} from '../nss16/automatic-leaf-plan.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {connectRouter} from '../nss27/connect-router.mjs';
const root='work/nss49',hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const old=JSON.parse(fs.readFileSync('work/nss25/closed-qualification.json')).dir;
const selected=JSON.parse(fs.readFileSync(old+'/selected-flows-private.json'));
const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));
const wan=JSON.parse(fs.readFileSync('work/nss25/prerequisites-private.json'));
const moduleProof=JSON.parse(fs.readFileSync('work/nss27/runtime-elf-comparison.json'));
const deployment=JSON.parse(fs.readFileSync('work/nss49/deployment-latest.json'));
const cfg=JSON.parse(fs.readFileSync(deployment.localDir+'/config.json'));
assert.equal(moduleProof.passed,true);
assert.equal(hash(fs.readFileSync('work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko')),moduleProof.runtimeSha256);
for(const [source,proof,key] of [['fast-path.lua','aba-qualified.json','sourceSha256'],['classifier.lua','consumer-qualified.json','adapterSha256']]){
 const result=JSON.parse(fs.readFileSync(root+'/'+proof));assert.equal(result.passed,true);assert.equal(hash(fs.readFileSync(root+'/'+source)),result[key]);
}
const owner='c'.repeat(32);
const model=packetTemplate({decisions:[{slot:'tcp',protocol:6,downTag:2399469568,flow:selected.tcp,validUntilUptime:0},{slot:'udp',protocol:17,downTag:2399535104,flow:selected.udp,validUntilUptime:0}]},owner,59999);
model.expected.nftables=model.expected.nftables.filter(x=>x.chain?.name!=='forward'&&x.rule?.chain!=='forward');
const tagPlan={table:model.expected.nftables[0].table.name,owner,mode:'rt',expected:model.expected};
const libraries=Object.fromEntries(['qos','phase','classifier','tags','normalizer'].map((k,i)=>[k,fs.readFileSync(root+'/'+['qos-physical.lua','core-guard-phase.lua','classifier.lua','classified-tags.lua','tag-normalizer.lua'][i],'utf8')]));
const {stagedCode,tagSource}=buildPayload({tagPlan},libraries);assert.ok(Buffer.byteLength(stagedCode)<=73728);
const scoped={wan:5,boot:wan.boot,auth:wan.auth,mode:wan.mode.map(x=>({ifindex:x.ifindex,address:x.address,link_index:x.link_index})),status:{up:wan.status.up,l3_device:wan.status.l3_device,'ipv4-address':wan.status['ipv4-address']}};
for(const slot of ['tcp','udp']){const f=selected[slot];f.classifierKey=[f.wan,f.mark,slot,f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|');}
const plan={mode:'stage',openFrontend:true,owner:'d'.repeat(32),boot:wan.boot,moduleBytes:moduleProof.runtimeBytes,moduleSha256:moduleProof.runtimeSha256,ecmSha256:'681cf250053ba3bb7ec1fe28866862ca989bfd168ccee7386139f71e37cc68e2',frozenHash:'e'.repeat(64),insmodArguments:'register_gate=1 diagnostic_only=0 tcp_ct_id_raw=123 game_ct_id_raw=456',coreGuard:{pid:526,start:'164199449',sha256:wan.coreSha},stateMajor:wan.stateMajor,wanPrerequisites:scoped,selected:{tcp:selected.tcp,udp:selected.udp},tagPlan:{table:tagPlan.table,owner,mode:'rt'},tagPolicyInStagedBundle:true,autoClassified:true,classifierOwner:{base:deployment.base,configSha256:deployment.configHash,workerSha256:cfg.files['worker.lua']},qosStaged:true,qosDevice:'lan4',qosBoot:wan.boot,qosTc:pin.tc,qosModule:pin.qdiscModule,qosBaseline:pin.interfaces.lan4.qdiscs,qosCodeBytes:Buffer.byteLength(stagedCode),qosCodeSha256:hash(stagedCode)};
plan.owner='1ba8793ea5246d08027f63c91eb45da6';plan.frozenHash=hash('bounded complete-parameter compilation fixture');
const values={register_gate:1,diagnostic_only:0};
for(const [slot,name] of [['tcp','tcp'],['udp','game']]){const f=selected[slot];Object.assign(values,{[name+'_ct_id_raw']:((f.id>>>24)|((f.id>>>8)&0xff00)|((f.id<<8)&0xff0000)|(f.id<<24))>>>0,[name+'_server']:f.original.dst,[name+'_source_port']:f.original.sport,[name+'_server_port']:f.original.dport,[name+'_ct_mark']:f.mark,[name+'_nat_address']:f.reply.dst,[name+'_nat_port']:f.reply.dport});}
values.frozen_record_sha256=plan.frozenHash;plan.insmodArguments=Object.entries(values).map(([k,v])=>k+'='+v).join(' ');
const source=fs.readFileSync(root+'/module-stage-guardian.lua','utf8');
const render=p=>source.replace('__PLAN__',()=>JSON.stringify(p)).replace('__CORE_PHASE__','return{}').replace('__QOS_PHYSICAL__','return{}');
const capsule=encode("/usr/bin/lua - <<'NSS27_STAGE_BEGIN'\n"+render(plan)+"\nNSS27_STAGE_BEGIN\n");
const checks={},c=await connectRouter();
try{
 for(const [name,text] of [['guardian',render({syntaxOnly:true})],...Object.entries(libraries),...['fast-path','wan-scope','state-node','read-prerequisites'].map(n=>[n,fs.readFileSync(root+'/'+n+'.lua','utf8')]),['tag-policy',tagSource]]){
  assert.ok(!text.includes(']===]'));
  const e=encode("/usr/bin/lua - <<'NSS27_SYNTAX_ONLY'\nassert(loadstring([===["+text+"]===]));print('SYNTAX_ONLY_PASS')\nNSS27_SYNTAX_ONLY\n");
  const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);assert.equal(r.stdout.trim(),'SYNTAX_ONLY_PASS');checks[name]={sha256:hash(text),execBytes:e.execBytes};
 }
 const e=encode("/usr/bin/lua - <<'NSS27_POLICY_RAM_ONLY'\nlocal p=assert(loadstring([===["+tagSource+"]===]))();print(require('luci.jsonc').stringify(p))\nNSS27_POLICY_RAM_ONLY\n");
 const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);assert.deepEqual(JSON.parse(r.stdout),tagPlan);
}finally{c.close()}
const out={passed:true,observedAt:new Date().toISOString(),readOnly:true,fixtureUsesHistoricalFlowOnlyForCompilation:true,routerMutationAttempted:false,stagedBytes:Buffer.byteLength(stagedCode),stageExecBytes:capsule.execBytes,unchangedTransportExecCeiling:9000,moduleSha256:moduleProof.runtimeSha256,exactPackedPolicyRoundtrip:true,phasedIntegration:true,nativeGateContractPreviouslyQualified:true,abaRuntimeQualified:false,checks};
fs.writeFileSync(root+'/mainline-preflight-qualified.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({...out,checks:Object.keys(checks)}));
